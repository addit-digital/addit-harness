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
    assert.ok(runs[0].logs.some(l => /HALT escalation: scope breach at light — risk-surface files outside the plan: auth\/login\.js/.test(l)))
    assert.ok(runs[1].logs.some(l => /Scope breach \(not escalating at standard\)/.test(l)))
    assert.equal(runs[1].result.qaPassed, true)
    assert.deepEqual(runs[0].result.scopeBreach.risk, ['auth/login.js'])
    assert.equal(runs[3].result.scopeBreach.magnitude, true)
  },
}
