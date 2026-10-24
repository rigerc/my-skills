# Recording patterns

## Deterministic CLI demo

Prefer fixed fixture inputs, a dedicated throwaway directory and `LANG=C` / controlled terminal dimensions where appropriate. Run the command outside VHS first to verify the exact output used by `Wait`.

```tape
Output demo.gif
Set Width 1000
Set Height 500
Set FontSize 24
Set TypingSpeed 65ms
Hide
Type "cd /workspace/sample && clear"
Enter
Show
Type "printf 'RESULT: ready\\n'"
Enter
Wait+Screen /RESULT: ready/
Sleep 2s
```

## Stable waiting

- `Wait+Line /pattern/` checks the last line, minimizing false matches from old screen content.
- `Wait+Screen /pattern/` searches the visible screen, useful for TUIs. Avoid matching a keyword already present in the typed command.
- Avoid `Sleep 5s` as the sole method of waiting for slow or variable commands.
- Prefer a **unique explicit completion marker**, and test that it appears only after the desired operation completes.
- Screen markers can be missed if scrolled away. Use layout-specific waits for TUIs.

## TUI recordings

Start the TUI, wait for a stable heading, navigate with `Down`, `Up`, `Tab`, `Enter`, and `Ctrl+C` as applicable. Avoid hard-coded long sleeps between navigation steps; where possible use `Wait+Screen /stable state/`.

## Golden fixtures

`Output golden.ascii` creates diffable output. Pin command versions, shell, locale, dimensions, and fixtures. Compare against reviewed snapshots. VHS recording is not a replacement for unit or integration assertions inside the application.
