import argparse
import json
from pathlib import Path
from typing import Any, cast

DEFAULT_WORKFLOWS = Path("translation_workflows/candidate_workflows.json")


def load_workflows(path: Path = DEFAULT_WORKFLOWS) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return cast(dict[str, Any], json.load(file))


def list_workflows(path: Path = DEFAULT_WORKFLOWS) -> None:
    data = load_workflows(path)
    defaults = data["defaults"]
    print("workflow_id\tlanguage\tlane\tcoding_agent\tmodel\treview_policy")
    for workflow in data["workflows"]:
        print(
            "\t".join(
                [
                    workflow["workflow_id"],
                    workflow["language"],
                    workflow["lane"],
                    defaults["coding_agent"],
                    defaults["model"],
                    defaults["review_policy"],
                ]
            )
        )


def show_workflow(workflow_id: str, path: Path = DEFAULT_WORKFLOWS) -> None:
    data = load_workflows(path)
    for workflow in data["workflows"]:
        if workflow["workflow_id"] == workflow_id:
            merged = {**data["defaults"], **workflow}
            print(json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True))
            return
    raise ValueError(f"Unknown workflow_id: {workflow_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect LLM-assisted translation workflow definitions.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list")
    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("workflow_id")
    args = parser.parse_args()

    if args.command == "list":
        list_workflows()
    elif args.command == "show":
        show_workflow(args.workflow_id)


if __name__ == "__main__":
    main()
