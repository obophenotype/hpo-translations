##### Process translations

###
prepare_data:
	rm -rf tests/data/all_translations
	unzip -d tests/data/all_translations tests/data/all_translations.zip

tests/data/translations/hp-%.babelon.tsv:
	mkdir -p tests/data/translations/
	python src/babelon/cli.py tests/data/all_translations/$*/hpo_notes.xliff $@


LANGUAGES=cs nl tr
HP_TRANSLATIONS=$(patsubst %, tests/data/translations/hp-%.babelon.tsv, $(LANGUAGES))

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