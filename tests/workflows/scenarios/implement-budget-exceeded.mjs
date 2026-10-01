import assert from 'node:assert/strict'

export default {
  args: { slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: 'standard' },
  respond: () => { throw Object.assign(new Error('budget exhausted'), { name: 'WorkflowBudgetExceededError' }) },
  expect: out => {
    assert.equal(out.error, null)
    assert.equal(out.result.haltedBy, 'budget-cap')
    assert.equal(out.calls, 1) // nothing is called after the halt
    assert.ok(out.logs.some(l => /HALT budget-cap/.test(l)))
  },
}
