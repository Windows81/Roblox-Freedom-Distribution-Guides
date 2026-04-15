**An earlier version of this write-up is [available on the devforum](https://devforum.roblox.com/t/research-on-csg/3554504).**

# Research on CSG

As of 2025, if you create a `UnionOperation` using current-day Studio, it will _not_ parse in the 2021E or 2018M versions of Rōblox that Rōblox Freedom Distribution uses.

That's because Rōblox invented several new constructive-solid-geometry (CSG) systems since approx 2022M. It's all proprietary stuff.

**Not to fear!**

I found some ground-breaking research on how modern CSG works on Rōblox:

https://github.com/krakow10/rbx_mesh

Geometry made with Studio versions from before approx 2022M used what we call CSGv2, whereas current builds exclusively use CSGv3.

Rōblox generally stores CSG data via one of two ways:

<!-- Credit to @kenso_d on Twitch for being timely with his request to be in the comments of this write-up. -->

1. embedded within a `rbxl` place file, or
2. as a separate `rbxm` remote asset with a numerical asset ID.

Note that `rbxl` and `rbxm` are similar formats. In _both_ cases, CSG data stored in the `SSTR` chunk. In `rbxlx` and `rbxmx` streams, these would be found base64-encoded in XML tags named `BinaryString`.

I used [`BinaryStrings.sh`](./BinaryStrings.sh) to extract the base64-encoded binary strings and store each one in its own file. This will be useful in comparisons.

In the [`CSGv2.rbxmx`](./CSGv2.rbxmx) file, the mesh data is as follows:

```xml
<BinaryString name="MeshData"><![CDATA[FX0pFXVsMgQ0aWkWPjJuYy1W ... AWcAGmAuaR1S]]></BinaryString>
```

Long string.

Here's what happens when I decode the base64 from the XML file:

```uwu
15 7d 29 15 75 6c 32 04 ...
```

No discernible magic header. I was stuck until I found the [rbx_mesh](https://github.com/krakow10/rbx_mesh)!!!

**WHAT THE HACK! THEY'RE USING XOR ENCRYPTION; I SHOULD'VE SÈÉN THAT COMING!!! :shock:**

```rust
pub const OBFUSCATION_NOISE_CYCLE_XOR:[u8;31]=[86,46,110,88,49,32,48,4,52,105,12,119,12,1,94,0,26,96,55,105,29,82,43,7,79,36,89,101,83,4,122];
```

The XOR block has 31 entries and goes in a loop :loop:.

And then it begins with:

```uwu
CSGMDL\x02 ...
```

CSGv3 unions are similar, but have `\x04` instead of `\x02`.

---

### CSGv2

```rust
#[binrw::binrw]
#[brw(little)]
#[derive(Debug,Clone)]
pub struct MeshData2{
	#[brw(magic=b"CSGMDL\x02\0\0\0")]
	pub hash:Hash,
	pub mesh:Mesh2,
}
```

### CSGv3

```rust
#[binrw::binrw]
#[brw(little)]
#[derive(Debug,Clone)]
pub struct MeshData4{
	#[brw(magic=b"CSGMDL\x04\0\0\0")]
	pub hash:Hash,
	pub mesh:Mesh2,
	pub _unknown1_count:u32,
	#[br(count=_unknown1_count)]
	pub _unknown1_list:Vec<u32>,
}
```

What does `Mesh2` mean? Glad you asked:

```rust
#[binrw::binrw]
#[brw(little)]
#[derive(Debug,Clone)]
pub struct Mesh2{
	pub vertex_count:u32,
	// vertex data length
	#[brw(magic=84u32)]
	#[br(count=vertex_count)]
	pub vertices:Vec<Vertex>,
	pub face_count:u32,
	#[br(count=face_count/3)]
	pub faces:Vec<[VertexId;3]>,
}
```

Note how similar their structures look. Both `MeshData2` and `MeshData4` begin with a magic header, then the same `Hash`, then the same `Mesh2`.

Only difference being that aside from that is the presence of some unknown values after all the `faces` in `MeshData4`. Even Krakow10 doesn't know yet.

---

More research:
https://devforum.roblox.com/t/some-info-on-sharedstrings-for-custom-collision-data-meshparts-unions-etc/294588
