import argparse
import csv
import json
import math
import os
import platform
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_domain_algorithms import (
    conformal_pvalue,
    rfc6962_consistency_proof,
    rfc6962_inclusion_proof,
    rfc6962_root,
    rfc6962_verify_consistency,
    rfc6962_verify_inclusion,
    shannon_entropy,
)

T_CRIT_95 = {4: 2.776, 9: 2.262, 19: 2.093, 29: 2.045}


def summarize_ci(values):
    n = len(values)
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if n > 1 else 0.0
    t_val = T_CRIT_95.get(n - 1, 1.96)
    half = t_val * (sd / math.sqrt(n)) if n > 1 else 0.0
    return {
        "n_seeds": n,
        "mean": round(mean, 4),
        "std": round(sd, 4),
        "ci95_low": round(mean - half, 4),
        "ci95_high": round(mean + half, 4),
    }


def bench_rfc6962_merkle(sizes=(100, 1000, 10000)):
    out = []
    for n in sizes:
        leaves = [f"garuda-incident-{i:06d}".encode("utf-8") for i in range(n)]
        t0 = time.perf_counter()
        root = rfc6962_root(leaves)
        build_ms = (time.perf_counter() - t0) * 1000.0

        t1 = time.perf_counter()
        proof = rfc6962_inclusion_proof(leaves, n // 2)
        inc_ok = rfc6962_verify_inclusion(leaves[n // 2], proof, root)
        inc_us = (time.perf_counter() - t1) * 1e6

        m = max(1, (n * 3) // 5)
        old_root = rfc6962_root(leaves[:m])
        t2 = time.perf_counter()
        cproof = rfc6962_consistency_proof(leaves, m)
        cons_ok = rfc6962_verify_consistency(old_root, root, m, n, cproof)
        cons_us = (time.perf_counter() - t2) * 1e6

        out.append({
            "n_leaves": n,
            "build_ms": round(build_ms, 3),
            "inclusion_hashes": len(proof),
            "inclusion_us": round(inc_us, 2),
            "consistency_hashes": len(cproof),
            "consistency_us": round(cons_us, 2),
            "all_verified": bool(inc_ok and cons_ok),
        })
    return out


def bench_conformal_multiseed(n_seeds=20, n_cal=1000, n_test=2000, alpha=0.05):
    ex_fprs, ex_tprs, drift_fprs = [], [], []
    for seed in range(n_seeds):
        rng = random.Random(1000 + seed)
        cal = [rng.gauss(0.0, 1.0) for _ in range(n_cal)]
        benign = [rng.gauss(0.0, 1.0) for _ in range(n_test)]
        anom = [rng.gauss(3.2, 1.0) for _ in range(400)]
        drifted = [rng.gauss(1.2, 1.0) for _ in range(n_test)]

        ex_fprs.append(sum(1 for x in benign if conformal_pvalue(cal, x) <= alpha) / n_test)
        ex_tprs.append(sum(1 for x in anom if conformal_pvalue(cal, x) <= alpha) / len(anom))
        drift_fprs.append(sum(1 for x in drifted if conformal_pvalue(cal, x) <= alpha) / n_test)

    return {
        "target_alpha": alpha,
        "exchangeable_fpr": summarize_ci(ex_fprs),
        "exchangeable_tpr": summarize_ci(ex_tprs),
        "covariate_shift_1_2sigma_fpr": summarize_ci(drift_fprs),
    }


def bench_realistic_telemetry_multiseed(n_seeds=20):
    try:
        import numpy as np
        from sklearn.ensemble import IsolationForest
        from sklearn.metrics import average_precision_score
    except ImportError:
        return {"skipped": True, "reason": "scikit-learn not installed"}

    ds_path = ROOT / "benchmarks/datasets/lan_telemetry_sample.jsonl"
    rows = [json.loads(line) for line in ds_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    benign_x = np.array([r["features"] for r in rows if r["label"] == 0], dtype=float)
    attack_x = np.array([r["features"] for r in rows if r["label"] == 1], dtype=float)

    pr_aucs, rec_1pct, rec_5pct, fit_ms_list, inf_ms_list = [], [], [], [], []
    for seed in range(n_seeds):
        rng = np.random.default_rng(2000 + seed)
        perm = rng.permutation(len(benign_x))
        n_train = int(len(benign_x) * 0.65)
        x_tr = benign_x[perm[:n_train]]
        x_te_b = benign_x[perm[n_train:]]
        x_te = np.vstack([x_te_b, attack_x])
        y_te = np.array([0] * len(x_te_b) + [1] * len(attack_x))

        t0 = time.perf_counter()
        clf = IsolationForest(n_estimators=100, contamination=0.05, random_state=seed)
        clf.fit(x_tr)
        fit_ms_list.append((time.perf_counter() - t0) * 1000.0)

        t1 = time.perf_counter()
        scores = -clf.decision_function(x_te)
        inf_ms_list.append((time.perf_counter() - t1) * 1000.0)

        pr_aucs.append(float(average_precision_score(y_te, scores)))
        q99 = float(np.quantile(scores[:len(x_te_b)], 0.99))
        q95 = float(np.quantile(scores[:len(x_te_b)], 0.95))
        rec_1pct.append(float(np.mean(scores[len(x_te_b):] > q99)))
        rec_5pct.append(float(np.mean(scores[len(x_te_b):] > q95)))

    return {
        "dataset": "benchmarks/datasets/lan_telemetry_sample.jsonl",
        "rows_total": len(rows),
        "hard_negatives_included": True,
        "pr_auc": summarize_ci(pr_aucs),
        "recall_at_1pct_fpr": summarize_ci(rec_1pct),
        "recall_at_5pct_fpr": summarize_ci(rec_5pct),
        "fit_ms": summarize_ci(fit_ms_list),
        "infer_ms": summarize_ci(inf_ms_list),
    }


def bench_dga_hard_negatives():
    ds_path = ROOT / "benchmarks/datasets/dga_domains_sample.csv"
    rows = list(csv.DictReader(ds_path.open("r", encoding="utf-8")))
    tp = fp = tn = fn = 0
    for r in rows:
        dom = r["domain"]
        y = int(r["label"])
        parts = dom.split(".")
        target = max(parts[:-1], key=len) if len(parts) > 1 else dom
        ent = shannon_entropy(target)
        alpha = [c for c in target if c.isalpha()]
        vratio = sum(1 for c in alpha if c in "aeiou") / max(1, len(alpha))
        pred = 1 if (ent >= 3.45 and vratio < 0.22 and len(target) >= 12) else 0
        if pred == 1 and y == 1:
            tp += 1
        elif pred == 1 and y == 0:
            fp += 1
        elif pred == 0 and y == 0:
            tn += 1
        else:
            fn += 1
    return {
        "dataset": "benchmarks/datasets/dga_domains_sample.csv",
        "total_domains": len(rows),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": round(tp / max(1, tp + fp), 4),
        "recall": round(tp / max(1, tp + fn), 4),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    seeds = 5 if args.quick else 20
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "quick" if args.quick else "full_20_seed",
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "cpu_count": os.cpu_count()},
        "merkle_rfc6962": bench_rfc6962_merkle((100, 1000) if args.quick else (100, 1000, 10000)),
        "conformal_multiseed": bench_conformal_multiseed(n_seeds=seeds),
        "realistic_lan_telemetry_iforest": bench_realistic_telemetry_multiseed(n_seeds=seeds),
        "dga_hard_negatives": bench_dga_hard_negatives(),
    }
    if not args.quick:
        (Path(__file__).resolve().parent / "RESULTS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
