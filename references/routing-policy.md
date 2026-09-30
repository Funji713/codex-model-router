# Routing Policy

## Capability Modes

The router has one direct-execution mode. It does not use advisory fallback by default.

| Mode | When to use it | Result |
| --- | --- | --- |
| Subtask | The host can spawn a subtask with selected model and reasoning, and the user explicitly invoked automatic routing. | Spawn exactly one execution subtask using a compact handoff. The subtask implements and validates; the parent reviews its result and reports it. |

If subtask routing is unavailable, stop and report unavailable automatic routing. Never silently execute at an unselected setting or imply a switch occurred.

## Parent And Subtask Contract

The parent performs classification and sends only `ROUTED_EXECUTION_SUBTASK: true`, the task, acceptance criteria, selected settings, relevant project constraints, and minimum evidence. The execution subtask owns implementation and validation. On seeing the sentinel, it must execute locally rather than attempting to route a nested subtask.

The subtask final response must include:

1. Completion status and a concise result.
2. Changed file paths or produced artifacts.
3. Validation commands and their results.
4. Remaining risk, limitation, or required user action.

The parent waits for the result only when needed, reviews the returned work, reports the outcome, and closes the subtask. It must not repeat the implementation.

## Model Selection Order

At the selected capability tier, choose the first available model in this order unless the user explicitly selects a model:

| Capability tier | Preferred model | Fallbacks | Reasoning range |
| --- | --- | --- | --- |
| Mechanical | `gpt-6-luna` | `gpt-5.6-luna`, `gpt-6.1-sol` | Low; Medium only for bounded local analysis |
| Workhorse | `gpt-6.1-sol` | `gpt-6-sol`, `gpt-5.6-sol`, `gpt-5.6-terra` | Medium by default; High for difficult but evidence-bounded work |
| Frontier | `gpt-6-astra` | `gpt-6.1-sol` at High/ XHigh | High by default; XHigh, Max, or Ultra only after documented evidence that lower reasoning or the workhorse tier was insufficient |

`gpt-5.5` is unsupported for automatic selection. It may be honored only when the user explicitly requests it. Never assume all listed models are present: inspect the host's current model identifiers and supported reasoning levels before spawning.

## Complexity Score

Score each dimension from 0 to 4 using the evidence currently available.

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Scope | One local edit | Several related files | Cross-cutting repository change |
| Reasoning | Mechanical | Non-obvious local logic | Novel or multi-stage reasoning |
| Ambiguity | Exact acceptance criteria | Some assumptions needed | Requirements or behavior are unclear |
| Dependencies | Isolated code | One internal or external dependency | Multiple services, frameworks, or contracts |
| Risk | Easily reversible | Behavior or data change | Security, migration, production, or irreversible risk |
| Context | Target file supplied | Direct dependencies needed | History, architecture, or broad discovery required |

| Total | Default capability | Default model | Reasoning default | Typical work |
| --- | --- | --- | --- |
| 0-5 | Mechanical | `gpt-6-luna` | Low | Formatting, one-file fix, narrow test update |
| 6-12 | Workhorse | `gpt-6.1-sol` | Medium | Normal feature, API endpoint, ordinary bug fix |
| 13-19 | Workhorse | `gpt-6.1-sol` | High | Root-cause analysis, architectural decision, multi-module refactor |
| 20-24 | Frontier candidate | `gpt-6.1-sol` High first; `gpt-6-astra` only if justified | High, then XHigh only if justified | Unfamiliar, high-risk, or genuinely novel system work |

The score is a starting point, not a substitute for judgment.

## Overrides

| Situation | Route |
| --- | --- |
| Large but mechanical rename, migration, or generated edit | `gpt-6-luna` with narrowly scoped tools and validation; use `gpt-6.1-sol` only if contracts or failures make it necessary. |
| Small but difficult concurrency, security, data-integrity, or algorithm issue | `gpt-6.1-sol` High even if few files are involved; Astra needs evidence of exceptional complexity. |
| Known framework convention with clear acceptance criteria | Prefer `gpt-6.1-sol` Medium; do not raise the model merely because a framework is present. |
| User explicitly selects a model or reasoning effort | Honor it for the created or reconfigured route. |

## Minimum Required Context

Acquire context in this order and stop when the task is sufficiently bounded:

1. Read the target file, the failing test, or the exact error.
2. Read direct imports, callers, and tests.
3. Inspect the related module boundary or configuration only if unresolved.
4. Search wider history or the repository only for evidence needed to decide or verify.

Do not inventory the entire repository, reread unchanged files, dump verbose tool output, or request broad context merely to feel safe.

## Failure And Escalation

| Signal | Response |
| --- | --- |
| Command, environment, dependency, or permissions failure | Fix the execution condition. Do not escalate model tier by itself. |
| Missing information | Acquire the smallest missing context or ask one focused question. |
| Two meaningful failed reasoning attempts after relevant context is present | Close the completed subtask. Raise `gpt-6.1-sol` from Medium to High first; select Astra only for a demonstrated model-capability gap, and state the evidence. |
| Risk emerges during implementation | Pause irreversible work, reassess scope and validation, then raise tier only if the analysis requires it. |
| Architecture phase is complete | De-escalate implementation to `gpt-6.1-sol` Medium when the contract is clear. |
| Implementation is mechanical and bounded | De-escalate final edits or test updates to `gpt-6-luna` Low where host capability permits. |

## Phase Routing

| Phase | Preferred route |
| --- | --- |
| Triage and reproduction | `gpt-6-luna` / Low for clear evidence; `gpt-6.1-sol` / Medium if the failure spans a module. |
| Root-cause analysis | `gpt-6.1-sol` / Medium by default; High for multi-layer or unclear failures. |
| Architecture and risk decisions | `gpt-6.1-sol` / High when a real tradeoff exists; use Astra only when `gpt-6.1-sol` has demonstrably insufficient capability. |
| Implementation | `gpt-6.1-sol` / Medium for ordinary changes; `gpt-6-luna` / Low for bounded mechanical work. |
| Focused verification | `gpt-6-luna` / Low unless diagnosing a remaining non-obvious failure. |

## Compact Internal Record

Keep this record internal unless the user asks for it:

```text
phase=<triage|analysis|design|implementation|verification>
score=<0-24>; capability=<Mechanical|Workhorse|Frontier candidate>; model=<host identifier>; reasoning=<Low|Medium|High|XHigh|Max|Ultra>
context=<target|direct-dependencies|module|repository>; mode=<subtask|blocked>
next=<single evidence-based next action>
```
