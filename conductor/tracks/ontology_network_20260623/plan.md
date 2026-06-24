# Plan - Define ontology network outputs for terminology triangulation, validation, and downstream artifacts

This plan coordinates the ontology network across UMLS, SNOMED CT, MedDRA, ICD-10, ICD-11, LOINC, MeSH, OMIM, Orphanet, DECIPHER, FMA, PATO, MP, uPheno, EFO, DO, OncoTree, and LDDB.

## Phase Dependency Note
Phase 1 is the upstream registry contract for individual ontology tracks. Phases 3 and 4 depend on source-governance outputs from UMLS, SNOMED CT, MedDRA, ICD-10, ICD-11, LOINC, MeSH, OMIM, Orphanet, DECIPHER, FMA, PATO, MP, uPheno, EFO, DO, OncoTree, and LDDB integration tracks.

## Implementation Result
Implemented as payload-free ontology-network governance artifacts generated from Conductor track metadata. The current implementation emits source registry, source access matrix, strict schemas, payload policy, release manifest, fail-fast samples, validation fixtures, crosswalk graph, language comparison packs, conflict heatmap, coverage summary, semantic drift report, provenance graph, review workload report, language review packs, license/access report, reproducibility capsule, and validation report. Raw, licensed, credentialed, or full source payload ingestion remains gated to the individual source tracks and local-only policies.

## Phase 0: Dependency, Blocker, Source, and Automation Gates
- [x] **Task 1:** Populate the network-level blocker registry.
  - Record dependency blockers across UMLS, SNOMED CT, MedDRA, ICD-10, ICD-11, LOINC, MeSH, OMIM, Orphanet, DECIPHER, FMA, PATO, MP, uPheno, EFO, DO, OncoTree, and LDDB.
  - Identify which downstream outputs are blocked by source access, license constraints, missing authority, schema gaps, or review capacity.
- [x] **Task 2:** Build the source access matrix before implementation.
  - For every ontology, capture access mode, license status, supported languages, GitHub repository, authoritative endpoint, local-only requirements, and whether source payloads can be committed.
  - Classify each ontology as open, restricted, API-only, local-only, documentation-only, or investigation-only.
- [x] **Task 3:** Define the restricted payload policy for the full network.
  - Establish repository-wide allowlists and denylists for raw payloads, derived rows, bounded samples, validation reports, and review packs.
  - Require local-only manifests and redaction proof before any track commits artifacts derived from restricted sources.
- [x] **Task 4:** Define fail-fast probes for every source class.
  - Each source track must prove one record end to end before bulk extraction, including registry row, provenance row, validation output, and candidate comparison or crosswalk edge when applicable.
  - Stop downstream network phases if any source class cannot pass its probe or has unresolved redistribution risk.
- [x] **Task 5:** Publish the shared artifact contract.
  - Define schemas and owners for registry records, crosswalk edges, multilingual comparison packs, conflict reports, coverage summaries, provenance manifests, validation fixtures, local-only manifests, and reviewer handoff packs.
  - Mark each artifact as committed, generated, local-only, PR-safe, release-safe, or reviewer-only.
- [x] **Task 6:** Set priority, write ownership, and parallelization groups.
  - Use P0 for conductor validation and network contracts, P1 for open ontology tracks, P2 for restricted-source governance tracks, and P3 for investigation-only or uncertain-source tracks.
  - Assign one merge owner per shared schema or generated artifact and allow parallel agents only on disjoint source folders.
- [x] **Task 7:** Define automated lifecycle gates.
  - Every phase requires local validation, task commit, conductor-review, authorized fix application, fix commit, phase push, GitHub Actions verification, and metadata update.
  - Track completion requires PR creation, PR-head checks passing, merged PR verification, and merge commit recorded.
- [x] **Task 8:** Define advanced evidence and telemetry outputs.
  - Capture model/agent telemetry, runtime, token/cost fields when available, source-version provenance, semantic-drift score, conflict heatmap inputs, reviewer workload estimates, and candidate-only LLM labels.

## Phase 1: Network Registry
- [x] **Task 1:** Create a registry schema for ontology source, version, license, access mode, languages, GitHub repository, and authoritative download or API endpoint.
- [x] **Task 2:** Populate the registry from the individual ontology tracks.
- [x] **Task 3:** Classify sources as open, restricted, API-only, local-only, or documentation-only.

## Phase 2: Translation Triangulation
- [x] **Task 1:** Define how multilingual labels and synonyms from each source can support HPO translation candidate review.
- [x] **Task 2:** Generate language-specific comparison packs for HPO labels, HPO synonyms, ontology labels, ontology synonyms, and LLM candidates.
- [x] **Task 3:** Report agreement, disagreement, missing source coverage, and source-specific caveats without promoting candidates automatically.

## Phase 3: Identifier Network
- [x] **Task 1:** Build a crosswalk graph keyed by HPO identifier, external identifier, mapping predicate, mapping source, and confidence.
- [x] **Task 2:** Prefer existing curated mappings from HPO, UMLS, Orphanet, DO, SNOMED CT, ICD, and other authoritative sources before text matching.
- [x] **Task 3:** Emit conflict reports for one-to-many, many-to-one, circular, deprecated, or ambiguous mappings.

## Phase 4: Non-Translation Outputs
- [x] **Task 1:** Produce ontology coverage summaries by HPO branch, language, predicate, source, access class, and review status.
- [x] **Task 2:** Produce provenance manifests for every generated work item, review pack, crosswalk, comparison pack, validation fixture, and import artifact.
- [x] **Task 3:** Produce validation fixtures for translation import dry-runs, source registry checks, restricted-payload exclusion, and regression tests.
- [x] **Task 4:** Produce license and access reports that identify which outputs can be committed, which are PR-safe, which are release-safe, and which must remain local-only.
- [x] **Task 5:** Produce semantic drift reports between source releases and the HPO release used for candidate generation.
- [x] **Task 6:** Produce conflict heatmaps for one-to-many, many-to-one, deprecated, circular, and language-specific disagreements.
- [x] **Task 7:** Produce reviewer workload estimates and active-learning queues ordered by impact, disagreement, coverage gap, and source confidence.
- [x] **Task 8:** Produce provenance graph exports and reproducibility capsules with commands, source versions, permitted checksums, validation output, and local-only manifest references.

## Phase 5: Review and Release Surface
- [x] **Task 1:** Define review-pack formats for maintainers, language reviewers, and ontology/domain reviewers.
- [x] **Task 2:** Add release packaging rules that exclude restricted source payloads while retaining manifests and reproducible instructions.
- [x] **Task 3:** Add CI checks that fail on missing provenance, missing license classification, or accidental restricted-payload inclusion.

## Phase 6: Integration With Existing Tracks
- [x] **Task 1:** Link each individual ontology track to the shared registry and network outputs.
- [x] **Task 2:** Link translation-agent outputs to ontology-network evidence without changing candidate review policy.
- [x] **Task 3:** Document which ontology-network outputs are required before any candidate translation profile is submitted upstream.
