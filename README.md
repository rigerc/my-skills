# Nosey registry template

Create shareable AI agent skill registries for [Nosey](https://github.com/rigerc/nosey). This template provides dependency-free generators, identity configuration, validation, and reviewed infrastructure updates.

<!-- BEGIN GENERATED SKILL CATALOG -->

## Skill catalog

Registry: rigerc/my-skills · 16 skills.

Generated from [skills-manifest.json](skills-manifest.json) and [skills-map.json](skills-map.json). Edit those sources or skill frontmatter, then regenerate this section.

Recommendation conditions below are alternatives; matching any condition can recommend a skill. Technology detection is handled by Nosey.

### [agentsmesh-authoring](skills/agentsmesh-authoring/SKILL.md)

Author, edit, migrate, troubleshoot, and validate AgentsMesh canonical configuration \(.agentsmesh rules, hooks, commands, agents, skills, MCP servers, permissions, ignore, lessons, and agentsmesh.yaml\) for multiple AI coding tools.

Available; no automatic recommendation.

### [agnix](skills/agnix/SKILL.md)

Use when asked to lint, validate, troubleshoot, or improve AI coding-agent configuration files \(SKILL.md, AGENTS.md, CLAUDE.md, hooks, MCP, or IDE agent rules\), or to set up agnix checks in CI. Run the agnix CLI, explain its diagnostics, and apply explicitly requested safe fixes across Claude Code, Codex, Cursor, Copilot, Kiro, OpenCode, and related tools.

**Recommended when:**

- agnix is detected \(Python packages: agnix; Rust crates: agnix-cli; config files: .agnix.toml; npm packages: agnix\)

### [fix-anti-slop](skills/fix-anti-slop/SKILL.md)

Diagnose and fix anti-slop Oxlint warnings and errors in TypeScript/JavaScript repositories, including optional Effect rules and oxc/no-accumulating-spread. Use when lint reports anti-slop violations, after installing or updating anti-slop, or when asked to make anti-slop checks pass without suppressing rules or weakening types.

Available; no automatic recommendation.

### [gum-cli](skills/gum-cli/SKILL.md)

Use Charmbracelet Gum to build polished interactive shell scripts with prompts, selectors, filters, spinners, formatting, tables, pagers, logging, and styled terminal output. Use when writing, reviewing, or debugging shell workflows that invoke the \`gum\` CLI.

**Recommended when:**

- Charmbracelet Gum is detected \(.justfile, Justfile, justfile containing any of: /\(^\|\[;&amp;\|\(\)\\s\]\)gum\\s\+\(choose\|confirm\|file\|filter\|format\|input\|join\|pager\|spin\|style\|table\|write\|log\|version-check\)\\b/m \(source extensions: .bash, .fish, .sh, .zsh; ignore hash comments\)\)

### [ink](skills/ink/SKILL.md)

Use when building, debugging, testing, or reviewing an Ink \(React terminal CLI\) application. Covers Ink 8 APIs, Node and React compatibility, components, input/paste, focus, terminal dimensions, scrolling, lifecycle, accessibility, and testing.

**Recommended when:**

- Ink is detected

### [ink-testing-library](skills/ink-testing-library/SKILL.md)

Write, improve, and debug automated tests for React-based Ink terminal/CLI components using the ink-testing-library package. Use when testing rendered terminal output, interactive keyboard input, rerenders, asynchronous UI changes, stdout/stderr frames, or teardown in Ink apps. Do not use for browser React DOM tests or when only a one-shot renderToString assertion is needed.

**Recommended when:**

- Ink is detected

### [justfile-expert](skills/justfile-expert/SKILL.md)

Just command runner expertise — Justfile syntax, recipes, parameters, modules, shebang recipes. Use when authoring justfiles, project commands, or task automation.

**Recommended when:**

- Just is detected

### [knap-skill](skills/knap-skill/SKILL.md)

Write, explain, validate, and render Knap templates for Markdown or text output. Use for Knap variables, filters, conditions, loops, local assignments, CLI rendering, or batch generation; do not apply to unrelated Jinja, Liquid, or Mustache templates.

**Recommended when:**

- Knap is detected \(npm packages: knap\)

### [noctalia-plugin-development](skills/noctalia-plugin-development/SKILL.md)

Develop, maintain, debug, test, and publish Noctalia v5\+ native Wayland shell plugins using plugin.toml manifests and isolated Luau entry scripts. Use for plugin widgets, panels, services, launcher providers, control-center shortcuts, desktop widgets, layer surfaces, declarative ui.\* trees, scripting APIs, cross-entry state, IPC, plugin API compatibility, or Noctalia plugin reviews. Distinguish native Luau plugins from older QML/Quickshell extensions.

**Recommended when:**

- Noctalia native Luau plugins is detected \(plugin.toml containing all of: /^\\s\*entry\\s\*=\\s\*\["'\]\[^"'\\r\\n\]\+\\.luau\["'\]/m, /^\\s\*plugin\_api\\s\*=\\s\*\[0-9\]\+\\b/m \(ignore hash comments\)\)

### [octokit-js](skills/octokit-js/SKILL.md)

Help build, review, and debug JavaScript or TypeScript integrations with GitHub using Octokit.js. Use for GitHub REST and GraphQL requests, pagination, authentication, GitHub Apps, webhook verification, permissions, and safe issue or pull-request automation.

**Recommended when:**

- Octokit.js is detected \(npm packages: @octokit/core, @octokit/rest, octokit\)

### [readme-crafter-skill](skills/readme-crafter-skill/SKILL.md)

Creates repository-specific README.md files that act as landing pages, onboarding guides, and trust signals. Use when the user asks to write, rewrite, improve, audit, localize, or restructure a README, or when a codebase needs a GitHub-facing project overview. Common triggers include "write a README", "improve my README", "generate README.md", "rewrite this project overview", and "make this repo easier to understand". Adapts to libraries, CLI tools, apps, research repos, browser extensions, internal tools, monorepos, and bilingual README workflows.

**Recommended when:**

- README documentation is detected \(config files: README.md\)

### [serena-usage](skills/serena-usage/SKILL.md)

Serena MCP for project memory and code navigation. Use when managing Serena memories, navigating symbols, performing intelligent refactoring, or maintaining context/continuity across AI agent sessions.

**Recommended when:**

- Serena MCP is detected \(MCP server matching pythonPackages: serena-agent; MCP server matching serverNames: serena; configFiles: .codex/config.toml, .cursor/mcp.json, .mcp.json, .vscode/mcp.json\)

### [t3-delegate](skills/t3-delegate/SKILL.md)

Delegate bounded implementation, research, review, design, or test assignments to T3 Code child tasks. Use for requested delegation or independent work where the active host permits it; preserve selected providers, models, and options, collect completion evidence, and integrate results.

Available; no automatic recommendation.

### [ue4ss-bridge](skills/ue4ss-bridge/SKILL.md)

Inspect and manipulate a live, running Unreal Engine game through the ue4ss-bridge MCP server \(UE4SS plus the UEBridge Lua mod\). Use this whenever the user wants to examine UObjects, properties, UFunctions or class hierarchies in a running game; read or change a value live; run Lua inside the game; snapshot/diff or watch/hook values while they play; find out what the camera is aimed at; trigger UE4SS dumps \(usmap, jmap, uht, cxx\); or whenever ue4ss-bridge tools \(bridge\_status, inspect\_object, eval\_lua, snapshot\_object, watch\_property, hook\_function, poll\_events, etc.\) are available. Also trigger on mentions of UE4SS, UEBridge, Unreal game modding or reverse engineering, "the player pawn/controller", or finding offsets and property names in a live game, even if the user never names the tool.

**Recommended when:**

- UE4SS Bridge MCP is detected \(MCP server matching pythonPackages: ue4ss-bridge; MCP server matching serverNames: ue4ss-bridge; configFiles: .codex/config.toml, .cursor/mcp.json, .mcp.json, .vscode/mcp.json\)

### [vhs-cli](skills/vhs-cli/SKILL.md)

Create and verify reproducible terminal recordings using Charmbracelet VHS. Use for .tape authoring, CLI/TUI demos, GIF/MP4/WebM recording, terminal screenshots, and ASCII golden fixtures. Offers simple \(lint without rendering\) and expanded \(render, inspect, review\) workflows.

**Recommended when:**

- Charmbracelet VHS is detected \(file extensions: .tape\)

### [vitest-testing](skills/vitest-testing/SKILL.md)

Write, configure, debug, migrate, and review JavaScript/TypeScript tests with Vitest and Vite. Use for Vitest unit tests, async assertions, mocks/spies, fake timers, DOM or Browser Mode tests, coverage, CI, workspaces, flaky tests, Jest migration, or contributions to vitest-dev/vitest.

**Recommended when:**

- Vitest is detected

<!-- END GENERATED SKILL CATALOG -->

## Create and configure a registry

GitHub's web **Use this template** flow copies files but does not run the configurator. A web-created repository is **unconfigured**: its `registryId` and local skill IDs still use `example/agent-skills`, and its root `AGENTS.md` still contains upstream maintainer instructions. Clone it and explicitly configure it before adding or publishing registry content:

```sh
gh repo clone your-org/your-skills
cd your-skills
node scripts/configure-registry.mjs your-org/your-skills
node scripts/check.mjs
```

Use Node.js 22. The registry requires no `package.json`, npm, `node_modules`, installation, or build step. The `.mjs` CLIs use Node built-ins and relative modules, and each CLI checks the Node version. Configuration rewrites the declared local identity, preserves external skill IDs and custom `$schema` annotations, regenerates the manifest and README catalog, and installs the canonical downstream `AGENTS.md` only when the existing guide is the verified template maintainer guide. A user-authored guide is preserved. The operation is safe to repeat with the same identity.

Validation fetches the two latest public Nosey schemas on every run and fails closed when fetching or evaluating them. It never follows a registry document's `$schema` value. `--schemas dir` supplies local schemas for explicit tests and CI fixtures only.

Add skills under `skills/<name>/SKILL.md`; nested skill directories are supported. Edit `skills-map.json` to associate local or declared external skills with technologies and combinations. Then regenerate and check the committed outputs:

```sh
node scripts/generate.mjs
node scripts/generate.mjs --check
node scripts/validate-registry.mjs
node --test
node scripts/check.mjs
```

Individual generator commands remain supported: `node scripts/generate-manifest.mjs` and `node scripts/generate-readme.mjs`. Every CLI defaults its root to the script location; `--root` and `--schemas` paths are resolved from the caller's current directory. `node scripts/configure-registry.mjs owner/repo [--root dir] [--schemas dir]` configures identity.

The manifest reader extracts only `name` and `description`; it is not a general YAML validator. Quote values that look like numbers, booleans, `null`, or timestamps. Ambiguous or unsupported values may be treated as absent, so a missing name falls back to the skill directory name and a missing description is omitted. Agnix validates skill frontmatter and content.

`node scripts/generate.mjs --check` is read-only. `node scripts/check.mjs` checks generated output, live schema validation, and tests; it does not run Agnix. Run `node scripts/run-agnix.mjs [--strict]` separately when skill content changes. Agnix is separately provisioned, never downloaded by these tools. See [Contributing](CONTRIBUTING.md) for the local commands.

The manual generation workflow is a safety net: its Actions UI defaults to `main`, honors the selected branch for checkout and push, and rejects tag refs. Manual runs bypass the last-bot loop guard; automatic relevant pushes remain limited to `main` and keep the guard. It commits only the generated manifest and README, and skips empty or force pushes.

## Receive template updates

Derived registries receive infrastructure updates through reviewed [template-sync pull requests](.github/workflows/template-sync.yml). Enable Actions and permit it to create pull requests. Add `TEMPLATE_SYNC_TOKEN` as a repository secret with only the repository's Contents, Pull requests, and Workflows write access; do not paste tokens into issues, chat, or files. The built-in `GITHUB_TOKEN` reads the public template; the secret authorizes writes to the derived repository, including workflow updates.

The workflow runs monthly or manually from the Actions tab. Manual runs select an upstream branch (default `main`) and can set `dry_run` to preview without pushing a branch or opening a pull request; the token is still required. Updates target the derived repository's default branch, use independent Git histories, and are never merged automatically. Inspect every proposed diff and require registry CI and Agnix before merging.

The action uses squash merge with `--allow-unrelated-histories --strategy=recursive -X theirs`, so upstream wins conflicts in synchronized files. Review local infrastructure edits on every proposal. Resolve any conflict markers on the PR branch before merging. `.templatesyncignore` is interpreted as Git pathspecs, not `.gitignore` syntax. It protects `skills/**`, `skills-map.json`, `skills-manifest.json`, `README.md`, `LICENSE`, root `AGENTS.md`, and optional downstream `package.json` and lockfiles; retain these exclusions and add local paths that must not be synchronized. Removing the former `my-skills` template wrapper is a separate migration. Upstream removal of its package metadata must not erase customized downstream package metadata or dependencies. The workflow requires a nonempty ignore file. For setup, preview, conflicts, or recovery, follow [Contributing](CONTRIBUTING.md#review-template-sync-updates).

## Use with Nosey

Register a local or published registry separately:

```sh
nosey registry add /path/to/your-skills
nosey scan .
```

```sh
nosey registry add https://github.com/your-org/your-skills.git --ref main
```

Nosey reads registry metadata and does not install or execute skill files during detection. For parser, filesystem, and cross-reference validation, use `nosey registry validate /path/to/your-skills` when the Nosey CLI is available.

## Repository boundaries and attribution

Nosey owns the runtime and registry schema contract. This repository owns the template tooling and its documentation. Schema changes begin in Nosey; update the template's bounded validator and tests in the reviewed compatibility sequence. The template uses Node.js 22 built-ins and relative modules, with no required package manifest, dependencies, install, or build step. The template-sync workflow proposes infrastructure changes; it does not publish or merge them automatically.

This template adapts repository practices from [ianlewis/repo-template](https://github.com/ianlewis/repo-template). See [NOTICE.md](NOTICE.md) for attribution and [LICENSE](LICENSE) for licensing terms.
