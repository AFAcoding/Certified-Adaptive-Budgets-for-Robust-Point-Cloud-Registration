"""Live GPU timing of CAB (PROTOCOL.md, addendum C), on the bundle written by export_bundle.py.

For every test set and estimator in the bundle: on each pair, the standard estimator on the full budget and the two
certified CAB configurations (without the gate: "v2"; the final method: "v3"), timed in one process with the device
synchronised around every run, the order of the runs rotated from pair to pair, after untimed warm-up runs. Every run
includes everything the configuration needs (ordering, gate signals and prediction, controller). Writes one JSON with
per-pair times, outcomes and stopping stages, and prints, per set: mean times, speed-ups, recall, and the agreement
of the stopping decisions and full-budget outcomes with the CPU logs.

Usage (Colab, GPU runtime): python run_gpu_timing.py --bundle /content/drive/MyDrive/gpu_bundle --out results_gpu.json
"""

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import torch

import cab_gpu as G


def model_arrays(models, key):
    pre = key + "/"
    return {k[len(pre):]: models[k] for k in models.files if k.startswith(pre)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default=".")
    ap.add_argument("--out", default="results_gpu.json")
    ap.add_argument("--sets", default=None, help="comma-separated set codes (default: every set in the bundle)")
    ap.add_argument("--estimators", default="sc2,turbo,mac")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--warmup", type=int, default=5)
    ap.add_argument("--limit", type=int, default=None, help="time only the first pairs of each set (smoke test)")
    args = ap.parse_args()
    bundle = Path(args.bundle)
    cfg = json.loads((bundle / "config.json").read_text())
    models = np.load(bundle / "models.npz")
    device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")
    if device.type == "cpu" and args.device != "cpu":
        print("WARNING: no GPU available, timing on the CPU")
    torch.backends.cuda.matmul.allow_tf32 = False  # full single precision, as on the CPU
    torch.backends.cudnn.allow_tf32 = False
    out = {"device": torch.cuda.get_device_name(device) if device.type == "cuda" else platform.processor(),
           "torch": torch.__version__, "cuda": torch.version.cuda, "python": platform.python_version(),
           "started": time.strftime("%Y-%m-%d %H:%M:%S"), "rows": []}
    print(f"device: {out['device']}, torch {out['torch']}, CUDA {out['cuda']}")
    sets = args.sets.split(",") if args.sets else list(cfg["sets"])
    for code in sets:
        entry = cfg["sets"][code]
        data = np.load(bundle / f"data_{code}.npz")
        n = len(data["n_all"]) if args.limit is None else min(args.limit, len(data["n_all"]))
        for est in [e for e in args.estimators.split(",") if e in entry["estimators"]]:
            e = entry["estimators"][est]
            fn, kw = G.ESTIMATORS[est], e["kw"]
            ctrls = {}
            for v, c in e["configs"].items():
                arrays = {"clf": model_arrays(models, c["clf"]["key"]),
                          "gate": model_arrays(models, c["gate"]["key"]) if c.get("gate") else None}
                ctrls[v] = G.Controller(c, arrays, entry["compat_thr"])

            def run(job, P, Q, ratio):
                if job == "full":
                    return fn(P, Q, **kw)[0], None
                return ctrls[job].run(fn, kw, P, Q, ratio, entry["inlier"])

            def load(i):
                k = int(data["n_all"][i])
                P = torch.as_tensor(data["P"][i, :k], dtype=torch.float64, device=device)
                Q = torch.as_tensor(data["Q"][i, :k], dtype=torch.float64, device=device)
                return P, Q, data["ratio"][i, :k]

            for i in range(min(args.warmup, n)):  # untimed warm-up (kernels, allocator, libraries)
                P, Q, ratio = load(i)
                for job in ("full", "v2", "v3"):
                    run(job, P, Q, ratio)
            t_set = time.time()
            rows = []
            for i in range(n):
                P, Q, ratio = load(i)
                jobs = ["full", "v2", "v3"]
                jobs = jobs[i % 3:] + jobs[:i % 3]
                row = {"set": code, "est": est, "pair_id": str(data["pair_id"][i]), "scene": str(data["scene"][i]),
                       "run_order": jobs}
                for job in jobs:
                    G.sync(device)
                    t0 = time.perf_counter()
                    T, stop = run(job, P, Q, ratio)
                    G.sync(device)
                    secs = time.perf_counter() - t0
                    ok = G.success(T.cpu().numpy(), data["T_gt"][i], entry["rot_deg"], entry["trans_m"])
                    row[job] = {"s": secs, "ok": ok, "stop": stop}
                rows.append(row)
            out["rows"] += rows
            ref = e["reference"]
            tf = np.array([r["full"]["s"] for r in rows])
            line = f"{code:4s} {est:5s} n={n}: full {1e3 * tf.mean():7.1f} ms RR {100 * np.mean([r['full']['ok'] for r in rows]):5.1f}%"
            for v in ("v2", "v3"):
                ta = np.array([r[v]["s"] for r in rows])
                agree = np.mean([r[v]["stop"] == s for r, s in zip(rows, ref[v]["offline_stop"][:n])])
                line += (f" | {v}: {1e3 * ta.mean():7.1f} ms {tf.mean() / ta.mean():.2f}x "
                         f"RR {100 * np.mean([r[v]['ok'] for r in rows]):5.1f}% stops as CPU {100 * agree:.0f}%")
            full_agree = np.mean([r["full"]["ok"] == o for r, o in zip(rows, ref["full_ok"][:n])])
            print(line + f" | full outcome as CPU {100 * full_agree:.0f}% ({time.time() - t_set:.0f}s)", flush=True)
            Path(args.out).write_text(json.dumps(out))  # saved after every set and estimator
    out["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    Path(args.out).write_text(json.dumps(out))
    print(f"results written to {args.out}")


if __name__ == "__main__":
    main()
