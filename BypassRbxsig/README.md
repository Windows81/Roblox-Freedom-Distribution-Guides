This should be a simple patch.

0. Launch x32dbg.

1. Search for references to strings which _begin_ with `"--rbxsig"` to as a user-module string. In v347, there are _four_ results; select the first one:

| Address    | Disassembly                          | String Address | String         |
| ---------- | ------------------------------------ | -------------- | -------------- |
| `00586DFE` | `push __robloxplayerbeta.1140908`    | `01140908`     | `"--rbxsig%"`  |
| `00586E1E` | `push __robloxplayerbeta.1140914`    | `01140914`     | `"--rbxsig2%"` |
| `00586EDA` | `mov ecx,__robloxplayerbeta.1140914` | `01140914`     | `"--rbxsig2%"` |
| `00586EDF` | `mov eax,__robloxplayerbeta.1140908` | `01140908`     | `"--rbxsig%"`  |

2. From that result, select the previous 25 lines, then right-click, navigate to _Find references to_, then go to _Selected address(es)_. Two results emerge in v347.

| Address    | Disassembly                      |
| ---------- | -------------------------------- |
| `004ED3DC` | `call __robloxplayerbeta.586DD0` |
| `00586DF8` | `jb __robloxplayerbeta.586DFC`   |

3. Navigate to the `call` result and copy the _destination_ address (i.e., `586DD0`).

4. If your destination appears in the _middle_ of an instruction, just hit _Ctrl + 9_ to replace all its bytes with `nop`.

5. Replace the instruction at the address from step (3) with `ret`.

## Investigation

According to [the 2016 source code](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/App/util/ContentProvider.cpp#L293),

```cpp
void ContentProvider::verifyScriptSignature(const ProtectedString& source, bool required)
{
    const char* script = source.getSource().c_str();

    try
    {
        // sig can be behind a Lua comment
        // looks like "--rbxsig%MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCtfLLFT36v5r9bNP7STBteDU5a%"
        const char* sigHeader = "--rbxsig%";
        if (strncmp(script, sigHeader, strlen(sigHeader)) == 0)
        {
            const char* sigStart = script + strlen(sigHeader);
            const char* sigEnd = strchr(sigStart, '%');
            if (!sigEnd)
            {
                throw std::runtime_error("");
            }
            std::string signature(sigStart, sigEnd - sigStart);
            const char* signedScript = sigEnd + 1; // skip terminal %. we signed the text after this signature.

            // verify now!, will throw runtime_error
            Crypt().verifySignatureBase64(signedScript, signature);

            return;
        }

        if (required)
        {
            throw std::runtime_error("");
        }
    }
    catch (RBX::base_exception&)
    {
        //Intentionally strip out the exceptions
        throw std::runtime_error("");
    }
}
```

This guide is designed to have this function return void before anything else can execute.

Since the return type is void, we do not need to include any instructions prior to the `ret`.
