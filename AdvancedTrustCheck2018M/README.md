Rōblox's clients _require_ use of Rōblox's website and services to operate under normal conditions. Some revivals get around this restriction by using a hex editor to _replace_ every raw-string instance of `roblox.com` with their own domain name (e.g. `synt2x.xyz`). This design works for some revival websites that don't need to keep swiching hostnames, but _not_ Rōblox Freedom Distribution.

Instead, Rōblox Freedom Distribution takes advantage of the open secret of how Rōblox allows use of a different hostname by introducing a custom `BaseUrl` field to `AppSettings.xml`. This mechanism exists so that Rōblox employees could test Rōblox's programs using their own staging servers (i.e., _not_ `roblox.com`).

However, what you can include in the `BaseUrl` input is tightly limited.

I have found two patches that are required for proper functioning:

## Quick Guides

0. Open your EXE (i.e., Player, RCC, or Studio) in x32dbg.

1. Search for references to `"Trust check failed"`.
   - There will be _one_ result in Rōblox version 347.

2. Navigate to that result, then scroll about 10 lines
   _up_ to a `call` instruction.

3. Once that `call` is found, navigate to _that_.

4. Replace the function head (i.e. `55 8B EC ...`) with `30 C0 C2 04 00`

---

5. Search for references to `"/serviceloginauth"`.
   - There will be _one_ result in Rōblox version 347.

6. Select the 50 lines _above_ the call, then hit _Ctrl + R_ to locate references to that function head.
   - Only one of these results should be a `call`.

7. Navigate to that `call` and go to its destination address. This is your function head.

8. Replace the function head (i.e. `55 8B EC ...`) with `0C FF C2 04 00`

9. Repeat steps (5) thru (8), except that step (5) uses `"login.facebook.com"`.

## Background

ll the functions that we're patching return _boolean_ values. **We need to ensure that each function returns a fixed value**.

In x86 assembly, we achieve this when the register `al` is _not_ equal to zero.

We can find the head of an x86 function by looking for the byte pattern `55 8B EC`. This will correspond to:

```asm
push
mov ebp,esp
```

Then, _replace_ the head's first five bytes with:

- `0C FF C2 04 00` for **`true`**, which corresponds to:

```asm
mov al, FF
ret 4
```

- `30 C0 C2 04 00` for **`false`**, which corresponds to:

```asm
xor al, al
ret 4
```

**If you happen to encounter a crash**, _redo_ the patch, but using `ret 8` instead of `ret 4`.

### (1) `"Trust check failed"`

This patch location will force code that throws an error with the string `"Trust check failed"` to never execute.

To do this, we need to modify `Http::trustCheck`.

#### Examples of Use Per 2016 Source

The same code pattern appears each time. Note that the exact same `Http::trustCheck`

```cpp
if (!Http::trustCheck(theUrl.c_str(), externalRequest))
	throw RBX::runtime_error("trust check failed for %s", theUrl.c_str());
```

```cpp
if (!Http::trustCheck(theUrl.c_str(), externalRequest))
	throw RBX::runtime_error("trust check failed for %s", theUrl.c_str());
```

... and most importantly ...

```cpp
ThrowIfFailure(trustCheck(url.c_str(), true), "Trust check failed");
```

#### Locating the Function

In `RCCservice.exe` version 347, the last snippet corresponds to:

```
00521176 | 8BC7                     | mov eax,edi                                     |
00521178 | 8B5D 18                  | mov ebx,dword ptr ss:[ebp+18]                   |
0052117B | 53                       | push ebx                                        |
0052117C | 50                       | push eax                                        |
0052117D | E8 1E230000              | call rccservice.5234A0                          |
00521182 | 83C4 08                  | add esp,8                                       |
00521185 | 837F 14 10               | cmp dword ptr ds:[edi+14],10                    |
00521189 | 72 02                    | jb rccservice.52118D                            |
0052118B | 8B3F                     | mov edi,dword ptr ds:[edi]                      |
0052118D | 84C0                     | test al,al                                      |
0052118F | 74 2B                    | je rccservice.5211BC                            |
00521191 | 68 1C6C0C01              | push rccservice.10C6C1C                         | 10C6C1C:"Trust check failed"
00521196 | 57                       | push edi                                        |
00521197 | 8D85 10FFFFFF            | lea eax,dword ptr ss:[ebp-F0]                   |
0052119D | 68 146C0C01              | push rccservice.10C6C14                         | 10C6C14:"%s: %s"
005211A2 | 50                       | push eax                                        |
005211A3 | E8 18B17000              | call rccservice.C2C2C0                          |
```

Our target is the most recent `call` prior to the string reference to `"Trust check failed"`.

Unlike in the 2016 source, where we would want the function to return _true_, we need to ensure **that `rccservice.5234A0` returns false**.

This is because of the `je` that follows the `test al,al`, _which would only jump if `al` is zero (i.e. false)_.

Also, you'll know when you're in the right function if `"about:blank"` shows up about 20 lines below the head.

### (2) `Http::isRobloxSite`

In the 2016 source code, we have a function called `Http::isRobloxSite`:

https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/App/util/Shared/Http.cpp#L1096

```cpp
bool Http::isRobloxSite(const char* url)
```

We want to make sure that this function always returns a bool-true value.

However, we need to find the function first. To do so, there are some strings that we could look for in the compiled binary. Fortunately, there are plenty of strings that we can use (according to the 2016 source code). Note that the totality of the strings listed below may not reflect other versions of Rōblox.

- `"roblox.com"`
- `"robloxlabs.com"`
- `"login.facebook.com"`
- `"/login.php"`
- `"ssl.facebook.com"`
- `"/connect/uiserver.php"`
- `"www.facebook.com"`
- `"/logout.php"`
- `"www.youtube.com"`
- `"/auth_sub_request"`
- `"/signin"`
- `"/issue_auth_sub_token"`
- `"uploads.gdata.youtube.com"`
- `"www.google.com"`
- `"/accounts/serviceloginauth"`
- `"accounts.google.com"`
- `"/serviceloginauth"`
- `".roblox.com"`
- `".robloxlabs.com"`

#### Locating the Function

_Using a code-analysis tool such as x32dbg_, we only need to look for user-module references to one these strings.

From my observations, Rōblox version 347 does not have a single function that contains all the strings listed.

Instead, I selected _two_ strings, and then patched the function once for each of these strings:

- `"/serviceloginauth"`
- `"login.facebook.com"`
