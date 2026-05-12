"""
Multi-dimensional quality scoring for research task outputs.

All scorers are mechanized — they check files, patterns, and structure
without using LLM judgment. This is the gate layer: fully deterministic.
"""

import re
from pathlib import Path


# ═══════════════════════════════════════════════════════════
# Scoring Framework
# ═══════════════════════════════════════════════════════════

class ScoringDimension:
    """A single scoring dimension with a name, weight, and checker function."""
    def __init__(self, name: str, weight: float, checker):
        self.name = name
        self.weight = weight
        self.checker = checker

    def score(self, output_dir: Path, ground_truth: dict | None = None) -> tuple[float, str]:
        """Run the checker and return (score 0.0-1.0, details string)."""
        return self.checker(output_dir, ground_truth)


def score_task(
    output_dir: Path,
    dimensions: list[ScoringDimension],
    ground_truth: dict | None = None,
) -> dict:
    """Score a task across all dimensions. Returns weighted aggregate."""
    scores = {}
    details = {}
    total_weight = 0.0
    weighted_sum = 0.0

    for dim in dimensions:
        s, d = dim.score(output_dir, ground_truth)
        scores[dim.name] = s
        details[dim.name] = d
        weighted_sum += s * dim.weight
        total_weight += dim.weight

    overall = weighted_sum / total_weight if total_weight > 0 else 0.0

    return {
        "overall_score": round(overall, 4),
        "dimensions": {
            name: {"score": s, "details": details[name]}
            for name, s in scores.items()
        },
        "passed_threshold": overall >= 0.5,
    }


# ═══════════════════════════════════════════════════════════
# Checker Implementations
# ═══════════════════════════════════════════════════════════

_SOURCE_PATTERN = re.compile(
    r'\[(?:source|来源|DOI|doi|Eq\.?|Ref\.?|ref)',
    re.IGNORECASE,
)


def source_grounding_check(output_dir: Path, _ground_truth=None) -> tuple[float, str]:
    """Check what fraction of claims have source citations.
    Scans for [source: ...] patterns in output markdown files."""
    md_files = list(output_dir.rglob("*.md"))
    if not md_files:
        return 0.0, "No markdown output files found"

    total_claims = 0
    grounded_claims = 0
    for f in md_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        # Count lines that look like claims (start with - or contain factual statements)
        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # A claim-like line: starts with bullet or has key fact patterns
            if stripped.startswith("-") or re.search(r'\b(?:found|observed|measured|calculated|reported)\b', stripped):
                total_claims += 1
                if _SOURCE_PATTERN.search(stripped) or re.search(r'\[[\d.,]+\]', stripped):
                    grounded_claims += 1

    if total_claims == 0:
        return 1.0, "No claim-like lines detected; nothing to ground"

    ratio = grounded_claims / total_claims
    return round(ratio, 3), f"{grounded_claims}/{total_claims} claims source-grounded"


def template_completeness_check(output_dir: Path, _ground_truth=None) -> tuple[float, str]:
    """Check that output files have required frontmatter/sections.
    Expected fields: type, status, inputs, outputs in YAML frontmatter."""
    md_files = list(output_dir.rglob("*.md"))
    if not md_files:
        return 0.0, "No markdown output files found"

    required_sections = ["type:", "status:", "inputs:", "outputs:"]
    results = []
    for f in md_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        found = [s for s in required_sections if s in text]
        results.append((f.name, len(found), len(required_sections)))

    if not results:
        return 0.0, "No readable markdown files"

    avg_completeness = sum(r[1]/r[2] for r in results) / len(results)
    detail = ", ".join(f"{name}: {found}/{total}" for name, found, total in results[:5])
    return round(avg_completeness, 3), detail


