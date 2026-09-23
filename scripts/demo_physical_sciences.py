"""Print a deterministic learner-question and teacher-memo demonstration."""

from __future__ import annotations

import argparse
import json
import sys

from assessment_platform.application.physical_sciences_demo import (
    MOMENTUM_TOPIC_ID,
    NEWTON_TOPIC_ID,
    SUPPORTED_DEMO_TOPICS,
    VERTICAL_PROJECTILE_TOPIC_ID,
    WORK_ENERGY_POWER_TOPIC_ID,
    PhysicalSciencesDemoRequest,
    generate_demo,
)
from assessment_platform.core import Difficulty


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--topic",
        choices=("all", *SUPPORTED_DEMO_TOPICS),
        default="all",
        help="supported topic route to demonstrate (default: all)",
    )
    parser.add_argument("--seed", type=int, default=42, help="non-negative deterministic seed")
    parser.add_argument(
        "--difficulty",
        choices=tuple(difficulty.value for difficulty in Difficulty),
        default=Difficulty.MODERATE.value,
    )
    parser.add_argument(
        "--no-visuals",
        action="store_true",
        help="omit learner-facing SVG assets from the demonstration",
    )
    args = parser.parse_args()
    topics = SUPPORTED_DEMO_TOPICS if args.topic == "all" else (args.topic,)
    examples = [
        generate_demo(
            PhysicalSciencesDemoRequest(
                topic=topic,
                seed=args.seed,
                difficulty=Difficulty(args.difficulty),
                include_visuals=not args.no_visuals,
            )
        )
        for topic in topics
    ]
    json.dump(examples[0] if len(examples) == 1 else {"examples": examples}, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
