# ue4ss-bridge tool reference

Source: the project README (wire protocol 3, mod v1.2.0). If `bridge_status` reports a newer mod or protocol version, trust the live tool schemas over this file.

## Contents
- Tools
- Settings (`scripts\settings.lua`)
- Serialisation rules
- Snapshots and streams
- Wire protocol and CLI

## Tools

All tools except `eval_lua` run through the structured `batch` op, so they keep working when `allow_eval = false`.

| Tool | Purpose | Notes |
|---|---|---|
| `bridge_status` | Game found, running, mod answering, version, permissions, round-trip time | Call first |
| `eval_lua(code, timeout)` | Any Lua chunk on the game thread | UE4SS API and `UEB` helpers in scope; `print` captured; refused if `allow_eval=false` or `allow_writes=false` |
| `world_info` | World, player controller, pawn, game instance, game mode | Source of exact paths for live objects |
| `find_object(path)` | Resolve one reference | |
| `find_objects(class, limit)` | List live instances of a class | |
| `list_types(pattern, limit)` | Loaded reflected types matching a Lua pattern | Lua patterns, not regex |
| `inspect_object(ref, include_super, pattern)` | Every reflected property with its value | `pattern` filters property names |
| `list_functions(ref)` | Every UFunction on the class chain | |
| `get_property` / `set_property` | One property | `set` returns `{previous, current}`; write |
| `call_function(ref, fn, args)` | Call a UFunction with positional args | Write |
| `console_command(cmd)` | Run a console command | Write |
| `snapshot_object(ref, label, include_super, pattern)` | Keep a property walk in the game under a label | Read-only |
| `diff_object(label, ref, update)` | Re-walk and report `{changed, added, removed, same}` against the snapshot | Max 500 rows per list, `truncated` count when exceeded. `ref` defaults to the snapshot's own reference. Check the live schema for exactly what `update` does before using it. Read-only |
| `list_snapshots()` | Labels, object path, `taken` timestamp (epoch seconds), property count | Read-only |
| `forget_snapshot(label)` | Drop one snapshot, or all with `"*"` | Read-only |
| `list_subclasses(ref, limit, pattern)` | Every loaded subclass incl. Blueprint classes: `{base, count, types}`, rows `{name, kind, path, parent}` sorted by path | About 1.5 s. Read-only |
| `targeted_actor(distance, channel, ref)` | Line trace from camera (or from `ref`'s location and forward vector): actor, component, impact point and normal, bone, physical material, materials | Read-only |
| `watch_property(ref, names, label, interval_ms, every)` | Sample properties on a timer and record changes under a label | Default 250 ms, floor 100 ms. Check the live schema for `every`. Read-only |
| `hook_function(function, label, max_args)` | Record every call of a UFunction with its parameters | Counts as a write |
| `poll_events(since, label, limit, clear)` | Drain recorded events: `{events, next, dropped, buffered}` | Read-only |
| `list_streams()` / `stop_stream(label)` | Running watches and hooks / stop one, or all with `"*"` | |
| `reload_mod()` | Re-read `settings.lua`, re-run the mod in place, no restart | Read-only; the way back after `allow_eval` was turned off |
| `batch(calls)` | Several of the above in one round trip | Prefer over parallel calls |
| `dump(kind)` | UE4SS dumpers: `usmap`, `jmap`, `uht`, `cxx`, `actors`, `objects`, `static_meshes` | 600 s timeout |

## Settings (`scripts\settings.lua`)

| Key | Default | Effect |
|---|---|---|
| `enabled` | `true` | `false` disables the bridge; nothing is polled |
| `allow_writes` | `true` | `false` = strict read-only: `set_property`, `call_function`, `console_command`, `hook_function`, `eval_lua` refused |
| `allow_eval` | `true` | `false` refuses `eval_lua`; structured tools still work |
| `poll_ms` | `50` | Request check interval; 50 is the floor |
| `bridge_dir` | unset | Absolute path override for the request/response folder |

The copy in `scripts\` wins over a legacy `settings.lua` at the mod root. After editing, run `reload_mod` (or `ue4ss-bridge reload`) or restart the game.

## Serialisation rules

- UObjects become `{"__object": fullname, "address": n}`. Reuse `fullname` as a `ref`.
- `FName`, `FString`, `FText` become strings.
- `TArray` becomes a list, first 200 elements only.
- Structs are walked through their reflected type, including inherited fields.
- `SoftObjectProperty` and `SoftClassProperty` values are skipped by default (reading one has hard-crashed a game inside UE4SS's property reader).

## Snapshots and streams

**Snapshots** live in the game process, keyed by label (not object address). They survive `reload_mod` and are lost when the game exits. Diffs ignore object and struct addresses and use the same depth and array caps as the original walk, so an unchanged object diffs empty.

**Streams** (watches and hooks) also live in the game process and survive `reload_mod`. Behaviour:
- One shared buffer of 2000 events with a rising sequence number. `poll_events` reports `dropped` if the cap evicted rows before you read them.
- Labels are unique.
- A watch holds its object between passes, rechecks with `IsValid()` each pass, and only looks it up again when invalid or a read failed. So it follows `first:PlayerController` across respawns.
- `resumed` is recorded when a watch adopts a different object (by address and full name) after the old one went invalid; the baseline resets so the first sample on the new object is not reported as a change. The same object returning after a blip records nothing.
- When the reference goes away it records one `lost` event and retries at a slow cadence.
- A hook callback copies parameters and nothing else. Calling a hooked function from `eval_lua` in the same session has crashed the game.

## Wire protocol (3) and CLI

```
request : {"id": str, "op": "hello"|"ping"|"eval"|"batch", "code": str, "calls": [ {op, ...} ]}
response: {"id", "ok": bool, "result", "output": [str], "error": str|null, "ms": int, "protocol": 3}
```

`hello` returns mod version, protocol and permissions; the server refuses to proceed on a protocol mismatch. Files are `request.json` / `response.json` in `ue4ss\bridge\`; `lastop.log` there records the in-flight operation for crash diagnosis.

CLI equivalents (useful as a fallback when MCP tools are not connected and a shell is available):

```
ue4ss-bridge status | hello | reload | streams | events [label]
ue4ss-bridge eval "return UEB.world()"
ue4ss-bridge props first:PlayerController
ue4ss-bridge types ^Narrative
ue4ss-bridge subclasses /Script/Engine.Pawn
ue4ss-bridge target 5000
ue4ss-bridge snapshot <ref> <label> [--super]
ue4ss-bridge diff <label>            # or: diff <ref> <label>
ue4ss-bridge watch <ref> <names> <label> --interval 500
ue4ss-bridge hook <Class:Function> <label>
ue4ss-bridge unwatch <label|"*">
```

Environment: `UE4SS_BRIDGE_GAME_DIR` pins the game folder; `UE4SS_BRIDGE_DATA_DIR` overrides the data folder. The pre-1.2.0 `UE_BRIDGE_*` names are still read. The package was renamed from `ue-bridge`; the `ue-bridge` command alias still works.
