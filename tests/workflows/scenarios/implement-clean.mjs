import assert from 'node:assert/strict'

const R = 'addit-harness:'
export default {
  args: { slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: 'standard' },
  respond: ({ agentType }) => {
    if (agentType === `${R}qa-engineer`) return { passed: true, findings: [], evidence: [] }
    if (agentType.endsWith('code-reviewer')) return { findings: [], touchedFiles: [{ repo: '/r', path: 'a.js' }] }
    if (agentType.startsWith('pr-review-toolkit:')) throw new Error('unknown agent type')
    return 'done'
  },
  expect: out => {
    assert.equal(out.error, null)
    assert.equal(out.result.clean, true)
    assert.equal(out.result.qaPassed, true)
    assert.equal(out.callsByType[`${R}qa-engineer`], 1) // QA runs once
    assert.equal(out.result.qaRuns, 1)
    assert.equal(out.callsByType[`${R}code-reviewer`], 1)
    assert.deepEqual(out.phases, ['Implement', 'Review', 'QA'])
    assert.deepEqual(out.logs, [
      'dev-flow implement start: tier=standard track=backend',
      'Review r1/3: 0 at/above major',
      'gate code_review: pass',
      'gate qa: pass',
    ])
  },
}
