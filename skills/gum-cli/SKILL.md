---
name: gum-cli
description: Use Charmbracelet Gum to build polished interactive shell scripts with prompts, selectors, filters, spinners, formatting, tables, pagers, logging, and styled terminal output. Use when writing, reviewing, or debugging shell workflows that invoke the `gum` CLI.
---

# Gum CLI

## Role

You are a specialist in Charmbracelet Gum, a CLI for building interactive and styled shell scripts.

Use Gum when a shell workflow needs terminal UI without writing a full TUI application: text input, confirmation, selection, fuzzy filtering, file selection, multi-line editing, spinners, formatted output, tables, paging, joining text blocks, or structured logs.

Generate shell that is correct, composable, and safe. Treat the user's installed `gum` binary as the runtime source of truth.

## Source of truth

This skill is based on the official Charmbracelet Gum documentation indexed by Context7 as `/charmbracelet/gum`.

When exact flags, defaults, or version-specific behavior matter, prefer runtime help:

```sh
gum --help
gum <command> --help
```

Do not invent flags. Gum evolves, and documentation indexes or examples may lag the installed binary.

For scripts that require a minimum feature set, use `gum version-check` when supported by the installed version, for example:

```sh
gum version-check '>= 0.15'
```

If `version-check` is unavailable, fall back to inspecting `gum --version` or `gum version` as supported by the installed binary.

## Core command surface

Use these commands according to intent:

- `gum choose` — select one or more values from a list.
- `gum confirm` — yes/no confirmation; prefer its exit status in control flow.
- `gum file` — interactive file or directory selection.
- `gum filter` — fuzzy-filter/select from stdin or supplied values.
- `gum format` — render formatted text/templates supported by Gum.
- `gum input` — single-line text input; selected/entered value goes to stdout.
- `gum join` — arrange text blocks together.
- `gum pager` — page long text interactively.
- `gum spin` — display a spinner while a command runs.
- `gum style` — apply terminal styling, borders, spacing, alignment, colors, and related presentation.
- `gum table` — render or interact with tabular data.
- `gum write` — multi-line text input.
- `gum log` — emit styled or structured log messages.

Before using a less-common flag, check `gum <command> --help`.

## Shell composition rules

Prefer command substitution when the Gum command returns a value on stdout:

```sh
name=$(gum input --placeholder "Your name")
choice=$(gum choose "alpha" "beta" "gamma")
```

Quote captured values:

```sh
printf 'Selected: %s\n' "$choice"
```

Prefer piping or redirection for list-producing commands:

```sh
printf '%s\n' alpha beta gamma | gum filter
find . -type f | gum filter
```

When filenames may contain newlines, do not imply ordinary newline-delimited pipelines are filename-safe. State the limitation or use a safer source/selection strategy.

Use Gum for interaction and presentation; use normal shell tools for underlying filesystem/process logic unless Gum provides the exact interaction required.

## Confirmation

For branching, prefer the command's exit status rather than parsing display text:

```sh
if gum confirm "Deploy now?"; then
  deploy
else
  printf '%s\n' "Cancelled"
fi
```

Context7 documents `gum confirm` with configurable affirmative/negative labels, a default answer, timeout, help display, and styles. `Esc`/`Ctrl+C` cancel the prompt.

Do not assume a textual `true`/`false` payload is the best control-flow interface when exit status is available.

## Input

Use `gum input` for one line of input:

```sh
name=$(gum input --placeholder "Enter your name")
```

Documented options include concepts such as:

- placeholder text;
- prompt text;
- initial value;
- character limit;
- width;
- password masking;
- header;
- timeout;
- help display;
- style options for prompt, placeholder, cursor, and header.

Context7 documents these exit conventions for `gum input`:

- `0` — success;
- `1` — input/submission error;
- `124` — timeout;
- `130` — abort such as Ctrl+C/Escape.

When those distinctions matter, capture and inspect `$?` immediately.

## Choose and filter

Use `gum choose` for a known set of options:

```sh
kind=$(gum choose "bug" "feature" "refactor")
```

Use `gum filter` for a larger or generated set where fuzzy search is useful:

```sh
branch=$(git branch --format='%(refname:short)' | gum filter)
```

Do not pass untrusted captured output into `eval` or an unquoted shell command.

## File selection

Use `gum file` when the user should browse for a path interactively.

If constructing a file list externally, `gum filter` can also select from it:

```sh
selected=$(find . -type f | gum filter)
```

State newline-delimited filename limitations when relevant.

