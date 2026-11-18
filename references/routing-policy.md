# Routing Policy

## Activation And Runtime

Automatically route requests requiring technical execution, including explicit `$codex-model-router` requests. Do not route informational explanations or recommendations, even when they name the skill or a model. UI metadata keeps `allow_implicit_invocation: true`.

Inspect the host's spawning tool, available model identifiers, and each selected model's supported reasoning levels. If the host cannot create the selected subtask, stop and report that routing is unavailable. An unavailable explicit choice must be reported; never silently substitute another model or effort.

The helper recommends settings. Supply `--available-models` and `--supported-reasoning` from the actual host when available. Without a reasoning map, the parent must verify the recommendation before spawning. With a supplied map, the route blocks if the selected model is omitted or its listed reasoning levels exclude the selected effort. The helper reports these conditions separately.

## Parent And Subtask Contract

Spawn one execution worker at a time with model and effort overrides and minimal inherited context. For `spawn_agent`, use `fork_turns: "none"`, `model`, and `reasoning_effort`; adapt enum casing to the host. Prepend `ROUTED_EXECUTION_SUBTASK: true`, then provide the task, acceptance criteria, selected settings, project constraints, and minimum evidence.

The sentinel tells the worker to implement and validate locally without routing again. Its final response includes completion status, changed paths/artifacts, validation commands and results, and remaining limitations. The parent reviews and reports the returned result without repeating implementation. Release the worker if the host supports that operation.

## Model Selection Order

Unless the user explicitly chooses a model, select the first available model in the chosen tier:

| Tier | Model preference order | Automatic reasoning |
| --- | --- | --- |
| Mechanical | `gpt-6.1-terra`, `gpt-6.2-sol` | Low, or Medium for bounded local reasoning |
| Scoped | `gpt-6.1-terra`, `gpt-6.2-sol` | Medium for eligible scoped tasks |
| Workhorse | `gpt-6.2-sol` | Medium, or High at score 12+, reasoning 3+, small difficult work, or two meaningful reasoning failures |
| Frontier | `gpt-6.2-astra`, `gpt-6.2-sol` | High, XHigh, Max, or Ultra according to the effort gates below |

Models outside the table require an explicit user choice and host support. Fallbacks preserve the required reasoning effort. The route blocks when the tier has no available model or the selected model lacks the required effort.

The helper's `--explicit-model` and `--explicit-reasoning` represent user choices. A supported explicit effort takes precedence at every score and capability.

## Complexity Score

Score each dimension from 0 to 4 using concrete evidence; intermediate values represent intermediate difficulty. Missing files, traces, or contracts call for gathering context, rather than inflated ambiguity scores.

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Scope | One local edit | Several related files | Cross-cutting repository change |
| Reasoning | Mechanical | Non-obvious local logic | Novel or multi-stage reasoning |
| Ambiguity | Exact acceptance criteria | Some assumptions needed | Competing requirements or behavior remain unclear after inspection |
| Dependencies | Isolated code | One internal or external dependency | Multiple interacting services, frameworks, or contracts |
| Risk | Easily reversible | Behavior or data change | Security, migration, production, or irreversible risk |
| Context | Target file supplied | Direct dependencies needed | History, architecture, or broad discovery required |

| Total | Starting route |
| --- | --- |
| 0–4 | Mechanical / Low; difficult reasoning still overrides this route |
| 5–11 | Workhorse / Medium |
| 12–14 | Workhorse / High |
| 15–24 | Frontier when the direct selection gate below is met, otherwise Workhorse / High |

For a well-defined scoped code fix or visual/computer-use workflow with clear inputs, acceptance criteria, and verification, use Scoped / Medium at scores 5–11 when reasoning and risk are below 3 and no mechanical, difficult, settled-plan, verification, or escalation override applies. Set `--scoped-task` only for such work; it does not override higher-risk or difficult routing.

### Frontier Capability

Select Frontier immediately when **all** of these hold:

- Total score is at least **15**.
- Reasoning is at least **3**.
- Ambiguity **or** dependencies is at least **3**.

