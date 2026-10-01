import assert from 'node:assert/strict'

// Standard tier: one blocking review round, then clean; QA fails once and passes after the fix; then a budget halt run.
const R = 'addit-harness:'
const CASES = [{ name: 'fix cycle' }, { name: 'budget halt' }]
const seen = { reviews: 0, qa: 0 }
export default {
  argsList: CASES.map(() => ({ slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: 'standard' })),
  respond: ({ agentType }, state) => {
    if (state.run === 1 && agentType.endsWith('developer')) {
      const e = new Error('SENTINEL-AGENT-OUTPUT over budget'); e.name = 'WorkflowBudgetExceededError'; throw e
    }
    if (agentType === `${R}qa-engineer`) return { passed: ++seen.qa > 1, findings: ['SENTINEL-AGENT-OUTPUT'], evidence: [] }
    if (agentType.endsWith('code-reviewer')) {
      const first = seen.reviews++ === 0
      return { findings: first ? [{ severity: 'blocking', description: 'SENTINEL-AGENT-OUTPUT' }] : [], touchedFiles: [{ repo: '/r', path: 'a.js' }] }
    }
    if (agentType.startsWith('pr-review-toolkit:')) throw new Error('unknown agent type')
    return 'done'
  },
  expect: ({ runs }) => {
    const [fix, halted] = runs
    assert.equal(fix.error, null)
    assert.deepEqual(fix.logs.filter(l => !/^agent failed/.test(l)), [
      'dev-flow implement start: tier=standard track=backend',
      'Review r1/3: 1 at/above major',
      'Review r2/3: 0 at/above major',
      'gate code_review: pass',
      'gate qa first: fail',
      'QA fix r1/1: 0 at/above major',
      'gate qa: pass',
    ])
    assert.equal(halted.result.haltedBy, 'budget-cap')
    assert.ok(halted.logs.some(l => /^HALT budget-cap:/.test(l)))
    assert.ok(halted.logs.includes('gate code_review: blocked'))
    assert.ok(halted.logs.includes('gate qa: skipped'))
    // no line carries agent output: HALT and agent-failed lines are fixed text too
    assert.ok(![...fix.logs, ...halted.logs].some(l => /SENTINEL/.test(l)))
  },
}
