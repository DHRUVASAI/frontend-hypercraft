# Streaming ML Anomaly Detection, Concept Drift, Bayes FDR & Conformal Calibration

## 1. Beyond Standard Isolation Forest: Eliminating Axis-Aligned Ghost Regions
Standard **Isolation Forest** (Liu, Ting & Zhou, ICDM 2008) splits along single coordinate axes ($x_j < s$), scoring $s(x, n) = 2^{-E(h(x))/c(n)}$. **Hariri, Kind & Brunner (IEEE TKDE 2019)** proved that axis-aligned splits create rectangular **"ghost regions"** of artificially low anomaly scores far from real clusters. **Extended Isolation Forest (EIF)** replaces axis cuts with random-slope hyperplanes $(\mathbf{x} - \mathbf{p}) \cdot \mathbf{n} \le 0$ ($\mathbf{n} \sim \mathcal{N}(\mathbf{0}, I_d)$), eliminating ghost regions in correlated telemetry.

## 2. True Streaming Anomaly & Concept Drift Detection
- **Robust Random Cut Forest (RRCF, Guha et al., ICML 2016):** $O(\log n)$ incremental insertion/deletion on sliding streams using **Collusive Displacement (`CoDisp`)**, robust against clustered bursts.
- **Half-Space Trees (Tan, Ting & Liu, IJCAI 2011):** Constant-memory unsupervised mass-profile streaming trees.
- **ADWIN (Bifet & Gavaldà, SDM 2007):** Automatically splits variable-length windows when sub-window means diverge past a Hoeffding bound $\epsilon_{\text{cut}}$, resetting stale baselines when a laptop changes networks.
- **Online Welford Variance (1962) + Anti-Poisoning Gate:** Guard baseline updates with `if z < 3.5: update_welford(x)` so active attack spikes cannot poison the running mean.

## 3. Production C2 Beaconing Math (RITA / Active Countermeasures)
Naive Coefficient of Variation misses jittered beacons (`sleep 60s ± 20%`). Combine:
1. **Bowley Skewness:** $S_B = (Q_3 + Q_1 - 2Q_2)/(Q_3 - Q_1)$, $\text{skewScore} = 1 - |S_B|$ (symmetric jitter yields $S_B \approx 0$).
2. **MADM Dispersion:** $\text{MADM} = \text{median}(|\Delta t_i - Q_2|)$, $\text{madmScore} = \max(0, 1 - \text{MADM}/30)$.
3. **Payload Size Consistency (`dsScore`) + FFT Periodogram Spectral Peak Ratio** for jittered periodicities.

## 4. Base-Rate Fallacy (FDR vs. FPR) & Conformal Calibration Assumptions
**Critical Terminology Distinction (Axelsson, 2000):**
- **FPR (False Positive Rate):** $P(\text{Alert} \mid H_0)$ — fraction of benign events incorrectly flagged.
- **FDR (False Discovery Rate):** $1 - \text{Precision} = P(H_0 \mid \text{Alert})$ — fraction of **raised alerts** that are false alarms.

At $\text{TPR} = 99\%$, $\text{FPR} = 1\%$, and attack prevalence $p = 0.01\%$ ($10^{-4}$):
$$\text{FDR} = \frac{(1 - p)\cdot\text{FPR}}{p\cdot\text{TPR} + (1 - p)\cdot\text{FPR}} = \frac{0.9999 \times 0.01}{0.0001 \times 0.99 + 0.9999 \times 0.01} = \mathbf{99.02\%} \quad (\text{Precision} = 0.98\%)$$
Even at `0.1%` prevalence, achieving `> 90%` precision (`FDR < 10%`) requires **`FPR ≤ 0.01%`** (`Precision = 90.83%`). Always evaluate detectors using **PR-AUC** and **Recall @ FPR = 0.01%**, never accuracy or ROC-AUC alone.

### Conformal Prediction & Multiple-Testing Assumptions (Mandatory Qualifications)
1. **Marginal Coverage Under Exchangeability Only:** For calibration nonconformity scores $s_1, \dots, s_m$ from $H_0$, the split conformal p-value
   $$p(x_{\text{new}}) = \frac{1 + |\{i : s_i \ge s(x_{\text{new}})\}|}{m + 1}$$
   guarantees **marginal** error control $\mathbb{P}(p(X_{\text{new}}) \le \alpha \mid H_0) \le \alpha$ **strictly under exchangeability** between calibration and test points—NOT conditional coverage for a specific device, VLAN, or hour of day.
2. **Handling Non-Stationary Network Drift:** Real LAN traffic violates exchangeability (diurnal cycles, OS updates, adversarial shifts). Production systems must replace static split conformal calibration with **Weighted Conformal Prediction** (Tibshirani et al., 2019), **Adaptive Conformal Inference (ACI)** (Gibbs & Candès, 2021, updating $\alpha_{t+1} = \alpha_t + \gamma(\alpha - \mathbf{1}\{\text{err}_t\})$), or **ADWIN-triggered recalibration windows**.
3. **Multiple-Hypothesis Correction Across $K$ Hosts:** **Benjamini-Hochberg (BH)** controls expected FDR under independence or PRDS (positive regression dependence on a subset). Because LAN hosts share routers, broadcasts, and correlated outages, apply **Benjamini-Yekutieli (BY)** (dividing the BH threshold by the harmonic number $H_K = \sum_{i=1}^K 1/i$) when arbitrary cross-host correlation is present.
