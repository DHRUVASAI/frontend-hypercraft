# Authoritative Bibliography: Textbooks, Primary Specs & Peer-Reviewed Papers

## 1. Visual Design, Color Science & Accessibility
1. **Björn Ottosson (2020)** — *A Perceptual Color Space for Image Processing* (Oklab / OKLCH forward & inverse transformation matrices): `https://bottosson.github.io/posts/oklab/`
2. **W3C CSS Color Module Level 4** — OKLCH/Oklab specification, wide-gamut `color(display-p3 ...)`, and CSS Gamut Mapping Algorithm: `https://www.w3.org/TR/css-color-4/`
3. **W3C WCAG 2.1** — Success Criteria 1.4.3 (Contrast Minimum), 1.4.11 (Non-text Contrast): `https://www.w3.org/TR/WCAG21/`
4. **Myndex / W3C Silver APCA (`0.0.98G-4g`)** — Exact piecewise constants (`mainTRC: 2.4`, `normBG: 0.56`, `normTXT: 0.57`, `revTXT: 0.62`, `revBG: 0.65`, `blkThrs: 0.022`, `blkClmp: 1.414`, `scale: 1.14`, `loOffset: 0.027`): `https://github.com/Myndex/apca-w3`
5. **Gustavo M. Machado, Manuel M. Oliveira & Leandro A. F. Fernandes (IEEE TVCG 2009)** — *A Physiologically-based Model for Simulation of Color Vision Deficiency*.
6. **Robert Bringhurst** — *The Elements of Typographic Style* (4th Ed., Hartley & Marks).
7. **Josef Albers** — *Interaction of Color* (Yale University Press).

## 2. 3D Graphics, PBR & Web Performance
8. **Tomas Akenine-Möller, Eric Haines, Naty Hoffman, et al.** — *Real-Time Rendering* (4th Ed., CRC Press).
9. **Matt Pharr, Wenzel Jakob & Greg Humphreys** — *Physically Based Rendering: From Theory to Implementation* (4th Ed., MIT Press).
10. **Alejandro Conty Estevez & Christopher Kulla (SIGGRAPH 2017)** — *Production Friendly Microfacet Sheen BRDF* ("Charlie" sheen).
11. **Emmanuel Turquin (2019)** — *Practical Multiple Scattering Compensation for Microfacet Models* (GGX multi-scattering energy conservation).
12. **Khronos Group** — glTF 2.0, `KHR_materials_sheen`, `KHR_texture_basisu` (KTX2/Basis Universal UASTC & ETC1S), and `EXT_meshopt_compression`.
13. **Three.js Releases (`r152`, `r155`, `r160`, `r181+`)** — Color Management, Physically Based Lighting, `AgXToneMapping`, `WebGPURenderer`, and TSL (Three.js Shading Language): `https://threejs.org/docs/`
14. **W3C Web Audio API 1.1** — `AudioParam` automation & `AnalyserNode`: `https://www.w3.org/TR/webaudio-1.1/`
15. **Google web.dev — Core Web Vitals & INP (`scheduler.yield()`)**: `https://web.dev/articles/vitals`

## 3. Machine Learning Anomaly Detection & Statistics
16. **Fei Tony Liu, Kai Ming Ting & Zhi-Hua Zhou (IEEE ICDM 2008)** — *Isolation Forest*.
17. **Sahand Hariri, Matias Carrasco Kind & Robert J. Brunner (IEEE TKDE 2019)** — *Extended Isolation Forest* (hyperplane cuts eliminating axis-aligned ghost regions).
18. **Sudipto Guha, Nina Mishra, Gourav Roy & Okke Schrijvers (ICML 2016)** — *Robust Random Cut Forest Based Anomaly Detection on Streams* (`CoDisp`).
19. **Swee Chuan Tan, Kai Ming Ting & Tony Fei Liu (IJCAI 2011)** — *Fast Anomaly Detection for Streaming Data* (Half-Space Trees).
20. **Albert Bifet & Ricard Gavaldà (SDM 2007)** — *Learning from Time-Changing Data with Adaptive Windowing* (`ADWIN`).
21. **B. P. Welford (Technometrics 1962)** — *Note on a Method for Calculating Corrected Sums of Squares and Products*.
22. **Claude E. Shannon (Bell System Technical Journal 1948)** — *A Mathematical Theory of Communication*.
23. **Active Countermeasures — RITA** — Open-source C2 beacon analyzer (Bowley skewness + MADM + data-size consistency): `https://github.com/activecm/rita`
24. **Vladimir Vovk, Alexander Gammerman & Glenn Shafer** — *Algorithmic Learning in a Random World* (Conformal Prediction finite-sample guarantees).

