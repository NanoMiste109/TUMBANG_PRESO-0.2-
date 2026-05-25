
from abc import ABC, abstractmethod


def points_from_power(power: int) -> int:
    if power >= 67:
        return 20
    if power >= 34:
        return 10
    return 5


class Character(ABC):

    def __init__(self, name: str, health: int = 0):
        self.name = name
        self.health = health  

    @abstractmethod
    def attack(self) -> str:
        pass

    @abstractmethod
    def special_skill(self) -> str:
        pass

    def sync_health(self, score_value: int) -> None:
        self.health = max(0, int(score_value))

    def compute_hit_points(self, power: int, special_active: bool) -> int:
        return points_from_power(power)

    def miss_penalty_amount(
        self,
        would_have_scored: int,
        special_active: bool,
        normal_miss_penalty: int,
    ) -> int:

        if special_active:
            return would_have_scored + 10
        return normal_miss_penalty


class JoseCharacter(Character):

    MAX_POWER_CAP = 110
    POWER_BOOST = 15

    def __init__(self):
        super().__init__(name="Jose", health=0)

    def attack(self) -> str:
        return "Jose throws a steady slipper shot!"

    def special_skill(self) -> str:
        return "Jose uses Steady Aim — higher maximum throw power!"

    def compute_hit_points(self, power: int, special_active: bool) -> int:
        if special_active:
            boosted = min(self.MAX_POWER_CAP, power + self.POWER_BOOST)
            return points_from_power(boosted)
        return points_from_power(power)


class BongCharacter(Character):

    HIT_MULTIPLIER = 2

    def __init__(self):
        super().__init__(name="Bong", health=0)

    def attack(self) -> str:
        return "Bong throws a fast low slipper shot!"

    def special_skill(self) -> str:
        return "Bong uses Doble Hampas — double points on a successful hit!"

    def compute_hit_points(self, power: int, special_active: bool) -> int:
        base = points_from_power(power)
        if special_active:
            return base * self.HIT_MULTIPLIER
        return base


class MariaCharacter(Character):

    def __init__(self):
        super().__init__(name="Maria", health=0)

    def attack(self) -> str:
        return "Maria throws a high arc slipper shot!"

    def special_skill(self) -> str:
        return "Maria uses Sipag — coming soon in the full game."


class GuardCharacter(Character):

    def __init__(self):
        super().__init__(name="Guard", health=0)

    def attack(self) -> str:
        return "Guard throws a heavy defensive slipper shot!"

    def special_skill(self) -> str:
        return "Guard uses Bantay Mode — coming soon in the full game."


_CHARACTER_BY_INDEX = {
    0: JoseCharacter,
    1: BongCharacter,
    2: MariaCharacter,
    3: GuardCharacter,
}


def character_from_index(index: int) -> Character:
    cls = _CHARACTER_BY_INDEX.get(index, JoseCharacter)
    return cls()
