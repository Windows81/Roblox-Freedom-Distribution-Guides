It's been known for years (as of 2026) that Rōblox Studio can be patched to allow use of 'internal' features.

How does this relate to Rōblox Freedom Disribution? Implementing a patch like this can potentially help debug issues in RFD's Studio builds.

It also gives creators the following powers, among potentially others:

1. Modify fast variables (i.e. FFlags) without leaving Studio
2. Using the command bar in various script-security contexts

## Prior Research

In 2023, the way this was done was to find and replace a fixed signature in ``RobloxStudioBeta.exe`. This is how [7ap's `internal-studio-patcher`](https://github.com/7ap/internal-studio-patcher/blob/dc3dc1cabc75599239fc1eab84b180335068f1d8/src/main.rs) did it:

```patch
- 41 80 be 50 01 00 00 00 74 05 e8
+ 41 80 be 50 01 00 00 00 90 90 e8
```

In June 2025, `internal-studio-patcher` changed the process, so that it now:

1. searches in the `.data` and `.rdata` regions for a string `"VoiceChatEnableApiSecurityCheck"`, then

2. searches in the `.text` region for a non-`lea` instruction which references that string's memory address, then

3. searches in the `.text` region for a function call shortly _before_ where that string is referenced, then

4. searches throughout the entire `.text` region for every other `call` statement which calls the same function _and also_ immediately follows a `jnz` statement, then

5. patches the `jnz` by filling its bytes with `nop`.

## My Own Findings

**The following process, despite having been discovered in 2026, has only been tested on Studio v463 (from early 2021). Please refer to other literature if my research doesn't take you to where you need to go.**

This patch only applies to Rōblox Freedom Distribution's v463 `RobloxStudioBeta.exe`.

In browsing the v548 PDB files (which some Rōblox reverse-engineers refer to for research), I discovered a string that we can easily find and apply patches from: `"Internal Permission is required for this feature."`.

This code snippet, decompiled in IDA, references this string exposes two static addresses which we can easily force into truish values.

```cpp
void __fastcall RBX::throwIfNoInternalPermission(RBX *this)
{
  std::runtime_error pExceptionObject; // [rsp+20h] [rbp-28h] BYREF

  if ( !RBX::hasPermission || !RBX::studioSettingEnableInternalPermission )
  {
    std::runtime_error::runtime_error(&pExceptionObject, "Internal Permission is required for this feature.");
    throw &pExceptionObject;
  }
}
```

Look out for `RBX::hasPermission` and `RBX::studioSettingEnableInternalPermission`.

### Finding Corresponsing Static Addresses

In v463 Studio, this corresponds with:

```
0000000140D113C0 | 48:83EC 48               | sub rsp,48                                                  |
0000000140D113C4 | 803D FA025F02 00         | cmp byte ptr ds:[1433016C5],0                               | RBX::hasPermission
0000000140D113CB | 74 0E                    | je robloxstudiobeta.140D113DB                               |
0000000140D113CD | 803D 94A53F02 00         | cmp byte ptr ds:[14310B968],0                               | RBX::studioSettingEnableInternalPermission
0000000140D113D4 | 74 05                    | je robloxstudiobeta.140D113DB                               |
0000000140D113D6 | 48:83C4 48               | add rsp,48                                                  |
0000000140D113DA | C3                       | ret                                                         |
0000000140D113DB | 48:8D15 EE489901         | lea rdx,qword ptr ds:[1426A5CD0]                            | 00000001426A5CD0:"Internal Permission is required for this feature."
0000000140D113E2 | 48:8D4C24 20             | lea rcx,qword ptr ss:[rsp+20]                               |
...
```

... and so on.

Two important addresses are exposed: `1433016C5` and `14310B968`.

I then searched for user-module references to each of the addresses:

#### `RBX::hasPermission`

| Address            | Disassembly                         |
| ------------------ | ----------------------------------- |
| `0000000140D110E4` | `cmp byte ptr ds:[1433016C5],0`     |
| `0000000140D110EF` | `mov byte ptr ds:[1433016C5],1`     |
| `0000000140D11110` | `cmp byte ptr ds:[1433016C5],0`     |
| `0000000140D11130` | `movzx eax,byte ptr ds:[1433016C5]` |
| `0000000140D11144` | `cmp byte ptr ds:[1433016C5],0`     |
| `0000000140D1114F` | `mov byte ptr ds:[1433016C5],0`     |
| `0000000140D113C4` | `cmp byte ptr ds:[1433016C5],0`     |

#### `RBX::studioSettingEnableInternalPermission`

| Address            | Disassembly                      |
| ------------------ | -------------------------------- |
| `0000000140D11119` | `cmp byte ptr ds:[14310B968],0`  |
| `0000000140D11170` | `mov byte ptr ds:[14310B968],cl` |
| `0000000140D113CD` | `cmp byte ptr ds:[14310B968],0`  |

I added breakpoints to each of the instruction addresses (such as `0000000140D113CD`) to trace if any values change.

During Studio's startup sequence, I found zero _writes_ to `1433016C5` and one to `14310B968`.

### Implementing Patches

Since both addresses are in the `.data` region, why didn't I just derive file addresses and modify the raw values and then save?

Because x64dbg is unable to resolve a file address from `1433016C5`. But `14310B968` resolves just fine.

I found the value at `14310B968` already set to `01`.

```
000000014310B968  01 00 00 00 00 00 00 00 08 5D 6A 42 01 00 00 00  .........]jB....
```

Why don't I redirect all the difficult addresses to easier ones?

In fact, I only need to change the `cmp` instructions which reference `1433016C5`, as per the table above.

```patch
 0000000140D110E0 | 48:83EC 28               | sub rsp,28                                                  |
-0000000140D110E4 | 803D DA055F02 00         | cmp byte ptr ds:[1433016C5],0                               |
+0000000140D110E4 | 803D 7DA83F02 00         | cmp byte ptr ds:[14310B968],0                               |
 0000000140D110EB | 75 15                    | jne robloxstudiobeta.140D11102                              |
 0000000140D110ED | B2 01                    | mov dl,1                                                    |
```
