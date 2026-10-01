import assert from 'node:assert/strict'

const R = 'addit-harness:'
const F = { minor: [{ severity: 'minor', description: 'm' }], major: [{ severity: 'major', description: 'M' }] }
const CASES = [
  ['light', 'minor', true], ['standard', 'minor', true], ['deep', 'minor', false],
  ['light', 'major', true], ['standard', 'major', false], ['deep', 'major', false],
]
export default {
  argsList: CASES.map(([tier]) => ({ slug: 's', track: 'backend', repo: '/r', request: 'x', needsUX: false, investigate: false, tier })),
  respond: ({ agentType, opts }, state) =>
    agentType === `${R}architect-reviewer` && opts.schema ? { approved: true, findings: F[CASES[state.run][1]] } : 'text',
  expect: ({ runs }) => {
    CASES.forEach(([tier, sev, want], i) => {
      assert.equal(runs[i].result.designApproved, want, `${tier} with only ${sev} findings`) // the reviewer's own `approved` is ignored
      assert.equal(runs[i].result.planApproved, want, `${tier} plan verdict`)
    })
    // an unapproved identical-findings loop trips the design breaker at round 2, not a halt
    assert.equal(runs[2].result.designBreaker, true)
    assert.equal(runs[2].callsByType[`${R}architect-reviewer`], 3) // 2 design reviews + the plan review
    assert.equal(runs[2].result.haltedBy, null)
  },
}
