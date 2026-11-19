# Cryptographic Forensic Ledgers, RFC 6962 Merkle Proofs & EIP-2929 EVM Gas

## 1. Two Classic Merkle Vulnerabilities & Tree Compatibility Warning
1. **CVE-2012-2459 (Odd-Leaf Duplication Malleability):** Duplicating the last hash on odd tree levels makes `[A, B, C]` and `[A, B, C, C]` produce the **exact same Merkle root**.
2. **Second-Preimage Forgery:** Using the same hash function for leaves and interior nodes lets an attacker submit a 64-byte interior concatenation as a forged leaf.

### RFC 6962 / RFC 9162 Canonical Construction
- **Domain-Separated Hashing:** $H_0(d) = \text{SHA256}(\texttt{0x00} \parallel d)$ for leaves; $H_1(L, R) = \text{SHA256}(\texttt{0x01} \parallel L \parallel R)$ for internal nodes.
- **Asymmetric Largest-Power-of-Two Split:** For $n > 1$, split at the largest $k = 2^j < n$:
  $$\text{MTH}(D[0:n]) = H_1(\text{MTH}(D[0:k]),\ \text{MTH}(D[k:n]))$$
  *Unit-tested in `tests/test_domain_algorithms.py`:* `MTH([A, B, C]) != MTH([A, B, C, C])`.
- **Inclusion Proofs + Consistency Proofs (`RFC 6962 §2.1.2`):** Inclusion proofs verify event membership in $T_n$; **consistency proofs** prove in $O(\log_2 n)$ hashes that an earlier anchored root $T_m$ is an append-only prefix of $T_n$.

### CRITICAL Interoperability Warning (RFC 6962 vs. OpenZeppelin `MerkleProof.sol`)
**Never mix these two tree formats between off-chain prover and on-chain verifier:**
- **RFC 6962 / RFC 9162:** Uses SHA-256, `0x00`/`0x01` prefixes, largest-power-of-two split, and **ordered** left/right children (requires explicit `bool[] isLeft` direction bits on-chain).
- **OpenZeppelin `MerkleProof.sol`:** Uses `keccak256`, **lexicographically sorted pairs** (no direction bits), and double-hashed leaves `keccak256(bytes.concat(keccak256(abi.encode(...))))`.
Pick **one** specification end-to-end (RFC 6962 SHA-256 for transparency logs/CT compatibility, or OpenZeppelin Keccak-256 for minimal EVM verification gas).

## 2. Ed25519 (RFC 8032 vs. ZIP-215) & Key Custody
- Curve25519 has cofactor $h = 8$. Pin ONE verification standard across all signers and auditors (**strict RFC 8032** canonical decoding with $S < L$, OR **ZIP-215** cofactored consensus verification) to avoid split-view acceptance bugs.
- Protect private keys in production with OS/hardware custody (**Windows DPAPI/CNG**, **macOS Secure Enclave**, **Linux TPM 2.0**) and record signed key-rotation blocks in the ledger.

## 3. Exact EVM Gas Economics (Yellow Paper + EIP-2929) & Solidity Safety
| EVM Operation | Exact Gas Schedule (Yellow Paper + EIP-2929) | Practical Engineering Consequence |
|---|---|---|
| **`KECCAK256` (`0x20`)** | `30 + 6 × ⌈bytes/32⌉` (+ memory expansion) | Native opcode; hashing two 32-byte nodes (2 words) costs **`42` base gas** in inline assembly. |
| **`SHA256` precompile (`0x02`)** | `60 + 12 × ⌈bytes/32⌉` **+ `100` gas warm `STATICCALL`** (EIP-2929 pre-warmed `0x01–0x0a`) + call/memory setup | Hashing two 32-byte nodes costs **`~184+` gas** per hop (~**3.5×–5× more expensive** than inline `keccak256` in a Merkle loop, not merely `2×`). |
| **`SSTORE` (cold `0 → non-zero`)** | **`22,100` gas** (`20,000` set + `2,100` cold slot access under EIP-2929) | Batch 100–10,000 incidents into one 32-byte `merkleRoot` for constant $O(1)$ storage cost. |
| **`LOG2` event emission** | `375 + 2×375 + 8×bytes` (`~1,381` gas for 32-byte data) | **~16× cheaper than `SSTORE`** when off-chain indexers verify roots and smart contracts don't need on-chain `anchors[root]` lookups. |

### Solidity Safety Rules (CRYSOL 2024 Study — 22.7% Defect Rate)
1. **`abi.encodePacked` Dynamic-Type Collision Rule:** Collisions occur specifically when **two or more dynamic types** (`string`, `bytes`, dynamic arrays) are concatenated adjacently without length delimiters (e.g., `abi.encodePacked("ab", "c") == abi.encodePacked("a", "bc")`). Fixed-width types (`bytes32`, `uint8`, `address`) are non-ambiguous, though `abi.encode` or `bytes.concat` is preferred for audit clarity.
2. **EIP-712 & Finality Honesty:** Include `chainId` and `verifyingContract` in off-chain signed payloads (`EIP-712`) to prevent cross-chain replay, or use **EAS (Ethereum Attestation Service)**. Distinguish **L2 sequencer soft confirmation (~1–2 s)** from **Ethereum L1 Casper FFG economic finality (~2 epochs / ~12.8 minutes)**.
