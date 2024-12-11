##### Process translations

install:
	pip install -U babelon


sort-%: babelon/hp-%.babelon.tsv babelon/hp-%.synonyms.tsv
	mkdir -p tmp
	{ head -n 1 babelon/hp-$*.synonyms.tsv && tail -n +2 babelon/hp-$*.synonyms.tsv | sort; } > tmp/$*_synonyms_sorted.tsv
	{ head -n 1 babelon/hp-$*.babelon.tsv && tail -n +2 babelon/hp-$*.babelon.tsv | sort; } > tmp/$*_babelon_sorted.tsv
	mv tmp/$*_babelon_sorted.tsv babelon/hp-$*.babelon.tsv
	mv tmp/$*_synonyms_sorted.tsv babelon/hp-$*.synonyms.tsv

clean-%: babelon/hp-%.babelon.tsv babelon/hp-%.synonyms.tsv
	sed -E 's/\t[[:space:]]+/\t/g; s/[[:space:]]+\t/\t/g' babelon/hp-$*.babelon.tsv > temp.tsv && mv temp.tsv babelon/hp-$*.babelon.tsv
	sed -E 's/\t[[:space:]]+/\t/g; s/[[:space:]]+\t/\t/g' babelon/hp-$*.synonyms.tsv > temp.tsv && mv temp.tsv babelon/hp-$*.synonyms.tsv

clean-all:
	$(MAKE) clean-pt clean-de clean-fr clean-pt clean-zh

sort-all:
	$(MAKE) sort-pt sort-de sort-fr sort-pt sort-zh

validate-%: babelon/hp-%.babelon.tsv babelon/hp-%.synonyms.tsv
	tsvalid babelon/hp-$*.babelon.tsv --skip "W1"
	tsvalid babelon/hp-$*.synonyms.tsv --skip "W1"

###
prepare_data:
	rm -rf crowdin_data/
	unzip -d crowdin_data/ all_translations.zip

babelon/hp-%.babelon.tsv:
	mkdir -p babelon/
	babelon parse crowdin_data/$*/hpo_notes.xliff -o $@

LANGUAGES=cs nl tr
HP_TRANSLATIONS=$(patsubst %, babelon/hp-%.babelon.tsv, $(LANGUAGES))

# Recipe: Go to https://crowdin.com/project/hpo-translation/translations# and click "Build and Download"
# Safe the downloaded file as tests/data/all_translations.zip
# Run "make prepare_data" to unpack the translations
# Run "make languages" to process them
# Copy the results into hpo/src/ontology/translations
translations: $(HP_TRANSLATIONS)



.PHONY: help
help:
	@echo "$$data"

define data
Usage: make command

----------------------------------------
	Command reference
----------------------------------------

Core commands:
* prepare_data:	Unpack XLIFF files from ZIP container
* translations:	Compute all Babelon translations from the XLIFF files

endef
export data