**The following guide was adapted from [Jetray's original text](./2021E%20roblox%20patching.txt) with significant help from Deepseek's _Instant_ model on _chat.deepseek.com_.** Whilst I dislike AI slop, one of my guilty pleasures is admiring how well LLMs organise their Markdown outputs. The least I do is disclose that I used LLMs here.

---

Thank you for the corrections. Here is the revised guide with GitHub-style admonitions, corrected notes about MediaFire links, and the updated `cacert.pem` information.

---

# Revised Guide: Patching Rōblox Client & RCCService (Version 463, "2021E")

> [!NOTE]
> The MediaFire links in the original guide are not dead as of 2026-05-22, but they are also **not needed** for a modern patching approach. This revision omits them entirely.

> [!IMPORTANT]
> The `ssl/cacert.pem` file **does not need to exist at all** anymore. SSL bypass is handled entirely via the `localhost/.test` method and the trust check patches.

---

## Prerequisites

- Basic x86/x64 patching knowledge (recognize `je`/`jne`/`jmp`, use a debugger)
- Windows OS (any version)
- **Tools needed:**
  - `x64dbg` (with `x32dbg.exe`)
  - `HxD` (hex editor)
  - `Stud_PE` (PE editor – full name: _Stud_PE The Portable Executables Viewer/Editor_)
  - A working local webserver (e.g., UwAMP, XAMPP, or PHP built-in server)

---

## Step 1: Client Patching (RobloxPlayerBeta.exe, version 463)

### 1.1 Basic configuration

- Locate `AppSettings.txt` next to the client.
- Change `http://www.roblox.com` → `http://localhost/.test`
  _(localhost bypasses SSL certificate validation in this build)_

### 1.2 Debugging & VMProtect bypass

- Open `x32dbg.exe` → drag in `RobloxPlayerBeta.exe`
- Go to **Symbols** tab → find `RobloxPlayerBeta.exe` → wait for it to load
- Click the **Run** (F9) button **twice** – this bypasses VMProtect entry point obfuscation

### 1.3 Patch trust check

- Right-click anywhere in CPU pane → **Search for** → **Current Module** → **String references**
- Search for `"trust check failed"`
- For each result:
  - Find the `je` or `jne` instruction **above** it
  - Click on that `je`/`jne` → press **Spacebar** → change to `jmp` → press Enter

### 1.4 Patch `127.0.0.1` check (if present)

- Search strings again for `"127.0.0.1"`
- Find the result where:
  - A `je` appears above it
  - Under that `je` there is a `push D188`
- Change that `je` → `jmp`
- If another `127.0.0.1` under a `je`/`jne` appears nearby, also `jmp` it.

### 1.5 `ClientAppSettings.json`

- Create a folder named `ClientSettings` next to `RobloxPlayerBeta.exe`
- Inside it, create `ClientAppSettings.json` with your desired flags (e.g., disabling telemetry, enabling local dev features).

> [!NOTE]
> The original MediaFire link for `ClientAppSettings.json` is not needed. Use your own or a known-good configuration for version 463.

### 1.6 SSL certificate replacement

> [!NOTE]
> **SKIPPED** – The `ssl/cacert.pem` file does not need to exist at all anymore. The `localhost/.test` method combined with trust check patches fully bypasses SSL requirements.

### 1.7 DLL injection via Stud_PE (deprecated)

> [!WARNING]
> **DEPRECATED** – The original guide's `Injector.dll` + Stud_PE import method is obsolete. Better patches exist. Do not follow this step.

---

## Step 2: Patching the Server (RCCService.exe)

### 2.1 Hex edit HTTPS → HTTP

- Open `RCCService.exe` in **HxD**
- Search for hex: `00 68 74 74 70 73 00`
- Replace with: `00 68 74 74 70 00 00`
- Save

### 2.2 Debugger patches (RCC has no VMProtect)

- Open `RCCService.exe` in `x32dbg` (no double-F9 needed)
- String references → search for `"trust check failed"` → patch `je`/`jne` → `jmp` as before
- Search for `"Non-trusted BaseURL used. HttpRbxApiService is only for Rōblox API calls"` → patch the conditional jump above it → `jmp`

### 2.3 Configuration files

Place these in **the same folder as `RCCService.exe`**:

- `DevSettingsFile.json`
- `gameserver.json`

> [!NOTE]
> The original MediaFire links for these files are not needed. Create your own or obtain version-463-compatible configurations.

---

## Step 3: Local Website Setup

> [!NOTE]
> Rōblox Freedom Distribution, a long-term successor to Jetray's Filtering Disabled is bundled with a Python-based webserver. The original MediaFire webserver package is not required.

- Use **UwAMP** (old) **or any capable webserver**
- Implement these minimal endpoints:
  - `POST /Login/Negotiate.ashx` – returns a dummy auth ticket
  - `GET /game/placelauncher.ashx` – returns place launch data (JSON)
  - `GET /asset/` – serves content from your local `Content` folder

---

## Step 4: Running

### Server command

```cmd
RCCService.exe -Console -verbose -placeid:1818 -localtest "gameserver.json" -settingsfile "DevSettingsFile.json" -port 64989
```

### Client command

```cmd
start RobloxPlayerBeta.exe -a "http://localhost/Login/Negotiate.ashx" -j "http://localhost/game/placelauncher.ashx" -t "1"
```

---

## Common Issues & Notes

| Error                         | Likely cause                                                                                              |
| ----------------------------- | --------------------------------------------------------------------------------------------------------- |
| `placeId verification failed` | Wrong or missing `Content` folder, or place ID not matching a valid place in your local `gameserver.json` |
| SSL errors                    | `localhost/.test` not set correctly in `AppSettings.txt`                                                  |
| `Injector.dll` not found      | You attempted the **deprecated** Stud_PE step – ignore and use modern patches instead                     |
| `Content.7z`                  | **Irrelevant** – ignore this step entirely                                                                |

> [!CAUTION]
> If you run into other issues, verify that all patches were applied correctly. The original guide's `Content.7z` link is not needed for a basic working setup.

---

## Final Notes

- The original guide's MediaFire links are not dead as of 2026-05-22, but they are **omitted here** as they are unnecessary for modern patching.
- The **Stud_PE + Injector.dll** method is **deprecated** – use direct in-memory patching instead.
- The `ssl/cacert.pem` file **no longer needs to exist**.
- For a fully working setup, you will need a **complete local emulator stack** (compatible `Content` folder, Lua executor hooks, and a webserver that mimics Rōblox APIs).
