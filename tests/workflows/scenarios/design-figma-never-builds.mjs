import assert from 'node:assert/strict'

const R = 'addit-harness:'
const designPrompts = []
export default {
  args: { slug: 's', track: 'backend', repo: '/r', request: 'x', needsUX: true, investigate: false, tier: 'standard' },
  respond: ({ agentType, opts, prompt }) => {
    if (agentType === `${R}figma-designer`) return null
    if (agentType === `${R}architect-reviewer` && opts.schema) return { findings: [] }
    if (prompt.startsWith('The target repo') && prompt.includes('Design the backend approach')) designPrompts.push(prompt)
    return 'text'
  },
  expect: out => {
    assert.equal(out.error, null)
    assert.equal(out.callsByType[`${R}ux-designer`], 3) // the UX loop stays bounded at 3 rounds
    assert.equal(out.callsByType[`${R}figma-designer`], 3)
    assert.equal(out.result.uxApproved, false)
    assert.equal(out.logs.filter(l => /no Figma build to verify/.test(l)).length, 3)
    assert.match(designPrompts[0], /UX spec is an UNAPPROVED draft/)
    assert.match(designPrompts[0], /solution-ux\.md/)
  },
}
