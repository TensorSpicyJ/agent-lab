# Problem Attribute Schema v0.1

This document defines the task-level and per-problem metadata fields used by included physics benchmarks.

## Suite-level fields

| Field | Meaning |
| --- | --- |
| `source_dataset` | Original dataset or benchmark source |
| `source_url` | Primary URL for the source benchmark |
| `suite_type` | Whether the local task is an original subset, public subset, custom variant, etc. |
| `answer_format` | Expected answer container, such as JSON scalar answers or Python code |
| `grading_mode` | Main scoring mode, such as result-only numeric grading or executable hidden checks |
| `verifier_style` | Concrete local verification mechanism |
| `multimodal_dependency` | Whether figures/images are required |
| `question_style` | Natural-language style of the problem statements |
| `primary_capabilities` | Main capabilities the suite probes |
| `benchmark_lane` | Role of the suite in the broader benchmark stack |

## Per-problem fields

| Field | Meaning |
| --- | --- |
| `order` | Local order inside the task |
| `local_field` / `local_function` | Local answer key or function identifier |
| `source_partition` | Original dataset file or split when available |
| `original_problem_id` | Original problem identifier in the source benchmark |
| `original_collection` / `source_collection` | Source-side category or collection |
| `original_book_family` | Underlying textbook family when known |
| `public_title` / `short_label` | Human-readable short name |
| `physics_domain` | Main physics area |
| `physics_subdomain` | More specific area inside the domain |
| `secondary_domain` | Secondary or cross-cutting area if needed |
| `task_type` | Problem style, such as textbook numeric word problem, scaling-law identification, or analytic expression derivation |
| `reasoning_profile` | Typical reasoning moves required to solve the problem |
| `target_declaration` / `target_declarations` | Lean declaration or declarations targeted by formal tasks |
| `source_module` / `source_modules` | Source Lean module or modules for formal tasks |
| `answer_object` | Shape of the answer: scalar, python function, etc. |
| `answer_unit` | Unit of the returned answer if applicable |
| `output_semantics` / `answer_semantics` | What physical quantity or relation the answer represents |
| `difficulty_band` / `original_difficulty_level` | Coarse local difficulty band or source difficulty level |
| `educational_level` | Typical training level implied by the problem |
| `frontier_relevance` | Low / medium / high relevance to research-style physics benchmarking |
| `uses_hidden_parameters` | Whether the local benchmark hides parameters or tests |
| `public_visibility` | Whether the problem is from a public release page |
| `figure_required` | Whether a figure is needed to solve the problem |
| `multiple_choice` | Whether the original task is multiple-choice |
| `code_interface` | For code-answer tasks, the required function signature and semantic meaning of inputs |

## Design rule

Every included benchmark task should eventually carry a `problem-metadata.yaml` file so that:
- tasks can be filtered by physics domain and subdomain
- tasks can be grouped by answer format and verifier style
- benchmark growth does not destroy provenance
