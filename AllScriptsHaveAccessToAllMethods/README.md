## Findings for v463

I wanted to use an FFlag initialised but not being used anywhere. For v463, I chose `FFlag::Q220PermissionsSettings` after my own personal research.

However, we'll be messing with some behaviour from `FFlag::ParallelLua` by overwriting some of its branch logic.

1. Use x32dbg on Rōblox v463.
1. Search for `Gur pheerag vqragvgl (%q) pnaabg %f (ynpxvat crezvffvba %q` (which is a ROT13 cypherstring for `The current identity (%d) cannot %s (lacking permission %d)`).
1. Add a breakpoint at the first line of the function (which is `push ebp`)
1. Execute a method which triggers an error `The current identity...` to print.

Perhaps

```lua
game.HttpService:RequestInternal({Url = "https://google.com"}):Start(function(success, dataTable) print(success) end)
```

1. Once the breakpoint is hit, go one level up the call stack.
1. FFlag values are often stored in static memory addresses **which change per build of Rōblox**. Locate the address for `Q220PermissionsSettings`. To do this, you'd want to search in use strings for `Q220PermissionsSettings`.

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

In this case, **`2539BC8`** is the address which I fill in for the next step.

1. When applying the provided patch for the v463 player, please ensure that you account for any differences in jmp instruction offsets between versions. Specifically, replace all instances of `2539BC8` with a new value tailored to your implementation.

However, keep in mind that `FFlag::ParallelLua` may have different behaviours in other versions, so this patch is version-specific and might not work elsewhere without adjustments.

A bit confusing, perhaps.

```patch
-00844937 | 803D 44B35302 00         | cmp byte ptr ds:[253B344],0             | 253B344 corresponds to FFlag::ParallelLua
+00844937 | 803D C89B5302 01         | cmp byte ptr ds:[2539BC8],1             | 2539BC8 corresponds to FFlag::Q220PermissionsSettings

 0084493E | 8B30                     | mov esi,dword ptr ds:[eax]              |

-00844940 | 74 0D                    | je robloxplayerbeta.84494F              |
+00844940 | 74 42                    | je robloxplayerbeta.844984              |

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

 0084494F | 8B46 20                  | mov eax,dword ptr ds:[esi+20]           |
 00844952 | 8945 0C                  | mov dword ptr ss:[ebp+C],eax            |
 00844955 | 85C0                     | test eax,eax                            | Security check
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
 00844984 | 8B7D 10                  | mov edi,dword ptr ss:[ebp+10]           |
 00844987 | 803D DC905302 00         | cmp byte ptr ds:[25390DC],0             |
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
 00844984 | 8B7D 10                  | mov edi,dword ptr ss:[ebp+10]           |
 00844987 | 803D DC905302 00         | cmp byte ptr ds:[25390DC],0             |
```

If you're using x32dbg, there should be 17 patches here total.

---

There are also patches we need to apply against `Class security check`.

1. Search for string references to `Class security check`. You'll find four grouped together in pairs pretty close to each other.

| Address    | Disassembly                     | String Address | String                   |
| ---------- | ------------------------------- | -------------- | ------------------------ |
| `0067A191` | `push robloxplayerbeta.1F495BC` | `01F495BC`     | `"Class security check"` |
| `0067A1C3` | `push robloxplayerbeta.1F495BC` | `01F495BC`     | `"Class security check"` |
| `0067A217` | `push robloxplayerbeta.1F495BC` | `01F495BC`     | `"Class security check"` |
| `0067A248` | `push robloxplayerbeta.1F495BC` | `01F495BC`     | `"Class security check"` |

Mentally group the four results into pairs.

- If you're patching RCC, proceed with the first pair (above result 1).
- If you're patching the client, proceed with the second pair (above result 3).

Then look for an instruction like:

```x86
mov eax,dword ptr ds:[ecx+C]
```

Look out for the `+C` (i.e., 12 in decimal). The registers' names don't matter so much.

Continue to go up until you find a `push` instruction followed by a `mov` instruction. This is where the function body begins.

You may encounter multiple `int3` instructions before the function — or you may come across some nonsensical instructions.

Apply the following patches carefully, accounting for differences in `jmp` destinations.

```patch
 0067A1E1 | C2 0400                  | ret 4                                   |
-0067A1E4 | FB                       | sti                                     |
-0067A1E5 | 8D01                     | lea eax,dword ptr ds:[ecx]              |
-0067A1E7 | 55                       | push ebp                                |
-0067A1E8 | DE89 A76A16C5            | fimul word ptr ds:[ecx-3AE99559]        |
-0067A1EE | A8 A2                    | test al,A2                              |

+0067A1E4 | 803D 9C7C4B02 01         | cmp byte ptr ds:[24B7C9C],1             |
+0067A1EB | 75 05                    | jne robloxplayerbeta.67A1F2             |
+0067A1ED | C2 0400                  | ret 4                                   |

-0067A1F0 | 55                       | push ebp                                |
-0067A1F1 | 8BEC                     | mov ebp,esp                             |
+0067A1F0 | EB F2                    | jmp robloxplayerbeta.67A1E4             |
+0067A1F2 | 55                       | push ebp                                |

 0067A1F3 | 51                       | push ecx                                |
 0067A1F4 | 8B41 0C                  | mov eax,dword ptr ds:[ecx+C]            |
```