Record the concrete evidence supporting the qualifying dimensions. This permits direct selection for a coupled architecture, difficult multi-system failure, or novel design; a failed Sol attempt is not required.

For a smaller task that misses the total or supporting-dimension threshold, select Frontier when reasoning is at least 3 and there is a written exceptional-complexity rationale. Examples include a novel concurrency proof, a difficult algorithm with interacting invariants, or a demonstrated Workhorse capability gap after relevant evidence is present. In the helper, supply both `--frontier-justified` and `--frontier-evidence "concrete rationale"`.

### Frontier Reasoning Effort

After phase and mechanical overrides, apply these gates in order to a Frontier route. Use the same effort if Sol is selected as the Frontier fallback.

| Effort | Required evidence | Example |
| --- | --- | --- |
| Ultra | Total 21+, reasoning 4, ambiguity 3+, and dependencies 3+ | Design a cross-service data migration with conflicting recovery requirements and interacting cutover contracts. |
| Max | Total 19+, reasoning 4, and either ambiguity or dependencies 3+ | Design a multi-service cutover with clear acceptance criteria and tightly coupled data, rollback, and release contracts. |
| XHigh | Total 17+, or reasoning 4 with a documented exceptional Frontier rationale | Prove interacting invariants in a localized lock-free algorithm that qualifies through the exceptional route. |
| High | Other Frontier work | Trace a coupled failure at score 15 when the dependency contracts are understood. |

Use observed task difficulty to score the gates. File count, high stakes, broad context, and domain names are insufficient on their own. Recover tooling failures and gather missing context before reconsidering difficulty. The thresholds are policy heuristics. The historical benchmark predates these gates, and their quality and cost tradeoffs have yet to be measured.

## Overrides And Phases

Apply explicit user settings to the final route; automatic overrides below govern the underlying capability need:

| Situation | Route |
| --- | --- |
| Large mechanical rename or generated migration with settled contracts | Mechanical / Low with targeted validation; `--large-mechanical` overrides total score. |
| Small difficult concurrency, security, integrity, or algorithm work | Workhorse / High minimum. Keep Frontier if its evidence gate is met and apply the Frontier effort rules. Use `--small-difficult` for the routing override. Reasoning 3+ also prevents a Mechanical route. |
| Known framework or standard API with clear contracts | Usually Workhorse / Medium; a framework name adds no automatic complexity. |
| Implementation after the uncertain phase is resolved | Workhorse / Medium when the plan is settled; `--phase implementation --settled-plan` makes this explicit. Difficult unresolved implementation still qualifies for Astra. |
| Focused, bounded verification | Mechanical / Low or Medium using `--phase verification --bounded-verification`; keep difficult diagnosis at its required tier. |
| Two meaningful failed reasoning attempts | Raise Mechanical to Workhorse High or Workhorse Medium to High. Apply the Frontier capability and effort gates when difficulty evidence warrants it. |
| Command, environment, dependency, permission failure | Recover the execution condition; do not escalate because of this failure. |
| Missing information | Gather the smallest missing context before spawning or escalating. |

Mechanical work remains Mechanical when it is also implementation against a settled plan. Do not label unresolved contracts or remaining difficult diagnosis as mechanical/bounded. The unavailable-host stop condition takes precedence over recovery and context actions.

For triage and root-cause analysis, score the actual phase. Architecture/design can select Astra directly when eligible. De-escalate once its uncertain work is complete, and avoid splitting tightly coupled reasoning just to obtain a cheaper route.

## Minimum Required Context

Read target files, errors, and failing tests first; then direct callers/imports/tests; then the related module boundary; then broader history or repository evidence only for a material unresolved question. Stop when the phase is sufficiently bounded.

## Compact Internal Record

Keep this record internal unless the user asks for it:

```text
phase=<triage|analysis|design|implementation|verification>
score=<0-24>; capability=<Mechanical|Scoped|Workhorse|Frontier>; model=<host identifier>; reasoning=<host enum>
frontier_evidence=<dimensions and concrete observations supporting capability and effort, or exceptional rationale>
context=<target|direct-dependencies|module|repository>; mode=<subtask|unavailable|blocked|skipped>
next=<single evidence-based next action>
```