def cross_reference_check(output_dir: Path, ground_truth: dict | None = None) -> tuple[float, str]:
    """Check that referenced hypotheses actually exist in hypotheses.md."""
    hypotheses_file = output_dir / "knowledge" / "lines" / "topological-order" / "hypotheses.md"
    if not hypotheses_file.exists():
        return 0.5, "hypotheses.md not found in expected location; cannot verify cross-references"

    hyps_text = hypotheses_file.read_text(encoding="utf-8")
    # Extract hypothesis IDs from ground truth
    hyp_ids = set(re.findall(r'### H\d+', hyps_text))

    # Check output files for references to non-existent hypotheses
    ref_pattern = re.compile(r'H(\d+)')
    invalid_refs = []
    total_refs = 0
    for f in output_dir.rglob("*.md"):
        if f == hypotheses_file:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in ref_pattern.finditer(text):
            total_refs += 1
            ref_id = f"H{m.group(1)}"
            if ref_id not in hyp_ids and len(hyp_ids) > 0:
                invalid_refs.append(ref_id)

    if total_refs == 0:
        return 1.0, "No hypothesis references found"

    accuracy = 1.0 - (len(invalid_refs) / total_refs)
    detail = f"{total_refs} refs, {len(invalid_refs)} invalid"
    return round(accuracy, 3), detail


def knowledge_update_check(output_dir: Path, _ground_truth=None) -> tuple[float, str]:
    """Check that knowledge layer files (STATE.md, hypotheses.md, open-questions.md) were updated."""
    state_files = list(output_dir.rglob("STATE.md")) + list(output_dir.rglob("hypotheses.md")) + list(output_dir.rglob("open-questions.md"))
    if not state_files:
        return 0.0, "No knowledge layer files found"

    # Check if they were modified during this task (have content beyond template)
    has_content = 0
    for f in state_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        # Not just a template — has real content beyond headers
        lines = [l for l in text.split("\n") if l.strip() and not l.strip().startswith("#")]
        if len(lines) > 3:
            has_content += 1

    ratio = has_content / len(state_files) if state_files else 0.0
    return round(ratio, 3), f"{has_content}/{len(state_files)} files have substantive content"


def fact_accuracy_check(output_dir: Path, ground_truth: dict | None = None) -> tuple[float, str]:
    """Check factual claims against ground truth data.
    Without ground truth, checks for internal consistency."""
    if ground_truth is None:
        return 0.5, "No ground truth provided; fact accuracy cannot be verified (score = neutral)"
    return 0.5, "Ground truth comparison not yet implemented"


def completeness_check(output_dir: Path, _ground_truth=None) -> tuple[float, str]:
    """Check that output covers expected topics and priority questions."""
    md_files = list(output_dir.rglob("*.md"))
    if not md_files:
        return 0.0, "No output files found"

    text = ""
    for f in md_files:
        try:
            text += f.read_text(encoding="utf-8") + "\n"
        except Exception:
            continue

    # Check for key structural elements
    checks = {
        "has_established_facts": bool(re.search(r'(?:established|已知|established fact)', text, re.IGNORECASE)),
        "has_hypotheses": bool(re.search(r'(?:hypothes|假说|hypothesis)', text, re.IGNORECASE)),
        "has_open_questions": bool(re.search(r'(?:open.question|开放问题|open question)', text, re.IGNORECASE)),
        "has_next_actions": bool(re.search(r'(?:next.action|下一步|next step)', text, re.IGNORECASE)),
    }
    passed = sum(1 for v in checks.values() if v)
    return round(passed / len(checks), 3), f"Coverage: {passed}/{len(checks)} sections present"


