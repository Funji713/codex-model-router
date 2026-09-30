#!/usr/bin/env python3
"""Deterministic policy checker for codex-model-router subtask routes."""

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
    routing_capability: str = "subtask"
    available_models: tuple[str, ...] = (
        "gpt-6.1-sol",
        "gpt-6-astra",
        "gpt-6-sol",
        "gpt-6-luna",
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "gpt-5.6-luna",
        "gpt-5.5",
    )
    frontier_justified: bool = False

    @property
    def score(self) -> int:
        return sum(getattr(self, dimension) for dimension in DIMENSIONS)


def base_capability(score: int) -> str:
    if score <= 5:
        return "Mechanical"
    if score <= 19:
        return "Workhorse"
    return "Frontier candidate"


MODEL_PREFERENCES = {
    "Mechanical": ("gpt-6-luna", "gpt-5.6-luna", "gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-5.6-terra"),
    "Workhorse": ("gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-5.6-terra"),
    "Frontier": ("gpt-6-astra", "gpt-6.1-sol"),
}


def select_model(capability: str, available_models: tuple[str, ...], frontier_justified: bool) -> str:
    selection = (
        "Frontier"
        if capability == "Frontier candidate" and frontier_justified
        else "Workhorse"
        if capability == "Frontier candidate"
        else capability
    )
    for model in MODEL_PREFERENCES[selection]:
        if model in available_models:
            return model
    raise ValueError(f"no supported model is available for {selection}: {available_models}")


def select_reasoning(task: RouteInput, capability: str) -> str:
    if capability == "Mechanical":
        return "Medium" if task.reasoning >= 2 and not task.large_mechanical else "Low"
    if capability == "Frontier candidate":
        return "XHigh" if task.frontier_justified else "High"
    if task.phase == "implementation" and task.ambiguity <= 1 and not task.small_difficult:
        return "Medium"
    return "High" if task.small_difficult or task.reasoning >= 3 or task.score >= 13 else "Medium"


def route_task(task: RouteInput) -> dict[str, object]:
    capability = base_capability(task.score)
    notes: list[str] = []

    if task.large_mechanical:
        capability = "Mechanical"
        notes.append("large mechanical work stays on the low tier with targeted validation")
    elif task.small_difficult:
        capability = "Workhorse"
        notes.append("small but difficult work overrides file-count assumptions")

    if task.execution_failure:
        notes.append("execution failure requires environment or dependency recovery, not model escalation")
    elif task.missing_context:
        notes.append("acquire the smallest missing context before escalating")
    elif task.reasoning_failures >= 2 and capability == "Mechanical":
        capability = "Workhorse"
        notes.append("two meaningful reasoning failures justify one-tier escalation")
    elif task.reasoning_failures >= 2 and capability == "Workhorse":
        notes.append("two meaningful reasoning failures justify raising the workhorse reasoning before an Astra escalation")

    if task.phase == "implementation" and task.ambiguity <= 1 and capability == "Frontier candidate":
        capability = "Workhorse"
        notes.append("clear implementation de-escalates after analysis")
    elif task.phase == "verification" and task.score <= 12 and not task.small_difficult:
        capability = "Mechanical"
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
    else:
        action = "spawn a selected execution subtask, then report its completed result to the parent"

    if task.execution_failure:
        action = "recover execution conditions in the routed task"
    elif task.missing_context:
        action = "acquire minimal missing context before spawning the execution subtask"

    model = select_model(capability, task.available_models, task.frontier_justified)
    reasoning = select_reasoning(task, capability)
    if capability == "Frontier candidate" and not task.frontier_justified:
        notes.append("high score begins with gpt-6.1-sol; Astra requires explicit evidence of a workhorse capability gap")
    elif model != "gpt-6-luna" and capability == "Mechanical":
        notes.append("preferred Luna model is unavailable; selected the least-cost compatible fallback")

    return {
        "mode": mode,
        "phase": task.phase,
        "score": task.score,
        "recommended_capability": capability,
        "recommended_model": model,
        "recommended_reasoning": reasoning,
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
    parser.add_argument("--routing-capability", choices=("subtask", "unavailable"), default="subtask")
    parser.add_argument("--available-models", default=",".join(RouteInput.available_models), help="comma-separated host model identifiers")
    parser.add_argument("--frontier-justified", action="store_true", help="evidence supports selecting Astra for an exceptional task")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def run_self_test() -> None:
    cases = (
        (RouteInput(0, 0, 0, 0, 0, 0), "Mechanical", "gpt-6-luna", "Low"),
        (RouteInput(1, 1, 1, 1, 2, 1), "Workhorse", "gpt-6.1-sol", "Medium"),
        (RouteInput(3, 3, 2, 3, 3, 3), "Workhorse", "gpt-6.1-sol", "High"),
        (RouteInput(4, 4, 4, 4, 4, 4), "Frontier candidate", "gpt-6.1-sol", "High"),
        (RouteInput(4, 4, 4, 4, 4, 4, frontier_justified=True), "Frontier candidate", "gpt-6-astra", "XHigh"),
        (RouteInput(4, 1, 0, 1, 1, 1, large_mechanical=True), "Mechanical", "gpt-6-luna", "Low"),
        (RouteInput(0, 4, 3, 2, 3, 2, small_difficult=True), "Workhorse", "gpt-6.1-sol", "High"),
        (RouteInput(1, 2, 2, 1, 2, 2, reasoning_failures=2), "Workhorse", "gpt-6.1-sol", "Medium"),
        (RouteInput(4, 3, 1, 3, 3, 3, phase="implementation"), "Workhorse", "gpt-6.1-sol", "Medium"),
        (RouteInput(1, 1, 1, 1, 1, 1, execution_failure=True), "Workhorse", "gpt-6.1-sol", "Medium"),
        (RouteInput(1, 1, 1, 1, 1, 1, routing_capability="subtask"), "Workhorse", "gpt-6.1-sol", "Medium"),
        (RouteInput(1, 1, 1, 1, 1, 1, routing_capability="unavailable"), "Workhorse", "gpt-6.1-sol", "Medium"),
        (RouteInput(0, 0, 0, 0, 0, 0, available_models=("gpt-5.6-luna",)), "Mechanical", "gpt-5.6-luna", "Low"),
    )
    for task, expected_capability, expected_model, expected_reasoning in cases:
        result = route_task(task)
        assert result["recommended_capability"] == expected_capability, result
        assert result["recommended_model"] == expected_model, result
        assert result["recommended_reasoning"] == expected_reasoning, result
    routed_task = next(task for task, *_ in cases if task.routing_capability == "subtask")
    unavailable_task = next(task for task, *_ in cases if task.routing_capability == "unavailable")
    assert route_task(routed_task)["mode"] == "subtask"
    assert route_task(unavailable_task)["action"] == "stop: automatic routing is unavailable"
    print(f"self-test passed: {len(cases)} routing cases")


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    route_input = RouteInput(
        **{
            field: getattr(args, field)
            for field in RouteInput.__dataclass_fields__
            if field not in {"available_models"}
        },
        available_models=tuple(model.strip() for model in args.available_models.split(",") if model.strip()),
    )
    print(json.dumps(route_task(route_input), indent=2))


if __name__ == "__main__":
    main()
