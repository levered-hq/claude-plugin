#!/usr/bin/env python3
"""Derive every analyst-layer number a results report needs from one
`levered optimizations report-data <id> --json` pack. Stdlib only.

Usage:
    levered optimizations report-data <id> > pack.json
    python3 report_calcs.py pack.json [--since YYYY-MM-DD]

Sections printed: CONFIG (with a config hash for update-mode comparisons),
VALIDATION (holdout share by day, enrollment reconciliation, baseline-sanity
gate), MEASURED (published + windowed recomputes on the same estimand),
GUARDRAILS, MODELED, VARIANTS, OUTCOME MIX (with monthly translation),
FACTOR UTILITIES, INTERACTIONS (day-controlled F-test + full deviation
matrix). Every derived figure is labeled with its basis so the report writer
never has to re-derive one with ad hoc warehouse SQL.
"""

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict

NONE_KEYS = {"__none__"}


def fmt_pct(x, digits=2):
    return f"{'+' if x >= 0 else ''}{x * 100:.{digits}f}%"


def level_values(factor):
    """Factor levels as plain strings. The platform stores levels either as
    strings or as {id, value, previous_values} objects; variants and the cube
    carry the VALUE, so that is the canonical form throughout."""
    out = []
    for lv in factor.get("levels") or []:
        if isinstance(lv, dict) and "value" in lv:
            out.append(str(lv["value"]))
        else:
            out.append(str(lv))
    return out


def norm_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def two_sided_p(z):
    return 2.0 * (1.0 - norm_cdf(abs(z)))


def f_sf(f_stat, d1, d2):
    """Survival function of the F distribution via the regularized incomplete
    beta function (continued fraction; Numerical Recipes)."""
    if f_stat <= 0:
        return 1.0
    x = d2 / (d2 + d1 * f_stat)
    return betainc(d2 / 2.0, d1 / 2.0, x)


def betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * betacf(a, b, x) / a
    return 1.0 - (math.exp(lbeta + b * math.log(1.0 - x) + a * math.log(x)) * betacf(b, a, 1.0 - x) / b)


def betacf(a, b, x):
    MAXIT, EPS, FPMIN = 200, 3e-9, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        if abs(d * c - 1.0) < EPS:
            break
    return h


