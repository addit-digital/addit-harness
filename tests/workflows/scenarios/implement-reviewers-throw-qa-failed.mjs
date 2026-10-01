import assert from 'node:assert/strict'

const R = 'addit-harness:'
const fixPrompts = []
export default {
  args: { slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: 'standard' },
  respond: ({ agentType, prompt }) => {
    if (agentType === `${R}qa-engineer`) return { passed: false, findings: ['login broken'], evidence: [] }
    if (agentType === `${R}code-reviewer` || agentType.startsWith('pr-review-toolkit:')) throw new Error('reviewer crashed')
    if (prompt.includes('Fix these review findings')) fixPrompts.push(prompt)
    return 'done'
  },
  expect: out => {
    assert.equal(out.error, null)
    assert.ok(out.logs.some(l => /Review round 1: all reviewer agents failed/.test(l)))
    assert.equal(out.result.clean, false) // all reviewers failing is never "clean"
    // QA has not run yet during review, so its failure drives the one post-QA fix cycle — with no floor
    assert.equal(fixPrompts.length, 1)
    assert.match(fixPrompts[0], /\[QA\].*login broken/)
    assert.equal(out.result.qaRuns, 2)
    assert.equal(out.result.postQaFixRan, true)
    assert.equal(out.result.qaPassed, false) // second failure: stop, never a third QA
    assert.equal(out.callsByType[`${R}qa-engineer`], 2)
  },
}
