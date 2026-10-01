import assert from 'node:assert/strict'

const R = 'addit-harness:'
const base = { slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64) }
const CASES = [
  { name: 'light + auth file outside plan', args: { tier: 'light', plannedFiles: ['src/a.js'] }, touched: ['src/a.js', 'auth/login.js'], halt: true },
  { name: 'standard + same breach: log only', args: { tier: 'standard', plannedFiles: ['src/a.js'] }, touched: ['src/a.js', 'auth/login.js'], halt: false },
  { name: 'deep + same breach: log only', args: { tier: 'deep', plannedFiles: ['src/a.js'] }, touched: ['src/a.js', 'auth/login.js'], halt: false },
  { name: 'light + magnitude (band 0 -> 1)', args: { tier: 'light', plannedFiles: ['a.js', 'b.js'] }, touched: ['a.js', 'b.js', 'c.js'], halt: true },
  { name: 'light + extras in the same band', args: { tier: 'light', plannedFiles: ['a.js', 'b.js', 'c.js'] }, touched: ['a.js', 'b.js', 'c.js', 'd.js', 'e.js'], halt: false },
  { name: 'light + triage-predicted risk dir', args: { tier: 'light', plannedFiles: ['a.js'], riskPaths: ['billing/'] }, touched: ['a.js', 'billing/x.js'], halt: true },
  { name: 'light + planned risk file is not a breach', args: { tier: 'light', plannedFiles: ['auth/login.js'] }, touched: ['auth/login.js'], halt: false },
  { name: 'light + work-item docs are ignored', args: { tier: 'light', plannedFiles: ['a.js'] }, touched: ['a.js', 'docs/work/s/plans/plan.md', 'docs/work/s/qa-reports/report.md', 'docs/work/s/x.md'], halt: false },
  { name: 'light + touchedFiles missing: scope unknown, escalate', args: { tier: 'light', plannedFiles: ['a.js'] }, touched: undefined, halt: true, unknown: true },
  { name: 'light + touchedFiles empty: scope unknown, escalate', args: { tier: 'light', plannedFiles: ['a.js'] }, touched: [], halt: true, unknown: true },
  { name: 'standard + touchedFiles missing: log only', args: { tier: 'standard', plannedFiles: ['a.js'] }, touched: undefined, halt: false, unknown: true },
  { name: 'light + same relative path in two repos counts twice', args: { tier: 'light', plannedFiles: ['src/a.js', 'src/b.js'], track: 'both', secondaryRepo: '/f' },
    touched: [{ repo: '/r', path: 'src/a.js' }, { repo: '/f', path: 'src/a.js' }, { repo: '/r', path: 'src/b.js' }], halt: true },
  { name: 'light + object entries within plan', args: { tier: 'light', plannedFiles: ['src/a.js', 'src/b.js'], track: 'both', secondaryRepo: '/f' },
    touched: [{ repo: '/r', path: 'src/a.js' }, { repo: '/f', path: 'src/b.js' }], halt: false },
]
export default {
  argsList: CASES.map(c => ({ ...base, ...c.args })),
  respond: ({ agentType }, state) => {
    if (agentType === `${R}qa-engineer`) return { passed: true, findings: [], evidence: [] }
    if (agentType.endsWith('code-reviewer') || agentType.startsWith('pr-review-toolkit:')) return { findings: [], touchedFiles: CASES[state.run].touched }
    return 'done'
  },
  expect: ({ runs }) => {
    CASES.forEach((c, i) => {
      const r = runs[i]
      assert.equal(r.error, null, c.name)
      assert.equal(r.result.haltedBy, c.halt ? 'escalation' : null, c.name)
      assert.equal(r.result.escalateTo, c.halt ? 'standard' : null, c.name)
      assert.equal(r.callsByType[`${R}qa-engineer`] ?? 0, c.halt ? 0 : 1, c.name) // the halt stops everything after the first review
      assert.equal(r.callsByType[`${R}code-reviewer`], 1, c.name)
    })
    assert.ok(runs[0].logs.includes('HALT escalation: scope breach at light — 1 risk-surface files outside the plan'))
    assert.ok(runs[3].logs.includes('HALT escalation: scope breach at light — 3 files touched vs 2 planned'))
    // paths stay in the returned result and never reach a log line
    assert.ok(!runs.flatMap(r => r.logs).some(l => /auth\/login|billing\/|\.js/.test(l)))
    assert.ok(runs[1].logs.some(l => /Scope breach \(not escalating at standard\)/.test(l)))
    assert.equal(runs[1].result.qaPassed, true)
    assert.deepEqual(runs[0].result.scopeBreach.risk, ['auth/login.js'])
    assert.equal(runs[3].result.scopeBreach.magnitude, true)
    CASES.forEach((c, i) => { if (c.unknown) assert.equal(runs[i].result.scopeBreach.unknown, true, c.name) })
    assert.ok(runs[8].logs.some(l => /HALT escalation: scope breach at light — the reviewers reported no touched files/.test(l)))
    assert.ok(runs[10].logs.some(l => /Scope breach \(not escalating at standard\): the reviewers reported no touched files/.test(l)))
    assert.equal(runs[10].result.qaPassed, true)
    assert.equal(runs[11].result.scopeBreach.magnitude, true)
  },
}
