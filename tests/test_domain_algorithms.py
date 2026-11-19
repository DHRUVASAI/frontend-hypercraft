import hashlib
import math
import re
import unittest

MAC_UNIFORM_RE = re.compile(r"^([0-9A-F]{2})([:-])(?:[0-9A-F]{2}\2){4}[0-9A-F]{2}$")
SLAP_QUADRANTS = {0: "ELI (x2)", 1: "SAI (x6)", 2: "AAI (xA)", 3: "Reserved (xE)"}


def classify_mac(mac: str) -> dict:
    if not isinstance(mac, str):
        return {"valid": False, "kind": "invalid", "reason": "non-string"}
    norm = mac.strip().upper()
    if not MAC_UNIFORM_RE.match(norm):
        return {"valid": False, "kind": "invalid", "reason": "malformed_or_mixed_separator"}
    octets = [int(p, 16) for p in norm.split(norm[2])]
    if all(b == 0x00 for b in octets):
        return {"valid": False, "kind": "invalid", "reason": "unspecified"}
    if all(b == 0xFF for b in octets):
        return {"valid": True, "kind": "broadcast", "is_unicast": False, "is_multicast": True, "is_laa": None, "slap_quadrant": None}
    b0 = octets[0]
    if b0 & 0x01:
        return {"valid": True, "kind": "multicast", "is_unicast": False, "is_multicast": True, "is_laa": None, "slap_quadrant": None}
    is_laa = bool(b0 & 0x02)
    return {
        "valid": True,
        "kind": "unicast_laa" if is_laa else "unicast_uaa",
        "is_unicast": True,
        "is_multicast": False,
        "is_laa": is_laa,
        "slap_quadrant": SLAP_QUADRANTS[(b0 >> 2) & 0x03] if is_laa else None,
    }


def wcag_contrast(fg_hex: str, bg_hex: str) -> float:
    def lum(h: str) -> float:
        h = h.lstrip("#")
        r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    l1, l2 = lum(fg_hex), lum(bg_hex)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def apca_contrast(txt_hex: str, bg_hex: str) -> float:
    def y_of(h: str) -> float:
        h = h.lstrip("#")
        r, g, b = ((int(h[i:i+2], 16) / 255.0) ** 2.4 for i in (0, 2, 4))
        y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        return y if y >= 0.022 else y + ((0.022 - y) ** 1.414)
    yt, yb = y_of(txt_hex), y_of(bg_hex)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:
        sapc = ((yb ** 0.56) - (yt ** 0.57)) * 1.14
        return 0.0 if sapc < 0.1 else (sapc - 0.027) * 100.0
    sapc = ((yb ** 0.65) - (yt ** 0.62)) * 1.14
    return 0.0 if sapc > -0.1 else (sapc + 0.027) * 100.0


def damp(current: float, target: float, lam: float, dt: float) -> float:
    return current + (target - current) * (1.0 - math.exp(-lam * min(dt, 0.05)))


def welford_stats(values):
    n = 0
    mean = 0.0
    m2 = 0.0
    for x in values:
        n += 1
        delta = x - mean
        mean += delta / n
        m2 += delta * (x - mean)
    return mean, (m2 / (n - 1)) if n > 1 else 0.0


def shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(text)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def bayes_fdr(tpr: float, fpr: float, prevalence: float) -> float:
    tp = prevalence * tpr
    fp = (1.0 - prevalence) * fpr
    return fp / (tp + fp)


def conformal_pvalue(cal_scores, test_score: float) -> float:
    greater_eq = sum(1 for s in cal_scores if s >= test_score)
    return (1 + greater_eq) / (len(cal_scores) + 1)


def _h_leaf(data: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + data).digest()


def _h_node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def _largest_pow2_lt(n: int) -> int:
    return 1 << ((n - 1).bit_length() - 1)


def rfc6962_root(leaves: list) -> bytes:
    if not leaves:
        return hashlib.sha256(b"").digest()
    if len(leaves) == 1:
        return _h_leaf(leaves[0])
    k = _largest_pow2_lt(len(leaves))
    return _h_node(rfc6962_root(leaves[:k]), rfc6962_root(leaves[k:]))


def rfc6962_inclusion_proof(leaves: list, index: int) -> list:
    n = len(leaves)
    if index < 0 or index >= n:
        raise IndexError(f"leaf index {index} out of bounds for tree size {n}")
    if n == 1:
        return []
    k = _largest_pow2_lt(n)
    if index < k:
        return rfc6962_inclusion_proof(leaves[:k], index) + [("R", rfc6962_root(leaves[k:]))]
    return rfc6962_inclusion_proof(leaves[k:], index - k) + [("L", rfc6962_root(leaves[:k]))]


