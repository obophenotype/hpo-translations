import csv
import subprocess
from pathlib import Path
from typing import Any

RecordKey = tuple[str, str, str]
Record = dict[str, Any]
ParsedRecords = dict[RecordKey, Record]


def get_git_file(branch: str, filepath: Path) -> str:
    # Run git show branch:filepath
    # Use forward slashes for git path
    git_path = filepath.as_posix()
    cmd = ["git", "show", f"{branch}:{git_path}"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode == 0:
        return res.stdout
    return ""


def get_baseline_content(filepath: Path) -> str:
    for branch in ["origin/main", "main", "origin/master", "master"]:
        content = get_git_file(branch, filepath)
        if content:
            return content
    return ""


def parse_babelon_tsv(content: str) -> ParsedRecords:
    records: ParsedRecords = {}
    reader = csv.DictReader(content.splitlines(), delimiter="\t")
    if not reader.fieldnames:
        return records
    for row in reader:
        # Key: (subject_id, predicate_id, translation_language)
        sub = row.get("subject_id")
        pred = row.get("predicate_id")
        lang = row.get("translation_language")
        val = row.get("translation_value")
        status = row.get("translation_status")
        if sub and pred and lang:
            records[(sub, pred, lang)] = {
                "value": val,
                "status": status,
                "row": row,
            }
    return records


def compare_records(
    baseline: ParsedRecords,
    current: ParsedRecords,
) -> tuple[
    list[tuple[RecordKey, Any, Any]], list[tuple[RecordKey, Any, Any]], list[tuple[RecordKey, Any, Any, Any, Any]]
]:
    added: list[tuple[RecordKey, Any, Any]] = []
    removed: list[tuple[RecordKey, Any, Any]] = []
    modified: list[tuple[RecordKey, Any, Any, Any, Any]] = []

    # Check all current keys
    for key, curr_data in current.items():
        if key not in baseline:
            added.append((key, curr_data["value"], curr_data["status"]))
        else:
            base_data = baseline[key]
            base_val = base_data["value"]
            base_status = base_data["status"]
            curr_val = curr_data["value"]
            curr_status = curr_data["status"]
            if base_val != curr_val or base_status != curr_status:
                modified.append((key, base_val, base_status, curr_val, curr_status))

    # Check removed keys
    for key, base_data in baseline.items():
        if key not in current:
            removed.append((key, base_data["value"], base_data["status"]))

    return added, removed, modified


def main() -> None:
    babelon_dir = Path("babelon")
    markdown_output: list[str] = []
    markdown_output.append("# Translation Diff Audit Summary\n")

    has_changes = False
    for filepath in sorted(babelon_dir.glob("*.babelon.tsv")):
        current_content = ""
        if filepath.exists():
            with open(filepath, encoding="utf-8") as f:
                current_content = f.read()

        baseline_content = get_baseline_content(filepath)
        if not baseline_content:
            if current_content:
                has_changes = True
                markdown_output.append(f"## {filepath.name} (New File)\n")
                records = parse_babelon_tsv(current_content)
                markdown_output.append(f"Contains {len(records)} translation records.\n\n")
            continue

        baseline_records = parse_babelon_tsv(baseline_content)
        current_records = parse_babelon_tsv(current_content)

        added, removed, modified = compare_records(baseline_records, current_records)

        if added or removed or modified:
            has_changes = True
            markdown_output.append(f"## Changes in `{filepath.name}`\n")
            if added:
                markdown_output.append(f"**Added ({len(added)}):**\n")
                for key, val, status in added[:10]:
                    markdown_output.append(f"- `{key[0]}` ({key[1]}): {val} [{status}]\n")
                if len(added) > 10:
                    markdown_output.append(f"- ... and {len(added) - 10} more\n")
            if removed:
                markdown_output.append(f"**Removed ({len(removed)}):**\n")
                for key, val, status in removed[:10]:
                    markdown_output.append(f"- `{key[0]}` ({key[1]}): {val} [{status}]\n")
                if len(removed) > 10:
                    markdown_output.append(f"- ... and {len(removed) - 10} more\n")
            if modified:
                markdown_output.append(f"**Modified ({len(modified)}):**\n")
                for key, b_val, b_status, c_val, c_status in modified[:10]:
                    markdown_output.append(f"- `{key[0]}` ({key[1]}):\n")
                    markdown_output.append(f"  - Old: {b_val} [{b_status}]\n")
                    markdown_output.append(f"  - New: {c_val} [{c_status}]\n")
                if len(modified) > 10:
                    markdown_output.append(f"- ... and {len(modified) - 10} more\n")
            markdown_output.append("\n")

    if not has_changes:
        markdown_output.append("No changes detected in translation files.\n")

    summary_text = "".join(markdown_output)
    print(summary_text)

    # Save to a file so that GHA can read and post it
    with open("translation_diff_summary.md", "w", encoding="utf-8") as f:
        f.write(summary_text)


if __name__ == "__main__":
    main()
