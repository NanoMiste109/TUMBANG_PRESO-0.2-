"""
Part 3 — Demonstrate Character abstraction output.
Run:  python demo_characters.py
"""

from entities.character import (
    JoseCharacter,
    BongCharacter,
    MariaCharacter,
    character_from_index,
)


def main():
    print("=" * 50)
    print("TUMBANG PRESO — Character Abstraction Demo")
    print("=" * 50)
    print()

    characters = [
        JoseCharacter(),
        BongCharacter(),
        MariaCharacter(),
    ]

    for c in characters:
        print(c.attack())
        print(c.special_skill())
        print(f"{c.name}'s health (score): {c.health}")
        print("-" * 40)

    print()
    print("Factory example (index 0 = Jose):")
    jose = character_from_index(0)
    print(jose.attack())
    print(jose.special_skill())

    print()
    print("Special scoring examples (health = score):")
    jose = JoseCharacter()
    bong = BongCharacter()
    power = 80
    special = True

    jose_hit = jose.compute_hit_points(power, special)
    jose_miss = jose.miss_penalty_amount(jose_hit, special, normal_miss_penalty=10)
    print(f"  Jose special @ power {power}: hit +{jose_hit}, miss -{jose_miss}")

    bong_hit = bong.compute_hit_points(power, special)
    bong_miss = bong.miss_penalty_amount(bong_hit, special, normal_miss_penalty=10)
    print(f"  Bong special @ power {power}: hit +{bong_hit}, miss -{bong_miss}")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