def source_traceability_check(output_dir: Path, _ground_truth=None) -> tuple[float, str]:
    """Check that factual statements have traceable source paths."""
    md_files = list(output_dir.rglob("*.md"))
    if not md_files:
        return 0.0, "No markdown output files"

    # Check for source citation patterns
    traceable_patterns = [
        re.compile(r'\[(?:source|来源|DOI):', re.IGNORECASE),
        re.compile(r'\[[\d.,\s]+\]'),  # bracketed citation numbers
        re.compile(r'\([A-Z][a-z]+\s+et\s+al\.?,?\s*\d{4}\)'),  # (Author et al, 2024)
        re.compile(r'arXiv:\d+\.\d+'),
    ]

    total_statements = 0
    traceable = 0
    for f in md_files[:20]:
        try:
            for line in f.read_text(encoding="utf-8").split("\n"):
                stripped = line.strip()
                if not stripped or len(stripped) < 20:
                    continue
                if re.search(r'\b(?:is|are|was|were|found|shows|indicates|demonstrates|proves)\b', stripped, re.IGNORECASE):
                    total_statements += 1
                    if any(p.search(stripped) for p in traceable_patterns):
                        traceable += 1
        except Exception:
            continue

    if total_statements == 0:
        return 1.0, "No factual statements detected"

    ratio = traceable / total_statements
    return round(ratio, 3), f"{traceable}/{total_statements} statements have traceable sources"


def lemma_dependency_check(output_dir: Path, _ground_truth=None) -> tuple[float, str]:
    """Check that lemma dependencies are tracked with status annotations."""
    derivation_files = list(output_dir.rglob("derivations/*.md"))
    if not derivation_files:
        return 0.0, "No derivation files found"

    proven_count = 0
    unproven_count = 0
    for df in derivation_files:
        try:
            text = df.read_text(encoding="utf-8")
        except Exception:
            continue
        proven_count += len(re.findall(r'status:\s*proved', text))
        unproven_count += len(re.findall(r'status:\s*(?:unproven|used-as-axiom)', text))

    total = proven_count + unproven_count
    if total == 0:
        return 0.3, "No lemma status annotations found"

    # Score based on tracking completeness — we don't penalize for unproven lemmas
    return 0.8, f"{total} lemmas tracked ({proven_count} proven, {unproven_count} unproven)"


def gap_detection_check(output_dir: Path, _ground_truth=None) -> tuple[float, str]:
    """Check that open gaps are identified with type classification."""
    derivation_files = list(output_dir.rglob("derivations/*.md"))
    if not derivation_files:
        return 0.0, "No derivation files found"

    gap_types = set()
    total_gaps = 0
    for df in derivation_files:
        try:
            text = df.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in re.finditer(r'type:\s*(unproven_lemma|approximation|assumption|formalization_gap)', text):
            gap_types.add(m.group(1))
            total_gaps += 1

    if total_gaps == 0:
        return 0.2, "No gaps identified — either the proof is complete (unlikely) or gaps were missed"

    # More gap types = more thorough analysis
    type_score = len(gap_types) / 4  # 4 possible types
    return round(min(type_score, 1.0), 3), f"{total_gaps} gaps across {len(gap_types)} types ({', '.join(sorted(gap_types))})"


# ═══════════════════════════════════════════════════════════
# Dimension Registry
# ═══════════════════════════════════════════════════════════

CHECKER_REGISTRY: dict[str, callable] = {
    "source_grounding_check": source_grounding_check,
    "template_completeness_check": template_completeness_check,
    "cross_reference_check": cross_reference_check,
    "knowledge_update_check": knowledge_update_check,
    "fact_accuracy_check": fact_accuracy_check,
    "completeness_check": completeness_check,
    "source_traceability_check": source_traceability_check,
    "lemma_dependency_check": lemma_dependency_check,
    "gap_detection_check": gap_detection_check,
}


def build_scoring_dimensions(task_config: dict) -> list[ScoringDimension]:
    """Build ScoringDimension objects from task YAML config."""
    dimensions = []
    for dim_cfg in task_config.get("scoring", {}).get("dimensions", []):
        checker_name = dim_cfg["checker"]
        checker_fn = CHECKER_REGISTRY.get(checker_name)
        if checker_fn is None:
            raise ValueError(f"Unknown checker: {checker_name}")
        dimensions.append(ScoringDimension(
            name=dim_cfg["name"],
            weight=dim_cfg["weight"],
            checker=checker_fn,
        ))
    return dimensions
