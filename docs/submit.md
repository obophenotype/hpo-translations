# How to submit a HPO language profile for inclusion in the HPO international edition

There are currently two ways we can process a language profile:

1. Crowdin. If you manage your [translation in Crowdin](https://crowdin.com/project/hpo-translation), then we can automatically process it. The only thing you need to do is [contact us](contact.md) and request to be added.
2. Babelon. If your manage your translation by yourself, in Excel, Google Sheets or your own program, you can [submit your translation in the Babelon TSV format](#babelon).

<a id="babelon"></a>

### How to submit your language profile in Babelon format

1. Prepare your spreadsheet using the Babelon format ([introduction](https://github.com/monarch-initiative/babelon/blob/main/README.md), [specification](https://monarch-initiative.github.io/babelon/), [example](https://github.com/obophenotype/hpo-translations/blob/main/examples/hp-zh.babelon.tsv)).
2. It is important to provide the required information exactly as indicated by the [example](https://github.com/obophenotype/hpo-translations/blob/main/examples/hp-zh.babelon.tsv), in particular the formatting of the values. It is important to note that we only process translations of labels and definitions, not synonyms (see next element).
3. If you want to submit your synonyms as well, please use the [ROBOT template](http://robot.obolibrary.org/template) format. For an example in Czech language, [see here](https://github.com/obophenotype/hpo-translations/blob/main/examples/hp-cs.synonyms.tsv). **Please make sure you use the correct [ISO 639-1](https://en.wikipedia.org/wiki/ISO_639-1) language code for your language**. If no code exists in ISO 639-1, you may use [ISO 639-3](https://en.wikipedia.org/wiki/ISO_639-3) instead.
4. Make a pull request to add the TSV files prepared into this directory: https://github.com/obophenotype/hpo-translations/tree/main/babelon. If you do not have the expertise to make a pull request, please email the profile to the [HPOIE contacts](contact.md). Whether you make a pull request or send an email, make sure you provide the following information:
    - Name of the submitter (mandatory)
    - [ORCID](https://orcid.org) of all contributors (for attribution, optional)
    - [ROR](https://ror.org) or [Wikidata ID](https://www.wikidata.org/) of the organisation providing the translation (for attribution, optional)
    - Short description of the translation, how it was made and how it is used (3-5 sentences)

