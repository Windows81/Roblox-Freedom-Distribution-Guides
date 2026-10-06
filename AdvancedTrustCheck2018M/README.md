Rōblox's clients _require_ use of Rōblox's website and services to operate under normal conditions. Some revivals get around this restriction by using a hex editor to _replace_ every raw-string instance of `roblox.com` with their own domain name (e.g. `synt2x.xyz`). This design works for some revival websites that don't need to keep swiching hostnames, but _not_ Rōblox Freedom Distribution.

Instead, Rōblox Freedom Distribution takes advantage of the open secret of how Rōblox allows use of a different hostname by introducing a custom `BaseUrl` field to `AppSettings.xml`. This mechanism exists so that Rōblox employees could test Rōblox's programs using their own staging servers (i.e., _not_ `roblox.com`). However, what you can include in the `BaseUrl` input is tightly limited.

In the 2016 source code, we have a function called `Http::isRobloxSite`:

https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/App/util/Shared/Http.cpp#L1096

```cpp
bool Http::isRobloxSite(const char* url)
```

### Locating the Function

We want to make sure that this function always returns true.

However, we need to find the function first. To do so, there are some strings that we could look for in the compiled binary. Fortunately, there are plenty of strings that we can use (according to the 2016 source code). Note that the totality of the strings listed below may not reflect other versions of Rōblox.

- `"roblox.com"`
- `"robloxlabs.com"`
- `"login.facebook.com"`
- `"/login.php"`
- `"ssl.facebook.com"`
- `"/connect/uiserver.php"`
- `"www.facebook.com"`
- `"/connect/uiserver.php"`
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
- `"roblox.com"`
- `"robloxlabs.com"`
- `"login.facebook.com"`
- `"/login.php"`
- `"ssl.facebook.com"`
- `"/connect/uiserver.php"`
- `"www.facebook.com"`
- `"/connect/uiserver.php"`
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
- `"roblox.com"`
- `".roblox.com"`
- `"robloxlabs.com"`
- `".robloxlabs.com"`
- `"login.facebook.com"`
- `"/login.php"`
- `"ssl.facebook.com"`
- `"/connect/uiserver.php"`
- `"www.facebook.com"`
- `"/connect/uiserver.php"`
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

_Using a code-analysis tool such as x32dbg_, we only need to look for user-module references to one these strings; I chose to do this twice, each on a different function:

- one with a string reference to `"/serviceloginauth"`, and
- one with a string reference to `"login.facebook.com"`

### Patching in x86

Since the function returns a boolean value, **we need to ensure that it always returns a true-ish value**.

In x86 assembly, we achieve this when the register `al` is _not_ equal to zero.

Scroll _up_ until you find the start of the function.

Note that:

- it takes some skill to find, but
- the first bytes are `55 8B EC 53` in v347.

Then, replace the head with:

```asm
mov al, FF
ret 4
```

If you encounter a crash, redo the patch, but using `ret 8` instead of `ret 4`.