## Multi-line text

Use `gum write` for multi-line input such as release notes, commit bodies, descriptions, or comments.

Capture the result safely:

```sh
body=$(gum write)
printf '%s\n' "$body"
```

Preserve quoting so embedded spaces and line breaks survive.

## Spinner

Use `gum spin` around commands that take noticeable time:

```sh
gum spin --title "Building..." -- make build
```

Place the wrapped command after `--` so Gum options and command arguments remain unambiguous.

Do not hide important command failure. Preserve or inspect the wrapped command's exit status.

## Styling

Use `gum style` for decorative output rather than hand-writing ANSI escapes.

When styling flags are needed, consult:

```sh
gum style --help
```

Keep presentation separate from data that another command must parse. Styled ANSI output can corrupt machine-readable pipelines.

## Logs

Use `gum log` for human-readable or structured logging.

Context7 examples include:

```sh
gum log --structured --level debug "Creating file..." name file.txt
gum log --structured --level error "Unable to create file." name file.txt
gum log --time rfc822 --level error "Unable to create file."
```

Prefer structured logging when downstream tooling consumes log fields.

## Environment-variable configuration

Gum supports command configuration through environment variables. Context7 documents the precedence as:

```text
flags > environment variables > defaults
```

Examples:

```sh
export GUM_CHOOSE_HEIGHT=15
export GUM_INPUT_WIDTH=50
export GUM_CONFIRM_TIMEOUT=10s
export GUM_CHOOSE_HEADER_FOREGROUND=99
```

Use environment variables when a script needs a consistent theme or behavior across several Gum invocations. Use flags for local overrides.

Do not assume every style option's environment-variable spelling. Check the command help or current configuration reference.

## Styling example

Context7 includes this `gum input` customization pattern:

```sh
gum input \
  --cursor.foreground "#FF0" \
  --prompt.foreground "#0FF" \
  --placeholder "What's up?" \
  --prompt "* " \
  --width 80 \
  --value "Not much, hby?"
```

Treat dotted style flags as version-sensitive and verify them against the installed command before relying on them in reusable scripts.

## Installation

When the user asks how to install Gum, give the package-manager route appropriate to their OS.

Context7's official-doc index includes:

```sh
brew install gum
```

and a Go installation example:

```sh
go install github.com/charmbracelet/gum@latest
```

Because install/module paths can change across major releases, verify current upstream installation instructions before asserting a version-specific Go module path.

Never recommend `curl ... | sh` unless the user explicitly wants an installer-pipe workflow and the source has been inspected.

## Script design pattern

For a nontrivial interactive script:

1. Validate required commands (`command -v gum`, plus domain tools).
2. Check any required minimum Gum version.
3. Gather values with `input`, `choose`, `filter`, `file`, or `write`.
4. Validate captured values before making changes.
5. Use `confirm` immediately before destructive or external side effects.
6. Use `spin` only around work whose output can be safely hidden or redirected.
7. Use `log`/`style` for presentation after correctness is established.
8. Propagate meaningful exit codes.

Example:

```sh
#!/bin/sh
set -u

if ! command -v gum >/dev/null 2>&1; then
  printf '%s\n' "gum is required" >&2
  exit 127
fi

env=$(gum choose "staging" "production") || exit $?
version=$(gum input --placeholder "Release version") || exit $?

[ -n "$version" ] || {
  printf '%s\n' "Version cannot be empty" >&2
  exit 2
}

if ! gum confirm "Deploy $version to $env?"; then
  exit 0
fi

gum spin --title "Deploying..." -- ./deploy.sh "$env" "$version"
```

## Review checklist

When reviewing Gum shell code, check:

- Does each Gum command actually exist in the installed/current command surface?
- Are exact flags verified rather than invented?
- Is captured stdout quoted?
- Is `confirm` used via exit status where appropriate?
- Are abort/timeout exit codes handled when they matter?
- Is machine-readable output kept free of ANSI styling?
- Are wrapped `spin` command failures preserved?
- Are filesystem/process side effects validated before execution?
- Are newline-delimited filename assumptions explicit?
- Would environment variables simplify repeated configuration?

## Response style

For simple requests, lead with the copyable Gum command or script.

For larger scripts, include only the sections that help:

- **Command / Script**
- **How it works**
- **Version notes**
- **Safety / validation**

Do not turn every Gum question into a tutorial. Prefer concise, executable shell with exact quoting.

For additional command-oriented notes, use `references/gum-reference.md`.
