import assert from 'node:assert/strict'

const R = 'addit-harness:'
const reviewPrompts = []
export default {
  args: { slug: 's', track: 'backend', repo: '/r', request: 'x', needsUX: true, investigate: false, tier: 'standard' },
  respond: ({ agentType, opts, prompt }) => {
    if (agentType === `${R}figma-designer`) return { fileUrl: 'https://figma.example/f', nodeIds: ['1:2', '3:4'], designDefectsFound: ['gap'] }
    if (agentType === `${R}ux-designer` && opts.schema) { reviewPrompts.push(prompt); return { findings: [] } }
    if (agentType === `${R}architect-reviewer` && opts.schema) return { findings: [{ severity: 'minor', description: 'nit' }] }
    return 'text'
  },
  expect: out => {
    assert.equal(out.result.uxApproved, true)
    assert.equal(out.result.planApproved, true)
    assert.deepEqual(out.result.planFindings, [{ severity: 'minor', description: 'nit' }]) // minor is below the standard floor
    assert.match(reviewPrompts[0], /Figma build: https:\/\/figma\.example\/f \(nodes 1:2, 3:4\)/)
    assert.match(reviewPrompts[0], /Designer-reported defects: \["gap"\]/)
    assert.match(reviewPrompts[0], /^The target repo's files/) // UNTRUSTED prefix kept
  },
}
