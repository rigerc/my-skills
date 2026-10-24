# CI integration

1. Pin the VHS version, recording CLI version, fonts, fixtures, and output dimensions.
2. Run `python3 scripts/run_workflow.py simple examples/demo.tape` on every tape change for fast feedback.
3. On the recording job, install VHS + `ttyd` + `ffmpeg` + your demo dependencies, then run `python3 scripts/run_workflow.py expanded examples/demo.tape`.
4. Inspect GIF/frame artifacts manually before promotion; use `ffprobe` and sampled frames for automated metadata checks.
5. Store approved `.ascii` golden files and diff them after rendering; review intentional changes.

See the official GitHub Action: https://github.com/charmbracelet/vhs-action

Docker alternative:

```sh
docker run --rm -v "$PWD:/vhs" ghcr.io/charmbracelet/vhs examples/demo.tape
```

This Docker invocation presumes the container can access the demo program and fixture paths. It is an alternative VHS executor, not a drop-in replacement for the local expanded workflow script.
