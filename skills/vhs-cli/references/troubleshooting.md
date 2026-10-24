# Troubleshooting

| Symptom | Diagnosis / action |
|---|---|
| `vhs` missing | Install VHS or use official Docker image. |
| `ttyd` or `ffmpeg` missing | Install runtime dependencies for local rendering. |
| Demo binary not found | Ensure binary exists **inside recording environment**, use `Require`, set PATH. |
| `Wait` timeout | Verify rendered text, regex scope, shell prompt, and whether output scrolled away. |
| `Wait` returns too early | Match a completion marker not present in typed commands or preexisting screen output. |
| Blank GIF | Inspect `Hide`/`Show`, whether anything ran, and GIF frames. |
| Cropped text | Increase dimensions / decrease font; avoid pixel/cell dimension conflicts. |
| Flaky timing | Pin tools/data/fonts/locale; prefer specific waits to sleeps. |
| No metadata for MP4 | Install `ffprobe`. |
| No contact sheet | Install Pillow; inspect rendered output manually. |
| `simple` passes, VHS fails | Linter is heuristic; use `vhs manual`, correct official syntax/runtime dependencies. |

When output appears visually wrong, review first/middle/last frames (or the full animation) and revise the tape. Metadata is not a replacement for viewing it.
