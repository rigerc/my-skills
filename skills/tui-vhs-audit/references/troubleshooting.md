# VHS screenshot audit troubleshooting

**`BLOCKED: missing recording dependencies`** — Install `vhs`, `ttyd`, and `ffmpeg` in the *same environment that will execute the TUI*. Inspect `vhs manual`. On some systems VHS bundles its browser automation but still requires a working Chrome/Chromium and terminal renderer.

**VHS renders but screenshots are absent** — Check the log/exit code, screenshot directories, and whether `Screenshot` appears after launch. VHS resolves relative image paths from the working directory in which you invoke it. This skill runs each tape with `cwd=tape.parent` and creates `screens/` first.

**Screenshot shows the next state or the final PNG is missing** — VHS queues `Screenshot` for the next video frame. Leave a short pause after the directive before sending more keys or ending the tape. Generated tapes include a 250ms pause; increase it if frame capture is slow in your environment.

**Recording hangs / times out** — Start the target manually in a disposable terminal. Check first-launch prompts, package install/network requests, shell environment, and exact `Wait+Screen` text. A changed heading will break synchronization; VHS's default wait timeout is about 15 seconds. Increase application startup stability via fixed local data and avoid fragile network dependencies.

**Wrong state captured** — Confirm the keybindings, status-specific marker, post-action settle delay, and that the marker wasn't already visible before the action. Example: `Wait+Screen /Help/` can falsely match the footer text `Press ? for Help`. Use a screen-unique heading if possible. Re-render the failing scenario.

**Blank/black capture** — The TUI may exit immediately without a TTY, shell cannot resolve the binary, app is still starting, or the colors/font are broken. Check VHS logs and the GIF timeline. The inspection script only flags nearly uniform frames; it cannot accurately detect every blank or visually broken TUI.

**Keyboard actions do nothing** — Inspect keybinding documentation; `Type "j"` differs from `Down`, and `Escape` can have different meaning. Raw-mode apps may need small delays after input; apps responding to `Enter`/`Tab` may not accept vi-style navigation.

**Narrow-screen layout differs from a real terminal** — VHS specifies pixels and font sizes. A 720px window does not always equal exactly 80 columns. If your requirement is an exact 80×24 grid, author a custom tape using `Set Columns 80` and `Set Rows 24` (do not mix with `Set Width`/`Set Height`) and record the font/theme used.

**Visual report says pending** — Intended behavior. `inspect` is a screenshot inventory and template generator, not an image-understanding system. Open the screenshots, assess the rubric, then write findings with evidence links.

**Secret exposure** — Delete unsafe screenshot outputs and re-run with sanitized fixture data. `Hide` stops frame recording but cannot be used to remove secrets from a tape or guarantee they never reach screenshots.
