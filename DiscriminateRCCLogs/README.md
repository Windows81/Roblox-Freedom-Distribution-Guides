Rōblox stores internal-access settings with keys whose names begin with `FLag`, `FInt`, et c. One of the prefixes carries the name `FLog`. `FLog` settings configure verbosity for logging various types of events.

So we need to extract every valid `FLog` setting. This can be done by running [Roblox-x64dbg-FFlag-Extractor](https://github.com/Windows81/Roblox-x64dbg-FFlag-Extractor) on the selected binary.

This tool supports `RobloxStudioBeta.exe`, `RCCService.exe`, and `RobloxPlayerBeta.exe`; the latter two were only tested up to v463.

We start with a value of 100 to ensure that each custom log levels will be unique and won't clash with any standard or predefined log levels. This can be quickly automated per the command below. A cached copy is saved in [`./RFD-FLogs.json`](./RFD-FLogs.json).

Starting from 100 was an arbitrary choice. Log files generated in 2018M don't print the actual name of the FLog tag that's being used. Instead, you only see a number that indicates its verbosity. So I took advantage of the fact that you can use any number as a verbosity marker. And I made it so that each FLog value produces a unique index.

```sh
curl -s "https://github.com/Windows81/Roblox-x64dbg-FFlag-Extractor/raw/refs/heads/main/test/v{348,463}-server.json" -L | jq -s 'add | keys | unique | map(select(. | test("^D?FLog")))'
```

Additionally:

- For 2018M, the level for `FLogRCCServiceInit` always sticks to 6, no matter how we set it in a setting.
- The FLog list did not return `FLogOutput` and `FLogError`, but we should include it anyway.
