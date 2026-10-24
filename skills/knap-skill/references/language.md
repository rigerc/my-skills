# Knap language reference

Use this reference when authoring or explaining Knap template syntax. Knap renders text—commonly Markdown—from typed input values.

## Variables and paths

Output an expression with double braces. Whitespace inside the delimiters is optional.

```knap
{{ title }}
{{title}}
```

Variables may contain strings, numbers, booleans, arrays, objects, and nullish values. Use dot notation for object properties and bracket notation for array positions or string keys.

```knap
{{ author.name }}
{{ authors[0].name }}
{{ metadata["article:section"] }}
```

A bracket expression may use another variable as its key or index:

```knap
{% for line in transcript %}
{{ timestamps[loop.index0] }} — {{ line }}
{% endfor %}
```

Top-level variable names may contain spaces, which is useful for CSV column headings and imported data:

```knap
{{ First name | trim }}
{{ Publication date | date:"YYYY-MM-DD" }}
```

## Filters and fallbacks

Append filters with `|`. Chained filters run from left to right.

```knap
{{ title | h2 | upper }}
```

The `??` operator returns the first value Knap treats as true:

```knap
{{ title ?? headline ?? "Untitled" }}
{{ title | upper ?? "UNTITLED" }}
```

Despite its spelling, `??` is a truthy fallback rather than JavaScript-style nullish coalescing. Each of these values is false in Knap conditions and therefore selects a fallback: `false`, `null`, `undefined`, an empty string, `0`, and an empty array. Other values are true. Filters run before the fallback check because `??` has the lowest precedence.

## Local assignments

Use `set` to assign a literal, expression, or filtered result. The variable is available to the remainder of the template, and assignments are evaluated in order.

```knap
{% set slug = title | lower | replace:" ":"-" %}
File: {{ slug }}.md
```

## Conditions

Logic tags use `{% ... %}` and do not emit text. Use `if`, optional `elseif` branches, and optional `else`, then close with `endif`.

```knap
{% if published %}
Published
{% elseif scheduled %}
Scheduled
{% else %}
Draft
{% endif %}
```

Supported operators:

| Operator | Meaning | Example |
| --- | --- | --- |
| `==` | equal | `status == "draft"` |
| `!=` | not equal | `status != "archived"` |
| `>` `<` `>=` `<=` | ordered comparison | `price >= 100` |
| `contains` | string substring or array member | `tags contains "reference"` |
| `and` or `&&` | both operands are true | `author and published` |
| `or` or `\|\|` | either operand is true | `draft or archived` |
| `not` or `!` | negate an expression | `not hidden` |

Use parentheses for explicit grouping:

```knap
{% if (premium or featured) and published %}
Featured reading
{% endif %}
```

## Loops

Use `for` to render a block once for every element in an array:

```knap
{% for tag in tags %}
- #{{ tag | kebab }}
{% endfor %}
```

Loops can consume host variables, local variables created with `set`, and arrays nested inside objects. Conditions, loops, and assignments may be nested.

```knap
{% for section in sections %}
## {{ section.title }}
{% for item in section.items %}
{% if item.active %}- {{ item.name }}{% endif %}
{% endfor %}
{% endfor %}
```

Loop metadata:

| Value | Meaning |
| --- | --- |
| `loop.index` | 1-based current iteration |
| `loop.index0` | 0-based current iteration |
| `loop.first` | true on the first iteration |
| `loop.last` | true on the last iteration |
| `loop.length` | total item count |
| `<iterator>_index` | backward-compatible 0-based index, named after the iterator |

```knap
{% for author in authors %}
{{ loop.index }}. {{ author.name }}{% if loop.last %}.{% else %};{% endif %}
{% endfor %}
```

Iterations are separated by a line break. Whitespace inside the loop is preserved; in particular, a blank line before `endfor` separates repeated paragraphs or tables.

## Comments

Template comments use `{# ... #}` and are removed from output. Knap does not evaluate variables, filters, or logic inside them.

```knap
Hello{# note for the template author #} world!
```

Comments may span lines. Surrounding spaces and line breaks remain, so a comment on its own line leaves a blank line. Comments end at the first `#}`, do not nest, and produce a syntax error when unclosed.

To emit an Obsidian-style `%%` comment in rendered Markdown, pass the value through the `comment` filter instead of using a Knap template comment.
