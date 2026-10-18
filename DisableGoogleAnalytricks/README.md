I observed that there is a chance that Rōblox Player and Studio sends information to Google for some reason. Let's fix that.

## Findings

According to the 2016 source-code leak, Google Analytics is enabled only after:

1. A session-unique UUID is generated in `googleClientID`,
2. That `googleClientID` is converted to an integer and modulo'd by 100 to integer `lottery`, then
3. The `lottery` value is greater than a certain `lotteryThreshold`.

Here's my [source](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/App/util/RobloxGoogleAnalytics.cpp#L133C28-L164C6) and its [header](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/App/include/util/RobloxGoogleAnalytics.h#L39C4-L39C81):

```cpp
void lotteryInit(const std::string &accountPropertyID, size_t maxThreadScheduleSize, int lotteryThreshold, const char * productName = NULL, int robloxAnalyticsLottery = -1, const std::string &sessionKey = "sessionID=")
{
	...

	robloxSessionKey = sessionKey;

	RobloxGoogleAnalytics::init(accountPropertyID, maxThreadScheduleSize, productName);

	if(robloxAnalyticsLottery == -1)
	{
		robloxAnalyticsLottery = lotteryThreshold;
	}

    std::size_t lottery = boost::hash_value(googleClientID) % 100;
    FASTLOG1(DFLog::GoogleAnalyticsTracking, "Google analytics lottery number = %d", lottery);
    // initialize google analytics
    if (lottery < (std::size_t)lotteryThreshold || FFlag::DebugAnalyticsForceLotteryWin)
    {
        canUseGA = true;
    }
	if (lottery < (std::size_t)robloxAnalyticsLottery || FFlag::DebugAnalyticsForceLotteryWin)
	{
		canUserRobloxEvents = true;
	}
}
```

How will we change `lotteryThreshold`? Good question.

The code above allows us to utilise an optional `robloxAnalyticsLottery` argument.

### Google Analytics in Studio

**In Studio v347, we can modify `FIntStudioRobloxAnalyticsLoad` to be equal to 0.** This _may_ work because, [here](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/RobloxStudio/RobloxMainWindow.cpp#L383):

```cpp
RBX::RobloxGoogleAnalytics::lotteryInit(googleAnalyticsAccountPropId,
	RBX::ClientAppSettings::singleton().GetValueGoogleAnalyticsThreadPoolMaxScheduleSize(), RBX::ClientAppSettings::singleton().GetValueGoogleAnalyticsLoadStudio(), "studio",
	FInt::StudioRobloxAnalyticsLoad, "studioSid=");
```

Note that `FInt::StudioRobloxAnalyticsLoad` is the (optional) fifth argument, which corresponds to `robloxAnalyticsLottery` in the initialisation function. Thus, _we can set `FIntStudioRobloxAnalyticsLoad` to 0_.

However, this flag had its name changed sometime between v410 and v463. According to [test files from my own FFlag extractor](https://github.com/Windows81/Roblox-x64dbg-FFlag-Extractor/tree/main/test), this was changed to `FIntStudioRobloxAnalyticsLoadHundredth`. The variable was _completely retired_ sometime between v548 and v695. Probaly because [they were moving away from Google Analytics](https://github.com/MaximumADHD/Roblox-FFlag-Tracker/blob/514d35ca3ba89fd92f7ee67eb6e364a538e7b49e/FVariables/FFlag/D/FFlagDeprecateGoogleAnalytics.json#L3).

### Google Analytics in Player

However, Player may not give us the same ease.

**In Player v463, we can change `FIntGoogleAnalyticsLoadPlayerHundredth` to 0.**

But v347 does not have any such option. For now, I added `"GoogleAnalyticsLoadPlayer": 0,` to `ClientAppSettings.json` (_without_ any `F` prefix). This is because [the 2016 codebase refers to it in an `IMPL_DATA` macro](https://github.com/PatoFlamejanteTV/ROBLOX/blob/93cd93079dbbc2b77519715b96fd3388165a8708/App/v8datamodel/FastLogSettings.cpp#L180). _I do not currently know if it works._

```cpp
IMPL_DATA(GoogleAnalyticsLoadPlayer, 1); // percent probability of using google analytics
```

Patches will be made to any misbehaving clients. They have been warned.

### Tracing Traffic in Mitmproxy

Using v347 and v463, I ran a simple test setup using Mitmproxy:

1. **`rfd server -c "./Examples/{PLACE}/"`** to launch a simple RCC server, then
2. **`rfd player -h localhost -u VisualPlugin`** to launch a client

_I did not find any external connections made by either peer in v347._

However, `RCCService.exe` v463 produces external UDP connections to `100.20.191.133`, which incidentally corresponds to [`DFString::TelegrafAddress`](https://github.com/Windows81/Roblox-x64dbg-FFlag-Extractor/blob/main/test/v463-studio.json#L13964).

**In v463 RCCService, fix by voiding all `FString` values whose keys contain _Telegraf_ into empty strings, i.e.:**

```json
...
"DFStringPerfTelegrafAddress": "",
"DFStringAltTelegrafAddress": "",
"DFStringAltTelegrafHTTPTransportUrl": "",
"DFStringTelegrafAddress": "",
...
```

Additionally, `RCCService.exe` v463 produces an HTTPS request to https://s3.amazonaws.com/setup.localhost:2005/Win32.463.305.gsi. Obviously, the asset it tries to reference does not exist.

Tracing the call path using x32dbg (and a whole lot of x86 training) led me to `FFlagDebugSkipGsiUrlPath`, which skips calling that URL if set to `true`.

**In v463 RCCService, set `FFlagDebugSkipGsiUrlPath` to `true`.**

```json
...
"FFlagDebugSkipGsiUrlPath": true,

...
```
