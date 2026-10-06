In keeping with the spirit of innovation, these guides should allow other Rōblox researchers to replicate my work. I've incorporated some of their material into various aspects of Rōblox Freedom Distribution.

Though, the guides _don't yet_ allow you to reproduce _all_ the patches I made to the Rōblox clients from scratch.

**Don't overwhelm yourself spending too much time dwelling on the material. Most of it is still poorly organised.**

**If you need any help, it'll save you time to contact VisualPlugin.**

## Where does Rōblox Freedom Distribution come from?

Rōblox Freedom Distribution (RFD) began its development in June 2023 using `exe` programs from _Rōblox Filtering Disabled_, a prior project which carries the same initials. Many guides in this repository contain files with a `.1337` extension, used for x32dbg. The addresses indicated in each patch file refer to RVAs (relative virtual addresses); these RVAs do not exactly indicate the _file_ offsets where patches are applied.

I have taken care to locate the original sources so as to create a complete lineage of Freedom Distribution's patches.

Consult [`./_misc/haxdiff/`](./_misc/haxdiff/) for more info; updated at _soonest_ 2026-10-01 (RFD 0.68.3).

### Version 347 (2018M)

- Server: `f21a8e91e6d1416a` ([Gametest2 RCCService](https://archive.org/download/gametest2-rccservice/version-f21a8e91e6d1416a-RCCService.zip) - [Archive](https://web.archive.org/web/20260919031822if_/https://dn721607.ca.archive.org/0/items/gametest2-rccservice/version-f21a8e91e6d1416a-RCCService.zip))

- Player: `2ec87a18126443e7` ([Wayback Machine](https://web.archive.org/web/20220726110401if_/http://setup.gametest2.robloxlabs.com/version-2ec87a18126443e7-RobloxApp.zip))

- Studio: `d9cf1f7e4fe14aa9` ([Robloxopolis Archive](<https://archive.robloxopolis.com/archive/Clients/DeployHistory/setup.roblox.com/Windows/Studio/0.347.0.28462%20(version-d9cf1f7e4fe14aa9).zip>))

### Version 463 (2021E)

- Server: `07b64feec0bd47c1` ([Rōblonium Archive](https://archive.roblonium.com/Client/Windows/RCCService/production/RCCServiceR7Z9CYTW7WBR95VW/version-07b64feec0bd47c1/version-07b64feec0bd47c1-RCCServiceR7Z9CYTW7WBR95VW.zip))

- Player: `5a54208fe8e24e87` ([Wayback Machine](https://web.archive.org/web/20240224094219if_/https://setup.rbxcdn.com/version-5a54208fe8e24e87-RobloxApp.zip))

- Studio: `c993d5e9c7224b14` ([Wayback Machine](https://web.archive.org/web/20240324082713if_/http://setup.rbxcdn.com/version-c993d5e9c7224b14-RobloxStudio.zip))

## Guide Index

Listed below are the directories in this repository, along with roughly how well they achieve their stated purpose.

Items with a high _Clarity_ rating will contain "quick guides" and a primer on additional findings to describe how we reached our conclusions.

| Guide                                                                                    | v347  | v463  | Clarity |
| ---------------------------------------------------------------------------------------- | ----- | ----- | ------- |
| [Aep's Guide for 2018M](./Aep2018MGuide/)                                                | True  | False | 0.9     |
| [Jetray's Guide for 2021E](./Jetray2021EGuide)                                           | False | True  | 0.7     |
| [Worships' Guide for 2021E](./Worships2021EGuide/)                                       | N/A   | N/A   | 0.7     |
| [Add Custom String Data in 2021E](./AddStrings2021E/)                                    | False | True  | 1.0     |
| [Attachments Not Parented to a `PartInstance`](./AttachmentsNotParentedToPartInstances/) | False | True  | 0.7     |
| [Force RCCService FFlags to Load](./RCCServiceFFlagsFetchPatch/)                         | N/A   | N/A   | 1.0     |
| [Advanced Trust Check for 2018M](./AdvancedTrustCheck2018M/)                             | False | True  | 1.0     |
| [Advanced Trust Check for 2021E](./AdvancedTrustCheck2021E/)                             | False | True  | 1.0     |
| [Give All Scripts Access to All Methods](./AllScriptsAccessAllMethods/)                  | False | False | 1.0     |
| [Change Method Security Permissions](./ChangeMethodSecurityPermissions/)                 | N/A   | N/A   | 1.0     |
| [Bypass `--rbxsig...` Checks](./BypassRbxsig/)                                           | True  | N/A   | 0.8     |
| [Patch Client 2021E `DataModelPatch.rbxm`](./PatchDataModelPatch/)                       | False | False | 0.4     |
| [Disable Gòógle Analytricks](./DisableGoogleAnalytricks/)                                | False | False | 0.5     |
| [Disable SOAP](./DisableSOAP/)                                                           | False | True  | 1.0     |
| [Discriminate RCC Logs](./DiscriminateRCCLogs/)                                          | False | True  | 0.9     |
| [Manage FFlags](./ManageFFlags/)                                                         | N/A   | N/A   | 0.9     |
| [Extract Core Roblox Assets](./ExtractRobloxCoreAssets/)                                 | False | True  | 0.7     |
| [Bypass Video Limits](./BypassVideoLimits/)                                              | False | True  | 1.0     |
| [Populate Insert-Objects Widget for 2021E](./InsertObjects2021E/)                        | False | True  | 0.8     |
| [Make Asset URLs Permissive](./MakeAssetURLsPermissive/)                                 | False | False | 0.2     |
| [Disable SOAP](./DisableSOAP/)                                                           | True  | True  | 1.0     |
| [Force Use of Simple HTTP](./ForceSimpleHTTP)                                            | False | False | 0.3     |
| [Allow Multiple Simultaneous Clients](./AllowMultipleClients/)                           | True  | True  | 1.0     |
| [Fix Occasional Client Crashes](./FixOccasionalClientCrashes/)                           | False | True  | 1.0     |
| [Constructive Solid Geometry (CSG) Research](./CSGv3Research/)                           | False | True  | 0.5     |
| [Patch Materials](./PatchMaterials/)                                                     | True  | True  | 1.0     |
| [Bypass Transport-Layer Security (TLS) Verification](./PatchTLSVerification/)            | False | True  | 1.0     |
| [Enable Port Agnosticness](./EnablePortAgnosticness/)                                    | False | True  | 0.7     |
| [Redirect App Data Directory](./RedirectAppDataDirectory/)                               | True  | True  | 0.8     |
| [Enable Save Place](./EnableSavePlace/)                                                  | False | True  | 0.8     |
| [Reclassify RakNet for Hostile ISPs](./ReclassifyRakNet/)                                | True  | True  | 1.0     |
| [Fix Security Timeout](./FixSecurityTimeout/)                                            | False | True  | 0.4     |
| [Bypass Studio Login](./StudioLogin/)                                                    | True  | True  | 1.0     |
| [Support `MessagingService`](./SupportMessagingService/)                                 | False | False | 0.4     |
| [Studio Internal Patch](./StudioInternalPatch/)                                          | False | True  | 0.6     |
| [Support `task.wait`](./SupportTaskWait/)                                                | N/A   | N/A   | 0.8     |
| [Fix `/Setting/QuietGet/%s/` to HTTPS](./FixQuietGetProtocol/)                           | True  | False | 0.8     |
| [Keep RCC's Settings Key Constant](./ConstantiseRCCSettingsKey)                          | True  | True  | 0.8     |
| [Pending Research on Terrain](./Terrain/)                                                | N/A   | N/A   | 0.3     |
| [Rearrange `./Content` Directory for Studio](./RearrangeContentFolder/)                  | True  | True  | 0.8     |
