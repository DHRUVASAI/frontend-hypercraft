# Realistic Network Telemetry & DGA Benchmark Datasets

Committed deterministic datasets (`seed=20261119`) designed to avoid trivially separable Gaussian toy tests:
1. `lan_telemetry_sample.jsonl` (`500` rows, `10%` attack prevalence): `380` benign baseline + `70` hard-negative benign (NAS backups, CDN DNS, IoT polling) + `50` attacks (jittered C2 beacons, ARP storms, SYN sweeps, stealthy MITM).
2. `dga_domains_sample.csv` (`40` rows, `50%` DGA): includes high-entropy cloud/CDN hard negatives (`cloudfront.net`, `amazonaws.com`, `googlevideo.com`).
