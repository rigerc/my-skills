---
name: ue4ss-bridge
description: Inspect and manipulate a live, running Unreal Engine game through the ue4ss-bridge MCP server (UE4SS plus the UEBridge Lua mod). Use this whenever the user wants to examine UObjects, properties, UFunctions or class hierarchies in a running game; read or change a value live; run Lua inside the game; snapshot/diff or watch/hook values while they play; find out what the camera is aimed at; trigger UE4SS dumps (usmap, jmap, uht, cxx); or whenever ue4ss-bridge tools (bridge_status, inspect_object, eval_lua, snapshot_object, watch_property, hook_function, poll_events, etc.) are available. Also trigger on mentions of UE4SS, UEBridge, Unreal game modding or reverse engineering, "the player pawn/controller", or finding offsets and property names in a live game, even if the user never names the tool.
---

# ue4ss-bridge

ue4ss-bridge connects Claude to a running Unreal Engine game that has UE4SS installed. Claude can read reflected properties, call UFunctions, run Lua on the game thread, and record changes over time, all without restarting the game. It is a developer tool for mod authors and reverse engineers; it adds no gameplay on its own.

How it works, because it explains most of the failure modes: the MCP server writes `request.json` into `ue4ss\bridge\`, the UEBridge mod polls for it every 50 ms, runs it on the game thread, and writes `response.json`. There are no sockets. Only one request is in flight at a time.

Tool names may be prefixed by the client (for example `mcp__ue4ss-bridge__bridge_status`). Full tool signatures, the serialisation rules and stream semantics are in `references/tool-reference.md`; read it when you need exact parameters or are unsure how a value will come back.

## Before anything else

1. **Call `bridge_status` first.** It reports whether a game was found, whether it is running, whether the mod answers, the mod version, the permissions (`allow_writes`, `allow_eval`) and round-trip time. Everything you do next depends on it.
2. If the tools are not available at all, the MCP server is not connected. In Claude Code the setup is `claude mcp add ue4ss-bridge -- uvx ue4ss-bridge`; for Claude Desktop, Cursor and others, add an `mcpServers` entry running `uvx ue4ss-bridge`. If you have a shell on the user's machine, `uvx ue4ss-bridge status` and `uvx ue4ss-bridge hello` test the channel from the CLI.
3. If the mod is not answering, ask the user to check `ue4ss\UE4SS.log` for `[UEBridge] ... ready`. The mod must be extracted into `<game>\<Project>\Binaries\Win64\` (so it lands in `ue4ss\Mods\UEBridge\`). No `mods.txt` edit is needed.

## Principles

**Prefer the structured tools over `eval_lua`.** `inspect_object`, `get_property`, `list_functions`, `find_objects` and the rest return serialised, size-capped results and keep working when the user has set `allow_eval = false`. Reach for `eval_lua` only when no structured tool covers the need (custom logic, calling an unusual API, exploring the `UEB` helper table).

**Read before you write.** Start with `world_info`, `inspect_object`, `list_functions`. Only call `set_property`, `call_function`, `console_command`, `hook_function` or `eval_lua` once you know what you are touching. These are all "writes" and are refused entirely if the user set `allow_writes = false`; respect that. Do not suggest flipping the setting to get around a refusal, just tell the user what is blocked and why. If they change `settings.lua`, `reload_mod` re-reads it without a restart.

**The game is live and a mistake can crash it.** Before writes or anything exotic, say what you are about to change. Unsaved progress can be lost on a crash, so for risky experiments suggest the user save first. `set_property` returns `{previous, current}`: report `previous` so the change can be reverted, and revert it yourself if the user was only testing.

**One request at a time.** Do not fire several tool calls in parallel. Use `batch(calls)` to combine several operations into one round trip. A `request.json` younger than 10 s is treated as another client's, so overlapping calls collide.

**Mind the cost.** A lookup costs roughly 10 to 25 ms of game-thread time, `list_subclasses` takes about 1.5 s, and `dump` can take minutes (600 s timeout). Use `limit` and `pattern` arguments to narrow results rather than pulling everything, and do not run slow operations in a loop.

**Summarise, don't dump.** `inspect_object` can return hundreds of properties and arrays are capped at 200 elements. Filter with `pattern`, then give the user the handful of properties that matter, with names and current values.

**Use it on the user's own single-player game or mod work.** If the user wants to use this in an online or anti-cheat-protected game to gain an advantage, decline that part.

## Object references

| Form | Meaning |
|---|---|
| `/Script/Pkg.Object` or any full path | Exact object |
| `first:ShortClassName` | First live instance UE4SS finds |
| `cdo:/Script/Pkg.Class` | Class default object |

`first:` is convenient but unreliable for gameplay objects: the "first" instance can be a template, a cutscene copy or a pooled actor, not the live one. **For the player pawn or controller, call `world_info` and use the exact paths it reports.** Use `first:` for exploration, and verify the result looks like the live object (check its properties or full name) before drawing conclusions from it.

## Workflows

### Explore: "what does this object have?"
1. `world_info` to get the world, player controller, pawn, game instance and game mode paths.
2. `inspect_object(ref, include_super=true, pattern=...)` with a pattern for what the user cares about (for example `Health|Stamina|Speed`). Without `include_super` you only see the class's own properties; with it you see inherited ones too, which is usually what you want for pawns and controllers.
3. `list_functions(ref)` for the callable surface; filter mentally for names related to the user's goal (movement, interaction, camera).
4. Use `list_types(pattern)` when you only know part of a class name, then `find_objects(class, limit)` for live instances.

### Find what changed: "what happens when I do X?"
This is a two-phase flow that needs the user to act in the game, so split it across turns.
1. `snapshot_object(ref, label, include_super, pattern)` to store a baseline in the game under a label.
2. Tell the user exactly what to do in the game and to reply when done. Then stop; you cannot play for them.
3. `diff_object(label)` reports `{changed, added, removed, same}` by dotted property path (max 500 rows per list, with a `truncated` count). Explain the changes in terms of the user's action, and note that addresses are ignored so an unchanged object diffs empty.
4. Clean up with `forget_snapshot(label)` or `"*"`. Snapshots live in the game process and vanish when the game exits.

### Watch over time: "tell me whenever X changes"
1. `watch_property(ref, names, label, interval_ms, every)` samples properties and records changes. Interval defaults to 250 ms with a 100 ms floor; do not ask for faster. Watching `first:PlayerController` follows the object across respawns (it logs `resumed` and `lost` events).
2. For function calls instead of values, `hook_function(function, label, max_args)` records each call with its parameters. This counts as a write.
3. Tell the user to play, then `poll_events(since, label, limit, clear)`. Pass the returned `next` as `since` on the next poll. If `dropped` is non-zero, the 2000-event shared buffer overflowed and rows were lost; narrow the watch or poll sooner.
4. **When finished, `stop_stream("*")`.** Streams persist inside the game and survive `reload_mod`, so forgotten ones keep costing game-thread time.

**Never call a hooked function from `eval_lua` in the same session.** It has crashed the game. Read hook output only through `poll_events`.

### What is the player looking at?
`targeted_actor(distance, channel, ref)` line-traces from the camera (or from `ref`'s own location and forward vector) and returns the actor, component, impact point, bone, physical material and materials. Useful for identifying meshes, materials and actors in the scene.

### Map a class hierarchy
`list_subclasses(ref, limit, pattern)` returns every loaded subclass, Blueprint classes included, as `{name, kind, path, parent}` rows. Pass a full path such as `/Script/Engine.Pawn`. It is slow (about 1.5 s), so run it once and reuse the result.

### Change a value or call a function
1. Inspect first so you know the property's type and current value.
2. `set_property(ref, name, value)` or `call_function(ref, fn, args)` (positional args). State the previous value from the response.
3. Verify with `get_property` if the effect matters, and revert if the user was only experimenting.
4. Be aware the game may overwrite the value on the next tick (a stat recalculated from a base value, for example). If it reverts, say so and look for the property that drives it instead of looping writes.

### Dumps
`dump(kind)` triggers UE4SS dumpers: `usmap`, `jmap`, `uht`, `cxx`, `actors`, `objects`, `static_meshes`. `usmap` is what the user needs to open cooked assets in tools like FModel. These are slow and write files into the game's UE4SS folder; tell the user the game may appear frozen while it runs and where to look for output.

### Custom Lua with `eval_lua`
The whole UE4SS Lua API plus a `UEB` helper table is in scope, and `print` output is captured. The only helpers documented publicly are `UEB.world()` and `UEB.reload()`. Do not guess other helper names: discover them first, for example `for k, v in pairs(UEB) do print(k, type(v)) end`. Keep chunks short and side-effect-free where possible, and return a value rather than relying on prints.

## Gotchas that cause crashes or wrong answers

- `SoftObjectProperty` and `SoftClassProperty` values are skipped by default because reading one has hard-crashed games inside UE4SS's property reader. Do not work around this with raw `eval_lua` reads unless the user explicitly accepts the crash risk.
- Serialisation is lossy on purpose: UObjects come back as `{"__object": fullname, "address": n}` (use the `__object` name as a new `ref`), arrays are truncated to 200 items, and structs are walked through their reflected type.
- The bridge cannot answer while the game thread is blocked (loading screens, long operations). A timeout there usually means "wait and retry", not "broken".

## Troubleshooting

| Symptom | Likely cause and next step |
|---|---|
| `bridge_status` says no game found | Game not running, or exe is not in a `Binaries\Win64` folder with `ue4ss\` beside it. Ask the user to start it, or pin the path with `--game-dir` / `UE4SS_BRIDGE_GAME_DIR`. |
| Request never picked up | Mod not installed or disabled (`enabled = false`). Check `UE4SS.log` for `[UEBridge] ... ready`. |
| Picked up, no response | Game thread blocked (loading screen) or the request is long. Wait and retry; for a crash, the error names the in-flight operation from `bridge\lastop.log` and the newest crash report. Relay that to the user. |
| Protocol mismatch | Python package and mod versions differ. Ask the user to update both to the same release. |
| "refused" on a write | `allow_writes = false` (or `allow_eval = false` for `eval_lua`). Tell the user; do not try to bypass. |
| Property values look wrong or empty | Probably a `first:` template/pooled instance. Switch to the exact path from `world_info`. |
| Request collisions | Another client or a parallel call. Wait about 10 s, and stop issuing calls in parallel. |
