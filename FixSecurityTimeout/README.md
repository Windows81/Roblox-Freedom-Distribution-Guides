_Referring to [this issue](https://github.com/Windows81/Roblox-Freedom-Distribution/issues/13#issuecomment-2389637948)_

> 2018 Server RCC crashes on startup. I tried to move the RFD directory from D: to C:, even tried blank files. Analyzed the dump, hoping not much out of it.
> WinDbg analyzing actually yielded something. The result is that RCCService of 2018M uses the `popcnt` instruction which the poor Pentium E6500 does not have.
>
> ```
> FAILED_INSTRUCTION_ADDRESS:
> RCCService+60738b
> 0123738b f30fb8c0        popcnt  eax,eax
> ```
>
> 2021E works just fine. I do not know why in HELL that happens. Analyzing it further, will return with results once I get them. Trying to patch RCCService to avoid this instruction, now testing it

---

![image](image-1.png)

In some cases, the 2021E RCC disconnects clients with an _error 266_ some time after joining.

The dev console says it's a "Security timeout" by RCCService.
![image](image-2.png)

If you're having problems, use [`./v463-server.1337`](./v463-server.1337) with x32dbg on the 2021E RCC.

Pre-patched versions (updated as of 2024-10-02) are in [`Server.zip`](./Server.zip).

**Don't overwhelm yourself spending too much dwelling on the material. If you need any help, it'll save you time to contact VisualPlugin.**
