#!/usr/bin/env python3
"""
Scrape PDC tour-card holders' last-10-matches form data from dartsorakel.com
and build a self-contained HTML dashboard.

Pipeline (single-shot, ~5-7 min total):
1. Fetch 2026 tour-card holders (filtered leaderboard).
2. Fetch each player's full match history (organisation=All — includes PL,
   TV majors, ET, World Series, PT, but excludes World Grand Prix).
3. Identify non-tour-card opponents in those last-10 windows; fetch them
   too so we can derive opponent average per match.
4. Pull season-wide checkout %, total 180s, and first-9 average.
5. Compute per-player summary (avg L10, trend L5−P5, std dev, win rate,
   strength-of-schedule, performance vs opponent).
6. Render docs/index.html with embedded data + write CSVs to docs/data/.

No external Python dependencies — stdlib only.
"""
from __future__ import annotations
import csv
import datetime as dt
import json
import os
import statistics
import sys
import time
import urllib.request
from urllib.error import HTTPError, URLError

# --- Config ---
TOUR_CARD_YEAR = 2026
SLEEP_BETWEEN_REQUESTS = 0.15  # polite throttle
RAW_BASE = "https://dartsorakel.com"
PLAYERS_URL = f"{RAW_BASE}/api/stats/player?tourCardYear={TOUR_CARD_YEAR}"
MATCHES_URL = f"{RAW_BASE}/api/player/matches/{{}}?organisation=All&organStat=All"
LEADER_URL  = f"{RAW_BASE}/api/stats/player?tourCardYear={TOUR_CARD_YEAR}&rankKey={{}}"
HEADERS = {
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{RAW_BASE}/stats/player",
    "User-Agent": "Mozilla/5.0 (compatible; darts-form-tracker/1.0)",
}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO_ROOT, "docs")
DATA = os.path.join(DOCS, "data")
os.makedirs(DATA, exist_ok=True)

