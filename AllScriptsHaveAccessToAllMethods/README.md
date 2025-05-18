Difficult patch.

This guide is only currently applicable for v463.

Prepared patches are availble, assuming that [you have ASLR disabled](https://github.com/adamhlt/ASLR-Disabler/releases).

- [[RCC]](v463-rcc.1337)
- [[Player]](v463-player.1337)

I wanted to use an FFlag initialised but not _really_ being used anywhere. For v463, I chose `FFlag::Q220PermissionsSettings` after my own personal research.

However, we'll be causing undefined behaviour with `FFlag::ParallelLua` by overwriting some of the branch logic it uses.

These steps should be followed for both RCC and the client to achieve your desired result.

1. Before anything else, make sure [you have ASLR disabled](https://github.com/adamhlt/ASLR-Disabler/releases).

   - Otherwise, the FFlag addresses will change after each program-run and x32dbg won't be able to account for that.

2. Open x32dbg and attach your executable.

3. Search for the ROT13 string: `Gur pheerag vqragvgl (%q) pnaabg %f (ynpxvat crezvffvba %q`.

   - This cypherstring correponds to `The current identity (%d) cannot %s (lacking permission %d)`.

4. Add a breakpoint at function entry (`push ebp`).

5. Run a command in the dev console to trigger the error message. Perhaps something like:

```lua
game.HttpService:RequestInternal({Url = "https://google.com"}):Start(function(success, dataTable) print(success) end)
```

6. Once the breakpoint is hit, go one level up the call stack.

---

###

7. FFlag values are often stored in static memory addresses. Locate the address for `Q220PermissionsSettings`.
   - To do this, you'd want to search for user-module code referencing the `Q220PermissionsSettings` string.
   - I personally receive _one_ result in v463 (as shown below). If you get more than one, look for the result which looks most similar to mine.
   - I'll take the statement above the string declaration (`push robloxplayerbeta.2539BC8`).
   - In this case, I'll keep **`2539BC8`** in my mind for future steps.

```
004E49AC | CC                       | int3                                    |
004E49AD | CC                       | int3                                    |
004E49AE | CC                       | int3                                    |
004E49AF | CC                       | int3                                    |
004E49B0 | 6A 01                    | push 1                                  |
004E49B2 | 68 C89B5302              | push robloxplayerbeta.2539BC8           |
004E49B7 | 68 EC3BF501              | push robloxplayerbeta.1F53BEC           | 1F53BEC:"Q220PermissionsSettings"
004E49BC | E8 5F460301              | call robloxplayerbeta.1519020           |
004E49C1 | 83C4 0C                  | add esp,C                               |
004E49C4 | A3 741E6A02              | mov dword ptr ds:[26A1E74],eax          |
004E49C9 | C3                       | ret                                     |
004E49CA | CC                       | int3                                    |
004E49CB | CC                       | int3                                    |
004E49CC | CC                       | int3                                    |
004E49CD | CC                       | int3                                    |
```

8. Apply the following patches, keeping in mind to

- Replace all instances in my example of `2539BC8` with a new value specific to your implementation, and to
- Look out for references to `84494F` and `844984` in the `je` statements.

**Note:** this patch is version-specific. Differences in jmp instruction offsets and `FFlag::ParallelLua` behaviour may require adjustments for compatibility with other versions.

```patch
-00844937 | 803D 44B35302 00         | cmp byte ptr ds:[253B344],0             | 253B344 corresponds to FFlag::ParallelLua
+00844937 | 803D C89B5302 01         | cmp byte ptr ds:[2539BC8],1             | 2539BC8 corresponds to FFlag::Q220PermissionsSettings

 0084493E | 8B30                     | mov esi,dword ptr ds:[eax]              |

-00844940 | 74 0D                    | je robloxplayerbeta.84494F              | 84494F {A} corresponds to the first address after our new `nop` cluster
+00844940 | 74 42                    | je robloxplayerbeta.844984              | 844984 {B} corresponds to where `jmp`s go after the failure guard clauses

-00844942 | 56                       | push esi                                |
-00844943 | 53                       | push ebx                                |
-00844944 | FF75 08                  | push dword ptr ss:[ebp+8]               |
-00844947 | E8 F4D6FFFF              | call robloxplayerbeta.842040            |
-0084494C | 83C4 0C                  | add esp,C                               |
+00844942 | 90                       | nop                                     |
+00844943 | 90                       | nop                                     |
+00844944 | 90                       | nop                                     |
+00844945 | 90                       | nop                                     |
+00844946 | 90                       | nop                                     |
+00844947 | 90                       | nop                                     |
+00844948 | 90                       | nop                                     |
+00844949 | 90                       | nop                                     |
+0084494A | 90                       | nop                                     |
+0084494B | 90                       | nop                                     |
+0084494C | 90                       | nop                                     |
+0084494D | 90                       | nop                                     |
+0084494E | 90                       | nop                                     |

 0084494F | 8B46 20                  | mov eax,dword ptr ds:[esi+20]           | Marker {A}
 00844952 | 8945 0C                  | mov dword ptr ss:[ebp+C],eax            |
 00844955 | 85C0                     | test eax,eax                            |
 00844957 | 74 2B                    | je robloxplayerbeta.844984              |
 00844959 | 8B7E 04                  | mov edi,dword ptr ds:[esi+4]            |
 0084495C | 837F 14 10               | cmp dword ptr ds:[edi+14],10            |
 00844960 | 72 02                    | jb robloxplayerbeta.844964              |
 00844962 | 8B3F                     | mov edi,dword ptr ds:[edi]              |
 00844964 | 50                       | push eax                                |
 00844965 | FF75 10                  | push dword ptr ss:[ebp+10]              |
 00844968 | E8 43ABAF00              | call robloxplayerbeta.133F4B0           |
 0084496D | 83C4 08                  | add esp,8                               |
 00844970 | 84C0                     | test al,al                              |
 00844972 | 75 10                    | jne robloxplayerbeta.844984             |
 00844974 | 57                       | push edi                                |
 00844975 | FF75 0C                  | push dword ptr ss:[ebp+C]               |
 00844978 | 8B7D 10                  | mov edi,dword ptr ss:[ebp+10]           |
 0084497B | 8BCF                     | mov ecx,edi                             |
 0084497D | E8 AEABAF00              | call robloxplayerbeta.133F530           |
 00844982 | EB 03                    | jmp robloxplayerbeta.844987             |
 00844984 | 8B7D 10                  | mov edi,dword ptr ss:[ebp+10]           | Marker {B}
 00844987 | 803D DC905302 00         | cmp byte ptr ds:[25390DC],0             |
```

If you're using x32dbg, there should be 17 patches here total.

---

**Note:** by default, classes of high security can't be contained by measly variables in user scripts. So we apply additional patches against `Class security check`.

9. Search for string references to `Class security check`. You'll find four grouped together in pairs pretty close to each other.

| Address    | Disassembly                     | String Address | String                   |
| ---------- | ------------------------------- | -------------- | ------------------------ |
| `0067A191` | `push robloxplayerbeta.1F495BC` | `01F495BC`     | `"Class security check"` |
| `0067A1C3` | `push robloxplayerbeta.1F495BC` | `01F495BC`     | `"Class security check"` |
| `0067A217` | `push robloxplayerbeta.1F495BC` | `01F495BC`     | `"Class security check"` |
| `0067A248` | `push robloxplayerbeta.1F495BC` | `01F495BC`     | `"Class security check"` |

- Mentally group the four results into pairs.
- The first pair is contained in a nearly identical function body to the second.
  - Both begin with `push ebp`, then `mov ebp, esp`, and finish with `ret 4`. And each should be about 120 bytes big.
  - In some cases, you may find random instructions (designated `[rubbish]` below). Ignore those.

10. Perform the patches below.
    - The long chain of `nop` instructions is what completely replaces the first function body.
    - Look out for lettered annotations.

```patch
 0067A15C | CC                       | int3                                    |
 0067A15D | CC                       | int3                                    |
 0067A15E | CC                       | int3                                    |
 0067A15F | CC                       | int3                                    |
-0067A160 | 55                       | push ebp                                |
-0067A161 | 8BEC                     | mov ebp,esp                             |
-0067A163 | 51                       | push ecx                                |
-0067A164 | 8B41 0C                  | mov eax,dword ptr ds:[ecx+C]            |
-0067A167 | 56                       | push esi                                |
-0067A168 | 894D FC                  | mov dword ptr ss:[ebp-4],ecx            |
-0067A16B | 8BB0 D0010000            | mov esi,dword ptr ds:[eax+1D0]          |
-0067A171 | 85F6                     | test esi,esi                            |
-0067A173 | 75 06                    | jne robloxplayerbeta.67A17B             |
-0067A175 | 8079 24 00               | cmp byte ptr ds:[ecx+24],0              |
-0067A179 | 74 62                    | je robloxplayerbeta.67A1DD              |
-0067A17B | 57                       | push edi                                |
-0067A17C | 8B7D 08                  | mov edi,dword ptr ss:[ebp+8]            |
-0067A17F | 85F6                     | test esi,esi                            |
-0067A181 | 74 1E                    | je robloxplayerbeta.67A1A1              |
-0067A183 | 56                       | push esi                                |
-0067A184 | 57                       | push edi                                |
-0067A185 | E8 2653CC00              | call robloxplayerbeta.133F4B0           |
-0067A18A | 83C4 08                  | add esp,8                               |
-0067A18D | 84C0                     | test al,al                              |
-0067A18F | 75 0D                    | jne robloxplayerbeta.67A19E             |
-0067A191 | 68 BC95F401              | push robloxplayerbeta.1F495BC           | 1F495BC:"Class security check"
-0067A196 | 56                       | push esi                                |
-0067A197 | 8BCF                     | mov ecx,edi                             |
-0067A199 | E8 9253CC00              | call robloxplayerbeta.133F530           |
-0067A19E | 8B4D FC                  | mov ecx,dword ptr ss:[ebp-4]            |
-0067A1A1 | 8079 24 00               | cmp byte ptr ds:[ecx+24],0              |
-0067A1A5 | 74 35                    | je robloxplayerbeta.67A1DC              |
-0067A1A7 | 53                       | push ebx                                |
-0067A1A8 | 33F6                     | xor esi,esi                             |
-0067A1AA | BB 01000000              | mov ebx,1                               |
-0067A1AF | 90                       | nop                                     |
-0067A1B0 | 8459 24                  | test byte ptr ds:[ecx+24],bl            |
-0067A1B3 | 74 1E                    | je robloxplayerbeta.67A1D3              |
-0067A1B5 | 56                       | push esi                                |
-0067A1B6 | 57                       | push edi                                |
-0067A1B7 | E8 F452CC00              | call robloxplayerbeta.133F4B0           |
-0067A1BC | 83C4 08                  | add esp,8                               |
-0067A1BF | 84C0                     | test al,al                              |
-0067A1C1 | 75 0D                    | jne robloxplayerbeta.67A1D0             |
-0067A1C3 | 68 BC95F401              | push robloxplayerbeta.1F495BC           | 1F495BC:"Class security check"
-0067A1C8 | 56                       | push esi                                |
-0067A1C9 | 8BCF                     | mov ecx,edi                             |
-0067A1CB | E8 6053CC00              | call robloxplayerbeta.133F530           |
-0067A1D0 | 8B4D FC                  | mov ecx,dword ptr ss:[ebp-4]            |
-0067A1D3 | 46                       | inc esi                                 |
-0067A1D4 | D1C3                     | rol ebx,1                               |
-0067A1D6 | 83FE 08                  | cmp esi,8                               |
-0067A1D9 | 7C D5                    | jl robloxplayerbeta.67A1B0              |
-0067A1DB | 5B                       | pop ebx                                 |
-0067A1DC | 5F                       | pop edi                                 |
-0067A1DD | 5E                       | pop esi                                 |
-0067A1DE | 8BE5                     | mov esp,ebp                             |
+0067A160 | E9 8B000000              | jmp robloxplayerbeta.67A1F0             | 67A1F0 {C} corresponds to the entry point of the second paired function
+0067A165 | 90                       | nop                                     |
+0067A166 | 90                       | nop                                     |
+0067A167 | 90                       | nop                                     |
+0067A168 | 90                       | nop                                     |
+0067A169 | 90                       | nop                                     |
+0067A16A | 90                       | nop                                     |
+0067A16B | 90                       | nop                                     |
+0067A16C | 90                       | nop                                     |
+0067A16D | 90                       | nop                                     |
+0067A16E | 90                       | nop                                     |
+0067A16F | 90                       | nop                                     |
+0067A170 | 90                       | nop                                     |
+0067A171 | 90                       | nop                                     |
+0067A172 | 90                       | nop                                     |
+0067A173 | 90                       | nop                                     |
+0067A174 | 90                       | nop                                     |
+0067A175 | 90                       | nop                                     |
+0067A176 | 90                       | nop                                     |
+0067A177 | 90                       | nop                                     |
+0067A178 | 90                       | nop                                     |
+0067A179 | 90                       | nop                                     |
+0067A17A | 90                       | nop                                     |
+0067A17B | 90                       | nop                                     |
+0067A17C | 90                       | nop                                     |
+0067A17D | 90                       | nop                                     |
+0067A17E | 90                       | nop                                     |
+0067A17F | 90                       | nop                                     |
+0067A180 | 90                       | nop                                     |
+0067A181 | 90                       | nop                                     |
+0067A182 | 90                       | nop                                     |
+0067A183 | 90                       | nop                                     |
+0067A184 | 90                       | nop                                     |
+0067A185 | 90                       | nop                                     |
+0067A186 | 90                       | nop                                     |
+0067A187 | 90                       | nop                                     |
+0067A188 | 90                       | nop                                     |
+0067A189 | 90                       | nop                                     |
+0067A18A | 90                       | nop                                     |
+0067A18B | 90                       | nop                                     |
+0067A18C | 90                       | nop                                     |
+0067A18D | 90                       | nop                                     |
+0067A18E | 90                       | nop                                     |
+0067A18F | 90                       | nop                                     |
+0067A190 | 90                       | nop                                     |
+0067A191 | 90                       | nop                                     |
+0067A192 | 90                       | nop                                     |
+0067A193 | 90                       | nop                                     |
+0067A194 | 90                       | nop                                     |
+0067A195 | 90                       | nop                                     |
+0067A196 | 90                       | nop                                     |
+0067A197 | 90                       | nop                                     |
+0067A198 | 90                       | nop                                     |
+0067A199 | 90                       | nop                                     |
+0067A19A | 90                       | nop                                     |
+0067A19B | 90                       | nop                                     |
+0067A19C | 90                       | nop                                     |
+0067A19D | 90                       | nop                                     |
+0067A19E | 90                       | nop                                     |
+0067A19F | 90                       | nop                                     |
+0067A1A0 | 90                       | nop                                     |
+0067A1A1 | 90                       | nop                                     |
+0067A1A2 | 90                       | nop                                     |
+0067A1A3 | 90                       | nop                                     |
+0067A1A4 | 90                       | nop                                     |
+0067A1A5 | 90                       | nop                                     |
+0067A1A6 | 90                       | nop                                     |
+0067A1A7 | 90                       | nop                                     |
+0067A1A8 | 90                       | nop                                     |
+0067A1A9 | 90                       | nop                                     |
+0067A1AA | 90                       | nop                                     |
+0067A1AB | 90                       | nop                                     |
+0067A1AC | 90                       | nop                                     |
+0067A1AD | 90                       | nop                                     |
+0067A1AE | 90                       | nop                                     |
+0067A1AF | 90                       | nop                                     |
+0067A1B0 | 90                       | nop                                     |
+0067A1B1 | 90                       | nop                                     |
+0067A1B2 | 90                       | nop                                     |
+0067A1B3 | 90                       | nop                                     |
+0067A1B4 | 90                       | nop                                     |
+0067A1B5 | 90                       | nop                                     |
+0067A1B6 | 90                       | nop                                     |
+0067A1B7 | 90                       | nop                                     |
+0067A1B8 | 90                       | nop                                     |
+0067A1B9 | 90                       | nop                                     |
+0067A1BA | 90                       | nop                                     |
+0067A1BB | 90                       | nop                                     |
+0067A1BC | 90                       | nop                                     |
+0067A1BD | 90                       | nop                                     |
+0067A1BE | 90                       | nop                                     |
+0067A1BF | 90                       | nop                                     |
+0067A1C0 | 90                       | nop                                     |
+0067A1C1 | 90                       | nop                                     |
+0067A1C2 | 90                       | nop                                     |
+0067A1C3 | 90                       | nop                                     |
+0067A1C4 | 90                       | nop                                     |
+0067A1C5 | 90                       | nop                                     |
+0067A1C6 | 90                       | nop                                     |
+0067A1C7 | 90                       | nop                                     |
+0067A1C8 | 90                       | nop                                     |
+0067A1C9 | 90                       | nop                                     |
+0067A1CA | 90                       | nop                                     |
+0067A1CB | 90                       | nop                                     |
+0067A1CC | 90                       | nop                                     |
+0067A1CD | 90                       | nop                                     |
+0067A1CE | 90                       | nop                                     |
+0067A1CF | 90                       | nop                                     |
+0067A1D0 | 90                       | nop                                     |
+0067A1D1 | 90                       | nop                                     |
+0067A1D2 | 90                       | nop                                     |
+0067A1D3 | 90                       | nop                                     |
+0067A1D4 | 90                       | nop                                     |
+0067A1D5 | 803D C89B5302 01         | cmp byte ptr ds:[2539BC8],1             | {E} òófset 15 (0xF) bytes from the end of the `nop`'ed function call
+0067A1DC | 89E5                     | mov ebp,esp                             |
+0067A1DE | 75 13                    | jne robloxplayerbeta.67A1F3             | 67A1F3 {D} corresponds to right after the first
 0067A1E0 | 5D                       | pop ebp                                 |
 0067A1E1 | C2 0400                  | ret 4                                   |
 0067A1E4 | FB                       | sti                                     |
 0067A1E5 | 8D01                     | lea eax,dword ptr ds:[ecx]              | Final

 0067A1E4 | FB                       | sti                                     | [rubbish]
 0067A1E5 | 8D01                     | lea eax, dword ptr ds:[ecx]             | [rubbish]
 0067A1E7 | 55                       | push ebp                                | [rubbish]
 0067A1E8 | DE89 A76A16C5            | fimul word ptr ds:[ecx-0x3AE99559]      | [rubbish]
 0067A1EE | A8 A2                    | test al, 0xA2                           | [rubbish]

 0067A1F0 | 55                       | push ebp                                | {C}
-0067A1F1 | 8BEC                     | mov ebp, esp                            |
+0067A1F1 | EB E2                    | jmp robloxplayerbeta.67A1D5             | 67A1D5 {E} corresponds to the start of our new code block
 0067A1F3 | 51                       | push ecx                                | {D}
 0067A1F4 | 8B41 0C                  | mov eax, dword ptr ds:[ecx+0xC]         |
 0067A1F7 | 56                       | push esi                                |
 0067A1F8 | 57                       | push edi                                |
 0067A1F9 | 8B7D 08                  | mov edi, dword ptr ss:[ebp+0x8]         |
 0067A1FC | 8BB0 D0010000            | mov esi, dword ptr ds:[eax+0x1D0]       |
 0067A202 | 894D FC                  | mov dword ptr ss:[ebp-0x4], ecx         |
```
