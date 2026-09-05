# Codex Model Router

Automatically classifies an explicitly routed technical task, then runs it in one selected Codex subtask with the least costly suitable model and reasoning effort. The parent task receives the subtask's validated handoff and reports the result.

## Install

Run this in PowerShell to install directly into your local Codex skills directory:

```powershell
git clone https://github.com/Funji713/codex-model-router.git "$env:USERPROFILE\.codex\skills\codex-model-router"
```

To update an existing installation:

```powershell
git -C "$env:USERPROFILE\.codex\skills\codex-model-router" pull --ff-only
```

Start a new Codex task after installation if the current task does not discover the skill.

## Use

Explicitly invoke it with the task that should be routed:

```text
$codex-model-router Investigate the failing checkout integration, implement the smallest verified fix, and run the focused tests.
```

The parent task scores scope, reasoning, ambiguity, dependencies, risk, and context need. It opens one execution subtask with the chosen model and reasoning setting. That subtask owns implementation and validation, then returns changed paths, test results, and any remaining limitations to the parent.

If the current host cannot create a selected subtask, the skill stops rather than silently executing with an unselected model.

See [SKILL.md](SKILL.md) for the routing contract and [routing-policy.md](references/routing-policy.md) for the scoring and escalation policy.
