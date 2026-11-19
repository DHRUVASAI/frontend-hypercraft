# Network Security Architecture: Kernel Telemetry, IEEE 802.3 LAA, IPv6 NDP & FoxIO JA4+

## 1. Beyond CLI Wrappers: Production OS Kernel Telemetry & Privilege Separation
Shelling out to `netsh` or `ufw` works cleanly for portable prototypes, but production cross-platform security daemons separate privileges and use native kernel interfaces:
- **Linux:** **eBPF / XDP** for wire-speed packet inspection with minimal userspace copy overhead + **netlink (`nftables`)** using least-privilege POSIX capabilities (`CAP_NET_RAW`, `CAP_NET_ADMIN` — avoiding full `uid=0` root).
- **Windows:** **WFP (Windows Filtering Platform)** callout drivers for deterministic packet/flow enforcement + Npcap for Layer-2 capture.
- **macOS:** **NetworkExtension (`NEFilterDataProvider`)** / signed `pfctl` anchor rules.
- **Privilege Separation Pattern:** Run the HTTP/WebSocket API and UI as an **unprivileged user**, communicating over an authenticated Unix domain socket / Windows named pipe with a minimal privileged enforcer that strictly validates every IP via `ipaddress.ip_address()` and calls `subprocess.run(argv_list, shell=False)` (eliminating shell-injection vectors).

## 2. IEEE 802.3 / 802c MAC Validation & Locally Administered Addresses (LAA)
**Critical Terminology & Validation Rules:**
- **Uniform Separator Enforcement:** Never accept mixed separators like `AA:BB-CC:DD-EE:FF`. Use a backreference regex `^([0-9A-F]{2})([:-])(?:[0-9A-F]{2}\2){4}[0-9A-F]{2}$` (rejecting mixed delimiters, wrong lengths, non-hex characters, and the all-zero unspecified address `00:00:00:00:00:00`).
- **Broadcast vs. Multicast vs. Unicast LAA:** Under **IEEE Std 802.3**, bit 0 (`0x01`) is Individual/Group (`0` = unicast, `1` = multicast/broadcast) and bit 1 (`0x02`) is Universal/Local (`0` = UAA factory OUI, `1` = **LAA**). Broadcast (`FF:FF:FF:FF:FF:FF`) and multicast (`(b0 & 0x01) == 1`) are **not** unicast LAA device addresses—set `is_laa = None` for non-unicast frames so callers never confuse broadcast/multicast with randomized client MACs.
- **Why Unicast LAA != Guaranteed OS Randomization:** Hypervisors (KVM, VMware, Hyper-V, Docker), VRRP/HSRP virtual routers, and manually configured NICs also set the U/L bit (second hex nibble in `{2, 6, A, E}`). Under **IEEE 802c-2017 (SLAP)**, bits 2–3 partition LAA space into 4 quadrants: `ELI (x2)`, `SAI (x6)`, `AAI (xA)`, and `Reserved (xE)`. Treat OS privacy randomization as a *heuristic inference* (corroborated by Wi-Fi medium + ephemeral churn), never a certainty.

