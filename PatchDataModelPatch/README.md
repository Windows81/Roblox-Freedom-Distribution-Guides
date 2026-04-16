# How I patched DataModelPatch for 2021E (v463)

I took the Rōblox client binary from [here](https://setup.rbxcdn.com/version-5a54208fe8e24e87-RobloxApp.zip).

I then did took the patches from [this guide](../Worships2021EGuide/README.md) and made a few more which weren't relevant to `DataModelPatch`.

Dum Rōblox decided that they won't load `./Content/models/DataModelPatch/DataModelPatch.rbxm` if it's been modified. Not to worry; I patched the signing requirement out.

Refer to [`DataModelPatchPatch.1337`](./DataModelPatchPatch.1337). Import it into **x32**dbg or something!

[](image-2.png)

With those patches, I took out the SIGN chunk at the end -- and everything loaded fine. It took me 2 or 3 days to do.

No Python was needed. Just many tries, traces, and branch-changes in x32dbg.

And I'm not done yet...

## DataModelPatch Bytecode Analysis

This is a super rough draft. Things do not make full sense now and _will_ be refined as we develop further.

### Preparation

1. Download [`DataModelPatch.rbxm`](DataModelPatch.rbxm). For Rōblox v463, `DataModelPatch.rbxm` can be pulled from:

```sh
curl -L "https://assetdelivery.roblox.com/v1/asset/?id=5345954812&version=897"
```

2. Decompress the `lz4` chunks. I'd save them to a new file. The following Python code snippet requires a module Rōblox Freedom Distribution to be imported:

```py
from assets.serialisers import rbxl as parser
read_file_name = "./DataModelPatch.rbxm"
write_file_name = "./DataModelPatchDecompressed.rbxm"

read_data = open(read_file_name, 'rb').read()
write_data = parser.parse(read_data, methods={})
open(write_file_name, 'wb').write(write_data)
```

### Basic Metadata Collection (Script Names)

Open the newly decompressed file in a hex-editing tool. Write down the address of the byte highlighted below. The `0x01` right after `Name` corresponds to the `String` [property type](https://github.com/RobloxAPI/spec/blob/master/formats/rbxl.md#value-types). So we want to collect the byte right after this metadatum.

![](image.png)

In this case, we're using `0x00094888` as the base address. The reason that these bytes follow as `0A 00 00 00` is because the `Connection` string afterwards is ten characters long.

And then:

```py
b = 0x00094888

b0 = b
head = b''
names = []
while True:
  head = write_data[b0:b0+4]
  if head == b'PROP':
   break
  l = int.from_bytes(head, 'little')
  e1 = b0 + 4
  e2 = b0 + 4 + l
  val = write_data[e1:e2]
  names.append((e1, e2, val))
  b0 += l + 4
```

That's just to get the names, which will be saved in the `names` list.

Now to get the values of the "Source" property.

### Bytecode Collection

Repeat for "Source". The 0x1D is _supposed_ to refer to the value type for [bytecode](https://github.com/strawbberrys/0x1D/tree/master/bytecode-poc).

![](image-1.png)

```py
b = 0x000B5407

b0 = b
head = b''
sources = []
while True:
  head = write_data[b0:b0+4]
  if head == b'PROP':
   break
  l = int.from_bytes(head, 'little')
  e1 = b0 + 4
  e2 = b0 + 4 + l
  val = write_data[e1:e2]
  sources.append((e1, e2, val))
  b0 += l + 4
```

The bytecode dumps are saved in a list named `sources`.

### [`DataModelPatchBytecodes.zip`](DataModelPatchBytecodes.zip)

In the previous two sections, we collected `names` and `sources`. Time to save them to a file.

```py
for n,s in zip(names, sources):
 fn=(
  rb'%08x-%s'
  %(s[0], n[2].split(b'/')[-1])
 ).decode('utf-8')
 with open(fn, 'wb') as f:
  f.write(d[s[0]:s[1]])
```

---

Just one thing:
**`005fceba-mapDispatchToProps`** (2021E)

```
Hex View  00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F

00000000  93 7A 27 C6 23 CD 09 9B  21 C4 82 C2 8D 53 C4 E2  .z'.#...!....S..
00000010  51 41 F4 87 F7 5C 99 2B  99 05 FD CF 3D A5 1E 73  QA...\.+....=..s
00000020  63 49 87 16 9D ED 28 BB  28 92 6E 5F CD 35 A8 1B  cI....(.(.n_.5..
00000030  71 DE 15 E5 04 AB B5 0A  91 13 C9 EC 67 16 2B E5  q...........g.+.
00000040  19 E9 B7                                         ...
```

[Rōblox Client Tracker](https://github.com/MaximumADHD/Roblox-Client-Tracker/blob/9f43a0b49e1069ad6bdd8927c4a3f46901cbb237/BuiltInPlugins/StyleEditor/Src/Util/mapDispatchToProps.luac.s) (2023L)

```
PROTO_0:
  DUPTABLE R1 K1 [{"dispatch"}]
  SETTABLEKS R0 R1 K0 ["dispatch"]
  RETURN R1 1

MAIN:
  PREPVARARGS 0
  DUPCLOSURE R0 K0 [PROTO_0]
  RETURN R0 1
```

Might be a match.

**bhk.sdfngjlsdngjldsng,englng;lksdklgmsd;lgk;lbdfb**

https://github.com/MaximumADHD/RCT-Source/blob/dc5b8cba752ebf0b7ce02fc59b645784415a2600/src/DataMiners/RobloxFileMiner.cs#L281

```cs
protected void unpackFile(string filePath, bool checkHash, bool delete = true)
```

...
https://github.com/MaximumADHD/RCT-Source/blob/dc5b8cba752ebf0b7ce02fc59b645784415a2600/src/DataMiners/RobloxFileMiner.cs#L62

```cs
public static bool PullInstanceData(Instance inst, ref string value, ref string extension)
```

---

In a script named `NotifyReady.lua` (there are like three copies in DataModelPatch),

There is content:

```lua
return {}
```

Bytecode:

```
A0 7B E7 85 B1 CC 49 58 12 C5 C2 01 FE 33 84 A1 82 78 34 44 27 5D D9 E8 CB 04 DE 8C 6E A4 DE 30 90 48 C7 D5 AE EC 69 78 5A 90 0E 1C D7 B6 E4 02 92 D8 70
```

In the CoreScripts, `CompleteRequest.lua` has the exact same content as `PurchaseCompleteRecieved.lua` and `RequestPremiumPurchase.lua` and `StartHidingPrompt.lua`.

Bytecode is:

```
71 DF 06 74 6E 30 E8 E9 43 61 A3 70 2F D1 DD 32 B3 2E 9C CF 48 50 41 71 4B BE 0B 51 D2 6B FF 7C 6A DF 61 4B C2 28 7F 82 57 75 80 54 69 70 62 AC 3C 81 1B F4 88 FF 96 21 44 2D 0E 6E DE 1A 47 13 84 D4 AB 0C FB 6D 38 56 57 1F 4D 1A B3 F2 E0 A9 C3 DD 2B 66 F5 FE 57 50 BC 88 AB B7 CB 2A 05 B4 D1 8F 1E 21 6F EA D2 7A 1B 30 6F 7B 79 31 A2 D2 C1 68 FB 0F 3B 64 2F B0 77 B0 E9 08 FE 6E 20 0B E0 EC 0E CE 4A 4D EC 51 D0 57 8A CE DF 9F
```

```lua
local makeActionCreator = require(script.Parent.makeActionCreator)

return makeActionCreator(script.Name)
```

Let's compare `ProductInfoReceived.lua`:

```lua
local makeActionCreator = require(script.Parent.makeActionCreator)

return makeActionCreator(script.Name, "productInfo")
```

```
4E D9 17 D6 7C 2E F9 8B 4C 67 B2 D2 28 CA 3C D7 AC 88 AC 68 74 3E 48 52 F4 AD 19 94 A5 C9 08 FF 70 45 11 B4 F0 5D 54 59 66 28 BD 4E 8B 7E 7C 46 DE BA 53 DA A2 90 97 C2 0A 7D AA 05 28 F9 A5 D2 FA 60 F9 0E B3 64 07 C8 72 B6 83 7B B6 DB 61 C0 5D 8C F1 18 AC A8 FF 64 77 4A 07 67 1B E9 4B 92 83 93 40 4C 34 7C 00 29 8C 86 75 41 6C 57 8A 3E 12 9E 5D BB D1 6A 86 6E 45 BE 2F 8C 80 74 36 D2 FE FE 03 52 1A 3A E7 7E E4 88 C6 C8 12 4A 9C 09 2A 9F 65 DC 89 FE DC AC 6E 18 B9 7D 70 01 F0 41
```

With `PremiumInfoRecieved.lua`:

```lua
local makeActionCreator = require(script.Parent.makeActionCreator)

return makeActionCreator(script.Name, "premiumInfo")
```

```
0D BE 18 97 BF 91 FE 4A 8F 80 8D 13 6B 65 2B 96 EF EF 23 28 B0 51 4F 57 37 39 0D B2 D0 E9 F4 5B 19 DE 32 E2 65 3B 2B F8 17 9F 36 23 6C F9 76 35 78 EB 39 44 91 1F 54 E4 A8 4E E8 3E 34 DF 2F F7 24 66 B7 15 45 8F 19 25 AD 5A F9 51 9D E9 5C 82 45 54 7D 6A 99 FA B1 07 21 30 FE 5F C4 34 8E 1D C2 B7 BB 0E 99 BA BD 49 56 55 EA 0F 8C 18 27 71 22 6C 2E 0A 3E 48 2A 29 48 51 82 D0 E9 29 56 BC 91 5B DC BD 53 82 F0 4E 1E 4C 80 E6 58 52 15 17 6F D6 33 76 C6 96 14 A0 A3 07 DA 79 FA 4B
```

The bytecode is encrypted/compressed, this is apparent due to no strings being visible in the bytecode.

---

According to Orblua,

> Roblox Studio and the Roblox client Luau bytecode have different opcodes

---

### Decompressing the Bytecode

It seems the bytecode *DataModelPatch* contains is serialized and compressed using an similar algorithm to one used by Rōblox as far back as 2016.

The difference being that 2021E uses ZSTD instead of LZ4 for compression, Luau rather than Lua and the bytecode proto's likely being encoded differently.

The serializer used in 2016E can be seen [here](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/App/script/LuaSerializer.inl#L44).

---

Using [decompress.py](decompress.py) on `PremiumInfoRecieved` we get the following: 
```
01 06 07 72 65 71 75 69 72 65 06 73 63 72 69 70 74 06 50 61 72 65 6E 74 11 6D 61 6B 65 41 63 74 69 6F 6E 43 72 65 61 74 6F 72 04 4E 61 6D 65 0B 70 72 65 6D 69 75 6D 49 6E 66 6F 01 04 00 00 01 12 A3 00 00 00 A4 00 01 00 00 00 00 40 A4 03 03 00 00 00 20 40 4D 02 03 24 04 00 00 00 4D 01 02 5B 05 00 00 00 9F 00 02 02 52 01 00 00 A4 03 03 00 00 00 20 40 4D 02 03 BA 06 00 00 00 6F 03 07 00 9F 01 03 00 82 01 00 00 08 03 01 04 00 00 00 40 03 02 04 00 00 20 40 03 03 03 04 03 05 03 06 00 00 01 18 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 01 00 00 00 00 00
```

Well there we go, we can see a Luau V1 bytecode header. `01` for the version and `06` being the numbers of strings.

If you view it as asicii, strings are clearly visible.

![](image-3.png)

---

It's possible and likely that the bytecode's opcodes are encoded/obfuscated considering that it's the case for bytecode observed from 2016E and current day Roblox. However I haven't completely looked into this yet.

### Serializing our own bytecode
Coming soon...