In keeping with the spirit of innovation, these guides should allow other Rōblox researchers to replicate my work. I've incorporated some of their material into various aspects of Rōblox Freedom Distribution.

Though, the guides _don't yet_ allow you to reproduce _all_ the patches I made to the Rōblox clients from scratch.

**Don't overwhelm yourself spending too much time dwelling on the material. Most of it is still poorly organised.**

**If you need any help, it'll save you time to contact VisualPlugin.**

## Where does Rōblox Freedom Distribution come from?

Rōblox Freedom Distribution (RFD) began its development in June 2023 using `exe` programs from _Rōblox Filtering Disabled_, a prior project which carries the same initials. Many guides in this repository contain files with a `.1337` extension, used for x32dbg. The addresses indicated in each patch file refer to RVAs (relative virtual addresses); these RVAs do not exactly indicate the _file_ offsets where patches are applied.

I have taken care to locate the original sources so as to create a complete lineage of Freedom Distribution's patches.

Consult [`./_misc/haxdiff/`](./_misc/haxdiff/) for more info; updated 2026-09-18 (RFD 0.68.0).

### Version 347 (2018M)

Server: _to be located_
Client: _to be located_
Studio: `d9cf1f7e4fe14aa9` ([Robloxopolis Archive](<https://archive.robloxopolis.com/archive/Clients/DeployHistory/setup.roblox.com/Windows/Studio/0.347.0.28462%20(version-d9cf1f7e4fe14aa9).zip>))

### Version 463 (2021E)

Server: `07b64feec0bd47c1` ([Rōblonium Archive](https://archive.roblonium.com/Client/Windows/RCCService/production/RCCServiceR7Z9CYTW7WBR95VW/version-07b64feec0bd47c1/version-07b64feec0bd47c1-RCCServiceR7Z9CYTW7WBR95VW.zip))
Client: `5a54208fe8e24e87` ([Internet Archive](https://web.archive.org/web/20240224094219if_/https://setup.rbxcdn.com/version-5a54208fe8e24e87-RobloxApp.zip))
Studio: `c993d5e9c7224b14` ([Internet Archive](https://web.archive.org/web/20240324082713if_/http://setup.rbxcdn.com/version-c993d5e9c7224b14-RobloxStudio.zip))

## Guide Index

Listed below are the directories in this repository, along with roughly how well they achieve their stated purpose.

The best items contain "quick guides", along with a primer on additional findings to describe how we reached our conclusions.

| Guide                                                                                         | Implemented | Clarity |
| --------------------------------------------------------------------------------------------- | ----------- | ------- |
| [Add Custom String Data in 2021E](./AddStrings2021E/)                                         | True        | 1.0     |
| [Attachments Not Parented to a `PartInstance`](./AttachmentsNotParentedToPartInstances/)      | True        | 0.7     |
| [Force RCCService FFlags to Load](./RCCServiceFFlagsFetchPatch/)                              | N/A         | 1.0     |
| [Advanced Trust Check for 2018M](./AdvancedTrustCheck2018M/)                                  | True        | 0.4     |
| [Advanced Trust Check for 2021E](./AdvancedTrustCheck2021E/)                                  | True        | 1.0     |
| [Give All Scripts Access to All Methods](./AllScriptsAccessAllMethods/)                       | True        | 1.0     |
| [Change Method Security Permissions](./ChangeMethodSecurityPermissions/)                      | N/A         | 1.0     |
| [Patch Client 2021E `DataModelPatch.rbxm`](./PatchDataModelPatch/)                            | False       | 0.3     |
| [Disable Gòógle Analytricks](./DisableGoogleAnalytricks/)                                     | False       | 0.4     |
| [Discriminate RCC Logs](./DiscriminateRCCLogs/)                                               | True        | 0.9     |
| [Extract Core Roblox Assets](./ExtractRobloxCoreAssets/)                                      | True        | 0.7     |
| [Bypass Video Limits](./BypassVideoLimits/)                                                   | True        | 1.0     |
| [Insert Objects for 2021E](./InsertObjects2021E/)                                             | True        | 0.8     |
| [Make Asset URLs Permissive](./MakeAssetURLsPermissive/)                                      | False       | 0.3     |
| [Force Use of Simple HTTP](./ForceNormalHTTP/)                                                | False       | 0.3     |
| [Allow Multiple Simultaneous Clients](./AllowMultipleClients/)                                | True        | 1.0     |
| [Fix Occasional Client Crashes](./FixOccasionalClientCrashes/)                                | True        | 1.0     |
| [Constructive Solid Geometry (CSG) Research](./CSGv3Research/)                                | True        | 0.5     |
| [Patch Materials](./PatchMaterials/)                                                          | True        | 1.0     |
| [Bypass Transport-Layer Security (TLS) Verification](./PatchTLSVerification/)                 | True        | 0.9     |
| [Enable Port Agnosticness](./EnablePortAgnosticness/)                                         | True        | 0.7     |
| [Redirect App Data Directory](./RedirectAppDataDirectory/)                                    | True        | 0.8     |
| [Enable Save Place](./EnableSavePlace/)                                                       | True        | 0.8     |
| [Reclassify RakNet for Hostile ISPs](./ReclassifyRakNet/)                                     | True        | 1.0     |
| [Fix Security Timeout](./FixSecurityTimeout/)                                                 | True        | 1.0     |
| [Bypass Studio Login](./StudioLogin/)                                                         | True        | 1.0     |
| [Support `MessagingService`](./SupportMessagingService/)                                      | False       | 0.6     |
| [Support `task.wait`](./SupportTaskWait/)                                                     | True        | 0.8     |
| [Stabilise `/Setting/QuietGet/%s/`](./StabiliseQuietGet/)                                     | True        | 0.8     |
| [Keep RCC's Settings Key Constant](./ConstantiseRCCSettingsKey)                               | True        | 0.8     |
| [Pending Research on Terrain](./Terrain/)                                                     | False       | 0.1     |
| [Rearrange `./Content` Directory for Studio](./RearrangeContentFolder/)                       | True        | 0.8     |
| [Jetray's Guide for 2021E <sub>need to derive relevant patches</sub>](./Jetray2021EGuide)     | True        | 0.7     |
| [Worships' Guide for 2021E <sub>need to derive relevant patches</sub>](./Worships2021EGuide/) | True        | 0.7     |
