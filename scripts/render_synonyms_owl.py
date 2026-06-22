import argparse
import csv
from pathlib import Path
from xml.sax.saxutils import escape


def language_from_template(template_header: list[str]) -> str:
    if len(template_header) < 2:
        raise ValueError("Synonym template is missing the ROBOT template header.")

    marker = template_header[1]
    prefix = "AL oboInOwl:hasExactSynonym@"
    if not marker.startswith(prefix):
        raise ValueError(f"Unsupported synonym template marker: {marker}")
    return marker.removeprefix(prefix)


def render_synonyms(template_path: Path, output_path: Path) -> None:
    with template_path.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="\t")
        columns = next(reader)
        template_header = next(reader)

        subject_index = columns.index("subject_id")
        value_index = columns.index("translation_value")
        language = language_from_template(template_header)

        output_path.parent.mkdir(exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="\n") as output:
            output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            output.write('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n')
            output.write('         xmlns:owl="http://www.w3.org/2002/07/owl#"\n')
            output.write('         xmlns:oboInOwl="http://www.geneontology.org/formats/oboInOwl#">\n')
            output.write('  <owl:Ontology rdf:about=""/>\n')
            for row in reader:
                if len(row) <= max(subject_index, value_index):
                    continue
                subject_id = row[subject_index].strip()
                synonym = row[value_index].strip()
                if not subject_id or not synonym:
                    continue
                iri = subject_id.replace(":", "_")
                output.write(f'  <owl:Class rdf:about="http://purl.obolibrary.org/obo/{escape(iri)}">\n')
                output.write(f'    <oboInOwl:hasExactSynonym xml:lang="{escape(language)}">')
                output.write(escape(synonym))
                output.write("</oboInOwl:hasExactSynonym>\n")
                output.write("  </owl:Class>\n")
            output.write("</rdf:RDF>\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render HPO translation synonym TSV templates to OWL/RDF.")
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    render_synonyms(args.template, args.output)


if __name__ == "__main__":
    main()
