# Gum CLI reference notes

Source basis: official Charmbracelet Gum documentation indexed by Context7 as `/charmbracelet/gum`.

## Commands documented by Context7

- `choose`
- `confirm`
- `input`
- `write`
- `filter`
- `file`
- `table`
- `pager`
- `style`
- `format`
- `join`
- `spin`
- `log`
- version/version-check functionality depending on the installed release

## Common idioms

### Input

```sh
name=$(gum input --placeholder "Enter your name")
```

### Choose

```sh
kind=$(gum choose "bug" "feature" "refactor")
```

### Confirm

```sh
if gum confirm "Continue?"; then
  do_work
fi
```

### Filter generated values

```sh
selection=$(printf '%s\n' one two three | gum filter)
```

Context7 also shows:

```bash
gum filter < <(find . -type f)
```

Note: process substitution is Bash/Zsh, not POSIX `sh`.

### Spinner

```sh
gum spin --title "Processing..." -- command arg1 arg2
```

### Logging

```sh
gum log --structured --level debug "Creating file..." name file.txt
gum log --structured --level error "Unable to create file." name file.txt
gum log --time rfc822 --level error "Unable to create file."
```

## `gum input` details from Context7

Documented flags/concepts include:

- `--placeholder`
- `--prompt`
- prompt/placeholder/cursor/header styles
- cursor mode
- `--value`
- `--char-limit`
- `--width`
- `--password`
- `--show-help`
- `--header`
- `--timeout`
- `--strip-ansi`
- padding

Documented statuses:

- success: `0`
- error: `1`
- timeout: `124`
- abort: `130`

Verify the exact current flag spelling with `gum input --help`.

## `gum confirm` details from Context7

Documented configuration concepts:

- default answer
- affirmative/negative labels
- prompt
- selected/unselected/prompt styles
- show help
- timeout
- padding

Keybindings documented by Context7:

- Tab / Left / Right: switch option
- Enter: confirm
- Esc / Ctrl+C: cancel/negative path

Environment-variable examples/patterns include:

- `GUM_CONFIRM_SHOW_HELP`
- `GUM_CONFIRM_TIMEOUT`
- `GUM_CONFIRM_PADDING`
- `GUM_CONFIRM_PROMPT_*`
- `GUM_CONFIRM_SELECTED_*`
- `GUM_CONFIRM_UNSELECTED_*`

## Configuration precedence

Context7 documents:

```text
flags > environment variables > defaults
```

Example script-level configuration:

```sh
export GUM_CHOOSE_HEIGHT=15
export GUM_INPUT_WIDTH=50
export GUM_CONFIRM_TIMEOUT=10s
export GUM_CHOOSE_HEADER_FOREGROUND=99
```

## Installation examples indexed by Context7

Homebrew:

```sh
brew install gum
```

Go example present in the indexed README:

```sh
go install github.com/charmbracelet/gum@latest
```

Treat Go module/install paths as version-sensitive and verify current upstream docs when the major version matters.

## Runtime discovery

Use the installed binary to avoid stale flag assumptions:

```sh
gum --help
gum input --help
gum choose --help
gum confirm --help
gum spin --help
gum style --help
```

Where supported:

```sh
gum version-check '>= 0.15'
```
