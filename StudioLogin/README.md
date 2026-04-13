## How to find the patch?

## Background

I found a version of Studio from late 2021 ([v493.1.15175](https://archive.org/details/roblox-version-1fca050e38094184)) with a patch applied in x86 such that no login screen would be required. There was a change from `jnz` to `jz` at file address `0x002B951C`. This patch was location near a unique string reference to `"Studio.App.AutoSaveDialog.OpenRobloxFile"`. The specific fix that Reggie applied, however, can't be reproduced in my target versions of v348 and v463. However, a very similar one has been confirmed to work in v463.

## Discovery

When you launch v463 Studio without command-line arguments, you are presented with a login screen.

![](image.png)

You may be tempted to try bypassing this through several methods:

1. **Ctrl + O:** a similar message shows up: `"You must log in to open files."`

2. **Dragging to Topbar:** in 2021, the login screen could be bypassed by dragging the desired file from File Explorer to the top of the Studio window. This option does not work in current-day (late 2025) versions of Studio.

3. **Ctrl + N:** Rōblox has this action accounted for. An error string `"You must log in to create new files."` shows up. Let's investigate this option further with x64dbg.

---

![](image-1.png)

In the `RobloxStudioBeta.exe` v463 executable, there are no results for the string `"You must log in to create new files."`

However, you will find that string in the Rōblox Client Tracker data at [`./QtResources/Translation/StudioStringsUntranslated.csv`](https://github.com/MaximumADHD/Roblox-Client-Tracker/blob/f867742be117235b24b2be7500eada1d20ba42f3/QtResources/Translation/StudioStringsUntranslated.csv#L789). The translation-agnostic key is **`"Studio.App.MainWindow.LogInToCreateNewFiles"`**. The CSV data was compressed as a Qt resource. The Client Tracker used the [qtextract](https://github.com/axstin/qtextract.git) tool to extract the CSV data.

I search for string references in user modules in `RobloxStudioBeta.exe` v463 executable (using x64dbg) for `"Studio.App.MainWindow.LogInToCreateNewFiles"`. One result shows up at address `000000014026CD15`.

I add a breakpoint right there at `000000014026CD15`. I make sure that Studio is at the starting login screen and hit Ctrl + N again. The breakpoint is hit.

I step over the execution trace and notice that the message box shows up during a call to `robloxstudiobeta.140266D90`. This call is the first instruction after the breakpoint to use opcode `E8` and is located at `000000014026CD59`: some 12 instructions after the breakpoint.

The routine we're calling begins at `0000000140266D90` and ends at `0000000140266FA1`. Judging by the `mov al, 0x1` near the end, we can infer that it returns a boolean.

---

```
0000000140266DBF | 4C:8B00                  | mov     r8, qword ptr ds:[rax]          |
0000000140266DC2 | 48:8BC8                  | mov     rcx, rax                        |
0000000140266DC5 | 41:FF90 80000000         | call    qword ptr ds:[r8 + 0x80]        | {C}
0000000140266DCC | 803D 6512E802 00         | cmp     byte ptr ds:[0x1430E8038], 0x0  |
0000000140266DD3 | 0F84 02010000            | je      robloxstudiobeta.140266EDB      | {B1}
0000000140266DD9 | 84C0                     | test    al, al                          |
...
0000000140266ED4 | E8 07769201              | call    <robloxstudiobeta.rbxDeallocate |
0000000140266ED9 | EB 08                    | jmp     robloxstudiobeta.140266EE3      |
0000000140266EDB | 84C0                     | test    al, al                          | {B2}
0000000140266EDD | 0F85 AC000000            | jne     robloxstudiobeta.140266F8F      | {A1}
0000000140266EE3 | 0FB60D DEEDEC02          | movzx   ecx, byte ptr ds:[0x143135CC8]  |
0000000140266EEA | 84C9                     | test    cl, cl                          |
0000000140266EEC | 74 0F                    | je      robloxstudiobeta.140266EFD      |
0000000140266EEE | 4C:8BC3                  | mov     r8, rbx                         |
0000000140266EF1 | 48:8D15 60461F02         | lea     rdx, qword ptr ds:[0x14245B558] | 000000014245B558:"[FLog::Always] %s"
0000000140266EF8 | E8 E3AB9201              | call    robloxstudiobeta.141B91AE0      |
0000000140266EFD | 48:8BD3                  | mov     rdx, rbx                        |
0000000140266F00 | 48:8D8C24 A8000000       | lea     rcx, qword ptr ss:[rsp + 0xA8]  |
0000000140266F08 | FF15 CAF3E501            | call    qword ptr ds:[<public: __cdecl  |
0000000140266F0E | 90                       | nop                                     |
0000000140266F0F | C74424 20 FFFFFFFF       | mov     dword ptr ss:[rsp + 0x20], 0xFF |
0000000140266F17 | 45:33C9                  | xor     r9d, r9d                        |
0000000140266F1A | 4C:8D05 0F211E02         | lea     r8, qword ptr ds:[0x142449030]  | 0000000142449030:"Studio.App.MainWindow.RobloxStudio"
0000000140266F21 | 48:8D9424 A0000000       | lea     rdx, qword ptr ss:[rsp + 0xA0]  |
0000000140266F29 | 48:8D0D 685F2102         | lea     rcx, qword ptr ds:[0x14247CE98] |
0000000140266F30 | FF15 AAF9E501            | call    qword ptr ds:[<public: class QS |
0000000140266F36 | 90                       | nop                                     |
0000000140266F37 | C74424 20 00000000       | mov     dword ptr ss:[rsp + 0x20], 0x0  |
0000000140266F3F | 41:B9 00040000           | mov     r9d, 0x400                      |
0000000140266F45 | 4C:8D8424 A8000000       | lea     r8, qword ptr ss:[rsp + 0xA8]   |
0000000140266F4D | 48:8D9424 A0000000       | lea     rdx, qword ptr ss:[rsp + 0xA0]  |
0000000140266F55 | 48:8BCF                  | mov     rcx, rdi                        |
0000000140266F58 | FF15 526BE601            | call    qword ptr ds:[<public: static e |
0000000140266F5E | 90                       | nop                                     |
0000000140266F5F | 48:8D8C24 A0000000       | lea     rcx, qword ptr ss:[rsp + 0xA0]  |
0000000140266F67 | FF15 C3F3E501            | call    qword ptr ds:[<public: __cdecl  |
0000000140266F6D | 90                       | nop                                     |
0000000140266F6E | 48:8D8C24 A8000000       | lea     rcx, qword ptr ss:[rsp + 0xA8]  |
0000000140266F76 | FF15 B4F3E501            | call    qword ptr ds:[<public: __cdecl  |
0000000140266F7C | 32C0                     | xor     al, al                          |
0000000140266F7E | 48:8B9C24 90000000       | mov     rbx, qword ptr ss:[rsp + 0x90]  | [rsp+90]:RtlUserThreadStart+28
0000000140266F86 | 48:81C4 80000000         | add     rsp, 0x80                       |
0000000140266F8D | 5F                       | pop     rdi                             |
0000000140266F8E | C3                       | ret                                     |
0000000140266F8F | B0 01                    | mov     al, 0x1                         | {A2}
0000000140266F91 | 48:8B9C24 90000000       | mov     rbx, qword ptr ss:[rsp + 0x90]  | [rsp+90]:RtlUserThreadStart+28
0000000140266F99 | 48:81C4 80000000         | add     rsp, 0x80                       |
0000000140266FA0 | 5F                       | pop     rdi                             |
0000000140266FA1 | C3                       | ret                                     |
```

To reach the branch where `1` is returned, we need to ensure that `al` is also `1` when the EIP is at `0000000140266EDB`. This is evident by how the statement I notated as `{A1}` can jump directly to `{A2}`. We know that this is the only way to reach this branch because:

1. An unconditional `jmp` instruction is placed in the statement prior to `{B2}`.
2. The statement prior to `{A2}` is a `ret` instruction, effectively serving as a jump.

Owing to the `jmp` statement per (1), we know that `al` comes from some other place, that being before `{B1}`, which is a jump for an unrelated condition. The `al` originates from the result of a function call at `{C}`.

To determine the exact address of this call, we need to add another breakpoint. We do the same test as before to get this breakpoint captured. Once hit, _step into_ that function. In v463, that destination function begins at `00000001405F2100`.

We apply the following patch to ensure that the function always returns a truish vaue.

```patch
-00000001405F2100 | 0FB641 48                | movzx   eax, byte ptr ds:[rcx + 0x48]   | rcx+48:AmdPowerXpressRequestHighPerformance+1C083C
+00000001405F2100 | 0C FF                    | or      al, 0xFF                        |
+00000001405F2102 | 90                       | nop                                     |
+00000001405F2103 | 90                       | nop                                     |
 00000001405F2104 | C3                       | ret                                     |
```
