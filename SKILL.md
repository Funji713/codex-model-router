---
name: codex-model-router
description: Classify coding, debugging, repository analysis, implementation, architecture, refactor, test, API integration, and AI/ML engineering tasks to recommend the least costly suitable Codex model tier, reasoning effort, and context strategy. Use to prevent unnecessary model escalation, broad repository reads, repeated failed attempts, and overthinking. Do not use for non-technical writing or tasks where model selection is irrelevant.
---

# Codex Model Router

## Goal

Complete the task reliably with the least expensive combination of model capability, reasoning effort, context, and retries. Prioritize correctness and reliability over cost or speed.

Use this skill with the domain skill that explains how to do the work. This skill decides the smallest justified capability and context budget; it does not replace `surgical-coding-debug`, `project-architecture-workflow`, test guidance, framework guidance, or security guidance.

## Runtime Contract

Treat routing capability as dynamic. Inspect the tools and model choices available in the current host before proposing a route.

- A skill cannot change the model or reasoning effort of the current task unless the host explicitly exposes that operation.
- A separate task or subagent may support model and reasoning overrides, but create or configure one only when the user explicitly authorizes that delegation for the current task.
- Never claim a model was changed, a subagent ran, or routing occurred unless the actual tool call succeeded.
- When direct routing is unavailable or unauthorized, use advisory mode: recommend the smallest suitable model and reasoning effort only when the current setup is insufficient or a clear downgrade opportunity exists.
- Respect an explicit user model or reasoning choice. Warn once if it creates a material reliability risk, then continue as requested.

Read [routing-policy.md](references/routing-policy.md) before a non-trivial classification. Use [route_task.py](scripts/route_task.py) when a deterministic score or a testable recommendation is useful; it is an advisory calculator, not a model-switching mechanism.

## Route The Task

1. Separate the request into independently verifiable phases when that reduces capability or reasoning requirements. Do not split a tightly coupled problem merely to use cheaper models.
2. For each phase, classify scope, reasoning, ambiguity, dependencies, risk, and context need. Do not infer complexity from prompt length or changed-file count alone.
3. Apply the score, override rules, and phase rules from `routing-policy.md`.
4. Start with Minimum Required Context: target files, then direct callers or imports, then the related module, then repository-wide search only when earlier stages cannot resolve a material unknown.
5. Execute silently when the current model and reasoning are sufficient. Give a concise recommendation only for a necessary upgrade, a meaningful de-escalation, or an explicitly requested route explanation.

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
- After one or two meaningful, evidence-backed attempts at the same reasoning level fail, recommend one appropriate escalation. Do not retry unchanged hypotheses indefinitely.
- De-escalate once the uncertain phase is complete. Architecture analysis can require Sol and high reasoning while implementation against an approved plan can use Terra and medium; deterministic cleanup can use Luna or Terra and low.

## Task-Specific Routing

- Route focused bug fixes through `surgical-coding-debug`. Reproduce, inspect the smallest relevant context, test the hypothesis, patch the proven cause, and validate narrowly.
- Route architecture work through `project-architecture-workflow`. Use Sol only when the architecture, migration boundary, compatibility, or dependency risk actually warrants it; a small service addition is often Terra.
- Treat normal Python, Django, Django REST Framework, FastAPI, REST API, JavaScript, HTML/CSS, Docker, database, standard inference API, and known-contract integration work as Terra by default, not Sol.
- Treat AI/ML pipeline architecture, multi-model orchestration, model serving design, unexplained inference behavior, and complex training or inference dependencies as Sol candidates.

## User-Facing Messages

Keep routing decisions internal by default. Use one concise message only when a user action is needed:

```text
Recommended model: Sol + High reasoning - the root cause remains ambiguous across multiple modules after targeted investigation.
```

```text
The architecture is settled; the remaining deterministic work can continue with Terra + Medium reasoning to save usage.
```

If the user elects to continue with the current setup, continue without repeated warnings.

## Avoid

- Beginning with a full repository scan.
- Defaulting normal work to Sol, Astra, High, or Extra-high reasoning.
- Escalating because many files need the same mechanical change.
- Staying at a high tier after the hard planning or investigation phase is complete.
- Re-reading unchanged files or repeating already rejected hypotheses.
- Confusing a recommendation with a successful model switch or delegated run.
