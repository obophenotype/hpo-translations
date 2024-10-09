# How to maintain your language profile

You have already added your language profile to the [HPO translation repository](https://github.com/obophenotype/hpo-translations/tree/main/babelon), and now it is time to update your language translations.

To remind yourself of the general process, please watch this introductory video again: <iframe src="https://drive.google.com/file/d/1hbIA-EzdTbm72WXQYK9L9N7f6mni4goB/preview" width="640" height="480" allow="autoplay"></iframe>

There are two important kinds changes that are typically maintained: new values (like HPO phenotype names) need to be translated, or changes to existing names need to be confirmed.

## Translating new, as of yet untranslated values

- The official HPO translation pipeline can be found [here](https://github.com/obophenotype/human-phenotype-ontology/tree/master/src/translations).
- All untranslated values can be found in the file called `hp-*-not-translated.babelon.tsv`. For an example (Czech translation), [see here](https://github.com/obophenotype/human-phenotype-ontology/blob/master/src/translations/hp-cs-not-translated.babelon.tsv). This file contains all values for all terms that are currently not translated in your language profile.
- We suggest to download this TSV file, and open it in the program of your choice (Google sheets, Excel) and add translations for all values. Change the translation status to something suitable, like `OFFICIAL` or `CANDIDATE`.
- Add all your newly updated translations to your translation profile in the [HPO translation repository](https://github.com/obophenotype/hpo-translations/tree/main/babelon), e.g. [this file for the Czech translation](https://github.com/obophenotype/hpo-translations/blob/main/babelon/hp-cs.babelon.tsv). We also call this file the "source of truth". If you update your translations, you should always remember to update this file!
- Open a Pull Request on the repository, and you are done! Alternatively, if you do not have the technical expertise for making a pull request yourself, please open an issue on the [issue tracker](https://github.com/obophenotype/hpo-translations/issues) with a link to your updated TSV file, and a request to update the current one. We assume that the link you provide contains _all_ your translations, so we will download the file, and overwrite whatever you have currently stored in the [HPO translation repository](https://github.com/obophenotype/hpo-translations/tree/main/babelon). If you do not have a GitHub account, please email the profile to the [HPOIE contacts](contact.md).

## Confirming changed values

HPO labels and definitions are revised on a regular basis. Similar to the case of new values (see above), the HPO release pipeline will create files that contain all the updated values [here](https://github.com/obophenotype/human-phenotype-ontology/tree/master/src/translations).

- All updated values can be found in the file called `hp-*-changed.babelon.tsv`. For an example (Czech translation), [see here](https://github.com/obophenotype/human-phenotype-ontology/blob/master/src/translations/hp-cs-changed.babelon.tsv).
- Download this file, and update your translation profile in the [HPO translation repository](https://github.com/obophenotype/hpo-translations/tree/main/babelon), e.g. [this file for the Czech translation](https://github.com/obophenotype/hpo-translations/blob/main/babelon/hp-cs.babelon.tsv) as follows:
   1. For each updated value, update the value in `source_value` column (the column with the orginial HPO value). This confirms that it is, indeed, that value that you are translating.
   1. Update, if needed, your translation (`translated_value`).
   1. Update the translation status, if needed (for example, to `OFFICIAL`).
- Follow the instructions for updating the source of truth in the section above (the translation of untranslated values)
