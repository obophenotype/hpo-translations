# Human Phenotype Ontology Internationalization Effort

We are in the process of forming the Human Phenotype Ontology Internationalization Effort (HPOIE) at the moment, and its final organisation is yet to be determined. The (provisional) purpose of the HPOIE is to coordinate the translation efforts surrounding the [Human Phenotype Ontology](https://github.com/obophenotype/human-phenotype-ontology). This entails:

1. Fostering collaboration between different groups translating the same language.
2. Standardising the representation of the translation profiles, capturing rich metadata that can be used by downstream sources to seperate, for example, professional, manual translations from automated ones.
3. Coordinating the release of language profiles in step with HPO releases.

It is our vision that eventually we can break down language barriers entirely and enable not only cross-border phenotyping (for example in national rare disease registries) but also cross-border ontology curation.

## Organisation

### Human Phenotype Ontology Internationalization Effort Operations Committee:

- Sebastian Koehler (@drseb)
- Nicolas Matentzoglu (@matentzn)

HPOIE Operations is responsible for cross-language coordination, translation onboarding and the release processes of the language profiles. HPOIE Operations does not concern itself with any specific translation effort.

### Join a Language Working Group

Reach out on the [issue tracker](https://github.com/obophenotype/hpo-translations/issues) if you want to join any of the Language Working Groups.

A list of all translation efforts and working groups can be found [here](https://obophenotype.github.io/hpo-translations/translations/).

## Contributing a translation

- [How to submit a translation](https://obophenotype.github.io/hpo-translations/submit/)
- [How to manage your translation](https://obophenotype.github.io/hpo-translations/maintain/)

The HPOEI does not concern itself how you perform translations (i.e. how to actually _do_ the translations, which apps you use etc). We expect you to provide translations in one of two ways:

1. XLIFF, as exported by Crowdin. We support an HPO translation community here: https://crowdin.com/project/hpo-translation. Reach out on the [issue tracker](https://github.com/obophenotype/hpo-translations/issues) if you want to join any of the teams on Crowdin.
2. [Babelon](https://github.com/monarch-initiative/babelon) TSV files on Google sheets. The format is table-based and closely aligned with xliff. We use it internally to manage language translations. This is the recommended format if you choose to use Google sheets to manage your translations ([see here](https://obophenotype.github.io/hpo-translations/submit/)).

Currently only Crowdin and Babelon TSV is supported by the HPOEI, but feel free to reach out if you wish to submit your translations in a different format.
