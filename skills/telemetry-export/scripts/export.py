#!/usr/bin/env python3
"""addit-harness telemetry export: ledger -> data.json + offline report.html. Stdlib only, no network.

Usage: export.py --root DIR [--days 30] [--out DIR] [--artifact]
Every ledger line is re-validated with validate() from hooks/telemetry.py. --artifact writes
artifact.html instead: aggregated KPIs only (no per-session rows, ids or hashes). An
uncomputable KPI is {status: "na", reason}; it never fails the export.
"""
import argparse
import calendar
import hashlib
import importlib.util
import json
import os
import statistics
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
PLUGIN = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(SKILL))
TIERS = {"light": 0, "standard": 1, "deep": 2}
ALWAYS_ON = ("session_start", "include")


def _load_telemetry():
    spec = importlib.util.spec_from_file_location("addit_telemetry", os.path.join(PLUGIN, "hooks", "telemetry.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tel = _load_telemetry()
validate = tel.validate


def epoch(s):
    try:
        return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")) + int(s[20:23]) / 1000.0
    except (ValueError, OverflowError):
        return 0.0


def when(rec):
    return rec.get("time") or rec.get("start") or ""


def pct(part, whole):
    return round(100.0 * part / whole, 1) if whole else None


def kpi(value, n, unit, detail=None, reason="no data in window"):
    if value is None or not n:
        return {"value": None, "n": 0, "unit": unit, "status": "na", "reason": reason}
    out = {"value": value, "n": n, "unit": unit, "status": "ok", "reason": ""}
    if detail is not None:
        out["detail"] = detail
    return out


def read_ledger(root, days, now):
    """{session id: {day, recs}} for the day folders inside the window."""
    cutoff = time.strftime("%Y/%m/%d", time.gmtime(now - days * 86400))
    base, sessions, invalid = os.path.join(root, "sessions"), {}, 0
    for dirpath, _, files in sorted(os.walk(base)):
        day = "/".join(os.path.relpath(dirpath, base).split(os.sep))
        if len(day) != 10 or day < cutoff:
            continue
        for name in sorted(files):
            if not name.endswith(".jsonl"):
                continue
            try:
                with open(os.path.join(dirpath, name), "rb") as fh:
                    lines = fh.read(20 * 1024 * 1024).splitlines()
            except OSError:
                continue
            for ln in lines:
                try:
                    clean, _, _ = validate(json.loads(ln))
                except ValueError:
                    clean = None
                if clean is None:
                    invalid += 1
                    continue
                entry = sessions.setdefault(clean["session.id"], {"day": day.replace("/", "-"), "recs": []})
                entry["recs"].append(clean)
    for entry in sessions.values():
        entry["recs"].sort(key=when)
    return sessions, invalid


class Acc:
    def __init__(self):
        self.versions, self.skills, self.gates, self.rules = set(), Counter(), Counter(), Counter()
        self.agents_used, self.spans, self.launches, self.fc = Counter(), [], [], []
        self.passed, self.approved, self.docs, self.states, self.fe_spans = set(), set(), defaultdict(list), Counter(), []
        self.tools_failed = Counter()


def summarize(sid, entry, acc):
    """One per_session row; an agent start with no stop counts as `interrupted`."""
    recs = entry["recs"]
    row = {"sid_hash": hashlib.sha256(sid.encode()).hexdigest()[:12], "day": entry["day"], "duration_s": None,
           "end_reason": "unknown", "setup_state": None, "agents": Counter(), "outcomes": Counter(), "workflows": [],
           "doc_writes": 0, "fc1_violations": 0, "always_on_bytes": 0}
    started, closed, ends = {}, set(), []
    for r in recs:
        name = r["name"]
        acc.versions.add(r["service.version"])
        if name == "session":
            row["end_reason"] = r["addit.session.end_reason"]
            row["duration_s"] = round(epoch(r["end"]) - epoch(r["start"]), 1)
        elif name == "addit.setup.state":
            row["setup_state"] = r["addit.setup.state"]
        elif name == "addit.agent.start":
            started[r["gen_ai.agent.id"]] = r
            row["agents"][r["gen_ai.agent.name"]] += 1
            acc.agents_used[r["gen_ai.agent.name"]] += 1
        elif name.startswith("invoke_agent "):
            closed.add(r["gen_ai.agent.id"])
            row["outcomes"][r["addit.outcome"]] += 1
            acc.spans.append((r["gen_ai.agent.name"], r["addit.outcome"]))
            if r["gen_ai.agent.name"] == "frontend-developer":
                acc.fe_spans.append((sid, r["start"], r["end"]))
        elif name.startswith("execute_tool Skill "):
            acc.skills[r["addit.skill.name"]] += 1
        elif name.startswith("invoke_workflow "):
            wf, tier, slug = r["gen_ai.workflow.name"], r.get("addit.devflow.tier"), r.get("addit.devflow.slug_hash")
            row["workflows"].append({"name": wf, "tier": tier})
            acc.launches.append((r["start"], wf, tier, slug))
        elif name == "addit.gate.verdict":
            acc.gates[(r["addit.gate.name"], r["addit.gate.verdict"])] += 1
            if r["addit.gate.name"] == "plan_approval" and r["addit.gate.verdict"] == "pass" and r.get("addit.devflow.slug_hash"):
                acc.passed.add(r["addit.devflow.slug_hash"])
        elif name == "addit.rule.loaded":
            acc.rules[r["addit.rule.name"]] += 1
            if r["addit.rule.load_reason"] in ALWAYS_ON:
                row["always_on_bytes"] += r["addit.rule.bytes"]
        elif name == "addit.doc.write":
            row["doc_writes"] += 1
            acc.docs[r["addit.doc.path_hash"]].append(r)
            if r.get("addit.doc.approved") and r.get("addit.devflow.slug_hash"):
                acc.approved.add(r["addit.devflow.slug_hash"])
        elif name == "addit.fc.violation":
            row["fc1_violations"] += 1
            acc.fc.append((sid, r["time"], r["gen_ai.agent.name"]))
        elif name == "addit.tool.failure":
            acc.tools_failed[r["gen_ai.tool.name"]] += 1
        ends.append(epoch(when(r)))
    if row["duration_s"] is None and ends:
        first = [epoch(when(r)) for r in recs if r["name"] == "addit.session.start"] or ends[:1]
        row["duration_s"] = round(max(0.0, max(ends) - min(first)), 1)
    for aid, r in started.items():
        if aid not in closed:
            row["outcomes"]["interrupted"] += 1
            acc.spans.append((r["gen_ai.agent.name"], "interrupted"))
    if row["setup_state"]:
        acc.states[row["setup_state"]] += 1
    for k in ("agents", "outcomes"):
        row[k] = dict(sorted(row[k].items()))
    return row


def compute_kpis(rows, acc, contract):
    ex, k = contract["export"], {}
    agents, skills = sorted(tel._stems("agents")), sorted(tel._skill_dirs() | tel._stems("commands"))
    used = [a for a in agents if acc.agents_used[a]]
    k["AR1"] = kpi(pct(len(used), len(agents)), len(agents), "% of shipped agents used", {
        "used": dict(sorted(acc.agents_used.items())), "never_used": [a for a in agents if a not in used],
        "skills_used": dict(sorted(acc.skills.items())), "skills_never_used": [s for s in skills if not acc.skills[s]]})
    outcomes = Counter(o for _, o in acc.spans)
    k["AR2"] = kpi(pct(outcomes["completed"], len(acc.spans)), len(acc.spans), "% completed", {
        "outcomes": dict(sorted(outcomes.items())), "failed_launches": dict(sorted(acc.tools_failed.items())),
        "by_agent": {a: dict(sorted(Counter(o for n, o in acc.spans if n == a).items())) for a in sorted({n for n, _ in acc.spans})}})
    comp = set(contract["competitors"])
    rev = [n for n, _ in acc.spans if n in comp or n == "code-reviewer"]
    k["AR3"] = kpi(pct(sum(n in comp for n in rev), len(rev)), len(rev), "% of reviews by a competitor")
    ao = [r["always_on_bytes"] for r in rows if r["always_on_bytes"]]
    k["CE3"] = kpi(int(statistics.median(ao)) if ao else None, len(ao), "median always-on bytes per session",
                   {"per_session": sorted(ao)})
    n_state = sum(acc.states.values())
    k["MH1"] = kpi(pct(acc.states["ok"], n_state), n_state, "% of sessions in sync", dict(sorted(acc.states.items())))
    rules = sorted(tel._stems("rules"))
    k["MH2"] = kpi(pct(sum(1 for r in rules if acc.rules[r]), len(rules)), len(rules), "% of shipped rules loaded",
                   {r: acc.rules[r] for r in rules})
    k["LE1"], k["DF1"], k["LE3"] = devflow_kpis(acc)
    k["DOC1"], k["DOC2"], k["DOC3"], k["SQ1"] = doc_kpis(acc, contract["doc_ceilings"])
    fe = 0
    for sid, a, b in acc.fe_spans:
        fe += not any(s == sid and a <= t <= b and ag == "frontend-developer" for s, t, ag in acc.fc)
    by_agent = Counter(ag for _, _, ag in acc.fc)
    k["FC-1"] = kpi(pct(fe, len(acc.fe_spans)), len(acc.fe_spans), "% of frontend-developer spans with no FC-1 line-cap hit",
                    {"violations_by_agent": dict(sorted(by_agent.items()))})
    for kid, reason in ex["na"].items():
        k[kid] = kpi(None, 0, "", reason=reason)
    if not rows:
        return {kid: kpi(None, 0, k[kid]["unit"], reason=k[kid]["reason"] if kid in ex["na"] else "no sessions in window") for kid in sorted(k)}
    return {kid: k[kid] for kid in sorted(k)}


def devflow_kpis(acc):
    designed, implemented = defaultdict(list), set()
    mix = Counter()
    for _, wf, tier, slug in sorted(acc.launches, key=lambda x: x[0]):
        if tier:
            mix[tier] += 1
        if slug and wf == "dev-flow-design":
            designed[slug].append(tier)
        elif slug and wf == "dev-flow-implement":
            implemented.add(slug)
    approved = {s for s in designed if s in acc.approved or s in acc.passed}
    final = {s: (t[-1] or "other") for s, t in designed.items()}
    funnel = {}
    for s, tier in final.items():
        row = funnel.setdefault(tier, {"design_launched": 0, "plan_approved": 0, "implement_launched": 0})
        row["design_launched"] += 1
        row["plan_approved"] += s in approved
        row["implement_launched"] += s in implemented
    le1 = kpi(pct(len(implemented & set(designed)), len(designed)), len(designed), "% of designed work items implemented",
              {"funnel_by_tier": dict(sorted(funnel.items()))})
    esc = sum(1 for t in designed.values() if any(TIERS.get(b, -1) > TIERS.get(a, 99) for a, b in zip(t, t[1:])))
    df1 = kpi(pct(esc, len(designed)), len(designed), "% of work items re-designed at a higher tier", {"tier_mix": dict(sorted(mix.items()))})
    impl = [s for _, wf, _, s in acc.launches if wf == "dev-flow-implement" and s]
    bypassed = sum(1 for s in impl if s not in acc.passed)
    gates = defaultdict(dict)
    for (g, v), n in sorted(acc.gates.items()):
        gates[g][v] = n
    if bypassed:
        gates.setdefault("plan_approval", {})["bypassed"] = gates["plan_approval"].get("bypassed", 0) + bypassed
    le3 = kpi(pct(len(impl) - bypassed, len(impl)), len(impl), "% of implement launches with a plan_approval pass", {"gates": dict(gates)})
    return le1, df1, le3


def doc_kpis(acc, ceilings):
    last = {h: w[-1] for h, w in acc.docs.items()}
    over, kinds = 0, {}
    for w in last.values():
        cap = ceilings.get(w["addit.doc.kind"], {}).get("deep")
        if cap:
            row = kinds.setdefault(w["addit.doc.kind"], {"within": 0, "over": 0, "max_lines": 0, "ceiling": cap})
            row["over" if w["addit.doc.lines"] > cap else "within"] += 1
            row["max_lines"] = max(row["max_lines"], w["addit.doc.lines"])
            over += w["addit.doc.lines"] > cap
    n1 = sum(r["within"] + r["over"] for r in kinds.values())
    doc1 = kpi(pct(n1 - over, n1), n1, "% of plans/solutions within the deep ceiling", {"by_kind": dict(sorted(kinds.items()))})
    growth = [w[-1]["addit.doc.lines"] - w[0]["addit.doc.lines"] for w in acc.docs.values() if len(w) > 1]
    doc2 = kpi(statistics.median(growth) if growth else None, len(growth), "median lines added per revised doc")
    later = [r for w in acc.docs.values() for r in w[1:]]
    doc3 = kpi(pct(sum(r["addit.doc.op"] == "edit" for r in later), len(later)), len(later), "% of revisions made as in-place edits")
    sol = [w for w in last.values() if w["addit.doc.kind"] == "solution" and "addit.doc.has_candidates" in w]
    ok = sum(1 for w in sol if w["addit.doc.has_candidates"] and (w.get("addit.doc.candidates_before_owner") or not w.get("addit.doc.has_owner_idea")))
    labels = [w.get("addit.doc.claim_labels", 0) for w in sol]
    sq1 = kpi(pct(ok, len(sol)), len(sol), "% of solution docs with candidates before the owner idea",
              {"claim_labels_median": statistics.median(labels) if labels else 0})
    return doc1, doc2, doc3, sq1


def build(root, days, now):
    contract = tel.contract()
    sessions, invalid = read_ledger(root, days, now)
    acc = Acc()
    rows = [summarize(sid, e, acc) for sid, e in sorted(sessions.items(), key=lambda kv: (kv[1]["day"], kv[0]))]
    return {"schema_version": contract["schema_version"], "generated_at": tel.iso(now),
            "window": {"from": time.strftime("%Y-%m-%d", time.gmtime(now - days * 86400)), "to": time.strftime("%Y-%m-%d", time.gmtime(now)), "days": days},
            "plugin_versions": sorted(acc.versions), "sessions_n": len(rows), "invalid_lines": invalid, "kpis": compute_kpis(rows, acc, contract), "per_session": rows}


def aggregated(data):
    ce3 = dict(data["kpis"]["CE3"], detail=None)
    return {k: v for k, v in dict(data, kpis=dict(data["kpis"], CE3=ce3)).items() if k != "per_session"}


def render(data, mode):
    with open(os.path.join(SKILL, "assets", "report.html"), encoding="utf-8") as fh:
        page = fh.read()
    blob = json.dumps(dict(data, mode=mode), separators=(",", ":"))
    blob = blob.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    if page.count("__DATA__") != 1:
        raise ValueError("template must contain __DATA__ exactly once")
    return page.replace("__DATA__", blob)


def write(path, text):
    os.makedirs(os.path.dirname(path), 0o700, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--days", type=int, default=tel.contract()["export"]["window_days"])
    ap.add_argument("--out")
    ap.add_argument("--artifact", action="store_true")
    a = ap.parse_args(argv)
    now = time.time()
    out = a.out or os.path.join(a.root, "export", time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now)))
    data = build(a.root, max(1, a.days), now)
    if a.artifact:
        page = os.path.join(out, "artifact.html")
        write(page, render(aggregated(data), "artifact"))
        print(page)
        return 0
    write(os.path.join(out, "data.json"), json.dumps(data, indent=1) + "\n")
    write(os.path.join(out, "report.html"), render(data, "local"))
    print(os.path.join(out, "data.json"))
    print(os.path.join(out, "report.html"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
