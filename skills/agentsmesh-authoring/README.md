# AgentsMesh Authoring Skill

A reusable AgentsMesh skill for AI coding assistants that author canonical config for rules, hooks, skills, agents, commands, MCP, permissions, ignore patterns, and project targets.

## Install into an AgentsMesh project

Copy this folder to:

```
<your-project>/.agentsmesh/skills/agentsmesh-authoring/
```

Its `SKILL.md` is the entry point. Supporting files in `references/` and `examples/` must stay alongside it. Ensure the project's `agentsmesh.yaml` has the `skills` feature enabled (or omits `features`, which enables all), then from the project root:

```
agentsmesh lint
agentsmesh diff
agentsmesh generate
agentsmesh check
```

For a pre-existing project with unimported native tool config, inspect the diff carefully and use AgentsMesh's import workflow before generation to avoid overwriting hand-authored files.

## Official references

Source: https://github.com/sampleXbro/agentsmesh
Documentation: https://samplexbro.github.io/agentsmesh/

These examples are illustrative, not a deployable policy. In particular, the MCP sample references a server script that you must implement, and the hook sample assumes your project has an npm lint script.
