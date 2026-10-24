---
name: knap-skill
description: Write, explain, validate, and render Knap templates for Markdown or text output. Use for Knap variables, filters, conditions, loops, local assignments, CLI rendering, or batch generation; do not apply to unrelated Jinja, Liquid, or Mustache templates.
---

# Knap

Use Knap's own syntax and runtime semantics when creating or changing templates. Preserve the user's output format and the variable shape supplied by their app, JSON, or CSV source.

## Load the relevant reference

- Read [references/language.md](references/language.md) for variables, assignments, expressions, conditions, fallbacks, loops, comments, and whitespace behavior.
- Read [references/filters.md](references/filters.md) for filter syntax, documented standard filters, structured values, HTML filters, and custom filters.
- Read [references/cli.md](references/cli.md) for installation, validation, rendering, data input, piping, batch generation, filenames, output, and failure behavior.

Read only the references needed for the request. They are part of this skill and are the source of truth for Knap behavior. If an installed Knap version offers additional filters or tags, inspect its focused help, such as `knap help filter date` or `knap help tag for`, before using undocumented syntax.

## Author templates

- Output values with `{{ expression }}` and chain filters left to right with `|`.
- Use `{% set %}`, `{% if %}`, and `{% for %}` for assignments and control flow; use `{# ... #}` for template-only comments.
- Access nested data with dot or bracket notation. Keep headings containing spaces intact when they are literal variable names, such as `{{ First name }}`.
- Treat `??` as a truthy fallback, not JavaScript-style nullish coalescing: `false`, `null`, `undefined`, `""`, `0`, and `[]` all select the fallback. Filters run before the fallback check.
- Remember that loop iterations are separated by a line break and whitespace inside a loop is preserved. Check rendered Markdown when blank lines or tables matter.
- Use only registered filters. CLI templates have the standard filters but not DOM-dependent HTML filters; those require `knap/html` through the library API.

## Check the result

When execution is part of the request and Knap is available:

1. Run `knap validate` on the template. This checks syntax, filter names, and statically checkable arguments only.
2. Render with representative data to verify variables, runtime values, dynamic arguments, whitespace, and final Markdown.
3. For batch generation, run with `--dry-run` first to inspect every destination. Add `--overwrite` only when replacing existing files is intended.

Use JSON for nested values and typed booleans, numbers, arrays, objects, or null. `--set` always supplies strings and defines literal top-level keys; it does not construct nested objects. When generating filenames, include the extension and use `safe_name` for data-derived components.
