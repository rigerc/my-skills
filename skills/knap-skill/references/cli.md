# Knap CLI reference

Use this reference to validate or render templates from the terminal. The CLI requires Node.js 20 or later and is part of the `knap` npm package.

## Run and install

Run without a permanent installation:

```shell
npx knap render -t '# {{ title }}' --set title=Hello
```

For regular use, install globally or add Knap to a project:

```shell
npm install -g knap
knap render template.md --data data.json --output note.md
```

```shell
npm install knap
npx knap render template.md --data data.json --output note.md
```

Offline language help is built into an installed CLI:

```shell
knap help syntax
knap help filters
knap help filter date
knap help tags
knap help tag for
```

The filter list includes only filters available in the CLI. Individual help pages provide syntax, parameters, examples, and expected output; example strings use JSON quoting to expose newlines and whitespace.

## Validate

Validate a file, inline template, or piped template:

```shell
knap validate template.md
knap validate -t '{{ title | upper }}'
cat template.md | knap validate
```

Choose exactly one template source: a file, `--template`/`-t`, or stdin. Omit the template argument or use `-` for piped input. Validation accepts no data, output, or batch options and writes no files.

Validation checks template syntax, filter names, and filter arguments that can be checked statically. It does not render, verify that variables exist, inspect runtime values, or evaluate dynamic filter arguments. Render with representative data for those checks.

Success exits `0`; errors exit `1`. Diagnostics and the success message go to stderr, while stdout remains empty.

## Render one output

```shell
knap render [template-file] [options]
```

Select one template source:

```shell
knap render template.md --data data.json
knap render -t '{{ title | upper }}' --set title=Hello
cat template.md | knap render --data data.json
```

Supply one JSON object with `--data`/`-d` or `--data-json`. Its properties become variables and nested values retain their JSON types. Without data, the variable object is empty.

```shell
knap render template.md --data data.json
knap render -t '{{ title }}' --data-json '{"title":"Hello"}'
```

Choose either `--data` or `--data-json` as the base data source. Use repeated `--set key=value` flags to add or override top-level variables. Overrides apply after JSON regardless of argument order, and the last value for a key wins.

```shell
knap render template.md --data data.json --set title="Custom title"
knap render -t '{{ First name }}' --set 'First name=Ada'
```

Every `--set` value is a string: `--set enabled=false` supplies the text `false`, not a boolean. Keys are literal top-level names. `--set a.b=hi` creates the top-level key `a.b`, which `{{ a.b }}` may resolve; it does not build `{ "a": { "b": "hi" } }`. Use JSON for nested or typed values.

Read data from stdin with `--data -`; only one input may use stdin, so provide the template as a file or inline text:

```shell
cat data.json | knap render template.md --data -
```

Rendered text goes to stdout without an added newline. Use `--output`/`-o` to write a file; `--output -` explicitly selects stdout.

```shell
knap render template.md --data data.json --output note.md
knap render template.md --data data.json > note.md
```

Knap creates missing parent directories for `--output`. It creates or overwrites the destination only after a successful render. A rendering failure leaves that destination untouched. Shell redirection is controlled by the shell and can truncate a destination before Knap starts.

Diagnostics go to stderr. Argument, input, rendering, and filesystem failures exit `1` and produce no rendered output. Non-fatal warnings still exit `0`.

Render options:

| Option | Short | Purpose |
| --- | --- | --- |
| `[template-file]` | | template file, or `-` for stdin |
| `--template <text>` | `-t` | inline template |
| `--data <file>` | `-d` | JSON object file, or `-` for stdin |
| `--data-json <json>` | | inline JSON object |
| `--set <key=value>` | | repeatable string override for a top-level variable |
| `--output <file>` | `-o` | output file, or `-` for stdout |
| `--help` | `-h` | usage help |
| `--version` | `-v` | package version |

To render an array into one output, place it beneath a named property such as `{ "articles": [...] }` and loop over that variable. Use `batch` for one file per record.

