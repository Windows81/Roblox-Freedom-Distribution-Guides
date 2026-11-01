For whatever reason setting `FFlag::DebugLocalRccServerConnection` to `true` in the mid-2018 version used by Rōblox Freedom Distribution causes clients to fail to connect.

## Background

I created this patch whilst adding support for Android versions of Rōblox Freedom Distribution.

I  use Keypatch (a plugin for IDA) to adapt the following patches for the Android build of a nearby Rōblox version:
- [`AdvancedTrustCheck2018M`](../AdvancedTrustCheck2018M/)
- [`BypassRbxsig`](../BypassRbxsig/)
- [`ChangeMethodSecurityPermissions`](../ChangeMethodSecurityPermissions/)
- [`FixQuietGetProtocol`](../FixQuietGetProtocol/)
- [`ReclassifyRakNet`](../ReclassifyRakNet/)

Using x32dbg, I opened `RCCService.exe` and added breakpoints to _every_ instruction that accesses the memory location of `FFlag::DebugLocalRccServerConnection`.  There were about 10 or so.

After that, I launched RFD's webserver. And then I connected the now-patched Android client to my RCC instance.

Each time a breakpoint hit, I would _sometimes_ invert the result so that the code that follows branches differently. And then I loom for the _one_ branch inversion that allows my Android client to connect.

After a few trials, I have found the check that, if changed, allows my Android client to connect:

```patch
 00C7C8F0 | 55                       | push ebp
 00C7C8F1 | 8BEC                     | mov ebp,esp
 00C7C8F3 | 64:A1 00000000           | mov eax,dword ptr fs:[0]
 00C7C8F9 | 6A FF                    | push FFFFFFFF
 00C7C8FB | 68 C6C20601              | push rccservice.106C2C6
 00C7C900 | 50                       | push eax
 00C7C901 | 64:8925 00000000         | mov dword ptr fs:[0],esp
 00C7C908 | 83EC 14                  | sub esp,14
 00C7C90B | 803D 235E4701 00         | cmp byte ptr ds:[<FFlag::DebugLocalRccServerConnection>],0
-00C7C912 | 74 12                    | je rccservice.C7C926
+00C7C912 | 90                       | nop
+00C7C913 | 90                       | nop
 00C7C914 | B0 01                    | mov al,1
 00C7C916 | 8B4D F4                  | mov ecx,dword ptr ss:[ebp-C]
 00C7C919 | 64:890D 00000000         | mov dword ptr fs:[0],ecx
 00C7C920 | 8BE5                     | mov esp,ebp
 00C7C922 | 5D                       | pop ebp
 00C7C923 | C2 0400                  | ret 4
```