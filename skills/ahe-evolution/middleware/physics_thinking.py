"""
Physics Thinking Middleware — inject 5 physics reflex prompts before each LLM call.

These are NOT gate checks. They are pre-reasoning orientation prompts that prime
the agent's attention before it starts thinking. Each prompt targets a specific
physics instinct that experienced physicists exercise before formal reasoning.

The 5 reflexes:
  1. Scale separation    — energy scales, decoupling, which effective theory?
  2. Symmetry→constraint — what does symmetry forbid/allow/protect?
  3. Perturbative instinct— soluble limit? small parameter? strong-correlation?
  4. Phenomenology first — what observable signal? what could be measured?
  5. Approximation awareness — what was dropped? when does it come back?

Only #1-#5 are injected by this middleware. #6 (dimensional analysis) and
#7 (known-limit regression) are mechanized checks → see dimensional_check.py
and limit_check.py.
"""

from . import HookResult, Middleware


PHYSICS_THINKING_INJECTION = """
## PHYSICS THINKING — answer these BEFORE proceeding

Before you begin formal reasoning on this task, briefly orient yourself by
answering the following. If any question does not apply to the current task,
state why and skip it.

### 1. Scale Separation
What are the relevant energy/temperature/length scales? Which is the fastest
degree of freedom, which is the slowest? Can they be decoupled? From which
energy scale does this problem start — UV (microscopic Hamiltonian) or IR
(effective field theory / emergent)?

### 2. Symmetry as Constraint
What symmetries are present (continuous, discrete, gauge)? For each:
- What does it **forbid**? (transitions, terms, phases)
- What does it **allow**? (selection rules, representations)
- What does it **protect**? (degeneracies, gapless modes, topological invariants)

If a symmetry is spontaneously broken: what is the order parameter? How many
Goldstone modes? Is there a Higgs mechanism?

### 3. Perturbative Starting Point
What is the closest exactly solvable limit (free theory, zero coupling,
infinite dimension, classical limit)? What is the small parameter for expansion
around that limit? If no small parameter exists, this is a strong-correlation
problem — what alternative approach applies (exact diagonalization, tensor
networks, holography, bootstrap)?

### 4. Phenomenology First
If the theoretical concept under discussion were correct, what would be the
observable signature? What experiment could measure it? What is the expected
signal magnitude? If you cannot name an observable, flag this concept as
not yet ready for active hypothesis status.

### 5. Approximation Self-Awareness
What approximations or truncations are in play? For each:
- Under what conditions does it fail?
- What is the leading correction you are dropping?
- If those conditions are violated, how does the conclusion change?

If you cannot identify the failure conditions of your approximations, your
confidence should be LOW.
"""


class PhysicsThinkingMiddleware(Middleware):
    """Inject 5 physics reflex prompts before each LLM call.

    The prompts are appended to the last system message so the model sees them
    as part of its core instructions. This is NOT a separate evaluation step —
    it primes the model's internal reasoning orientation.
    """

    def __init__(self, enabled: bool = True, skip_on_turn: int = 0):
        """
        Args:
            enabled: Whether to inject physics thinking prompts.
            skip_on_turn: Skip injection after this many turns (0 = always inject).
                          Useful because the agent internalizes the orientation
                          after a few turns and repeated injection wastes tokens.
        """
        self.enabled = enabled
        self.skip_on_turn = skip_on_turn
        self._turn_count = 0

    def before_model(self, messages: list[dict]) -> HookResult:
        if not self.enabled:
            return HookResult.no_changes()

        if self.skip_on_turn > 0 and self._turn_count >= self.skip_on_turn:
            return HookResult.no_changes()

        self._turn_count += 1

        modified = [dict(m) for m in messages]
        for i, msg in enumerate(modified):
            if msg.get("role") == "system":
                modified[i] = {
                    "role": "system",
                    "content": msg["content"] + "\n" + PHYSICS_THINKING_INJECTION,
                }
                break

        return HookResult.with_messages(modified)

    def reset(self):
        """Reset turn counter (call at start of each new task)."""
        self._turn_count = 0
