In the 2016 source code, we have a function called

https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/App/util/Shared/Http.cpp#L1096

```cpp
bool Http::isRobloxSite(const char* url)
```

We want to make sure that this function always returns true.

However, we need to find the function first. To do so, there are some strings that we could look for in the compiled binary. Fortunately, there are plenty that we can use (according to the 2016 source code). Note that the totality of the strings listed below may not reflect other versions of Rōblox.

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

We only need to look for user-module references to one these strings; I chose `"robloxlabs.com"`.

Once I found that string, I made sure that I could find at least one other that is also in the list.
