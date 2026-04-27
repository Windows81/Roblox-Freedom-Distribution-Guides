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

Only difference is there are also some unknown values after all the `faces` in `MeshData4`.

---

### CSG... v4? (a.k.a. `CSGMDL\x08`)

So you grab a fresh union out of 2024+ Studio, base64-decode it, XOR-strip with the same 31-byte cycle, and...

```
CSGMDL\x08\x00\x00\x00 ...
```

It seems that `\x06` or `\x07` does not appear to be in the wild; Rōblox skipped it.

The header XOR cycle is unchanged. However, the rest of the CSG body (i.e., anything after the header) is _not_ encrypted at all.

Speaking of which...

### CSGPHS

`CSGMDL` is the renderable mesh; **`CSGPHS`** is the physics/collision mesh that travels alongside it in the same `SSTR` chunk.

Unlike with `CSGMDL` chunks, any `CSGPHS` chunks absolutely do not involve XOR encryption.

Multiple `CSGPHS` versions have been in circulation over the years.

```rust
#[binrw::binrw]
#[brw(little)]
#[brw(magic=b"CSGPHS")]
#[derive(Debug,Clone)]
pub enum CSGPHS{
	// concat_bytes!(0u32,b"BLOCK")
	#[brw(magic=b"\0\0\0\0BLOCK")]
	Block,
	#[brw(magic=3u32)]
	V3(CSGPHS3),
	#[brw(magic=5u32)]
	V5(CSGPHS3),
	#[brw(magic=6u32)]
	V6(CSGPHS6),
	#[brw(magic=7u32)]
	V7(CSGPHS7),
}
```

Versions 3 and 5 are functionally identical. They appear to support multiple physics meshes in a single `CSGPHS` chunk.

```rust
#[binrw::binrw]
#[brw(little)]
#[derive(Debug,Clone)]
pub struct CSGPHS3{
	#[br(parse_with=binrw::helpers::until_eof)]
	pub meshes:Vec<Mesh>,
}
```

Version 6 adds a 40-byte `PhysicsInfo` chunk directly after the header, which consists of pre-calculated physical properties of the mesh.

```rust
#[binrw::binrw]
#[brw(little)]
#[derive(Debug,Clone)]
pub struct PhysicsInfo{
	pub volume:f32,
	pub center_of_gravity:[f32;3],
	// upper triangular matrix read left to right top to bottom
	pub moment_of_inertia_packed:[f32;6],
}

#[binrw::binrw]
#[brw(little)]
#[derive(Debug,Clone)]
pub struct CSGPHS6{
	pub physics_info:PhysicsInfo,
	pub mesh:Mesh,
}
```

Version 7 appears to be similar to version 6, also containing `PhysicsInfo`.

```rust
#[binrw::binrw]
#[brw(little)]
#[derive(Debug,Clone)]
pub struct CSGPHS7{
	#[brw(magic=3u8)]
	pub physics_info:PhysicsInfo,
	#[br(parse_with=binrw::helpers::until_eof)]
	pub meshes:Vec<Mesh>,
}
```

#### `CSGPHS\x08`

Circa January 2026, version 8 was introduced which behaves completely differently.

The good news is that `CSGPHS\x08` _has_ been reverse-engineered (huge thanks to `clv2`'s work, as implemented in [the Mesh Lab plugin](https://create.roblox.com/store/asset/90513270797757/Mesh-Lab)), and the layout is almost certainly what `CSGMDL\x08` is built on top of.

After XOR-stripping the header, `CSGPHS\x08` looks like this:

```
CSGPHS\x08\x00\x00\x00  (10 bytes magic, like CSGMDL)
\x00\x00                (2 bytes alignment / version-minor — keep but ignore)
<zstd payload>          (everything from offset 12 onward is zstd)
```

Decompress everything with `zstd` from byte 12 onwards, and you get a flat blob with a structure like:

```rust
#[binrw::binrw]
#[brw(little)]
#[derive(Debug,Clone)]
pub struct CSGPHS8Body{
	pub hull_count:        u32, // number of convex hulls
	pub total_verts:       u32, // sum of vertices across all hulls
	pub total_faces:       u32, // sum of triangles (NOT triangle*3)
	pub fhvc:              u32, // first-hull vertex count (cached)
	pub fhfc:              u32, // first-hull face count   (cached)
	pub raw_geometry_size: u32, // bytes of the RawHulls fallback block
	pub clers_bit_count:   u32, // valid bits in the Edgebreaker stream
	pub clers_buffer_size: u32, // bytes reserved for the bitstream
	pub vertices_size:     u32, // bytes of the vertex block (== total_verts*12)
	pub bbox:              [f32;6], // min.xyz, max.xyz
	#[br(count=raw_geometry_size)]
	pub raw_geometry:      Vec<u8>, // see RawHulls layout below
	#[br(count=clers_buffer_size)]
	pub clers_buffer:      Vec<u8>, // packed CLERS bitstream
	#[br(count=total_verts)]
	pub vertices:          Vec<[f32;3]>, // global, addressed by Edgebreaker
}
```

Two parallel encodings. Most hulls live in `clers_buffer` + `vertices` (compressed); pathological hulls that Edgebreaker can't encode get dumped verbatim into `raw_geometry`. To recover the full set, decode both and concatenate.

---

### Edgebreaker / CLERS; How Rōblox Compresses Hulls

Edgebreaker is a 1990s mesh-compression algorithm by Jarek Rossignac. Each triangle visit emits one of five symbols — **C**, **L**, **E**, **R**, **S** — describing how the next triangle relates to the current cursor edge. The decoder rebuilds adjacency on the fly using a "zip" routine that re-stitches boundary edges as new triangles arrive.

Rōblox stores the per-triangle CLERS labels as a packed bitstream. **C** is encoded as a single `0` bit. The other four symbols start with a `1` bit followed by two more bits:

| Symbol | Bits  | What it means                                                |
| ------ | ----- | ------------------------------------------------------------ |
| C      | `0`   | New triangle introduces a new vertex (`vertex_counter += 1`) |
| S      | `100` | Split: recurse, then resume                                  |
| L      | `101` | Left turn: advance cursor along left boundary                |
| R      | `110` | Right turn: advance, zip the right boundary                  |
| E      | `111` | End: close the strip, zip, return                            |

Bit packing is a little fiddly.

The buffer is treated as a `Vec<u32>` (little-endian when read as bytes), but bits _may_ be consumed _most-significant-bit-first within each word_.

The very last word may be partially populated; only `clers_bit_count % 32` bits may be valid in the tail word.

A reference port (Lua, originally from the Mesh Lab plugin) may handle this with:

```python
total_words = (total_bits + 31) // 32

def read_bit() -> int:
    word_idx    = bit_pos // 32
    bit_in_word = bit_pos % 32
    bits_in_word = 32
    if word_idx == total_words - 1:
        bits_in_word = total_bits % 32 or 32
    shift = bits_in_word - bit_in_word - 1
    word  = struct.unpack_from("<I", clers_bytes, word_idx * 4)[0]
    bit_pos += 1
    return (word >> shift) & 1
```

Each hull starts with three vertices (indices 0, 1, 2) and a single seeded triangle, then `decode_recursive` walks the bitstream until it sees an `E`. Vertex indices are local-to-hull — the decoder maintains a `global_vert_offset` that increments by however many vertices the hull consumed, so successive hulls slice into the global `vertices` array in order.

---

More research:
https://devforum.roblox.com/t/some-info-on-sharedstrings-for-custom-collision-data-meshparts-unions-etc/294588
