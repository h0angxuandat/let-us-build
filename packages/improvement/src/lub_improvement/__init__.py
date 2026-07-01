"""Self-improvement for let-us-build (sia-inspired harness lever).

After a ticket reaches a verifiable outcome, a feedback step reads the trajectory + a per-role
verifier score and writes a Lesson, retrieved into future same-role/type tickets. This IS the
Agile retrospective mechanism (D10). Weight-update (LoRA) lever deferred. Lands in M7.
See `document/system-design.md` §6.
"""

from lub_improvement.lessons import Lesson
from lub_improvement.verifiers import Verifier

__all__ = ["Lesson", "Verifier"]
