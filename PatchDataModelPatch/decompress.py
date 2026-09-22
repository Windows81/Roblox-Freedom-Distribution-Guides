import zstandard as zstd
import xxhash
import sys
import os

argv = sys.argv

kBytecodeMagic = b'RSB1'
kBytecodeHashMultiplier = 41
kBytecodeHashSeed = 42

# Borrowed from https://github.com/4bzr/agent-api-injector/blob/451ecfc0f20629bf86d24fbbf9dd1abec304ffd7/cert/utils/bytecode.py#L34
def Decompress(source):
    ss = bytearray(source)
    
    hb = ss[:4]
    
    for i in range(4):
        hb[i] ^= kBytecodeMagic[i]
        hb[i] = (hb[i] - i * kBytecodeHashMultiplier) % 256

    for i in range(len(ss)):
        ss[i] ^= (hb[i % 4] + i * kBytecodeHashMultiplier) % 256

    hash_bytes = hb[:4]
    hash_value = int.from_bytes(hash_bytes, 'little')
    rehash = xxhash.xxh32(ss, seed=kBytecodeHashSeed).intdigest()

    if rehash != hash_value:
        raise Exception("Failed to decompress bytecode. (1)")

    decompressed_size = int.from_bytes(ss[4:8], 'little')
    compressed_data = ss[8:]
    
    decompressed = zstd.decompress(compressed_data, max_output_size=decompressed_size)
    return decompressed

def Compress(data):
    compressed_data = zstd.compress(data)

    decompressed_size = len(data).to_bytes(4, 'little')
    ss = bytearray(kBytecodeMagic + decompressed_size + compressed_data)

    rehash = xxhash.xxh32(ss, seed=kBytecodeHashSeed).intdigest()
    hb = bytearray(rehash.to_bytes(4, 'little'))

    for i in range(len(ss)):
        ss[i] ^= (hb[i % 4] + i * kBytecodeHashMultiplier) % 256

    source = bytearray(ss)
    for i in range(4):
        val = (hb[i] + i * kBytecodeHashMultiplier) % 256
        source[i] = val ^ kBytecodeMagic[i]

    return bytes(source)

if len(argv) < 2:
    raise Exception("Usage: decompress.py <bytecodepath.luac>")

path = argv[1]

if not os.path.exists(path):
    raise Exception(f"File doesn't exist ({path})")

with open(path, "rb") as File:
    Bytecode = File.read()

Bytecode = Decompress(Bytecode)

with open(path, "wb") as BytecodeFile:
    BytecodeFile.write(Bytecode)

print(f"Wrote decompressed bytecode to '{path}'")