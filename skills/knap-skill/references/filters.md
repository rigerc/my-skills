# Knap filter reference

Use this reference when transforming values or extending Knap with custom filters.

## Syntax and evaluation

Place a filter after a `|` and chain filters as needed. They run from left to right.

```knap
{{ title | h2 | upper }}
```

Only filters registered in the active engine are valid. Unknown names and statically invalid parameters are diagnostics during validation and rendering.

Filter parameters follow the filter name after a colon. Examples documented by Knap include:

```knap
{{ source | code:"typescript" }}
{{ footer | hr:before }}
{{ tags | join:", " }}
{{ published | date:"YYYY-MM-DD" }}
{{ title | replace:" ":"-" }}
```

Do not invent an argument signature. When a filter is not described here and Knap is installed, use `knap help filter <name>` for its syntax, parameters, examples, and expected output.

## Documented standard filters

The supplied Knap documentation uses these standard filters:

| Filter | Demonstrated purpose |
| --- | --- |
| `h1`, `h2` | format a value as a Markdown heading |
| `bold`, `italic` | apply Markdown emphasis |
| `code` | create Markdown code, optionally with a language |
| `math` | format mathematical content |
| `hr` | add a horizontal rule; `hr:before` places it before the value |
| `escape_md` | escape literal text for Markdown |
| `embed` | format an attachment as an embed |
| `upper`, `lower` | change letter case |
| `trim` | remove surrounding whitespace |
| `replace` | replace text using supplied arguments |
| `join` | join collection values with a delimiter |
| `date` | format a date using a supplied pattern |
| `kebab` | convert text to kebab case |
| `safe_name` | sanitize a value for use in a filename |
| `comment` | emit an Obsidian-flavored `%%` comment |

These examples show valid combinations:

```knap
{{ title | h1 }}
{{ summary | italic }}
{{ source | code:"typescript" }}
{{ expression | math }}
{{ footer | hr:before }}
{{ literal_text | escape_md }}
{{ attachment | embed }}
{{ tags | bold | join:", " }}
```

Markdown formatting filters recognize both typed arrays or objects and their serialized forms. They recursively transform string values while leaving object keys and non-string values unchanged. The result may then continue through a collection filter such as `join`.

```knap
{{ tags | bold | join:", " }}
{{ json_text | italic | join:", " }}
```

## CLI versus HTML filters

The CLI enables the standard filters. The `html_to_json` and `remove_html` filters depend on browser-compatible DOM globals and are exported separately from `knap/html`; they are not CLI filters.

```ts
import { createEngine, standardFilters } from 'knap';
import { htmlFilters } from 'knap/html';

const engine = createEngine({
  filters: { ...standardFilters, ...htmlFilters },
});
```

## Custom filters

Custom filters may be synchronous or asynchronous. Register them by name when creating an engine. Optional metadata lets an editor validate parameters before rendering.

```ts
import { createEngine, standardFilters, type TemplateFilter } from 'knap';

const surround: TemplateFilter = (value, param = '') => {
  const marker = param.replace(/^(['"])(.*)\1$/s, '$2');
  return marker + value + marker;
};

surround.metadata = { example: 'surround:"**"' };

const engine = createEngine({
  filters: { ...standardFilters, surround },
});
```

A filter receives a serialized string as its first argument for compatibility. Use `context.rawValue` when it must distinguish a typed array or object from text containing JSON. Evaluated arguments are available through `context.rawArguments`; the serialized parameter string remains available unchanged. A filter may call `context.reportWarning()` when it preserves a fallback value but should surface a non-fatal diagnostic.
