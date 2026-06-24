import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BABELON_DIR = Path("babelon")
DEFAULT_SUMMARY = Path("translation_audit_summary.tsv")
DEFAULT_WORK_ITEMS = Path("tmp/translation_agent_work_items.jsonl")
CANONICAL_STATUSES = {"OFFICIAL", "CANDIDATE", "NOT_TRANSLATED"}


@dataclass(frozen=True)
class TranslationRow:
    language: str
    row_number: int
    source_language: str
    subject_id: str
    predicate_id: str
    source_value: str
    translation_value: str
    translation_status: str

    @property
    def is_complete(self) -> bool:
        return self.translation_status in {"OFFICIAL", "CANDIDATE"}

    @property
    def needs_translation(self) -> bool:
        return self.translation_status == "NOT_TRANSLATED" or not self.translation_value.strip()


def language_from_path(path: Path) -> str:
    name = path.name
    return name.removeprefix("hp-").removesuffix(".babelon.tsv")


def babelon_paths(language: str | None = None) -> list[Path]:
    if language:
        path = BABELON_DIR / f"hp-{language}.babelon.tsv"
        if not path.exists():
            raise FileNotFoundError(f"No Babelon profile found for language: {language}")
        return [path]
    return sorted(BABELON_DIR.glob("hp-*.babelon.tsv"))


def synonym_path(language: str) -> Path:
    return BABELON_DIR / f"hp-{language}.synonyms.tsv"


def read_translation_rows(path: Path) -> list[TranslationRow]:
    language = language_from_path(path)
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        rows = []
        for row_number, row in enumerate(reader, start=2):
            rows.append(
                TranslationRow(
                    language=language,
                    row_number=row_number,
                    source_language=row.get("source_language", ""),
                    subject_id=row.get("subject_id", ""),
                    predicate_id=row.get("predicate_id", ""),
                    source_value=row.get("source_value", ""),
                    translation_value=row.get("translation_value", ""),
                    translation_status=row.get("translation_status", ""),
                )
            )
        return rows


def count_synonyms(language: str) -> int:
    path = synonym_path(language)
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="\t")
        return max(0, sum(1 for _ in reader) - 2)


def audit_rows(language: str | None = None) -> list[dict[str, Any]]:
    records = []
    for path in babelon_paths(language):
        rows = read_translation_rows(path)
        language_code = language_from_path(path)
        by_status = Counter(row.translation_status or "UNKNOWN" for row in rows)
        by_predicate = Counter(row.predicate_id or "UNKNOWN" for row in rows)
        unknown_statuses = sorted(status for status in by_status if status not in CANONICAL_STATUSES)
        total = len(rows)
        complete = sum(1 for row in rows if row.is_complete)
        needs_translation = sum(1 for row in rows if row.needs_translation)
        records.append(
            {
                "language": language_code,
                "total_rows": total,
                "complete_rows": complete,
                "needs_translation_rows": needs_translation,
                "completion_percent": round((complete / total * 100) if total else 0, 2),
                "official_rows": by_status["OFFICIAL"],
                "candidate_rows": by_status["CANDIDATE"],
                "not_translated_rows": by_status["NOT_TRANSLATED"],
                "label_rows": by_predicate["rdfs:label"],
                "definition_rows": by_predicate["IAO:0000115"],
                "synonym_rows": count_synonyms(language_code),
                "unknown_statuses": ",".join(unknown_statuses),
            }
        )
    return records


def write_summary(records: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True) if output.parent != Path(".") else None
    fieldnames = [
        "language",
        "total_rows",
        "complete_rows",
        "needs_translation_rows",
        "completion_percent",
        "official_rows",
        "candidate_rows",
        "not_translated_rows",
        "label_rows",
        "definition_rows",
        "synonym_rows",
        "unknown_statuses",
    ]
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(records)


def work_item(row: TranslationRow) -> dict[str, Any]:
    return {
        "language": row.language,
        "row_number": row.row_number,
        "subject_id": row.subject_id,
        "predicate_id": row.predicate_id,
        "source_language": row.source_language,
        "source_value": row.source_value,
        "current_translation_value": row.translation_value,
        "current_translation_status": row.translation_status,
        "requested_status": "CANDIDATE",
        "instructions": (
            "Provide a faithful HPO translation for source_value. Return JSONL with "
            "language, subject_id, predicate_id, source_value, translation_value, and translation_status."
        ),
    }


def export_work_items(language: str | None, status: str, limit: int | None, output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", encoding="utf-8", newline="\n") as file:
        for path in babelon_paths(language):
            for row in read_translation_rows(path):
                if status != "*" and row.translation_status != status:
                    continue
                if not row.needs_translation and status == "NOT_TRANSLATED":
                    continue
                file.write(json.dumps(work_item(row), ensure_ascii=False, sort_keys=True) + "\n")
                count += 1
                if limit is not None and count >= limit:
                    return count
    return count


def load_agent_suggestions(path: Path) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    suggestions = {}
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            item = json.loads(line)
            key = (
                item["language"],
                item["subject_id"],
                item["predicate_id"],
                item["source_value"],
            )
            if not item.get("translation_value"):
                raise ValueError(f"Missing translation_value on line {line_number}")
            suggestions[key] = item
    return suggestions


def apply_suggestions(input_path: Path, apply: bool) -> int:
    suggestions = load_agent_suggestions(input_path)
    changed_by_language: dict[str, int] = defaultdict(int)

    for path in babelon_paths():
        language = language_from_path(path)
        with path.open(encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file, delimiter="\t")
            fieldnames = reader.fieldnames
            if fieldnames is None:
                continue
            rows = list(reader)

        changed = 0
        for row in rows:
            key = (language, row["subject_id"], row["predicate_id"], row["source_value"])
            suggestion = suggestions.get(key)
            if not suggestion:
                continue
            if row.get("translation_status") not in {"NOT_TRANSLATED", "CANDIDATE"}:
                continue
            row["translation_value"] = suggestion["translation_value"]
            row["translation_status"] = suggestion.get("translation_status", "CANDIDATE")
            changed += 1

        if changed and apply:
            with path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        changed_by_language[language] += changed

    total = sum(changed_by_language.values())
    for language, count in sorted(changed_by_language.items()):
        if count:
            print(f"{language}\t{count}")
    print(f"total\t{total}")
    if not apply:
        print("dry_run\ttrue")
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit HPO translation completeness and agent work items.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Write translation completeness summary TSV.")
    audit_parser.add_argument("--language")
    audit_parser.add_argument("--output", type=Path, default=DEFAULT_SUMMARY)

    export_parser = subparsers.add_parser("export-work-items", help="Export JSONL work items for translation agents.")
    export_parser.add_argument("--language")
    export_parser.add_argument("--status", default="NOT_TRANSLATED")
    export_parser.add_argument("--limit", type=int)
    export_parser.add_argument("--output", type=Path, default=DEFAULT_WORK_ITEMS)

    apply_parser = subparsers.add_parser("apply-agent-output", help="Apply JSONL translation suggestions.")
    apply_parser.add_argument("--input", type=Path, required=True)
    apply_parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()
    if args.command == "audit":
        records = audit_rows(args.language)
        write_summary(records, args.output)
        print(f"Wrote {len(records)} language audit rows to {args.output}")
    elif args.command == "export-work-items":
        count = export_work_items(args.language, args.status, args.limit, args.output)
        print(f"Wrote {count} work items to {args.output}")
    elif args.command == "apply-agent-output":
        apply_suggestions(args.input, args.apply)


if __name__ == "__main__":
    main()
