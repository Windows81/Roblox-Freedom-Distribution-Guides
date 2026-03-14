# Terrain Research

For our intents and purposes, there are three types of terrain active throughout Rōblox's history:

1. **Voxel:** 2011 thru 2016-12-31
2. **Smooth: (pre-shorelines):** 2015-05 thru 2023
3. **Shorelines-upgraded:** 2022 thru present

## Voxel Terrain

Likely corresponds with the `GridV3` property of `Terrain`.

Deserialised from the internal C++ type `Voxel::Grid`.

Not currently relevant for the Freedom Distribution project as no support is enabled on any of its Rōblox clients.

## Smooth Terrain

Likely corresponds with the `SmoothGrid` property of `Terrain`.

Deserialised from the internal C++ type `Voxel2::Grid`.

To convert from `Voxel2::Grid` to the `BinaryString` we see in the `rbxl` format, [`void Grid::deserialize(const std::string& data)`](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/App/voxel2/Grid.cpp#L756) is used.

```cpp
void Grid::deserialize(const std::string& data)
{
    if (data.empty())
        return;

    unsigned int readOffset = 0;

	int version = static_cast<char>(readUInt8(data, readOffset));

    if (version != 1)
		throw RBX::runtime_error("Error while decoding data: unsupported version");

	int chunkSizeLog2 = readUInt8(data, readOffset);
	int chunkSize = 1 << chunkSizeLog2;

	if (chunkSizeLog2 > 8)
		throw RBX::runtime_error("Error while decoding data: malformed chunk size");

    Vector3int32 lastIndex;
	std::vector<Cell> cells;

	Box box(chunkSize, chunkSize, chunkSize);

    while (readOffset < data.size())
	{
        // decode chunk id
        for (int i = 3; i >= 0; --i)
        {
            lastIndex.x += static_cast<int>(readUInt8(data, readOffset) << (i * 8));
            lastIndex.y += static_cast<int>(readUInt8(data, readOffset) << (i * 8));
            lastIndex.z += static_cast<int>(readUInt8(data, readOffset) << (i * 8));
        }

        // decode chunk data
		decodeChunk(data, readOffset, box, cells);

		write(Region(lastIndex << chunkSizeLog2, chunkSize), box);
	}
}
```