```python
import re

MAC_UNIFORM_RE = re.compile(r"^([0-9A-F]{2})([:-])(?:[0-9A-F]{2}\2){4}[0-9A-F]{2}$")
SLAP_QUADRANTS = {0: "ELI (x2)", 1: "SAI (x6)", 2: "AAI (xA)", 3: "Reserved (xE)"}

def classify_mac(mac: str) -> dict:
    if not isinstance(mac, str):
        return {"valid": False, "kind": "invalid", "reason": "non-string"}
    norm = mac.strip().upper()
    if not MAC_UNIFORM_RE.match(norm):
        return {"valid": False, "kind": "invalid", "reason": "malformed_or_mixed_separator"}
    octets = [int(part, 16) for part in norm.split(norm[2])]
    if all(b == 0x00 for b in octets):
        return {"valid": False, "kind": "invalid", "reason": "unspecified"}
    if all(b == 0xFF for b in octets):
        return {"valid": True, "kind": "broadcast", "is_unicast": False, "is_multicast": True, "is_laa": None, "slap_quadrant": None}
    b0 = octets[0]
    if b0 & 0x01:
        return {"valid": True, "kind": "multicast", "is_unicast": False, "is_multicast": True, "is_laa": None, "slap_quadrant": None}
    is_laa = bool(b0 & 0x02)
    quadrant = SLAP_QUADRANTS[(b0 >> 2) & 0x03] if is_laa else None
    return {
        "valid": True,
        "kind": "unicast_laa" if is_laa else "unicast_uaa",
        "is_unicast": True,
        "is_multicast": False,
        "is_laa": is_laa,
        "slap_quadrant": quadrant,
    }
```

Pair verified unicast MACs with 5 concurrent resolution layers: **mDNS/DNS-SD (RFC 6762/6763)** -> **UPnP SSDP XML** -> **DHCP Option 12 (RFC 2132)** -> **NetBIOS UDP 137 + rDNS** -> **Official IEEE OUI CSV (~35,000+ prefixes)**.

## 3. The IPv6 Blind Spot Most LAN Guardians Miss (MITM6 / NDP Spoofing)
Monitoring only IPv4 ARP leaves modern Windows/macOS/Linux hosts exposed to **IPv6 Neighbor Discovery Protocol (RFC 4861)** attacks:
- **Rogue Router Advertisement (RA) / MITM6:** Even on "IPv4-only" LANs, Windows prefers IPv6 by default. An attacker broadcasting forged ICMPv6 Type 134 Router Advertisements carrying **RDNSS (RFC 8106)** silently becomes the victim's IPv6 DNS resolver without touching IPv4 ARP.
- **Defense:** Monitor ICMPv6 Type 134 (RA) and Type 136 (unsolicited NA) alongside IPv4 ARP, cross-check DNS via **RFC 8484 Cloudflare DoH (`1.1.1.1`)**, and enable **RFC 6105 RA-Guard** + **DAI (Dynamic ARP Inspection)** on managed switches.

## 4. Modern Encrypted Traffic Inspection: FoxIO JA4+ & TLS ECH (RFC 9849)
- **Why JA3 Broke (2023+):** Chrome began randomizing TLS ClientHello extension order on every connection, invalidating order-sensitive MD5 JA3 hashes.
- **FoxIO JA4 Specification (`a_b_c`, e.g. `t13d1516h2_8daaf6152771_e5627efa2ab1`):**
  - **Part `a`:** Transport (`t`=TCP/TLS, `q`=QUIC, `d`=DTLS) + TLS version (`13`) + SNI presence (`d`=domain, `i`=bare IP) + 2-digit cipher count + 2-digit extension count + ALPN (`h2`).
  - **Part `b`:** First 12 hex chars of SHA-256 over **sorted** cipher suites.
  - **Part `c`:** First 12 hex chars of SHA-256 over **sorted** extensions + **presented-order** signature algorithms.
  - **RFC 8701 GREASE Filtering:** Strip GREASE values everywhere (ciphers, extensions, supported groups, versions, and signature algorithms) so one client does not fragment into multiple fingerprints.
- **TLS Encrypted Client Hello (ECH — RFC 9849):** **RFC 9849** encrypts `ClientHelloInner` (including the true SNI and ALPN) inside `ClientHelloOuter`, using **HPKE (RFC 9180)** for public-key encryption and **HTTPS/SVCB DNS records (RFC 9460)** to distribute `ECHConfigList` public keys. Passive observers see only `ClientHelloOuter` (`public_name` SNI), so `JA4` fingerprints the outer TLS stack rather than the hidden inner destination—requiring correlation with flow timing, destination ASN, and host process HIDS.