def rfc6962_verify_inclusion(leaf: bytes, proof: list, expected_root: bytes) -> bool:
    if not isinstance(expected_root, (bytes, bytearray)) or len(expected_root) != 32:
        return False
    cur = _h_leaf(leaf)
    for item in proof:
        if not isinstance(item, tuple) or len(item) != 2:
            return False
        side, sibling = item
        if side not in ("L", "R") or not isinstance(sibling, (bytes, bytearray)) or len(sibling) != 32:
            return False
        cur = _h_node(cur, sibling) if side == "R" else _h_node(sibling, cur)
    return cur == expected_root


def _subproof(m: int, leaves: list, b: bool) -> list:
    n = len(leaves)
    if m == n:
        return [] if b else [rfc6962_root(leaves)]
    k = _largest_pow2_lt(n)
    if m <= k:
        return _subproof(m, leaves[:k], b) + [rfc6962_root(leaves[k:])]
    return _subproof(m - k, leaves[k:], False) + [rfc6962_root(leaves[:k])]


def rfc6962_consistency_proof(leaves: list, m: int) -> list:
    n = len(leaves)
    if m <= 0 or m > n:
        raise ValueError(f"Invalid consistency sizes: m={m}, n={n}")
    if m == n:
        return []
    return _subproof(m, leaves, True)


def rfc6962_verify_consistency(old_root: bytes, new_root: bytes, m: int, n: int, proof: list) -> bool:
    if m <= 0 or n <= 0 or m > n:
        return False
    if len(old_root) != 32 or len(new_root) != 32:
        return False
    if m == n:
        return len(proof) == 0 and old_root == new_root
    if not proof or any(not isinstance(h, (bytes, bytearray)) or len(h) != 32 for h in proof):
        return False

    nodes = ([old_root] + list(proof)) if (m & (m - 1)) == 0 else list(proof)
    fn = m - 1
    sn = n - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1

    fr = nodes[0]
    sr = nodes[0]
    for c in nodes[1:]:
        if sn == 0:
            return False
        if (fn & 1) or (fn == sn):
            fr = _h_node(c, fr)
            sr = _h_node(c, sr)
            while fn != 0 and (fn & 1) == 0:
                fn >>= 1
                sn >>= 1
        else:
            sr = _h_node(sr, c)
        fn >>= 1
        sn >>= 1

    return sn == 0 and fr == old_root and sr == new_root


