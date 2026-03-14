Look [here](https://github.com/rbxcdn/RBXGuides/blob/725e38c6a054f7e64c04c26492fe9a1a3987d40e/2020%2B%20Insane%20Guides/SSL.txt):

> [ ⚠️ This asset is provided by https://github.com/rbxcdn ]
>
> patch ssl by jmping CURLOPT_SSL_VERIFYPEER

---

I tried the instructions above. They were unclear and failed when I followed through.

What does this mean?

This procedure is supposed to allow your Rōblox clients to access unsigned HTTPS sites _without_ needing to create a custom cert file in `./ssl/cacert.pem`.

In other words, the included `libcurl` internal stuff will make this change:

```patch
- curl https://setup.roblox.com
+ curl https://setup.roblox.com --insecure
```

This practice is not recommended for most uses. However, RFD's current implementation requires it.

## Quick Guide

1. Search among user-referenced strings for `"CURLOPT_SSL_VERIFYPEER"` and `"CURLOPT_SSL_VERIFYHOST"`, taking into account for results from _both_ searches.

2. For each result, navigating _up_ about 10 instructions until you find one until you see a constant value `0x40` or `0x51`.
   - Ex: `push 40`, `mov r8d, 51`, et c.
   - If one is not found, it is probably safe to skip to the next result.

3. Look nearby for a statement which uses `1` or `2` as a constant value.
   - Ex: `push 1`, et c.
   - If one is not found **here**, best to set a breakpoint at the call that takes place _after_ and take other unexplained measures.

4. Re-assemble the statement from (3) so as to replace `1` or `2` with `0`.

## Background

The actual function which sets the `CURLOPT` isn't in the function call _below_ the string references, but instead above. That's because cURL options are actually defined as enum integers.

For example, in [the 2016 source code](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/App/util/Shared/HttpPlatformImpl.cpp#L641):

```cpp
logCurlError("CURLOPT_FOLLOWLOCATION", curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1));
```

Which corresponds, in the compiled RobloxPlayerBeta v463, to:

```x86asm
push 0
push 34
push dword ptr ds:[edi+148]
call robloxplayerbeta.1540770 // 1540770:curl_easy_setopt
add esp,C
push eax
push robloxplayerbeta.21AA128 // 21AA128:"CURLOPT_FOLLOWLOCATION"
```

Note the `push 34`, whose `CURLOPT` enum integer corresponds to `0x34`, according to [other programs which define the enums](https://github.com/ServersHub/Ark-Server-Plugins/blob/eabcf9276787889b2c0ef74b64bcd691a7821799/GamingOGs%20Plugins/gogcommandlogger-master/include/API/ARK/Enums.h#L10486):

```c
CURLOPT_FOLLOWLOCATION = 0x34,
```

We do not specifically need to change `CURLOPT_FOLLOWLOCATION`. I just use it as an example since its name is present in the 2016 source code.

But rather, I am interested in

- `CURLOPT_SSL_VERIFYPEER` to be set to 0, and
- `CURLOPT_SSL_VERIFYHOST` to be set to 0 (only if explicitly provided).

## 0.463 RobloxPlayerBeta

Two entries for `CURLOPT_SSL_VERIFYPEER`.

![alt text](image-3.png)

Both are nearby.

![alt text](image-9.png)

```c
CURLOPT_SSL_VERIFYPEER = 0x40,
```

Note how the assembly code before the references differs between each.

```x86asm
push 0
push 0x40
push dword ptr ds:[edi+148]
call robloxplayerbeta.1540770
```

```x86asm
push 1
push 0x40
push dword ptr ds:[edi+148]
call robloxplayerbeta.1540770
```

Arguments are put on the stack in reverse order in x86. So the `0` or `1` disables or enables the `CURLOPT_SSL_VERIFYPEER` option, depending on branching action. Let's patch the second one.

```patch
- push 0
+ push 1
push 0x40
push dword ptr ds:[edi+148]
call robloxplayerbeta.1540770
```

We're not done yet! Because we need to ensure that `CURLOPT_SSL_VERIFYHOST` is also set to `0`. Note that unlike the previous cURL option, the value that we need to replace from is `2`, instead of `1`.

```c
CURLOPT_SSL_VERIFYHOST = 0x51,
```

![alt text](image-11.png)

```patch
push 1
- push 2
+ push 0
push 0x51
push dword ptr ds:[edi+148]
call robloxplayerbeta.1540770
add esp,C
push eax
push robloxplayerbeta.21AA068 # 21AA068:"CURLOPT_SSL_VERIFYHOST"
push edi
call robloxplayerbeta.14EAFE0
```

## 0.463 RCCService

Let's open 2021E (v463) RCCService.exe in `x32dbg`.

![Search for user-module strings](image.png)

**Four** different results for `CURLOPT_SSL_VERIFYPEER`!

But we only need to concern ourselves with one pair of results, as the other is completely irrelevant and has a completely different execution flow to what we did for `RobloxPlayerBeta`.

![alt text](image-12.png)

![alt text](image-13.png)

We have no results for `CURLOPT_SSL_VERIFYHOST`,

![alt text](image-14.png)

But there is no need to fix that.

![alt text](image-15.png)

RCC already uses your system's certs anyway.

## 0.463 Studio

I found three results for `"CURLOPT_SSL_VERIFYHOST"`.

I looked at the first result, `0000000141B404EC`.

When I navigated to the preceding call, I found that the immediate `2` is not visible:

```
0000000141B404C2 | BA 51000000              | mov     edx, 0x51                       |
0000000141B404C7 | 44:8D42 B1               | lea     r8d, qword ptr ds:[rdx - 0x4F]  | {A}
0000000141B404CB | 48:8B8F 98010000         | mov     rcx, qword ptr ds:[rdi + 0x198] |
0000000141B404D2 | E8 C9390A00              | call    robloxstudiobeta.141BE3EA0      | {B}
```

However, upon setting a breakpoint at `{B}`, x64dbg it gives me the following call stack:

```
1: rcx 0000000002EE37E0 0000000002EE37E0
2: rdx 0000000000000051 0000000000000051
3: r8 0000000000000002 0000000000000002
4: r9 0000000000000000 0000000000000000
5: [rsp+20] FFFFFFFFFFFFFFFE FFFFFFFFFFFFFFFE
```

Since Studio is a 64-bit program, some of the function arguments are in individual registers. We find the `2` in register `r8`. This register seems to be extracted from another variable in a specific address at `{A}`. We want to make sure that it always loads `0` into `r8d`.

We know of a shorthand that does not take up too many bytes: `xor r8d, r8d`.

```patch
0000000141B404C2 | BA 51000000              | mov     edx, 0x51                       |
- 0000000141B404C7 | 44:8D42 B1               | lea     r8d, qword ptr ds:[rdx - 0x4F]  |
+ 0000000141B404C7 | 45:31C0                  | xor     r8d, r8d                        |
+ 0000000141B404CA | 90                       | nop                                     |
0000000141B404CB | 48:8B8F 98010000         | mov     rcx, qword ptr ds:[rdi + 0x198] |
0000000141B404D2 | E8 C9390A00              | call    robloxstudiobeta.141BE3EA0      |
```

I discovered I only need to make that change for one single result.
