---
name: codex-model-router
description: When the user explicitly invokes $codex-model-router to execute a technical task, classify coding, debugging, repository analysis, implementation, architecture, refactor, test, API integration, and AI/ML engineering work, then directly route execution to the least costly suitable Codex model tier and reasoning effort. Use only when the user expects automatic model routing, not merely an explanation or recommendation.
---

# Codex Model Router

## Goal

Complete the task reliably with the least expensive combination of model capability, reasoning effort, context, and retries. Directly route execution rather than merely recommending a setting. Prioritize correctness and reliability over cost or speed.

Use this skill with the domain skill that explains how to do the work. This skill decides the smallest justified capability and context budget; it does not replace `surgical-coding-debug`, `project-architecture-workflow`, test guidance, framework guidance, or security guidance.

## Runtime Contract

Treat routing capability as dynamic. Inspect the tools and model choices available in the current host before routing a task.

- Activate only when the user explicitly invokes `$codex-model-router` or explicitly requests automatic model routing and execution. That request authorizes a routed task for the supplied work; do not implicitly route ordinary coding requests.
- If the host exposes an in-place current-task model and reasoning configuration operation, use it and then execute the task in the current task.
- Otherwise, if the host can create a separate task or subagent with model and reasoning overrides, create one in the matching project, workspace, or worktree context. Pass it the original task, essential acceptance criteria, selected model, selected reasoning effort, and only the minimum context already gathered. The routed task performs the work; do not duplicate implementation in the parent task.
- Never claim a model was changed, a task ran, or routing occurred unless the actual tool call succeeded. Report the created task identifier and selected settings after success.
- If neither direct route is available, stop before implementation and report that the host cannot perform the requested automatic routing. Do not fall back to advisory execution unless the user explicitly permits it.
- Respect an explicit user model or reasoning choice. It overrides automatic selection for that route.

Read [routing-policy.md](references/routing-policy.md) before a non-trivial classification. Use [route_task.py](scripts/route_task.py) when a deterministic score or a testable execution route is useful; it validates policy only and does not itself call host tools.

## Route The Task

1. Separate the request into independently verifiable phases when that reduces capability or reasoning requirements. Do not split a tightly coupled problem merely to use cheaper models.
2. For each phase, classify scope, reasoning, ambiguity, dependencies, risk, and context need. Do not infer complexity from prompt length or changed-file count alone.
3. Apply the score, override rules, and phase rules from `routing-policy.md`.
4. Start with Minimum Required Context: target files, then direct callers or imports, then the related module, then repository-wide search only when earlier stages cannot resolve a material unknown.
5. Select the lowest suitable current-host model and reasoning identifiers, then invoke the available direct-routing operation. Prefer one routed task that owns the work over parallel duplication.
6. Verify the routing tool result before reporting success. If it fails, report the concrete failure and do not continue implementation in the parent task.

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
- After one or two meaningful, evidence-backed attempts at the same reasoning level fail, route a follow-up task one appropriate tier higher. Do not retry unchanged hypotheses indefinitely.
- De-escalate once the uncertain phase is complete. Architecture analysis can require Sol and high reasoning while implementation against an approved plan can use Terra and medium; deterministic cleanup can use Luna or Terra and low.

## Task-Specific Routing

- Route focused bug fixes through `surgical-coding-debug`. Reproduce, inspect the smallest relevant context, test the hypothesis, patch the proven cause, and validate narrowly.
- Route architecture work through `project-architecture-workflow`. Use Sol only when the architecture, migration boundary, compatibility, or dependency risk actually warrants it; a small service addition is often Terra.
- Treat normal Python, Django, Django REST Framework, FastAPI, REST API, JavaScript, HTML/CSS, Docker, database, standard inference API, and known-contract integration work as Terra by default, not Sol.
- Treat AI/ML pipeline architecture, multi-model orchestration, model serving design, unexplained inference behavior, and complex training or inference dependencies as Sol candidates.

## User-Facing Messages

Keep classification details internal. Report actual routing concisely:

```text
Routed to a new task: Sol + High reasoning. It will investigate the ambiguous multi-module root cause and implement the verified fix.
```

```text
Automatic routing is unavailable in this host, so I stopped before execution rather than run the task using an unselected model.
```

## Avoid

- Beginning with a full repository scan.
- Defaulting normal work to Sol, Astra, High, or Extra-high reasoning.
- Escalating because many files need the same mechanical change.
- Staying at a high tier after the hard planning or investigation phase is complete.
- Re-reading unchanged files or repeating already rejected hypotheses.
- Executing the routed task in the parent after creating a routed task.
- Treating a failed or unavailable host route as a successful model switch.
