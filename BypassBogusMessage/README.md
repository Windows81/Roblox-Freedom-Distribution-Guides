# Bypass Bogus Message

I have two potential solutions; I recommend using option (1).

In Rōblox Freedom Distribution, option (1) was applied to Rōblox v463 and option (1) was applied to v347.

## Option (1)

1. Open the `RobloxPlayerBeta.exe` in x32dbg.

2. Search for references to `"Loading shader files"` as a _user-module_ string. One result should appear.

3. Click on this result. There should be a `call` just before the most recent `je` above `"Important !Loading shader files"`.

4. Navigate to the function destination.

5. Replace the first few bytes with `30 C0 C3`.

# Option (2)

1. Open the `RobloxPlayerBeta.exe` in x32dbg.

2. Search for references to `"Loading shader files"` as a _user-module_ string. One result should appear.

3. Click on this result. There should be a `je` above `"Important !Loading shader files"`.

4. Change the `je` to a `jmp`.

## Why?

This patch can be achieved in two ways:

- By ensuring `VerifyCryptSignature` (or its equivalent) returns a value that causes the if-statement to skip the error case, or
- By forcibly skipping the if-statement, replacing the `je`/`jne` with an unconditional `jmp`.

Either way, this patch addresses this code behaviour as outlined [in the 2016 source](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/WindowsClient/Application.cpp#L1104C1-L1115C2).

```cpp
// Inform client to tell server to disconnect game if we are not a signed
void Application::setWindowFrame()
{
#if !defined(LOVE_ALL_ACCESS) && !defined(_DEBUG) && !defined(_NOOPT) && !defined(RBX_STUDIO_BUILD)
	if(!::VerifyCryptSignature(utf8_decode(moduleFilename)))
	{
		// bugus message for security reasons
		RBX::StandardOut::singleton()->print(RBX::MESSAGE_ERROR, "Important !Loading shader files");
		RBX::DataModel::sendStats |= HATE_SIGNATURE;
	}
#endif
}
```
