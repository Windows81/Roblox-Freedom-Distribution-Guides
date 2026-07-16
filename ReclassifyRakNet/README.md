# Let's Transform RakNet into Not-RakNet

🟥⬜⬛
In Feburary 2026, the Supreme Council for Media Regulation in Egypt [passed an ordinance blocking access to Rōblox for the entire country](https://www.afr.com/technology/minister-to-grill-roblox-over-child-grooming-fears-20260209-p5o0sw). This was accomplished via at least two ways:

1. any traffic to roblox.com (128.116.13.3) is dropped.
1. "offline-message" RakNet connection packets destined for _any_ IP address are blocked.

I live in California, a state in the western United States. In July 2026, I was visiting Egypt to catch up with family. [WE (Telecomegypt)](https://te.eg/en/personal) is a government-owned ISP whose broadband infrastructure is used by just about everyone I know.

Other ISPs (such as Vodafone, e&, and Orange) may have behave differently.

## Investigation

I was attempting to join @Yakovexplorer on a Rōblox Freedom Distribution server whilst I'm in Egypt.

I discover that accessing the server using RFD's v463 client would cause the "joining..." label to remain indefinitely, even though he was able to join by himself just fine.

I suspected that the culprit was with RakNet. We both confirmed that our firewalls were properly permissive; _no problem there_.

We also tried Radmin. Radmin was too unreliable to allow fluid gameplay, but RakNet packets _did_ transmit.

So, what started out as a routine troubleshooting round revealled something else...

### Experiment Setup

I prepared an experiment to validate whether RakNet packets are blocked at the ISP level:

1. Sender and receiver each log UDP packets usign Wireshark.

2. Sender sends two raw UDP packets with arbitrary data:
   1. one packet with the actual desired payload
   2. one redundancy packet with a magic string

3. Receiver checks that packets were received.
   - if both are received, no blockage
   - if only _latter_ was received, ISP blockage occurs
   - otherwise, experiment setup is faulty

```py
import socket
import os
import time
import base64

p = '2c276859ca755cfb3ac4532b0800450004a44043400080114f74c0a8640d33d20e0adadc399504905a627b00ffff00fefefefefdfdfdfd12345678050000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
p = bytearray.fromhex(p)
p = p[42:]

# Target configuration
TARGET_IP = "find it yourself"
TARGET_PORT = 0_0

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send the data
sock.sendto(p, (TARGET_IP, TARGET_PORT))
sock.sendto(b'.' * 6767, (TARGET_IP, TARGET_PORT))

sock.close()
```

### Experiment Results

In attempting to connect to the server, I copied the first UDP packet that gets transmitted, in the variable `p` above. Note that `p` is the body for the _entire_ UDP packet.

We need to trim the first 42 bytes so that the Python script can re-generate the 42-byte-large UDP header for us.

Yes, when a RakNet connection is initiated, the initial request's payload bytes will contain `00ffff00fefefefefdfdfdfd12345678` from index 1 (i.e., counting up from the _second_ byte).

_This value is completely distinct from `PROTOCOL_MAGIC` in RakNet's [`SphynxTransport.hpp`](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/Network/raknet/Source/cat/net/SphynxTransport.hpp#L195)._

Once Wireshark sees that initial request, it then assumes that all subsequent packets are also RakNet.

Per WireShark's [`RakPeer.cpp`](https://github.com/wireshark/wireshark/blob/f1af73573ffcdf5d65039d345352ec36c8ffd536/epan/dissectors/packet-raknet.c#L32):

```cpp
static uint8_t RAKNET_OFFLINE_MESSAGE_DATA_ID[16] = {0x00, 0xff, 0xff, 0x00, 0xfe, 0xfe, 0xfe, 0xfe, 0xfd, 0xfd, 0xfd, 0xfd, 0x12, 0x34, 0x56, 0x78};
```

Per Rōblox's [2016 source-code](https://github.com/Artifaqt/ROBLOX2016/blob/e0cfac59fea3a5b986843e65b0fda286e439f9fc/Network/raknet/Source/RakPeer.cpp#L131):

```cpp
static const char OFFLINE_MESSAGE_DATA_ID[16]={0x00,0xFF,0xFF,0x00,0xFE,0xFE,0xFE,0xFE,0xFD,0xFD,0xFD,0xFD,0x12,0x34,0x56,0x78};
```

## Finding in Rōblox

In the v463 client, this exact data is found at `020815AC`. In RCC, it is found at `019087E4`,

This will work because the memory nearby looks the same between client and server.

Although the nearby memory will look different between any v347 and v463, the memory looks identical between client v347 and server v347.

Note that the magic sequence takes up the entire middle row in each of the examples below.

### Client v463

```
0208159C  00 00 00 00 D4 05 00 00 B0 04 00 00 40 02 00 00  ....Ô...°...@...
020815AC  00 FF FF 00 FE FE FE FE FD FD FD FD 12 34 56 78  .ÿÿ.þþþþýýýý.4Vx
020815BC  52 61 6B 4E 65 74 43 6F 6E 6E 65 63 74 54 72 61  RakNetConnectTra
```

### Server v463

```
019087D4  00 00 00 00 D4 05 00 00 B0 04 00 00 40 02 00 00  ....Ô...°...@...
019087E4  00 FF FF 00 FE FE FE FE FD FD FD FD 12 34 56 78  .ÿÿ.þþþþýýýý.4Vx
019087F4  52 61 6B 4E 65 74 43 6F 6E 6E 65 63 74 54 72 61  RakNetConnectTra
```

### Client v347

```
01531AAC  50 2D 02 01 30 A9 47 00 30 92 72 00 C0 E6 CE 00  P-..0©G.0.r.ÀæÎ.
01531ABC  00 FF FF 00 FE FE FE FE FD FD FD FD 12 34 56 78  .ÿÿ.þþþþýýýý.4Vx
01531ACC  00 00 00 00 D4 05 00 00 B0 04 00 00 40 02 00 00  ....Ô...°...@...
```

### Server v347

```
011C7A98  30 EC CA 00 30 A7 47 00 50 87 64 00 F0 23 CF 00  0ìÊ.0§G.P.d.ð#Ï.
011C7AA8  00 FF FF 00 FE FE FE FE FD FD FD FD 12 34 56 78  .ÿÿ.þþþþýýýý.4Vx
011C7AB8  00 00 00 00 D4 05 00 00 B0 04 00 00 40 02 00 00  ....Ô...°...@...
```

## Applying Patches

Since this is a constant value only really used by RakNet, it should be safe to assume that there will be thirteen (13) results for when you search for references to that magic string.

I noticed that _all_ memory dumps above had the values at address-minus-1 equal to `00`. For this reason, let's subtract `0x1` to each instance I see.

For example,

```diff
-push robloxplayerbeta.20815AC
+push robloxplayerbeta.20815AB
```

### Client v463

| Address    | Disassembly                                          |
| ---------- | ---------------------------------------------------- |
| `01167E00` | `push robloxplayerbeta.20815AC`                      |
| `01167EDA` | `mov dword ptr ss:[ebp-10],robloxplayerbeta.20815AC` |
| `01167F69` | `mov dword ptr ss:[ebp-10],robloxplayerbeta.20815AC` |
| `01167FAB` | `mov dword ptr ss:[ebp-10],robloxplayerbeta.20815AC` |
| `01168031` | `mov dword ptr ss:[ebp-10],robloxplayerbeta.20815AC` |
| `01168071` | `mov dword ptr ss:[ebp-10],robloxplayerbeta.20815AC` |
| `0116818A` | `push robloxplayerbeta.20815AC`                      |
| `0116A852` | `push robloxplayerbeta.20815AC`                      |
| `0116E566` | `push robloxplayerbeta.20815AC`                      |
| `0116F821` | `push robloxplayerbeta.20815AC`                      |
| `011702AA` | `push robloxplayerbeta.20815AC`                      |
| `0117041C` | `push robloxplayerbeta.20815AC`                      |
| `01170769` | `push robloxplayerbeta.20815AC`                      |

### Server v463

| Address    | Disassembly                                    |
| ---------- | ---------------------------------------------- |
| `0069ABB0` | `push rccservice.19087E4`                      |
| `0069AC8A` | `mov dword ptr ss:[ebp-10],rccservice.19087E4` |
| `0069AD19` | `mov dword ptr ss:[ebp-10],rccservice.19087E4` |
| `0069AD5B` | `mov dword ptr ss:[ebp-10],rccservice.19087E4` |
| `0069ADE1` | `mov dword ptr ss:[ebp-10],rccservice.19087E4` |
| `0069AE21` | `mov dword ptr ss:[ebp-10],rccservice.19087E4` |
| `0069AF3A` | `push rccservice.19087E4`                      |
| `0069D58D` | `push rccservice.19087E4`                      |
| `006A1166` | `push rccservice.19087E4`                      |
| `006A2553` | `push rccservice.19087E4`                      |
| `006A33AA` | `push rccservice.19087E4`                      |
| `006A350D` | `push rccservice.19087E4`                      |
| `006A383A` | `push rccservice.19087E4`                      |
