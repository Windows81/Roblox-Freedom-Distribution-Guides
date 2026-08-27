Rōblox was not designed to portably allow one to use whatever domain they want. I've had to make plenty of patches for Rōblox Freedom Distribution to use a webserver run on _unsigned_ HTTPS; that's easier to make patches for.

However, this made fetching client settings (i.e. FFlags, et c.) break for v347 Player and Server.

Here's a hacky patch to make that work:

---

Using x32dbg, search in user-referenced string for `"/Setting/QuietGet/%s/"`. The query result is as shown in `RCCService.exe` v347:

| Address    | Disassembly               | String Address | String                    |
| ---------- | ------------------------- | -------------- | ------------------------- |
| `00C336AF` | `push rccservice.119E298` | `0119E298`     | `"/Setting/QuietGet/%s/"` |

The scroll up a couple pages and patch the conditional-move statement out, so that `edx` is always set to `"https"`:

```patch
 00C3361E | BA 1CEB0B01              | mov edx,rccservice.10BEB1C   | 10BEB1C:"https"
 00C33623 | B8 E4680C01              | mov eax,rccservice.10C68E4   | 10C68E4:"http"
 00C33628 | C745 FC 00000000         | mov dword ptr ss:[ebp-4],0   |
-00C3362F | 0F44D0                   | cmove edx,eax                |
+00C3362F | 90                       | nop                          |
+00C33630 | 90                       | nop                          |
+00C33631 | 90                       | nop                          |
```

---

This guide is not applicable for v463 because it uses a completely different API endpoint.