class TestKnowledgeBasePrimitives(unittest.TestCase):
    def test_mac_classification_uniform_separators_and_slap(self):
        self.assertEqual(classify_mac("3C:22:FB:11:22:33")["kind"], "unicast_uaa")
        self.assertEqual(classify_mac("3C-22-FB-11-22-33")["kind"], "unicast_uaa")
        laa = classify_mac("DE:AD:BE:EF:00:01")
        self.assertEqual(laa["kind"], "unicast_laa")
        self.assertEqual(laa["slap_quadrant"], "Reserved (xE)")
        self.assertEqual(classify_mac("02:11:22:33:44:55")["slap_quadrant"], "ELI (x2)")
        self.assertEqual(classify_mac("06:11:22:33:44:55")["slap_quadrant"], "SAI (x6)")
        self.assertEqual(classify_mac("0A:11:22:33:44:55")["slap_quadrant"], "AAI (xA)")

        mcast = classify_mac("03:00:5E:00:00:01")
        self.assertEqual(mcast["kind"], "multicast")
        self.assertIsNone(mcast["is_laa"])

        bcast = classify_mac("FF:FF:FF:FF:FF:FF")
        self.assertEqual(bcast["kind"], "broadcast")
        self.assertIsNone(bcast["is_laa"])

        for bad in ("AA:BB-CC:DD-EE:FF", "00:00:00:00:00:00", "ZZ:11:22:33:44:55", "AA:BB:CC:DD:EE", 12345):
            self.assertFalse(classify_mac(bad)["valid"], f"Should reject {bad}")

    def test_wcag_and_apca_palette_verification(self):
        self.assertAlmostEqual(apca_contrast("#000000", "#FFFFFF"), 106.0, places=1)
        self.assertAlmostEqual(apca_contrast("#FFFFFF", "#000000"), -107.9, places=1)
        self.assertGreaterEqual(wcag_contrast("#16181D", "#F3F0EA"), 15.0)
        self.assertGreaterEqual(apca_contrast("#16181D", "#F3F0EA"), 95.0)
        self.assertGreaterEqual(wcag_contrast("#C6CDD9", "#12151B"), 11.0)
        self.assertLessEqual(apca_contrast("#C6CDD9", "#12151B"), -75.0)
        self.assertGreaterEqual(wcag_contrast("#117750", "#F3F0EA"), 4.8)

    def test_damping_frame_rate_invariance(self):
        v60, v120 = 0.0, 0.0
        for _ in range(30):
            v60 = damp(v60, 1.0, 8.0, 1.0 / 60.0)
        for _ in range(60):
            v120 = damp(v120, 1.0, 8.0, 1.0 / 120.0)
        self.assertAlmostEqual(v60, v120, places=12)
        self.assertAlmostEqual(v60, 1.0 - math.exp(-4.0), places=12)

    def test_welford_stability_large_offset(self):
        mean, var = welford_stats([1e9 + 4.0, 1e9 + 7.0, 1e9 + 13.0, 1e9 + 16.0])
        self.assertAlmostEqual(mean, 1e9 + 10.0, places=6)
        self.assertAlmostEqual(var, 30.0, places=6)

    def test_shannon_entropy_dga_separation(self):
        self.assertEqual(shannon_entropy("aaaa"), 0.0)
        self.assertAlmostEqual(shannon_entropy("abcd"), 2.0, places=12)
        self.assertGreater(shannon_entropy("qx7k9m2p8v4z1b6n"), shannon_entropy("google"))

    def test_bayes_fdr_not_fpr(self):
        fdr = bayes_fdr(tpr=0.99, fpr=0.01, prevalence=0.0001)
        self.assertAlmostEqual(fdr, 0.9901960784, places=6)

    def test_adversarial_rfc6962_inclusion_proofs(self):
        self.assertNotEqual(rfc6962_root([]), rfc6962_root([b""]))
        for odd_n in (3, 5, 7):
            leaves = [f"L{i}".encode() for i in range(odd_n)]
            self.assertNotEqual(rfc6962_root(leaves), rfc6962_root(leaves + [leaves[-1]]))

        leaves = [b"evt-0", b"evt-1", b"evt-2", b"evt-3", b"evt-4"]
        root = rfc6962_root(leaves)
        for idx, leaf in enumerate(leaves):
            proof = rfc6962_inclusion_proof(leaves, idx)
            self.assertTrue(rfc6962_verify_inclusion(leaf, proof, root))
            flipped = [("L" if s == "R" else "R", h) for s, h in proof]
            self.assertFalse(rfc6962_verify_inclusion(leaf, flipped, root))
            self.assertFalse(rfc6962_verify_inclusion(leaf, proof[:-1], root))
            self.assertFalse(rfc6962_verify_inclusion(leaf, proof + [("R", b"\xaa" * 32)], root))
            self.assertFalse(rfc6962_verify_inclusion(leaf + b"x", proof, root))

        forged_leaf = _h_leaf(b"evt-0") + _h_leaf(b"evt-1")
        parent_proof = [("R", rfc6962_root(leaves[2:4])), ("R", rfc6962_root(leaves[4:]))]
        self.assertFalse(rfc6962_verify_inclusion(forged_leaf, parent_proof, root))

        with self.assertRaises(IndexError):
            rfc6962_inclusion_proof(leaves, 5)
        self.assertFalse(rfc6962_verify_inclusion(b"evt-0", [("R", b"short")], root))

    def test_rfc6962_consistency_proofs_exhaustive_and_adversarial(self):
        max_n = 16
        all_leaves = [f"log-entry-{i:02d}".encode() for i in range(max_n)]
        for n in range(1, max_n + 1):
            new_leaves = all_leaves[:n]
            new_root = rfc6962_root(new_leaves)
            for m in range(1, n + 1):
                old_root = rfc6962_root(all_leaves[:m])
                cproof = rfc6962_consistency_proof(new_leaves, m)
                self.assertTrue(
                    rfc6962_verify_consistency(old_root, new_root, m, n, cproof),
                    f"Valid consistency proof failed for m={m}, n={n}",
                )

        m, n = 6, 13
        old_root = rfc6962_root(all_leaves[:m])
        tampered_leaves = list(all_leaves[:n])
        tampered_leaves[2] = b"TAMPERED-HISTORY"
        tampered_root = rfc6962_root(tampered_leaves)
        fake_proof = rfc6962_consistency_proof(tampered_leaves, m)
        self.assertFalse(rfc6962_verify_consistency(old_root, tampered_root, m, n, fake_proof))

        good_proof = rfc6962_consistency_proof(all_leaves[:n], m)
        good_new_root = rfc6962_root(all_leaves[:n])
        self.assertFalse(rfc6962_verify_consistency(old_root, good_new_root, m, n, good_proof[:-1]))
        self.assertFalse(rfc6962_verify_consistency(old_root, good_new_root, n + 1, n, good_proof))
        self.assertFalse(rfc6962_verify_consistency(old_root, good_new_root, 0, n, good_proof))


if __name__ == "__main__":
    unittest.main()
