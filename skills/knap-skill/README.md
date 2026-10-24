# Knap Skill for Codex

A self-contained Codex skill for writing, explaining, validating, and rendering templates with the [Knap](https://www.npmjs.com/package/knap) templating language.

The skill keeps Knap-specific syntax and runtime behavior close at hand—including truthy fallbacks, typed data, filters, loops, CLI validation, and safe batch rendering—without depending on external documentation at runtime.

## What it helps with

- Create Markdown templates from JSON, CSV, or app-provided variables.
- Write conditions, fallbacks, assignments, and nested loops in Knap syntax.
- Apply documented Markdown filters and build custom TypeScript filters.
- Diagnose invalid templates and surprising truthiness or `--set` behavior.
- Design `render` and `batch` commands with safe filenames and dry runs.
- Translate templates from similar languages without carrying over incompatible syntax.

## Install

Clone the repository into your Codex skills directory:

```shell
git clone https://github.com/rigerc/knap-skill.git ~/.codex/skills/knap
```

The skill itself has no runtime dependencies. To execute Knap CLI commands, install Node.js 20 or later and run Knap through `npx` or install the `knap` package.

## Use

Invoke the skill explicitly with `$knap`:

```text
Use $knap to create a reading-note template from this article JSON.
```

```text
Use $knap to add an optional author section and loop over nested references.
```

```text
Use $knap to generate one Markdown file per CSV row, previewing all filenames first.
```

```text
Use $knap to explain why 0 ?? "Unknown" selects the fallback.
```

Codex can also select the skill automatically for requests specifically involving Knap templates.

## Package structure

```text
knap/
├── SKILL.md                 Skill entrypoint and routing
├── agents/openai.yaml       UI metadata and default prompt
└── references/
    ├── language.md          Variables, logic, loops, and comments
    ├── filters.md           Standard, HTML, and custom filters
    └── cli.md               Validation, rendering, and batches
```

The files under `references/` are packaged with the skill and contain the guidance it needs. The repository's `docs/` directory preserves the original source material but is not required by the installed skill.

## Validate changes

From the repository root, run the validator bundled with Codex's skill creator:

```shell
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

For changes to Knap examples, also validate and render representative templates with the Knap CLI when available.

## Contributing

Issues and pull requests are welcome. Keep `SKILL.md` concise, put conditional detail in the relevant packaged reference, and avoid making the skill depend on the source documentation or network access.
