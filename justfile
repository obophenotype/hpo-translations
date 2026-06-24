set shell := ["cmd.exe", "/c"]

default:
    just --list

list:
    pixi task list

qc:
    pixi run qc

lint:
    pixi run lint

package:
    pixi run package

diff-audit:
    pixi run diff-audit

audit:
    pixi run audit-translations

agent-export:
    pixi run agent-export

agent-apply-dry-run input:
    pixi run agent-apply-dry-run --input {{input}}

workflow-list:
    pixi run workflow-list

workflow-show workflow_id:
    pixi run workflow-show {{workflow_id}}

profile:
    pixi run profile

update:
    pixi run update

sort-all:
    pixi run sort-all

clean-all:
    pixi run clean-all

pre-commit-install:
    pixi run pre-commit-install

pre-commit-run:
    pixi run pre-commit-run

validate-conductor:
    pixi run validate-conductor

validate-conductor-report:
    pixi run validate-conductor-report

test-conductor-validation:
    pixi run test-conductor-validation

build-ontology-network:
    pixi run build-ontology-network

validate-ontology-network:
    pixi run validate-ontology-network

validate-ontology-network-artifacts:
    pixi run validate-ontology-network-artifacts

check-ontology-network-drift:
    pixi run check-ontology-network-drift

ontology-network:
    pixi run ontology-network