# --- HTTP helper ---
def get(url: str, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def is_grand_prix(r: dict) -> bool:
    name = (r.get("tournament_name") or "").lower()
    cat = r.get("pdc_category") or r.get("category") or ""
    return "grand prix" in name or cat == "WGP"


# --- Pipeline ---
def main():
    t0 = time.time()
    print(f"[{dt.datetime.utcnow().isoformat(timespec='seconds')}Z] starting scrape")

    # 1. Tour-card holders
    players = get(PLAYERS_URL)["data"]
    tc_keys = {p["player_key"] for p in players}
    print(f"  tour-card holders: {len(players)}")

    # 2. Each TC player's full match history
    raw_matches: dict[int, list[dict]] = {}
    for i, p in enumerate(players, 1):
        try:
            raw_matches[p["player_key"]] = get(MATCHES_URL.format(p["player_key"])).get("data", [])
        except Exception as e:
            print(f"  ! {p['player_name']}: {e}")
            raw_matches[p["player_key"]] = []
        if i % 25 == 0:
            print(f"    {i}/{len(players)} players ({time.time()-t0:.0f}s)")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # 3. Non-TC opponents seen in last-10 windows
    needed_opps: set[int] = set()
    for p in players:
        rows = raw_matches.get(p["player_key"], [])
        clean = [r for r in rows if not r.get("is_bye") and not is_grand_prix(r)]
        for r in clean[:10]:
            opk = r["loser_key"] if r["result"] == "Won" else r["winner_key"]
            if opk not in tc_keys:
                needed_opps.add(opk)
    print(f"  non-TC opponents to scrape: {len(needed_opps)}")
    for i, k in enumerate(sorted(needed_opps), 1):
        try:
            raw_matches[k] = get(MATCHES_URL.format(k)).get("data", [])
        except Exception as e:
            print(f"  ! opponent {k}: {e}")
            raw_matches[k] = []
        if i % 25 == 0:
            print(f"    {i}/{len(needed_opps)} opponents ({time.time()-t0:.0f}s)")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # 4. Season-wide stats by rankKey
    EXTRA_KEYS = {"checkout_pct": 1053, "total_180s": 26, "first9_avg": 1029}
    extra_lookups: dict[str, dict[int, float | None]] = {}
    for label, rk in EXTRA_KEYS.items():
        try:
            data = get(LEADER_URL.format(rk))["data"]
        except Exception as e:
            print(f"  ! season stat {label}: {e}")
            data = []
        out = {}
        for r in data:
            v = r.get("stat")
            if isinstance(v, str) and v.endswith("%"):
                try: v = float(v[:-1])
                except: v = None
            elif isinstance(v, str):
                try: v = float(v)
                except: pass
            out[r["player_key"]] = v
        extra_lookups[label] = out
        time.sleep(SLEEP_BETWEEN_REQUESTS)
    print(f"  pulled extra season stats: {list(EXTRA_KEYS)}")

    # 5. Compute summary + long matches + opp_avg join
    def find_opp_avg(my_match: dict, opp_key: int) -> float | None:
        for r in raw_matches.get(opp_key, []):
            if r.get("event_key") == my_match.get("event_key") and r.get("round") == my_match.get("round"):
                if {r.get("winner_key"), r.get("loser_key")} == {my_match.get("winner_key"), my_match.get("loser_key")}:
                    v = r.get("stat")
                    if v in (None, "", "-"): return None
                    try: return float(v)
                    except: return None
        return None

    summary = []
    matches_long = []
    full_for_artifact: dict[str, list[dict]] = {}

    for p in players:
        rows = raw_matches.get(p["player_key"], [])
        clean = [r for r in rows if not r.get("is_bye") and not is_grand_prix(r)]
        last10 = clean[:10]
        avgs = [float(r["stat"]) for r in last10 if r.get("stat") not in (None, "", "-")]
        opp_avgs = []
        perfs = []
        for r in last10:
            opk = r["loser_key"] if r["result"] == "Won" else r["winner_key"]
            oa = find_opp_avg(r, opk)
            if oa is not None: opp_avgs.append(oa)
            try:
                ma = float(r["stat"])
                if oa is not None: perfs.append(ma - oa)
            except (TypeError, ValueError):
                pass

        if avgs:
            recent_5, prior_5 = avgs[:5], avgs[5:10]
            rec = sum(recent_5)/len(recent_5) if recent_5 else None
            pri = sum(prior_5)/len(prior_5)  if prior_5  else None
            trend = round(rec - pri, 2) if rec is not None and pri is not None else None
            wins = sum(1 for r in last10 if r.get("result") == "Won")
            last_dt = (last10[0].get("match_date") or "")[:10]
        else:
            rec = pri = trend = wins = last_dt = None

        summary.append({
            "player_key": p["player_key"],
            "player_name": p["player_name"],
            "country": p.get("country"),
            "season_avg": float(p["stat"]) if p.get("stat") else None,
            "season_rank": p.get("rank"),
            "matches_in_window": len(last10),
            "avg_last10": round(sum(avgs)/len(avgs), 2) if avgs else None,
            "stdev_last10": round(statistics.pstdev(avgs), 2) if len(avgs) > 1 else None,
            "best_last10": round(max(avgs), 2) if avgs else None,
            "worst_last10": round(min(avgs), 2) if avgs else None,
            "avg_last5":  round(rec, 2) if rec is not None else None,
            "avg_prev5":  round(pri, 2) if pri is not None else None,
            "trend": trend,
            "wins_last10": wins,
            "win_rate_last10": round(wins/len(last10), 3) if last10 else None,
            "last_match_date": last_dt,
            "mean_opp_avg":     round(sum(opp_avgs)/len(opp_avgs), 2) if opp_avgs else None,
            "mean_perf_vs_opp": round(sum(perfs)/len(perfs), 2)         if perfs    else None,
            "sos_n":            len(opp_avgs),
            "checkout_pct": extra_lookups.get("checkout_pct", {}).get(p["player_key"]),
            "total_180s":   extra_lookups.get("total_180s", {}).get(p["player_key"]),
            "first9_avg":   extra_lookups.get("first9_avg", {}).get(p["player_key"]),
            "profile_url":  p.get("player_profile_url"),
        })

        for idx, r in enumerate(last10, 1):
            opk = r["loser_key"] if r["result"] == "Won" else r["winner_key"]
            oa = find_opp_avg(r, opk)
            ma = float(r["stat"]) if r.get("stat") not in (None, "", "-") else None
            matches_long.append({
                "player_key": p["player_key"],
                "player_name": p["player_name"],
                "match_idx": idx,
                "match_date": (r.get("match_date") or "")[:10],
                "tournament": r.get("tournament_name"),
                "category": r.get("pdc_category") or r.get("category"),
                "round": r.get("round"),
                "result": r.get("result"),
                "score": r.get("score"),
                "opponent": (r.get("loser_name") if r.get("result") == "Won" else r.get("winner_name")),
                "opponent_key": opk,
                "three_dart_average": ma,
                "opponent_avg": round(oa, 2) if oa is not None else None,
                "perf_vs_opp": round(ma - oa, 2) if (ma is not None and oa is not None) else None,
                "points_scored": r.get("stat1"),
                "darts_thrown": r.get("stat2"),
            })

        # For the H2H panel: trim last 50 matches per player
        full_for_artifact[str(p["player_key"])] = []
        for r in clean[:50]:
            opk = r["loser_key"] if r["result"] == "Won" else r["winner_key"]
            oa = find_opp_avg(r, opk)
            full_for_artifact[str(p["player_key"])].append({
                "d": (r.get("match_date") or "")[:10],
                "t": r.get("tournament_name"),
                "c": r.get("pdc_category") or r.get("category"),
                "r": r.get("round"),
                "w": 1 if r.get("result") == "Won" else 0,
                "s": r.get("score"),
                "op": r.get("loser_name") if r.get("result") == "Won" else r.get("winner_name"),
                "opk": opk,
                "a": float(r["stat"]) if r.get("stat") not in (None, "", "-") else None,
                "oa": round(oa, 2) if oa is not None else None,
            })

    # 6. Write CSVs
    fetched_at = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with open(os.path.join(DATA, "tourcard_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)
    with open(os.path.join(DATA, "tourcard_matches_long.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(matches_long[0].keys())); w.writeheader(); w.writerows(matches_long)

    payload = {
        "fetched_at_utc": fetched_at,
        "filter": f"{TOUR_CARD_YEAR} PDC tour-card holders · Last 10 matches across all event types except World Grand Prix",
        "summary": summary,
        "matches": matches_long,
        "full": full_for_artifact,
    }

    # 7. Render dashboard HTML
    from build_html import render_html
    html = render_html(payload)
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nDONE in {time.time()-t0:.0f}s")
    print(f"  summary: {len(summary)} players")
    print(f"  matches: {len(matches_long)} rows")
    print(f"  HTML: docs/index.html ({os.path.getsize(os.path.join(DOCS,'index.html')):,} bytes)")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
