# Bypassing Video Limits in Rōblox v463

As of Rōblox v463, videos are limited to a resolution of 1280x720 by default. Also, for concurrency, Rōblox limits clients to two simultaneous videos. I went ahead and fixed these issues.

**Only `.webm` containers are supported in v463.** Use FFmpeg or something if you couldn't bring one of these containers with you.

## Quick Guide

This guide walks you through freeing Rōblox v463 from the limitations specified above.

In Rōblox version 463, you can simply apply the `v463-player.1337` and `v463-studio.1337` files as patches in x96dbg.

### Resolution Limits

In Studio v463:

```
000000014130B0E4 | 48:8983 60010000         | mov     qword ptr ds:[rbx + 0x160], rax |
000000014130B0EB | 48:89BB 68010000         | mov     qword ptr ds:[rbx + 0x168], rdi |
000000014130B0F2 | 48:89AB 70010000         | mov     qword ptr ds:[rbx + 0x170], rbp |
000000014130B0F9 | 48:89AB 78010000         | mov     qword ptr ds:[rbx + 0x178], rbp |
000000014130B100 | 48:8BCE                  | mov     rcx, rsi                        |
000000014130B103 | E8 58C0B000              | call    <JMP.&_Mtx_unlock>              |
000000014130B108 | 85C0                     | test    eax, eax                        |
000000014130B10A | 74 08                    | je      robloxstudiobeta.14130B114      |
000000014130B10C | 8BC8                     | mov     ecx, eax                        |
000000014130B10E | E8 53C0B000              | call    <JMP.&void __cdecl std::_Throw_ |
000000014130B113 | 90                       | nop                                     |
000000014130B114 | 803D 3DCDE001 00         | cmp     byte ptr ds:[0x143117E58], 0x0  |
000000014130B11B | 75 1B                    | jne     robloxstudiobeta.14130B138      |
000000014130B11D | 48:83BB 58030000 00      | cmp     qword ptr ds:[rbx + 0x358], 0x0 |
000000014130B125 | 75 11                    | jne     robloxstudiobeta.14130B138      |
000000014130B127 | 48:8BCB                  | mov     rcx, rbx                        |
000000014130B12A | E8 51D1FFFF              | call    robloxstudiobeta.141308280      |
000000014130B12F | 48:8D15 42774C01         | lea     rdx, qword ptr ds:[0x1427D2878] | 00000001427D2878:"Video files without video streams are not supported."
000000014130B136 | EB 3F                    | jmp     robloxstudiobeta.14130B177      |
000000014130B138 | 8B8B 28030000            | mov     ecx, dword ptr ds:[rbx + 0x328] | {R1}
000000014130B13E | 3B0D 9CCBE001            | cmp     ecx, dword ptr ds:[0x143117CE0] |
000000014130B144 | 7F 22                    | jg      robloxstudiobeta.14130B168      | {A1}
000000014130B146 | 8B83 2C030000            | mov     eax, dword ptr ds:[rbx + 0x32C] |
000000014130B14C | 3B05 92CBE001            | cmp     eax, dword ptr ds:[0x143117CE4] |
000000014130B152 | 7F 14                    | jg      robloxstudiobeta.14130B168      | {A2}
000000014130B154 | 3B0D 9ECBE001            | cmp     ecx, dword ptr ds:[0x143117CF8] |
000000014130B15A | 7C 0C                    | jl      robloxstudiobeta.14130B168      | {A3}
000000014130B15C | 3B05 9ACBE001            | cmp     eax, dword ptr ds:[0x143117CFC] |
000000014130B162 | 7C 04                    | jl      robloxstudiobeta.14130B168      | {A4}
000000014130B164 | 33C0                     | xor     eax, eax                        |
000000014130B166 | EB 1E                    | jmp     robloxstudiobeta.14130B186      | {B} {R2}
000000014130B168 | 48:8BCB                  | mov     rcx, rbx                        | {A0}
000000014130B16B | E8 10D1FFFF              | call    robloxstudiobeta.141308280      |
000000014130B170 | 48:8D15 39774C01         | lea     rdx, qword ptr ds:[0x1427D28B0] | 00000001427D28B0:"Video is using a resolution that is not supported."
000000014130B177 | B9 03000000              | mov     ecx, 0x3                        |
000000014130B17C | E8 9F729BFF              | call    robloxstudiobeta.140CC2420      |
000000014130B181 | B8 05000080              | mov     eax, 0x80000005                 |
000000014130B186 | 48:8B5C24 50             | mov     rbx, qword ptr ss:[rsp + 0x50]  |
000000014130B18B | 48:8B6C24 58             | mov     rbp, qword ptr ss:[rsp + 0x58]  |
000000014130B190 | 48:8B7424 60             | mov     rsi, qword ptr ss:[rsp + 0x60]  |
000000014130B195 | 48:8B7C24 68             | mov     rdi, qword ptr ss:[rsp + 0x68]  |
000000014130B19A | 48:83C4 40               | add     rsp, 0x40                       |
000000014130B19E | 41:5E                    | pop     r14                             |
000000014130B1A0 | C3                       | ret                                     |
```

First, we are targeting the string `"Video is using a resolution that is not supported."`; that error string gets printed if a video exceeds a set resolution limit of 720p.

Note that multiple conditional jumps converge upon `{A0}` as shown above. I've thus labelled them `{A1}` thru `{A4}`. This is because multiple conditions are checked. If none of them take the branch, we make an unconditional jump at `{B}`.

Let's fill these jumps and their associated comparisons with `nop`. This means every instruction between `{R1}` and `{R2}`, inclusive.

### Concurrency Limits

By default, Rōblox only allows clients to play two videos simultaneously. Let's bypass this.

There is one user-string reference to `"At most %d videos can play simultaneously."`, which we can bypass by making unconditional the preceding jump statement.

```patch
 0000000141265F62 | E8 D910CEFF              | call    robloxstudiobeta.140F47040      |
 0000000141265F67 | 84C0                     | test    al, al                          |
-0000000141265F69 | 75 27                    | jne     robloxstudiobeta.141265F92      |
+0000000141265F69 | EB 27                    | jmp     robloxstudiobeta.141265F92      |
 0000000141265F6B | 44:8B05 021EEB01         | mov     r8d, dword ptr ds:[0x143117D74] |
 0000000141265F72 | 48:8D15 B7CD5401         | lea     rdx, qword ptr ds:[0x1427B2D30] | 00000001427B2D30:"At most %d videos can play simultaneously."
```
