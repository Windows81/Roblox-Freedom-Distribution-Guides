All `rbxasset://textures/` material things get redirected to `rbxassetid://rbxmtl-` when you apply these patches.

**If you're using a client version of Rōblox that obfuscates strings in the** `**exe**` **until they're loaded (such as v463), refer [here](../AddStrings2021E/README.md).**

---

Modify the following user-referenced strings (no substrings):

- `"rbxasset://textures/plastic/studs.dds"`
- `"rbxasset://textures/plastic/diffuse.dds"`
- `"rbxasset://textures/plastic/normal.dds"`
- `"rbxasset://textures/plastic/normaldetail"`
- `"rbxasset://textures/"` (yes, this full string counts too)

All _single_ slashes, _including_ at the end of those strings, are to be replaced with `-`. For example, `"rbxasset://textures/plastic/studs.dds"` becomes `"rbxassetid://rbxmtl-plastic-studs.dds"`.

There is still more to do.

To allow us to re-locate material paths such as `rbxasset://textures/woodplanks/diffuse.dds`, we'll also need to replace some instances of `/` with `-`.

1. Find a string in program memory which ends with `"-"`. One good place to look is in the string which we modified previously: `rbxassetid://rbxmtl-`. Take the memory address of the _final_ character of that string (the dash). In client v348, this address is `01539923`.

2. Search user-string results for `"diffuse"`. There will be multiple results.
   - For each result, keep navigating up until you find a `push` instruction with a constant value as the argument. If the opcode is not equal to `68`, you can safely ignore.
   - Replace the address in that instruction with the one you collected from step (1). In v348, you replace `push 01129658` with `push 01539923`.

For example, in client v348:

```
01059809 | 6A 01                    | push    0x1                                                      |
0105980B | 68 58963801              | push    robloxplayerbeta.1129658                                 | {MEMORY ADDRESS OF LONE SLASH: 1129658}
01059810 | 8D8D 2CFFFFFF            | lea     ecx, dword ptr ss:[ebp - 0xD4]                           |
01059816 | E8 B56368FF              | call    robloxplayerbeta.6DFBD0                                  |
0105981B | C785 98FEFFFF 0F000000   | mov     dword ptr ss:[ebp - 0x168], 0xF                          |
01059825 | C785 94FEFFFF 00000000   | mov     dword ptr ss:[ebp - 0x16C], 0x0                          |
0105982F | C685 84FEFFFF 00         | mov     byte ptr ss:[ebp - 0x17C], 0x0                           |
01059836 | C785 B0FEFFFF 0F000000   | mov     dword ptr ss:[ebp - 0x150], 0xF                          |
01059840 | C785 ACFEFFFF 00000000   | mov     dword ptr ss:[ebp - 0x154], 0x0                          |
0105984A | C685 9CFEFFFF 00         | mov     byte ptr ss:[ebp - 0x164], 0x0                           |
01059851 | C785 C8FEFFFF 0F000000   | mov     dword ptr ss:[ebp - 0x138], 0xF                          |
0105985B | C785 C4FEFFFF 00000000   | mov     dword ptr ss:[ebp - 0x13C], 0x0                          |
01059865 | C685 B4FEFFFF 00         | mov     byte ptr ss:[ebp - 0x14C], 0x0                           |
0105986C | 8B75 0C                  | mov     esi, dword ptr ss:[ebp + 0xC]                            |
0105986F | 837E 68 00               | cmp     dword ptr ds:[esi + 0x68], 0x0                           |
01059873 | 8D46 58                  | lea     eax, dword ptr ds:[esi + 0x58]                           |
01059876 | C645 FC 03               | mov     byte ptr ss:[ebp - 0x4], 0x3                             |
0105987A | 75 23                    | jne     robloxplayerbeta.105989F                                 |
0105987C | 68 28997901              | push    robloxplayerbeta.1799928                                 | 1799928:"diffuse"
```

And client v463:

```
019DC619 | 8D4D C8                  | lea     ecx, dword ptr ss:[ebp - 0x38]  | ecx:AmdPowerXpressRequestHighPerformance+84C84F
019DC61C | 52                       | push    edx                             | edx:AmdPowerXpressRequestHighPerformance+84C84F
019DC61D | 50                       | push    eax                             |
019DC61E | E8 2D57C0FE              | call    robloxplayerbeta.5E1D50         |
019DC623 | 6A 01                    | push    0x1                             |
019DC625 | 68 1435C701              | push    robloxplayerbeta.1C73514        | {MEMORY ADDRESS OF LONE SLASH: 1C73514}
019DC62A | 8D4D C8                  | lea     ecx, dword ptr ss:[ebp - 0x38]  | ecx:AmdPowerXpressRequestHighPerformance+84C84F
019DC62D | E8 1E57C0FE              | call    robloxplayerbeta.5E1D50         |
019DC632 | 8B45 0C                  | mov     eax, dword ptr ss:[ebp + 0xC]   |
019DC635 | 83C0 48                  | add     eax, 0x48                       |
019DC638 | 8378 10 00               | cmp     dword ptr ds:[eax + 0x10], 0x0  |
019DC63C | 75 20                    | jne     robloxplayerbeta.19DC65E        |
019DC63E | 68 E46B2B02              | push    robloxplayerbeta.22B6BE4        | 22B6BE4:"diffuse"
```

Notice how the relevant `push` command appears some instructions prior to where `diffuse` is put in. Because this slash is only one character, it will not appear annotated as a string on x64dbg. Replace the slash with a dash.

This snippet appends `rbxasset://textures/woodplanks` (from earlier in the routine), `**/**` (per `0105980B`), and `diffuse` (per `0105987C`).

---

[`MaterialPacks.json`](./MaterialPacks.json) contains data manually extracted from the default values of `FStringPartTexturePacksJson2022` and `FStringPartTexturePacksJsonPre2022`. It includes Rōblox numeric asset idens that provide additional material info when loaded.

[`MaterialPacks2.json`](./MaterialPacks2.json) is a generated file created by [`_.py`](./_.py) using [`MaterialPacks.json`](./MaterialPacks.json). It includes additional asset idens for each subtexture, such as diffuse and normal maps.
