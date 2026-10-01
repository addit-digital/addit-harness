---
name: telemetry-export
description: Build a summary page (data.json + an offline report.html) from the local addit-harness telemetry log, and optionally publish aggregated KPIs as a private Artifact on claude.ai. Run only when the user asks for it; it needs the telemetry_local option turned on earlier.
user-invocable: true
disable-model-invocation: true
argument-hint: "[--days N]"
---

# Telemetry export

Turns the local, metadata-only log (written only while `telemetry_local` is on) into a summary on this
machine. Nothing leaves the machine unless the user says yes in step 2.

1. Run the exporter, forwarding any `--days N` the user gave, then print both output paths it prints
   (`data.json` and `report.html`, in one `export/<timestamp>/` folder under the log):

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/telemetry-export/scripts/export.py" --root "${CLAUDE_PLUGIN_DATA}/telemetry"
   ```

   If the log folder does not exist or is empty, the report says so ("n/a" everywhere); tell the user to
   turn on `telemetry_local` in `/config` and use the plugin for a while. Tell them `report.html` opens
   offline in any browser.

2. Ask exactly, and wait for the answer:

   > Publish the aggregated KPIs (no per-session rows, ids or hashes) as a private Artifact on claude.ai? This uploads them to Anthropic's hosted service under your account. yes/no

3. Only after an explicit "yes" in this invocation:
   - Load `artifact-design` as the Artifact tool requires, then run the same command with
     `--artifact --out <the export/<timestamp> folder from step 1>`. It writes `artifact.html` there.
   - Publish that file unmodified with the Artifact tool, `icon: "chart"`.
   - If the Artifact tool is unavailable (API-key login, Bedrock, Vertex, zero-data-retention), print the
     local path of `artifact.html` and stop. Never use any other upload route.

A "yes" applies to this invocation only; never treat it as standing consent. On "no" or no answer, stop
after step 1.
