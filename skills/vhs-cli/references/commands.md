# VHS quick command reference

This is a compact summary of the upstream README, not a replacement for `vhs manual` for the installed version.

| Tape directive | Purpose | Example |
| --- | --- | --- |
| `Output` | Render destination(s) | `Output demo.gif` / `Output demo.mp4` / `Output demo.webm` / `Output golden.ascii` |
| `Require` | Require executable | `Require git` |
| `Set Width/Height` | Pixel dimensions | `Set Width 1200` |
| `Set Columns/Rows` | Character grid dimensions | `Set Columns 100` |
| `Set FontSize` | Font size | `Set FontSize 24` |
| `Set Theme` | Built-in theme | `Set Theme "Catppuccin Frappe"` |
| `Set TypingSpeed` | Delay between typed keys | `Set TypingSpeed 100ms` |
| `Set Framerate` | Capture framerate | `Set Framerate 30` |
| `Set PlaybackSpeed` | Output playback multiplier | `Set PlaybackSpeed 2.0` |
| `Type` | Type literal text | `Type "git status"` |
| `Type@...` | Override typing interval | `Type@50ms "hello"` |
| `Enter`, `Tab`, `Up`, `Down` | Press keys | `Enter` |
| `Ctrl+...` | Press modified key | `Ctrl+C` |
| `Wait` | Wait for last line | `Wait /ready/` |
| `Wait+Screen` | Wait across terminal screen | `Wait+Screen /Done/` |
| `Sleep` | Pause during capture | `Sleep 750ms` |
| `Hide` / `Show` | Suppress/resume captured frames | `Hide` |
| `Screenshot` | Capture current frame | `Screenshot image.png` |
| `Env` | Add environment value | `Env DEMO "1"` |
| `Source` | Include tape | `Source setup.tape` |

## Common CLI invocations

```sh
vhs new demo.tape
vhs demo.tape
vhs manual
vhs themes
vhs serve
```

## Example: interactive program

```tape
Output tui.gif
Set Width 1100
Set Height 650
Set FontSize 22
Set TypingSpeed 70ms

Require my-tui
Type "my-tui"
Enter
Wait+Screen /Choose an option/
Down
Enter
Sleep 1s
Ctrl+C
```

Change the markers and key sequence to match the actual TUI. Review the exact latest syntax at https://github.com/charmbracelet/vhs#vhs-command-reference.
