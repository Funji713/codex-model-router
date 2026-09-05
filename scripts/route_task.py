#!/usr/bin/env python3
"""Deterministic policy checker for direct codex-model-router execution routes."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass


DIMENSIONS = ("scope", "reasoning", "ambiguity", "dependencies", "risk", "context")


@dataclass(frozen=True)
class RouteInput:
    scope: int
    reasoning: int
    ambiguity: int
    dependencies: int
    risk: int
    context: int
    phase: str = "analysis"
    large_mechanical: bool = False
    small_difficult: bool = False
    execution_failure: bool = False
    missing_context: bool = False
    reasoning_failures: int = 0
    routing_capability: str = "delegated"

    @property
    def score(self) -> int:
        return sum(getattr(self, dimension) for dimension in DIMENSIONS)


def base_tier(score: int) -> str:
    if score <= 5:
        return "Luna"
    if score <= 12:
        return "Terra"
    if score <= 19:
        return "Sol"
    return "Astra candidate"


def tier_reasoning(tier: str) -> str:
    return {
        "Luna": "Low",
        "Terra": "Medium",
        "Sol": "High",
        "Astra candidate": "Extra-high",
    }[tier]


def route_task(task: RouteInput) -> dict[str, object]:
    tier = base_tier(task.score)
    notes: list[str] = []

    if task.large_mechanical:
        tier = "Luna"
        notes.append("large mechanical work stays on the low tier with targeted validation")
    elif task.small_difficult:
        tier = "Sol"
        notes.append("small but difficult work overrides file-count assumptions")

    if task.execution_failure:
        notes.append("execution failure requires environment or dependency recovery, not model escalation")
    elif task.missing_context:
        notes.append("acquire the smallest missing context before escalating")
    elif task.reasoning_failures >= 2 and tier == "Luna":
        tier = "Terra"
        notes.append("two meaningful reasoning failures justify one-tier escalation")
    elif task.reasoning_failures >= 2 and tier == "Terra":
        tier = "Sol"
        notes.append("two meaningful reasoning failures justify one-tier escalation")

    if task.phase == "implementation" and task.ambiguity <= 1 and tier in {"Sol", "Astra candidate"}:
        tier = "Terra"
        notes.append("clear implementation de-escalates after analysis")
    elif task.phase == "verification" and task.score <= 12 and not task.small_difficult:
        tier = "Luna"
        notes.append("focused verification uses the low tier")

    context_level = (
        "target"
        if task.context <= 1
        else "direct-dependencies"
        if task.context <= 2
        else "module"
        if task.context <= 3
        else "repository"
    )

    mode = task.routing_capability
    if mode == "unavailable":
        action = "stop: automatic routing is unavailable"
    elif mode == "in-place":
        action = "set the current task model and reasoning, then execute"
    else:
        action = "create a selected routed task, then execute there"

    if task.execution_failure:
        action = "recover execution conditions in the routed task"
    elif task.missing_context:
        action = "acquire minimal missing context before creating the routed task"

    return {
        "mode": mode,
        "phase": task.phase,
        "score": task.score,
        "recommended_tier": tier,
        "recommended_reasoning": tier_reasoning(tier),
        "context_strategy": context_level,
        "action": action,
        "notes": notes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for dimension in DIMENSIONS:
        parser.add_argument(f"--{dimension}", type=int, choices=range(5), default=0)
    parser.add_argument("--phase", choices=("triage", "analysis", "design", "implementation", "verification"), default="analysis")
    parser.add_argument("--large-mechanical", action="store_true")
    parser.add_argument("--small-difficult", action="store_true")
    parser.add_argument("--execution-failure", action="store_true")
    parser.add_argument("--missing-context", action="store_true")
    parser.add_argument("--reasoning-failures", type=int, default=0)
    parser.add_argument("--routing-capability", choices=("in-place", "delegated", "unavailable"), default="delegated")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def run_self_test() -> None:
    cases = (
        (RouteInput(0, 0, 0, 0, 0, 0), "Luna", "Low"),
        (RouteInput(1, 1, 1, 1, 2, 1), "Terra", "Medium"),
        (RouteInput(3, 3, 2, 3, 3, 3), "Sol", "High"),
        (RouteInput(4, 1, 0, 1, 1, 1, large_mechanical=True), "Luna", "Low"),
        (RouteInput(0, 4, 3, 2, 3, 2, small_difficult=True), "Sol", "High"),
        (RouteInput(1, 2, 2, 1, 2, 2, reasoning_failures=2), "Sol", "High"),
        (RouteInput(4, 3, 1, 3, 3, 3, phase="implementation"), "Terra", "Medium"),
        (RouteInput(1, 1, 1, 1, 1, 1, execution_failure=True), "Terra", "Medium"),
        (RouteInput(1, 1, 1, 1, 1, 1, routing_capability="in-place"), "Terra", "Medium"),
        (RouteInput(1, 1, 1, 1, 1, 1, routing_capability="unavailable"), "Terra", "Medium"),
    )
    for task, expected_tier, expected_reasoning in cases:
        result = route_task(task)
        assert result["recommended_tier"] == expected_tier, result
        assert result["recommended_reasoning"] == expected_reasoning, result
    assert route_task(cases[-2][0])["mode"] == "in-place"
    assert route_task(cases[-1][0])["action"] == "stop: automatic routing is unavailable"
    print(f"self-test passed: {len(cases)} routing cases")


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    route_input = RouteInput(**{field: getattr(args, field) for field in RouteInput.__dataclass_fields__})
    print(json.dumps(route_task(route_input), indent=2))


if __name__ == "__main__":
    main()