def solve(A, y):
    """Gaussian elimination with partial pivoting; A is n×n, y length n."""
    n = len(A)
    M = [row[:] + [y[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            M[col][col] += 1e-9  # ridge nudge for a singular design
        M[col], M[piv] = M[piv], M[col]
        for r in range(col + 1, n):
            f = M[r][col] / M[col][col]
            for c in range(col, n + 1):
                M[r][c] -= f * M[col][c]
    beta = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = M[r][n] - sum(M[r][c] * beta[c] for c in range(r + 1, n))
        beta[r] = s / M[r][r]
    return beta


def wls(groups, cols):
    """Weighted least squares on grouped data.

    groups: list of (xrow, n, mean, var) — var is the exact within-group
    variance. Returns (beta, rss, n_total) where rss includes the within-group
    sum of squares, so F-tests match a per-user regression exactly.
    """
    k = len(cols)
    XtX = [[0.0] * k for _ in range(k)]
    Xty = [0.0] * k
    for xrow, n, mean, _var in groups:
        for i in range(k):
            if xrow[i] == 0.0:
                continue
            Xty[i] += n * xrow[i] * mean
            for j in range(k):
                XtX[i][j] += n * xrow[i] * xrow[j]
    beta = solve(XtX, Xty)
    rss = 0.0
    n_total = 0
    for xrow, n, mean, var in groups:
        pred = sum(b * x for b, x in zip(beta, xrow))
        rss += n * (mean - pred) ** 2 + n * var
        n_total += n
    return beta, rss, n_total


def lift_with_ci(h_n, h_mean, h_sd, o_n, o_mean, o_sd):
    if h_n == 0 or o_n == 0 or h_mean == 0:
        return None
    diff = o_mean - h_mean
    se = math.sqrt(o_sd**2 / o_n + h_sd**2 / h_n) if o_n > 1 and h_n > 1 else float("nan")
    lift = diff / h_mean
    if not math.isfinite(se) or se == 0:
        return (lift, None, None, None)
    return (lift, (diff - 1.96 * se) / h_mean, (diff + 1.96 * se) / h_mean, two_sided_p(diff / se))


def mean_sd_from_sums(n, vsum, vsumsq):
    if n == 0:
        return 0.0, 0.0
    mean = vsum / n
    var = max(0.0, (vsumsq - vsum * vsum / n) / (n - 1)) if n > 1 else 0.0
    return mean, math.sqrt(var)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack")
    ap.add_argument("--since", help="Converged-window start (YYYY-MM-DD); auto-detected when omitted.")
    args = ap.parse_args()
    pack = json.load(open(args.pack))

    opt = pack.get("optimization", {})
    o = opt.get("optimization", opt)
    model_config = opt.get("model_config") or {}
    results = pack.get("results", {})
    hd = pack.get("holdout_daily", {})
    mix = pack.get("outcome_mix", {})
    guardrails = pack.get("guardrails", {})
    lift_hist = pack.get("policy_lift_history", {})

    for key in ("results", "holdout_daily", "outcome_mix", "guardrails", "policy_lift_history"):
        err = (pack.get(key) or {}).get("error") or (pack.get(key) or {}).get("warehouse_error")
        if err:
            print(f"!! surface '{key}' unavailable: {err}")

    # ── CONFIG ────────────────────────────────────────────────────────────
    factors = (model_config.get("design_factors") or [])
    reward_cfg = (model_config.get("reward") or {})
    outcomes = mix.get("outcomes") or [
        {"key": oc.get("key"), "weight": oc.get("weight")} for oc in (reward_cfg.get("outcomes") or [])
    ]
    weight_of = {oc["key"]: float(oc["weight"]) for oc in outcomes}
    if not weight_of:
        weight_of = {"__converted__": 1.0}
    config_fingerprint = {
        "factors": [(f.get("name"), sorted(level_values(f))) for f in factors],
        "outcomes": sorted((k, v) for k, v in weight_of.items()),
        "holdout": o.get("holdout_percentage"),
        "window": o.get("reward_conversion_window"),
        "excluded": o.get("excluded_combinations"),
        "reward_metric": o.get("reward_metric_id"),
    }
    config_hash = hashlib.sha256(json.dumps(config_fingerprint, sort_keys=True, default=str).encode()).hexdigest()[:12]

    print("== CONFIG ==")
    print(f"name: {o.get('name')}   status: {o.get('status')}   id: {o.get('id')}")
    for f in factors:
        print(f"factor {f.get('name')}: {', '.join(level_values(f))} (level 0 = baseline)")
    print(f"reward outcomes/weights: {weight_of}")
    print(f"conversion window: {o.get('reward_conversion_window')}   holdout: {o.get('holdout_percentage')}%")
    print(f"excluded combinations: {o.get('excluded_combinations')}")
    print(f"config_hash: {config_hash}  (compare with the notes file; a change re-runs full validation)")

    # ── Cube prep ─────────────────────────────────────────────────────────
    rows = mix.get("rows") or []
    days = sorted({r["day"] for r in rows})

    def arm_of(r):
        return "holdout" if r["in_holdout"] else "optimized"

    def value_of(outcome_key):
        return weight_of.get(outcome_key, 0.0)

    # ── VALIDATION ────────────────────────────────────────────────────────
    print("\n== VALIDATION ==")
    by_day_arm = defaultdict(int)
    for r in rows:
        by_day_arm[(r["day"], arm_of(r))] += r["users"]
    shares = []
    for d in days:
        h, op = by_day_arm[(d, "holdout")], by_day_arm[(d, "optimized")]
        tot = h + op
        share = h / tot if tot else 0.0
        shares.append(share)
        print(f"  {d}: holdout {h} / optimized {op}  ({share * 100:.1f}% holdout)")
    if shares:
        med = sorted(shares)[len(shares) // 2]
        drift = [d for d, s in zip(days, shares) if abs(s - med) > 0.05 and by_day_arm[(d, 'holdout')] + by_day_arm[(d, 'optimized')] > 200]
        print(f"holdout-share gate: {'FIRED — step change on ' + ', '.join(drift) + '; pooled lift may be biased (SKILL step 4a)' if drift else 'ok (stable)'}")

    primary = results.get("primary_metric_vs_holdout") or {}
    cube_users = defaultdict(int)
    for r in rows:
        cube_users[arm_of(r)] += r["users"]
    print(
        f"enrollment: published {primary.get('optimization_exposures')}/{primary.get('holdout_exposures')} "
        f"(optimized/holdout) vs cube {cube_users['optimized']}/{cube_users['holdout']} "
        "(small gaps = maturation edges; large gaps are a finding)"
    )

    # Baseline sanity (SKILL step 4c): model's baseline arm vs recent holdout mean.
    variants = results.get("variants") or []
    # Baseline = every factor at its index-0 level → variant number 1 by convention.
    baseline_v = next((v for v in variants if v.get("number") == 1), None)
    stats = results.get("stats") or {}
    recent_days = days[-3:]
    rh_n = sum(r["users"] for r in rows if arm_of(r) == "holdout" and r["day"] in recent_days)
    rh_v = sum(r["users"] * value_of(r["outcome_key"]) for r in rows if arm_of(r) == "holdout" and r["day"] in recent_days)
    if baseline_v and rh_n:
        bm = baseline_v.get("expected_reward_mean")
        hold_recent = rh_v / rh_n
        modeled_lift_abs = (stats.get("estimated_improvement_percent") or 0.0) / 100.0 * (bm or 1)
        gap = abs((bm or 0) - hold_recent)
        frac = gap / modeled_lift_abs if modeled_lift_abs else float("inf")
        verdict = "PASS (modeled figures may present normally)" if frac < 0.35 else "FAIL (stale-baseline caveat required; keep modeled out of Summary)"
        print(
            f"baseline sanity: model baseline arm {bm:.3f} vs recent-holdout mean {hold_recent:.3f} "
            f"(gap = {frac * 100:.0f}% of modeled lift) → {verdict}"
        )

    # ── MEASURED ──────────────────────────────────────────────────────────
    print("\n== MEASURED (per user vs randomized holdout) ==")
    if primary:
        ci = primary.get("lift_ci") or [None, None]
        print(
            f"published (quote this): {primary.get('metric_name')}  holdout {primary.get('holdout_rate'):.4g} "
            f"(n={primary.get('holdout_exposures')})  optimized {primary.get('optimization_rate'):.4g} "
            f"(n={primary.get('optimization_exposures')})  lift {fmt_pct((primary.get('lift_percent') or 0) / 100)} "
            f"[{fmt_pct((ci[0] or 0) / 100)}, {fmt_pct((ci[1] or 0) / 100)}]  p={primary.get('p_value'):.4g}"
        )

    # Windowed recomputes from holdout_daily's reward series (same estimand as published).
    reward_series = None
    for m in hd.get("metrics") or []:
        if m.get("key") == "reward":
            reward_series = m
    leader_share_by_day = {}
    ts = results.get("time_series") or []
    top_variant_key = None
    if variants:
        top_variant_key = max(variants, key=lambda v: v.get("weight") or 0).get("variant_key")
    for point in ts:
        vv = point.get("variants") or {}
        tot = sum(x.get("exposures", 0) for x in vv.values())
        lead = (vv.get(top_variant_key) or {}).get("exposures", 0)
        if tot:
            leader_share_by_day[point.get("date")] = lead / tot
    since = args.since
    if not since:
        for d in sorted(leader_share_by_day):
            if leader_share_by_day[d] >= 0.5:
                since = d
                break
    if reward_series:
        def pool(day_min=None):
            agg = {"holdout": [0, 0.0, 0.0], "levered": [0, 0.0, 0.0]}
            for drow in reward_series.get("daily") or []:
                if day_min and drow["date"] < day_min:
                    continue
                for arm in ("holdout", "levered"):
                    b = drow.get(arm) or {}
                    agg[arm][0] += b.get("exposures", 0)
                    agg[arm][1] += b.get("rewardsValueSum") or 0.0
                    agg[arm][2] += b.get("rewardsValueSumSq") or 0.0
            return agg

        for label, day_min in (("full window", None), (f"since {since} (converged allocation)", since)):
            if day_min is None and label != "full window":
                continue
            a = pool(day_min)
            hn, hs, hq = a["holdout"]
            on, os_, oq = a["levered"]
            hm, hsd = mean_sd_from_sums(hn, hs, hq)
            om, osd = mean_sd_from_sums(on, os_, oq)
            res = lift_with_ci(hn, hm, hsd, on, om, osd)
            if res:
                lift, lo, hi, p = res
                ci_txt = f" [{fmt_pct(lo)}, {fmt_pct(hi)}] p={p:.3g}" if lo is not None else ""
                print(f"{label}: holdout {hm:.4g} (n={hn})  optimized {om:.4g} (n={on})  lift {fmt_pct(lift)}{ci_txt}")
    if since:
        print(f"converged-window start used: {since} (leader >=50% of optimized traffic; override with --since)")

    # ── GUARDRAILS ────────────────────────────────────────────────────────
    print("\n== GUARDRAILS (quote as published) ==")
    for g in (guardrails.get("guardrails") or []):
        print(f"  {json.dumps(g, default=str)[:400]}")

    # ── MODELED ───────────────────────────────────────────────────────────
    print("\n== MODELED (label as model estimates; dashboard Model tab cards) ==")
    ii = stats.get("estimated_improvement_interval") or [None, None]
    bi = stats.get("best_vs_baseline_interval") or [None, None]
    if stats:
        print(f"Lift (now, policy): {fmt_pct((stats.get('estimated_improvement_percent') or 0) / 100)}  [{ii[0]:.2f}%, {ii[1]:.2f}%]")
        print(f"Lift (best variant, ceiling): {fmt_pct((stats.get('best_vs_baseline_percent') or 0) / 100)}  [{bi[0]:.2f}%, {bi[1]:.2f}%]")
        print(f"progress to best: {(stats.get('estimated_progress') or 0) * 100:.0f}%")
    for drow in (lift_hist.get("daily") or [])[-5:]:
        print(f"  lift-history {json.dumps(drow, default=str)[:200]}")

    # ── VARIANTS ──────────────────────────────────────────────────────────
    print("\n== VARIANTS (rates are lifetime per-exposure; not comparable to windowed lift) ==")
    holdout_frac = (o.get("holdout_percentage") or 0) / 100.0
    for v in sorted(variants, key=lambda x: -(x.get("expected_reward_mean") or 0)):
        share_opt = (v.get("weight") or 0) / (1 - holdout_frac) if holdout_frac < 1 else 0
        print(
            f"  #{v.get('number')}  {json.dumps(v.get('variant'))}  exposures={v.get('exposures')}  "
            f"rate={v.get('rate'):.4g}  E[r]={v.get('expected_reward_mean'):.4g} "
            f"[{v.get('expected_reward_lo'):.4g},{v.get('expected_reward_hi'):.4g}]  "
            f"P(best)={v.get('prob_best'):.3f}  traffic(opt)={share_opt * 100:.1f}%"
        )

    # ── OUTCOME MIX ───────────────────────────────────────────────────────
    print("\n== OUTCOME MIX (first in-window choice per user; cube basis) ==")

    def mix_table(day_min=None, label="full window"):
        per = {"optimized": defaultdict(int), "holdout": defaultdict(int)}
        for r in rows:
            if day_min and r["day"] < day_min:
                continue
            per[arm_of(r)][r["outcome_key"]] += r["users"]
        tot = {a: sum(per[a].values()) for a in per}
        if not tot["optimized"] or not tot["holdout"]:
            return
        print(f"[{label}]  optimized n={tot['optimized']}  holdout n={tot['holdout']}")
        keys = sorted(set(per["optimized"]) | set(per["holdout"]), key=lambda k: -weight_of.get(k, 0))
        for k in keys:
            po = per["optimized"][k] / tot["optimized"]
            ph = per["holdout"][k] / tot["holdout"]
            se = math.sqrt(po * (1 - po) / tot["optimized"] + ph * (1 - ph) / tot["holdout"])
            w = weight_of.get(k, 0)
            print(
                f"  {k:<22} weight={w:<6g} holdout {ph * 100:5.1f}%  optimized {po * 100:5.1f}%  "
                f"diff {'+' if po - ph >= 0 else ''}{(po - ph) * 100:.1f}pp (±{1.96 * se * 100:.1f}pp)"
            )

    mix_table()
    if since:
        mix_table(since, f"since {since}")
    full_days = days[:-1] if len(days) > 1 else days  # drop the partial last day
    recent = full_days[-7:]
    if recent:
        opt_recent = sum(by_day_arm[(d, "optimized")] for d in recent)
        per_day = opt_recent / len(recent)
        print(f"traffic: ~{per_day:.0f} optimized users/day over the last {len(recent)} full days → ~{per_day * 30:,.0f}/month (for the absolute translation)")

    # ── FACTOR UTILITIES (model estimates) ────────────────────────────────
    print("\n== FACTOR UTILITIES (model estimates: mean E[r] over other factors, vs level 0) ==")
    for imp in results.get("factor_importance") or []:
        print(f"  importance {imp.get('factor')}: {imp.get('mean'):.3f} (q1 {imp.get('q1'):.3f}, q3 {imp.get('q3'):.3f}, kind {imp.get('kind')})")
    fnames = [f.get("name") for f in factors]
    if variants and fnames:
        for f in factors:
            name, levels = f.get("name"), level_values(f)
            means = {}
            for lv in levels:
                vs = [v.get("expected_reward_mean") for v in variants if str((v.get("variant") or {}).get(name)) == lv]
                if vs:
                    means[lv] = sum(vs) / len(vs)
            if means and levels and levels[0] in means:
                base = means[levels[0]]
                for lv in levels:
                    if lv in means:
                        print(f"  {name}={lv:<20} {means[lv]:.4g}  ({fmt_pct((means[lv] - base) / base)} vs level 0)")

    # ── INTERACTIONS (cube basis, optimized arm, day-controlled) ──────────
    ia = results.get("interaction_importance") or {}
    if ia:
        print(f"\n== INTERACTIONS ==\nmodel interaction importance: mean {ia.get('mean'):.3f} (q1 {ia.get('q1'):.3f}, q3 {ia.get('q3'):.3f})")
    if len(fnames) >= 2 and rows:
        imp_sorted = sorted(results.get("factor_importance") or [], key=lambda x: -(x.get("mean") or 0))
        fa = imp_sorted[0]["factor"] if imp_sorted else fnames[0]
        fb = imp_sorted[1]["factor"] if len(imp_sorted) > 1 else fnames[1]
        la = next((level_values(f) for f in factors if f.get("name") == fa), [])
        lb = next((level_values(f) for f in factors if f.get("name") == fb), [])
        cells = defaultdict(lambda: defaultdict(int))  # (day, a, b) -> outcome -> users
        for r in rows:
            if r["in_holdout"]:
                continue
            try:
                variant = json.loads(r["variant"])
            except (json.JSONDecodeError, TypeError):
                continue
            a, b = str(variant.get(fa)), str(variant.get(fb))
            if a in la and b in lb:
                cells[(r["day"], a, b)][r["outcome_key"]] += r["users"]

        def cell_stats(counts):
            n = sum(counts.values())
            if n == 0:
                return 0, 0.0, 0.0
            mean = sum(c * value_of(k) for k, c in counts.items()) / n
            var = sum(c * (value_of(k) - mean) ** 2 for k, c in counts.items()) / (n - 1) if n > 1 else 0.0
            return n, mean, var

        cell_days = sorted({d for (d, _, _) in cells})
        cols = ["intercept"] + [f"{fa}={x}" for x in la[1:]] + [f"{fb}={x}" for x in lb[1:]] + [f"day={d}" for d in cell_days[1:]]
        int_cols = [f"{fa}={x}×{fb}={y}" for x in la[1:] for y in lb[1:]]

        def xrow(a, b, d, interact):
            row = [1.0]
            row += [1.0 if a == x else 0.0 for x in la[1:]]
            row += [1.0 if b == y else 0.0 for y in lb[1:]]
            row += [1.0 if d == dd else 0.0 for dd in cell_days[1:]]
            if interact:
                row += [1.0 if (a == x and b == y) else 0.0 for x in la[1:] for y in lb[1:]]
            return row

        g0, g1 = [], []
        for (d, a, b), counts in cells.items():
            n, mean, var = cell_stats(counts)
            if n == 0:
                continue
            g0.append((xrow(a, b, d, False), n, mean, var))
            g1.append((xrow(a, b, d, True), n, mean, var))
        beta0, rss0, n_tot = wls(g0, cols)
        _beta1, rss1, _ = wls(g1, cols + int_cols)
        d1 = len(int_cols)
        d2 = n_tot - (len(cols) + len(int_cols))
        if d1 > 0 and d2 > 0 and rss1 > 0:
            F = ((rss0 - rss1) / d1) / (rss1 / d2)
            p = f_sf(F, d1, d2)
            print(f"interaction test ({fa} × {fb}, day-controlled, optimized arm): F({d1},{d2}) = {F:.2f}, p = {p:.3g}")
        print(f"deviation matrix (observed − additive prediction, value units; z in parens; rows={fa}, cols={fb}):")
        header = "  " + " | ".join(f"{y:>14}" for y in lb)
        print(header)
        for x in la:
            line = []
            for y in lb:
                obs_n, obs_sum, obs_var_sum, pred_sum = 0, 0.0, 0.0, 0.0
                for (d, a, b), counts in cells.items():
                    if a != x or b != y:
                        continue
                    n, mean, var = cell_stats(counts)
                    pred = sum(bb * xx for bb, xx in zip(beta0, xrow(a, b, d, False)))
                    obs_n += n
                    obs_sum += n * mean
                    obs_var_sum += n * var
                    pred_sum += n * pred
                if obs_n == 0:
                    line.append(f"{'·':>14}")
                    continue
                dev = (obs_sum - pred_sum) / obs_n
                se = math.sqrt(obs_var_sum / obs_n / obs_n) if obs_n > 1 else float("nan")
                z = dev / se if se and math.isfinite(se) and se > 0 else float("nan")
                line.append(f"{dev:+7.2f} ({z:+.1f}z) n={obs_n}".rjust(14))
            print(f"{x:>16} " + " | ".join(line))
        print("(mask cells with small n in the report; |z|<2 rows are directional — see cross-effects checklist)")

    print("\nBases reminder: published/holdout_daily figures share the platform estimand (weight of first in-window matched")
    print("outcome per user); the cube's mix shares are user counts on the same attribution. Variant rates are per exposure.")


if __name__ == "__main__":
    sys.exit(main())
