##### Process translations

install:
	pip install babelon

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