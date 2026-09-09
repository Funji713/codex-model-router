---
name: codex-model-router
description: When a technical task needs execution, automatically classify coding, debugging, repository analysis, implementation, architecture, refactor, test, API integration, and AI/ML engineering work, then spawn a subtask at the least costly suitable Codex model and reasoning effort. The parent task receives and reports the completed subtask result. Use for execution tasks, including explicit $codex-model-router requests; do not route merely informational explanations or recommendations.
---

# Codex Model Router

## Goal

Complete the task reliably with the least expensive combination of model capability, reasoning effort, context, and retries. Directly route execution through a selected subtask rather than merely recommending a setting. Prioritize correctness and reliability over cost or speed.

Use this skill with the domain skill that explains how to do the work. This skill decides the smallest justified capability and context budget; it does not replace `surgical-coding-debug`, `project-architecture-workflow`, test guidance, framework guidance, or security guidance.

## Runtime Contract

Treat routing capability as dynamic. Inspect the subtask tools and model choices available in the current host before routing a task.

### Execution-handoff sentinel

The parent must prepend `ROUTED_EXECUTION_SUBTASK: true` to every spawned worker's handoff. This sentinel is definitive: when it is present, the receiving agent is already the selected execution subtask. It must skip all routing-capability checks, must not call `spawn_agent`, and must perform the assigned implementation and validation directly in its own workspace. It must not treat the absence of a nested spawning tool as a blocker.

- Activate by default when the current request needs execution of a technical task. An explicit `$codex-model-router` request is also sufficient. This default applies across conversations for users who install the skill; do not require them to repeat the invocation. Do not route merely informational explanations or recommendations.
- When already running as a subtask, do not route again. Own the assigned implementation and validation locally; recursive delegation is prohibited.
- If the host can spawn a subtask with model and reasoning overrides, use that operation. Select the current host's identifier and reasoning enum that correspond to the policy tier.
- Spawn exactly one execution subtask with `fork_context: false` unless the smallest necessary prior context cannot be restated. Prepend the execution-handoff sentinel, then pass the original task, essential acceptance criteria, selected model tier and reasoning level, workspace or project constraints, and the minimum already-gathered evidence. Do not pass a full conversation merely for convenience.
- Require the subtask to own implementation and validation. Its final report must include completion status, changed paths or produced artifacts, validation commands and results, known limitations, and a concise handoff for the parent task.
- The parent task waits only when it needs the completed result, reviews the returned result or change artifact, then reports the outcome to the user. Do not duplicate the implementation in the parent task. Close the completed subtask after its result has been captured.
- Never claim a subtask ran or routing occurred unless the spawn operation and completion result succeeded. Report the subtask identifier and selected settings after success.
- If the host cannot spawn a selected subtask, stop before implementation and report that automatic routing is unavailable. Do not fall back to advisory execution unless the user explicitly permits it.
- Respect an explicit user model or reasoning choice. It overrides automatic selection for that route.

Read [routing-policy.md](references/routing-policy.md) before a non-trivial classification. Use [route_task.py](scripts/route_task.py) when a deterministic score or a testable execution route is useful; it validates policy only and does not itself call host tools.

## Route The Task

1. Separate the request into independently verifiable phases when that reduces capability or reasoning requirements. Do not split a tightly coupled problem merely to use cheaper models.
2. For each phase, classify scope, reasoning, ambiguity, dependencies, risk, and context need. Do not infer complexity from prompt length or changed-file count alone.
3. Apply the score, override rules, and phase rules from `routing-policy.md`.
4. Start with Minimum Required Context: target files, then direct callers or imports, then the related module, then repository-wide search only when earlier stages cannot resolve a material unknown.
5. Select the lowest suitable current-host model and reasoning identifiers, then spawn one subtask. Prefer one subtask that owns the work over parallel duplication.
6. Wait only for the needed completion result. Review the subtask report or returned change artifact, then report the result from the parent task.
7. If spawning or completion fails, report the concrete failure and do not continue implementation in the parent task.

## Tier Defaults

Use the current host's available model identifiers. The conceptual tiers are:

| Tier | Default use | Reasoning default |
| --- | --- | --- |
| Luna | Clear, localized, mechanical, and reversible work | Low |
| Terra | Normal engineering, Django/API work, integration, moderate debugging, and multi-file implementation | Medium |
| Sol | Architecture, difficult unknown root causes, broad dependency analysis, or high-cost changes | High |
| Astra | Last escalation for exceptional multi-system reasoning after a justified lower-tier attempt, or when explicitly required | Extra-high candidate |

Do not turn this table into a rigid mapping. Apply the large-but-mechanical and small-but-difficult overrides before escalating.

## Failure And Phase Control

- Treat command errors, missing packages, permissions, bad test setup, and syntax mistakes as execution failures. Fix the execution issue; do not raise model tier or reasoning effort.
- Before escalating a reasoning failure, first check whether evidence or context is missing. Do not replace missing callers, error traces, schemas, contracts, or tests with deeper reasoning.
- After one or two meaningful, evidence-backed attempts at the same reasoning level fail, close the completed subtask and route one follow-up subtask at an appropriate higher tier. Do not retry unchanged hypotheses indefinitely.
- De-escalate once the uncertain phase is complete. Architecture analysis can require Sol and high reasoning while implementation against an approved plan can use Terra and medium; deterministic cleanup can use Luna or Terra and low.

## Task-Specific Routing

- Route focused bug fixes through `surgical-coding-debug`. Reproduce, inspect the smallest relevant context, test the hypothesis, patch the proven cause, and validate narrowly.
- Route architecture work through `project-architecture-workflow`. Use Sol only when the architecture, migration boundary, compatibility, or dependency risk actually warrants it; a small service addition is often Terra.
- Treat normal Python, Django, Django REST Framework, FastAPI, REST API, JavaScript, HTML/CSS, Docker, database, standard inference API, and known-contract integration work as Terra by default, not Sol.
- Treat AI/ML pipeline architecture, multi-model orchestration, model serving design, unexplained inference behavior, and complex training or inference dependencies as Sol candidates.

## User-Facing Messages

Keep classification details internal. Report actual routing concisely:

```text
Subtask `agent_...` completed using Sol + High reasoning. It changed `...`, passed `...`, and returned the following limitation: `...`.
```

```text
This host cannot spawn a subtask with the selected model settings, so I stopped before execution rather than run the task using an unselected model.
```

## Avoid

- Beginning with a full repository scan.
- Defaulting normal work to Sol, Astra, High, or Extra-high reasoning.
- Escalating because many files need the same mechanical change.
- Staying at a high tier after the hard planning or investigation phase is complete.
- Re-reading unchanged files or repeating already rejected hypotheses.
- Executing the routed work in the parent after spawning its subtask.
- Passing the entire parent conversation when a compact handoff is sufficient.
- Treating a failed or unavailable subtask route as a successful model switch.
