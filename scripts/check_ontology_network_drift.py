import subprocess
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", "ontology_network"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    changes = result.stdout.strip()
    if changes:
        print("ontology_network generated artifacts are not clean after regeneration:")
        print(changes)
        diff = subprocess.run(
            ["git", "diff", "--", "ontology_network"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if diff.stdout.strip():
            print(diff.stdout)
        raise SystemExit(1)
    print("ontology_network generated artifacts are clean")


if __name__ == "__main__":
    main()
