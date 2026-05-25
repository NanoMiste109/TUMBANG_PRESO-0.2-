"""
Score — demonstrates Operator Overloading.

  score + points   →  adds points, clamps to [0, target]
  score - penalty  →  subtracts, clamps to 0
  score > other    →  compare two Score objects or an int
  score >= other
  int(score)       →  raw integer value
  str(score)       →  "75 / 100"
"""


class Score:
    def __init__(self, value: int = 0, target: int = 100):
        self.target = target
        self._value = max(0, min(value, target))

    # ── properties ──────────────────────────────────────────────────────────
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = max(0, min(int(v), self.target))

    def is_complete(self):
        return self._value >= self.target

    # ── operator overloading ─────────────────────────────────────────────────
    def __add__(self, points):
        """score + 20  →  new Score with value clamped to target."""
        return Score(self._value + int(points), self.target)

    def __iadd__(self, points):
        """score += 20  →  mutate in place."""
        self.value = self._value + int(points)
        return self

    def __sub__(self, penalty):
        """score - 10  →  new Score, floor at 0."""
        return Score(self._value - int(penalty), self.target)

    def __isub__(self, penalty):
        """score -= 10  →  mutate in place."""
        self.value = self._value - int(penalty)
        return self

    def __gt__(self, other):
        other_val = other.value if isinstance(other, Score) else int(other)
        return self._value > other_val

    def __ge__(self, other):
        other_val = other.value if isinstance(other, Score) else int(other)
        return self._value >= other_val

    def __eq__(self, other):
        other_val = other.value if isinstance(other, Score) else int(other)
        return self._value == other_val

    def __int__(self):
        return self._value

    def __str__(self):
        return f"{self._value} / {self.target}"

    def __repr__(self):
        return f"Score({self._value}, target={self.target})"
