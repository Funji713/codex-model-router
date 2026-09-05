# Routing Policy

## Capability Modes

The router has two direct-execution modes. It does not use advisory fallback by default.

| Mode | When to use it | Result |
| --- | --- | --- |
| In-place | The host exposes a successful current-task operation that sets model and reasoning. | Set the selected settings, then execute in the current task. |
| Delegated | The host can create a separate task or subagent with selected model and reasoning, and the user explicitly invoked automatic routing. | Create exactly the needed task in the matching project context; that task executes the work. |

If neither route is available, stop and report unavailable automatic routing. Never silently execute at an unselected setting or imply a switch occurred.

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

| Total | Default tier | Reasoning default | Typical work |
| --- | --- | --- | --- |
| 0-5 | Luna | Low | Formatting, one-file fix, narrow test update |
| 6-12 | Terra | Medium | Normal feature, API endpoint, ordinary bug fix |
| 13-19 | Sol | High | Root-cause analysis, architectural decision, multi-module refactor |
| 20-24 | Sol, then Astra candidate only if justified | High, then Extra-high only if justified | Unfamiliar, high-risk, or genuinely novel system work |

The score is a starting point, not a substitute for judgment.

## Overrides

| Situation | Route |
| --- | --- |
| Large but mechanical rename, migration, or generated edit | Luna with narrowly scoped tools and validation; use Terra only if contracts or failures make it necessary. |
| Small but difficult concurrency, security, data-integrity, or algorithm issue | Sol with High reasoning even if few files are involved. |
| Known framework convention with clear acceptance criteria | Prefer Terra; do not raise the tier merely because a framework is present. |
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
| Two meaningful failed reasoning attempts after relevant context is present | Create a follow-up route one tier or reasoning level higher, and state the evidence. |
| Risk emerges during implementation | Pause irreversible work, reassess scope and validation, then raise tier only if the analysis requires it. |
| Architecture phase is complete | De-escalate implementation to Terra when the contract is clear. |
| Implementation is mechanical and bounded | De-escalate final edits or test updates to Luna where host capability permits. |

## Phase Routing

| Phase | Preferred route |
| --- | --- |
| Triage and reproduction | Luna / Low for clear evidence; Terra / Medium if the failure spans a module. |
| Root-cause analysis | Terra / Medium by default; Sol / High for multi-layer or unclear failures. |
| Architecture and risk decisions | Sol / High when a real tradeoff exists; avoid Astra unless Sol has demonstrably insufficient capability. |
| Implementation | Terra / Medium for ordinary changes; Luna / Low for bounded mechanical work. |
| Focused verification | Luna / Low unless diagnosing a remaining non-obvious failure. |

## Compact Internal Record

Keep this record internal unless the user asks for it:

```text
phase=<triage|analysis|design|implementation|verification>
score=<0-24>; tier=<Luna|Terra|Sol|Astra candidate>; reasoning=<Low|Medium|High|Extra-high>
context=<target|direct-dependencies|module|repository>; mode=<in-place|delegated|blocked>
next=<single evidence-based next action>
```
