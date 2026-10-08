> [!NOTE]
> The following guide is abridged from [Aep's original text](./aep2018m.txt) to support Rōblox Freedom Distribution's needs as a website-agnostic launcher.

# 2018M Patching Guide by Aep

In order to get a version of mid-2018 Rōblox to work in a revival, Aep recommended doing three things:

1. converting two `je` statements into unconditional `jmps`, and
2. replacing string instances of `roblox.com` with a different domain

Let's _simplify_ this!

## Solution for (1.1)

The first patch in Aep's guide was not very complicated. However, VisualPlugin later discovered that its effects can be exactly replicated just by:

- **setting `FFlag::DebugLocalRccServerConnection` to `true`**

## Solution for (1.2)

_Refer to [VisualPlugin's `"Important !Loading shader files"` guide](../BypassBogusMessage/) for the solution._

## Solution for (2)

_Refer to [VisualPlugin's trust-check-bypass guide](../AdvancedTrustCheck2018M/) for the solution._

### Why?

Rōblox's clients _require_ use of Rōblox's website and services to operate under normal conditions. Some revivals get around this restriction by using a hex editor to _replace_ every raw-string instance of `roblox.com` with their own domain name (e.g. `synt2x.xyz`). This design works for some revival websites that don't need to keep swiching hostnames, but _not_ Rōblox Freedom Distribution.

Instead, Rōblox Freedom Distribution takes advantage of the open secret of how Rōblox allows use of a different hostname by introducing a custom `BaseUrl` field to `AppSettings.xml`. This mechanism exists so that Rōblox employees could test Rōblox's programs using their own staging servers (i.e., _not_ `roblox.com`). However, what you can include in the `BaseUrl` input is tightly limited. [VisualPlugin's trust-check-bypass guide](../AdvancedTrustCheck2018M/) overcomes this stòópid limitation.