## 4. Security Architecture, Cryptography & EVM Engineering
25. **IETF RFC 6962 / RFC 9162** — *Certificate Transparency v1/v2* (domain-separated Merkle trees, inclusion & consistency proofs, immunity to CVE-2012-2459).
26. **IETF RFC 8032 & Zcash ZIP-215** — *EdDSA (Ed25519)* strict vs. cofactored signature verification and malleability rules.
27. **Gavin Wood — Ethereum Yellow Paper** — EVM gas schedule (`KECCAK256` `0x20` = `30 + 6/word` vs. `SHA256` precompile `0x02` = `60 + 12/word`).
28. **CRYSOL Empirical Study (arXiv:2408.04939, 2024)** — *Demystifying and Detecting Cryptographic Defects in Ethereum* (`22.7%` of 25,745 contracts had defects; `abi.encodePacked` dynamic-type hash collisions).
29. **EIP-712** — Typed Structured Data Hashing & Signing; **OpenZeppelin `MerkleProof.sol`** double-hashed sorted-pair leaves.
30. **FoxIO JA4+ Specification (2023–2026)** & **RFC 8701 (GREASE)** & **RFC 9849 (TLS ECH)**, **RFC 9180 (HPKE)**, **RFC 9460 (HTTPS/SVCB)** — Modern TLS client fingerprinting.
31. **IEEE 802.3**, **RFC 4861 (IPv6 NDP)**, **RFC 6105 (RA-Guard)**, **RFC 6762/6763 (mDNS/DNS-SD)**, **RFC 8484 (DoH)**.

## 5. Voice-First AI & AI Builder Pricing Sources (Verified Nov 2026)
32. **AI4Bharat — IndicVoices (arXiv:2403.01926)** — Multilingual Indian speech corpus & IndicASR across all 22 scheduled languages.
33. **Nelson Cowan (Behavioral & Brain Sciences, 2001)** — *The Magical Number 4 in Short-Term Memory* (audio working-memory ceiling).
34. **Official Platform Pricing Docs (Verified November 2026):** `docs.lovable.dev/introduction/credits-and-usage`, `v0.app/pricing`, `bolt.new/pricing`, `cursor.com/help/account-and-billing/pricing`, `replit.com/pricing`, and Windsurf/Devin Desktop quota specs.

## 6. Additional Audit References Added in v4
35. **IETF RFC 9849** — *TLS Encrypted Client Hello (ECH)*; **RFC 9180** (HPKE); **RFC 9460** (SVCB & HTTPS DNS Resource Records).
36. **IEEE Std 802c-2017** — *Local Medium Access Control (MAC) Address Usage (SLAP — Structured Local Address Plan)*.
37. **Stefan Axelsson (ACM TISSEC, 2000)** — *The Base-Rate Fallacy and the Difficulty of Intrusion Detection* (FDR vs. FPR).
38. **Ryan J. Tibshirani, Rina Foygel Barber, Emmanuel J. Candès & Aaditya Ramdas (NeurIPS 2019)** — *Conformal Prediction Under Covariate Shift* (Weighted Conformal Prediction).
39. **Isaac Gibbs & Emmanuel Candès (NeurIPS 2021)** — *Adaptive Conformal Inference Under Distribution Shift (ACI)*.
40. **Yoav Benjamini & Daniel Yekutieli (Annals of Statistics, 2001)** — *The Control of the False Discovery Rate in Multiple Testing Under Dependency*.
41. **EIP-2929** — *Gas Cost Increases for State Access Opcodes* (`2,100` cold `SSTORE` access, `100` warm precompile `STATICCALL`).
42. **Devin Plans & Pricing (Verified 2026-11-19):** `https://devin.ai/pricing`; **Replit Starter & Billing Docs:** `https://docs.replit.com/billing/plans/starter-plan`, `https://docs.replit.com/help/pricing-and-plans`.
