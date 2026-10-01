// The progress-view log contract (docs: solution-tui.md, "A, log contract"). mock-run applies it to every
// scenario run, so a workflow that drops a line, mis-formats one, or leaks request text fails all of them.
// Lines are metadata only: tier, round counts, blocking counts, gate verdicts, halt ids.
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const { enums } = JSON.parse(readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), '../../hooks/telemetry-contract.json'), 'utf8'))
const alt = list => `(?:${list.join('|')})`
const START = new RegExp(`^dev-flow (triage|design|implement) start: tier=(${alt([...enums.tier.filter(t => t !== 'other'), 'pending'])}) track=(backend|frontend|both)$`)
const GATE = new RegExp(`^gate (${alt(enums.gate)})(?: first)?: (${alt(enums.verdict)})$`)
const ROUND = /^(UX|Design|Plan|Review|QA fix) r(\d+)\/(\d+): (\d+) at\/above (blocking|major|minor)$/
const FLOOR = { light: 'blocking', standard: 'major', deep: 'minor' } // the tier's severity floor: what a round count is of
// HALT and failure lines are fixed text plus counts: never agent error text, request text or paths.
const BREACH = '(?:the reviewers reported no touched files, so the scope cannot be verified|\\d+ risk-surface files outside the plan(?:; \\d+ files touched vs \\d+ planned)?|\\d+ files touched vs \\d+ planned)'
const HALT = {
  'budget-cap': /^HALT budget-cap: agent budget exceeded$/,
  'config-error': /^HALT config-error: agent config error$/,
  'call-ceiling': /^HALT call-ceiling: (?:light|standard|deep) cap \d+$/,
  'implement-failed': /^HALT implement-failed: a developer agent returned no result — nothing to review$/,
  escalation: new RegExp(`^HALT escalation: scope breach at light — ${BREACH}$`),
}
const AGENT_FAILED = /^agent failed: [\w:. -]+$/
const SCOPE_BREACH = new RegExp(`^Scope breach \\(not escalating at (?:standard|deep)\\): ${BREACH}$`)
const REQUIRED_GATES = { design: ['design_review'], implement: ['code_review', 'qa'] }
const LEAK_MIN = 12 // shorter strings ('x') would match by accident

export const checkLogContract = (out, runArgs, workflow) => {
  const { logs, result, error } = out
  const fail = m => { throw new Error(`log contract: ${m}\n  logs: ${JSON.stringify(logs)}`) }
  const starts = logs.filter(l => l.startsWith('dev-flow '))
  if (error === null) {
    if (starts.length !== 1) fail(`expected exactly one start line, got ${starts.length}`)
    const m = START.exec(starts[0])
    if (!m) fail(`malformed start line '${starts[0]}'`)
    if (m[1] !== workflow) fail(`start line names '${m[1]}', workflow is '${workflow}'`)
    if (workflow !== 'triage' && m[2] === 'pending') fail('only triage may log tier=pending')
    for (const g of REQUIRED_GATES[workflow] ?? []) if (!logs.some(l => l.startsWith(`gate ${g}: `))) fail(`no 'gate ${g}' line`)
    if (workflow === 'triage' && !result.triageFailed && !logs.some(l => /^Triage: tier=\w+ S=\d+ R=\d+ floors=\S+$/.test(l))) fail('no Triage tier line')
    if (result.haltedBy && !logs.some(l => l.startsWith(`HALT ${result.haltedBy}:`))) fail(`haltedBy '${result.haltedBy}' has no HALT line`)
  }
  for (const l of logs) {
    if (/^gate /.test(l) && !GATE.test(l)) fail(`gate line outside the telemetry enums: '${l}'`)
    const h = /^HALT ([\w-]+):/.exec(l)
    if (h && !HALT[h[1]]?.test(l)) fail(`HALT line carries free text or an unknown id: '${l}'`)
    if (/^agent failed/.test(l) && !AGENT_FAILED.test(l)) fail(`agent-failed line carries free text: '${l}'`)
    if (/^Scope breach/.test(l) && !SCOPE_BREACH.test(l)) fail(`scope-breach line carries free text or paths: '${l}'`)
    const r = ROUND.exec(l)
    if (r && (+r[2] < 1 || +r[2] > +r[3])) fail(`round out of range: '${l}'`)
    if (r && starts[0] && r[5] !== FLOOR[START.exec(starts[0])?.[2]]) fail(`round count not labelled with the tier floor: '${l}'`)
  }
  // 'gate qa first' is the pre-fix verdict; the last plain 'gate qa' line is the final one and must match the result
  if (error === null && workflow === 'implement') {
    const final = logs.filter(l => l.startsWith('gate qa: ')).at(-1)?.slice('gate qa: '.length)
    if ((final === 'pass') !== (result.qaPassed === true)) fail(`last 'gate qa' verdict '${final}' disagrees with result.qaPassed=${result.qaPassed}`)
  }
  for (const k of ['request', 'ownerProposal', 'briefPath']) {
    const secret = runArgs?.[k]
    if (typeof secret === 'string' && secret.length >= LEAK_MIN && logs.some(l => l.includes(secret))) fail(`a log line leaks args.${k}`)
  }
}
