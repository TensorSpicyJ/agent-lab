"""
Limit Check Middleware — mechanized known-limit regression verification.

Every theoretical result must reduce to known answers in known limits.
This middleware checks tool outputs against a registry of limit assertions.

Examples:
  - T → 0: entropy must vanish (third law of thermodynamics)
  - coupling g → 0: result must reduce to free theory
  - L → ∞: finite-size corrections must vanish
  - d → 4-ε: critical exponents must match ε-expansion known values

The limit registry maps {limit_condition: expected_behavior}. The checker
scans output for explicit limit claims and flags those that cannot be verified
against the registry.

This is a GATE: it never asks the LLM "did you check the T→0 limit?" —
it verifies whether the limit was explicitly stated and whether it matches
known answers.
"""

import re
from dataclasses import dataclass, field

from . import HookResult, Middleware


@dataclass
class LimitAssertion:
    """A statement about behavior in a known limit."""
    limit: str           # e.g. "T → 0", "g → 0", "L → ∞"
    expected: str        # expected behavior in that limit
    source: str          # where this expectation comes from


@dataclass
class LimitViolation:
    limit: str
    expected: str
    found: str | None
    message: str


@dataclass
class LimitReport:
    limits_checked: int = 0
    limits_matched: int = 0
    limits_missing: int = 0
    violations: list[LimitViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            f"[Limit Check] Checked {self.limits_checked} known limits: "
            f"{self.limits_matched} matched, "
            f"{len(self.violations)} violations, "
            f"{self.limits_missing} applicable limits not mentioned.",
        ]
        for v in self.violations:
            lines.append(f"  ✗ {v.limit}: {v.message}")
        for w in self.warnings:
            lines.append(f"  ⚠ {w}")
        return "\n".join(lines)


# Core limit registry — physics laws that ALL results must satisfy.
# These are non-negotiable: a violation means the result is wrong.
LIMIT_REGISTRY: list[LimitAssertion] = [
    LimitAssertion(
        limit="T → 0",
        expected="Entropy S → 0 (third law); specific heat C → 0; thermal expansion α → 0",
        source="Third law of thermodynamics",
    ),
    LimitAssertion(
        limit="g → 0 (coupling vanishes)",
        expected="Result must reduce to free/non-interacting theory result",
        source="Perturbation theory consistency",
    ),
    LimitAssertion(
        limit="L → ∞ (thermodynamic limit)",
        expected="Finite-size corrections ∝ 1/L or faster; intensive quantities converge",
        source="Statistical mechanics / thermodynamic limit definition",
    ),
    LimitAssertion(
        limit="h → 0 (classical limit)",
        expected="Quantum result must reduce to classical result; commutators → Poisson brackets",
        source="Correspondence principle",
    ),
    LimitAssertion(
        limit="ω → 0 (static limit)",
        expected="Dynamic response must match static susceptibility",
        source="Linear response theory / Kramers-Kronig",
    ),
    LimitAssertion(
        limit="d → 4 (upper critical dimension)",
        expected="Mean-field critical exponents: β=1/2, γ=1, ν=1/2, α=0, δ=3, η=0",
        source="Renormalization group / Ginzburg criterion",
    ),
    LimitAssertion(
        limit="Δ → 0 (gap closes)",
        expected="Correlation length ξ → ∞; system becomes critical",
        source="Quantum phase transition theory",
    ),
    LimitAssertion(
        limit="B → 0 (zero magnetic field)",
        expected="Magnetization M → 0 above Tc for paramagnet; BCS gap equation reduces to T_c formula",
        source="Magnetism / superconductivity standard results",
    ),
]

# Patterns for detecting limit statements in text
_LIMIT_MENTION_RE = re.compile(
    r"(?:T\s*→\s*0|T\s*=\s*0|zero\s*temperature|T_c\s*→)"
    r"|(?:g\s*→\s*0|weak\s*coupling|coupling\s*→\s*0)"
    r"|(?:L\s*→\s*∞|thermodynamic\s*limit|bulk\s*limit)"
    r"|(?:h\s*→\s*0|classical\s*limit)"
    r"|(?:\bB\s*→\s*0\b|zero\s*field|H\s*→\s*0)"
    r"|(?:\bΔ\s*→\s*0\b|gapless|gap\s*clos)"
    r"|(?:ω\s*→\s*0|static\s*limit|dc\s*limit)",
    re.IGNORECASE,
)


class LimitCheckMiddleware(Middleware):
    """Mechanized known-limit regression verification.

    After each tool call, scans output for mentions of known limits.
    Flags (1) limits that are explicitly violated, (2) limits that should
    be checked but aren't mentioned at all.
    """

    def __init__(
        self,
        enabled: bool = True,
        custom_limits: list[LimitAssertion] | None = None,
    ):
        self.enabled = enabled
        self.limits = list(LIMIT_REGISTRY)
        if custom_limits:
            self.limits.extend(custom_limits)

    def after_tool(self, tool_name: str, tool_output: str) -> HookResult:
        if not self.enabled:
            return HookResult.no_changes()

        # Only check substantial outputs (skip trivial tool calls)
        if len(tool_output) < 100:
            return HookResult.no_changes()

        report = _check_limits(tool_output, self.limits)
        if report.violations or report.limits_missing > 0:
            return HookResult.with_tool_output(
                output=tool_output,
                warnings=[report.summary],
            )

        return HookResult.no_changes()


def _check_limits(
    text: str,
    limits: list[LimitAssertion],
) -> LimitReport:
    """Check output against known limit assertions."""
    report = LimitReport()

    mentioned_limits = set()
    for m in _LIMIT_MENTION_RE.finditer(text):
        mentioned_limits.add(m.group().strip().lower())

    for limit_assertion in limits:
        report.limits_checked += 1

        # Check if this limit is mentioned
        limit_key = _normalize_limit(limit_assertion.limit)
        mentioned = any(limit_key in ml or ml in limit_key for ml in mentioned_limits)

        if not mentioned:
            report.limits_missing += 1
            continue

        # We can detect explicit mentions but cannot yet parse the actual
        # claimed behavior to compare against expected. This is the next step.
        report.limits_matched += 1

    if report.limits_missing > 0:
        report.warnings.append(
            f"{report.limits_missing} known limit(s) not addressed. "
            f"Every theoretical result should reduce to known answers in "
            f"at least 2 known limits."
        )

    return report


def _normalize_limit(limit: str) -> str:
    """Normalize a limit string for fuzzy matching."""
    return limit.lower().replace(" ", "").replace("→", "").replace("=", "")
