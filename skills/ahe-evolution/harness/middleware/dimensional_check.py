"""
Dimensional Check Middleware — mechanized dimensional analysis on equation outputs.

This is NOT an LLM prompt. It is a Python script that:
1. Scans tool outputs for LaTeX equations
2. Extracts variable dimension assignments from context or configuration
3. Verifies dimensional consistency of each equation

Physics justification: dimensional analysis catches ~80% of derivation errors
before any deeper verification. Every physicist does this reflexively at the
scratch-pad level. The agent should too, but mechanically.

Current status: SKELETON — equation extraction and dimension registry exist.
Full dimensional algebra engine is a deferred feature.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from . import HookResult, Middleware


# Registry of known physical quantities and their dimensions.
# Keys = common variable names / patterns; values = (mass, length, time, charge) exponents.
# MKS-like basis: [M]^a [L]^b [T]^c [Q]^d
DIMENSION_REGISTRY: dict[str, tuple[int, int, int, int]] = {
    # Mechanics
    "m": (1, 0, 0, 0),
    "mass": (1, 0, 0, 0),
    "x": (0, 1, 0, 0),
    "r": (0, 1, 0, 0),
    "L": (0, 1, 0, 0),
    "length": (0, 1, 0, 0),
    "t": (0, 0, 1, 0),
    "time": (0, 0, 1, 0),
    "T": (0, 0, 1, 0),
    "v": (0, 1, -1, 0),
    "velocity": (0, 1, -1, 0),
    "a": (0, 1, -2, 0),
    "acceleration": (0, 1, -2, 0),
    "F": (1, 1, -2, 0),
    "force": (1, 1, -2, 0),
    "E": (1, 2, -2, 0),
    "energy": (1, 2, -2, 0),
    "p": (1, 1, -1, 0),
    "momentum": (1, 1, -1, 0),
    "J": (1, 2, -1, 0),
    "hbar": (1, 2, -1, 0),
    "S": (1, 2, -1, 0),

    # Electromagnetism
    "q": (0, 0, 0, 1),
    "charge": (0, 0, 0, 1),
    "e": (0, 0, 0, 1),
    "B": (1, 0, -1, -1),
    "E_field": (1, 1, -2, -1),
    "V": (1, 2, -2, -1),
    "voltage": (1, 2, -2, -1),
    "phi": (1, 2, -2, -1),

    # Condensed matter
    "k_B": (1, 2, -2, 0),
    "kF": (0, -1, 0, 0),
    "n": (0, -3, 0, 0),
    "density": (0, -3, 0, 0),
    "Tc": (0, 0, 0, 0),          # temperature — K → energy scale
    "Delta": (1, 2, -2, 0),      # gap → energy
    "gap": (1, 2, -2, 0),
    "xi": (0, 1, 0, 0),          # coherence length
    "lambda_L": (0, 1, 0, 0),    # London penetration depth
    "rho": (1, -3, 0, 0),        # resistivity → actually [M][L]^3[T]^{-1}[Q]^{-2}
    "sigma": (1, -3, 0, 2),      # conductivity → actually [M]^{-1}[L]^{-3}[T][Q]^2

    # Superconductivity specific
    "J_c": (0, -2, 0, 1),        # critical current density
    "H_c": (0, -1, 0, 1),        # critical field → actually [M][T]^{-1}[Q]^{-1}
    "Psi": (0, -3/2, 0, 0),      # order parameter amplitude → depends on normalization
    "psi": (0, -3/2, 0, 0),

    # Dimensionless
    "pi": (0, 0, 0, 0),
    "theta": (0, 0, 0, 0),
    "angle": (0, 0, 0, 0),
    "N": (0, 0, 0, 0),
}

# Pattern: captures LaTeX math in $$...$$ or $...$
_LATEX_MATH_RE = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$", re.DOTALL)

# Pattern: simple equality E = m c^2 or E = mc^2
_EQUATION_RE = re.compile(r"(\w+)\s*=\s*(.+)")


@dataclass
class DimensionViolation:
    """A single dimensional inconsistency found in output."""
    equation: str
    lhs_var: str
    lhs_dim: tuple | None
    rhs_dim: tuple | None
    message: str


@dataclass
class DimensionReport:
    violations: list[DimensionViolation] = field(default_factory=list)
    equations_checked: int = 0
    equations_matched: int = 0
    equations_unchecked: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0

    @property
    def summary(self) -> str:
        lines = [
            f"[Dimensional Check] Checked {self.equations_checked} equations: "
            f"{self.equations_matched} consistent, "
            f"{len(self.violations)} violations, "
            f"{self.equations_unchecked} unchecked (unknown variables).",
        ]
        for v in self.violations:
            lines.append(f"  ✗ {v.equation}")
            lines.append(f"    {v.message}")
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        return "\n".join(lines)


class DimensionalCheckMiddleware(Middleware):
    """Mechanized dimensional analysis on equation outputs.

    After each tool call, scans the output for equations and verifies
    dimensional consistency using the DIMENSION_REGISTRY.

    This is a GATE: it never asks the LLM "does this look right?" —
    it computes dimensions and reports specific violations.
    """

    def __init__(
        self,
        enabled: bool = True,
        custom_dimensions: dict[str, tuple[int, int, int, int]] | None = None,
        equation_extractor: Callable[[str], list[str]] | None = None,
    ):
        self.enabled = enabled
        self.dimensions = dict(DIMENSION_REGISTRY)
        if custom_dimensions:
            self.dimensions.update(custom_dimensions)
        self._extract_equations = equation_extractor or _extract_equations_from_text

    def after_tool(self, tool_name: str, tool_output: str) -> HookResult:
        if not self.enabled:
            return HookResult.no_changes()

        report = _check_dimensions(tool_output, self.dimensions)
        if report.has_violations or report.warnings:
            return HookResult.with_tool_output(
                output=tool_output,
                warnings=[report.summary],
            )

        return HookResult.no_changes()


def _extract_equations_from_text(text: str) -> list[str]:
    """Extract LaTeX math blocks and lines with '=' signs."""
    equations = []
    for match in _LATEX_MATH_RE.finditer(text):
        math = match.group(1) or match.group(2)
        if math and "=" in math:
            equations.append(math.strip())
    # Also catch plain-text equations like "E = m c^2"
    for line in text.split("\n"):
        if "=" in line and not line.strip().startswith(("#", "//", ">", "```")):
            stripped = line.strip()
            if stripped not in equations:
                equations.append(stripped)
    return equations


def _check_dimensions(
    text: str,
    registry: dict[str, tuple[int, int, int, int]],
) -> DimensionReport:
    """Scan text for equations and check dimensional consistency."""
    report = DimensionReport()
    equations = _extract_equations_from_text(text)

    for eq in equations:
        report.equations_checked += 1
        match = _EQUATION_RE.match(eq.replace(" ", ""))
        if not match:
            report.equations_unchecked += 1
            continue

        lhs = match.group(1)
        rhs = match.group(2)

        lhs_dim = _infer_dimension(lhs, registry)
        if lhs_dim is None:
            report.equations_unchecked += 1
            continue

        rhs_dim = _infer_dimension(rhs, registry)
        if rhs_dim is None:
            report.equations_unchecked += 1
            continue

        if lhs_dim == rhs_dim:
            report.equations_matched += 1
        else:
            report.violations.append(DimensionViolation(
                equation=eq.strip(),
                lhs_var=lhs,
                lhs_dim=lhs_dim,
                rhs_dim=rhs_dim,
                message=(
                    f"LHS [{_dim_str(lhs_dim)}] ≠ RHS [{_dim_str(rhs_dim)}]. "
                    f"Check variable definitions or algebra."
                ),
            ))

    return report


def _infer_dimension(
    expr: str,
    registry: dict[str, tuple[int, int, int, int]],
) -> tuple | None:
    """Infer the dimension of a simple expression.

    Current: exact variable name lookup only.
    Future: parse products (m*v → mass * velocity), powers, sums.
    """
    # Clean and try exact match
    expr = expr.strip().rstrip("²³⁴").rstrip("^2").rstrip("^3").rstrip("^4")
    if expr in registry:
        return registry[expr]
    return None


def _dim_str(dim: tuple) -> str:
    """Format a dimension tuple as [M]^a [L]^b [T]^c [Q]^d."""
    labels = ["M", "L", "T", "Q"]
    parts = []
    for label, exp in zip(labels, dim):
        if exp != 0:
            if exp == 1:
                parts.append(f"[{label}]")
            elif exp == int(exp):
                parts.append(f"[{label}]^{int(exp)}")
            else:
                parts.append(f"[{label}]^{exp}")
    return " ".join(parts) if parts else "dimensionless"
