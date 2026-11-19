# Reproducible Multi-Seed Performance & ML Benchmark Report (v5)

- **Captured:** `2026-11-19T16:19:54.867084+00:00` (`20` independent seeds, 95% Student-t CIs)
- **Environment:** Python `3.10.16` · `Linux-4.19.0-gvisor-x86_64-with-glibc2.36` (8 CPUs)
- **Raw JSON:** `benchmarks/RESULTS.json` (`python3 benchmarks/run_benchmarks.py`)

## 1. RFC 6962 Merkle Tree: Build, Inclusion & Consistency Proof Timings

| Leaves ($N$) | Full Build | Inclusion Proof | Consistency Proof (`m=0.6N`) | Verified |
|---:|---:|---:|---:|:---:|
| `100` | `0.374 ms` | `7` (`330.5 us`) | `6` (`329.24 us`) | `True` |
| `1,000` | `2.988 ms` | `10` (`3010.84 us`) | `8` (`2959.62 us`) | `True` |
| `10,000` | `29.605 ms` | `14` (`29899.1 us`) | `11` (`30276.27 us`) | `True` |

## 2. 20-Seed Split Conformal Calibration (`alpha = 0.05`, 95% CI)

| Regime | Mean | Std | 95% CI |
|---|---:|---:|---|
| **Exchangeable FPR** | `0.0495` | `0.009` | `[0.0453, 0.0536]` |
| **Exchangeable TPR** | `0.9395` | `0.0181` | `[0.931, 0.948]` |
| **Covariate Shift (`+1.2 sigma`) FPR** | `0.3286` | `0.0286` | `[0.3152, 0.342]` |

## 3. 20-Seed IsolationForest on Realistic LAN Telemetry (With Hard Negatives)

Dataset: `benchmarks/datasets/lan_telemetry_sample.jsonl` (`500` rows, incl. `70` NAS/CDN/IoT hard negatives):
- **PR-AUC (Average Precision):** `0.9907` (95% CI `[0.9863, 0.9952]`)
- **Recall @ 1% FPR:** `0.923` (95% CI `[0.8791, 0.9669]`)
- **Recall @ 5% FPR:** `1.0` (95% CI `[1.0, 1.0]`)
- **Fit / Inference Latency:** `152.402 ms` fit · `3.7127 ms` inference

## 4. DGA Entropy + Vowel-Scarcity Detector on Hard-Negative Cloud/CDN Domains

Dataset: `benchmarks/datasets/dga_domains_sample.csv` (`40` domains):
- **Precision:** `0.8824` (`TP=15`, `FP=2`) · **Recall:** `0.75` (`FN=5`, `TN=18`)