## Batch rendering

```shell
knap batch template.md --data articles.csv --output-dir notes \
  --filename '{{ title | safe_name }}.md'
```

Supported data sources:

| Source | One output per | Variables |
| --- | --- | --- |
| CSV file | row | headers become names; values remain strings |
| JSON array file | object | properties retain JSON types |
| folder of JSON files | file | each file's object properties |

```shell
knap batch template.md --data articles.json --output-dir notes
knap batch template.md --data ./articles --output-dir notes
cat articles.json | knap batch template.md --data - --output-dir notes
knap batch -t '# {{ title }}' --data-json '[{"title":"One"}]' --output-dir notes
```

Piped data defaults to a JSON array. Select CSV explicitly with `--format csv`:

```shell
cat articles.csv | knap batch template.md --data - --format csv --output-dir notes
```

File format is detected as CSV only for a `.csv` extension and as JSON otherwise. `--format csv` or `--format json` overrides detection. Folder input and `--data-json` require JSON and cannot use CSV mode. Only one of template or data may read stdin. `--template` and repeatable `--set` flags also work in batch mode; overrides apply to every record.

CSV uses commas, not tabs. The first nonempty row supplies headers. Values remain strings, preserving values such as `00123` and `false`. Quoted commas, escaped double quotes, embedded newlines, and UTF-8 BOMs are supported. Blank lines are skipped. Empty or duplicate headers and inconsistent row lengths are errors.

Folder input reads regular `.json` files in filename order, with case-insensitive extensions. It ignores subfolders, symlinks, and other file types. Every file must hold one JSON object. An empty batch is an error.

### Output filenames

Without `--filename`, folder input preserves source basenames and changes `.json` to `.md`; CSV and JSON-array items become `1.md`, `2.md`, and so on.

Filename templates use record variables and standard filters. Include the extension and apply `safe_name` to data-derived components:

```shell
knap batch template.md --data articles.json --output-dir notes \
  --filename '{{ published | date:"YYYY-MM-DD" }}-{{ title | safe_name }}.md'
```

The result must be one filename: no directory separators, control characters, or Windows-reserved characters. It must contain more than whitespace, dots, hyphens, or underscores. Leading whitespace is rejected; clean it with `trim` or `safe_name`. An optional value may be empty if the rest remains valid. For an intentional dotfile, begin the template with a literal dot, such as `.{{ name }}`.

Duplicate output names fail the entire batch, including names that differ only by case or Unicode normalization.

### Preview, overwrite, and failures

Preview every intended path without creating directories or files:

```shell
knap batch template.md --data articles.csv --output-dir notes --dry-run
```

Dry runs perform the same template, filename, duplicate, and existing-file checks as a real run. They list one path per line on stdout; summaries and warnings go to stderr. If validation fails, no paths are printed. Use `--overwrite --dry-run` to preview replacements.

`--output-dir` is required and created when needed. Existing files fail unless `--overwrite` is explicit. Directories and symlinks cannot be overwritten.

Knap validates all input, filenames, and rendered content before writing. A filesystem failure during the write phase can still leave some outputs written; the diagnostic reports the completed count. Batch input and prepared outputs are held in memory.

Batch options:

| Option | Short | Purpose |
| --- | --- | --- |
| `[template-file]` | | template file, or `-` for stdin |
| `--template <text>` | `-t` | inline template |
| `--data <source>` | `-d` | CSV file, JSON array file, JSON folder, or `-` |
| `--data-json <json>` | | inline JSON array of objects |
| `--format <csv\|json>` | | override format detection or set stdin format |
| `--set <key=value>` | | repeatable string override applied to all records |
| `--output-dir <dir>` | | required destination directory |
| `--filename <template>` | | output basename template |
| `--overwrite` | | allow replacement of existing regular files |
| `--dry-run` | | validate and list paths without writing |
| `--help` | `-h` | usage help |
| `--version` | `-v` | package version |
