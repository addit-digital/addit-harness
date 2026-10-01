import assert from 'node:assert/strict'

const R = 'addit-harness:'
const isExplorer = c => /role: explorer/.test(c.prompt)
const isSynth = c => /role: synthesizer/.test(c.prompt)
const base = { slug: 'abc', track: 'backend', repo: '/r', request: 'x', needsUX: false, investigate: false }
const ALT = { candidate: 'Y', rationale: 'dominates' }
// Run 0 (deep): the first review returns betterAlternative and no findings -> not approved, ONE extra synth (+ review),
// designRounds unchanged by the switch; a second betterAlternative does not switch again.
// Run 1 (standard): no fan-out, so betterAlternative becomes a major finding and goes through a normal revision round.
export default {
  argsList: [{ ...base, tier: 'deep' }, { ...base, tier: 'standard' }],
  respond: (call, state) => {
    if (isExplorer(call)) return { summary: 's', priorArt: [], preMortem: [], typicality: 0.5 }
    if (call.agentType === `${R}architect-reviewer` && call.opts.schema) {
      if (call.opts.phase === 'Plan') return { findings: [] }
      state.reviews = (state.reviews ?? 0) + 1
      if (state.run === 0) return { findings: [], betterAlternative: state.reviews <= 2 ? ALT : null }
      return { findings: [], betterAlternative: state.reviews === 1 ? ALT : null }
    }
    return 'text'
  },
  expect: ({ runs: [deep, standard] }) => {
    assert.equal(deep.error, null)
    assert.equal(deep.callList.filter(isExplorer).length, 3)
    assert.equal(deep.callList.filter(isSynth).length, 2) // first synthesis + exactly one switch
    const reviews = deep.callList.filter(c => c.agentType === `${R}architect-reviewer` && c.opts.phase === 'Design')
    assert.equal(reviews.length, 3) // switch trigger, post-switch review (its own alternative becomes a major finding), revision review
    assert.equal(deep.result.designBreaker, false)
    assert.ok(deep.callList.filter(isSynth)[1].prompt.includes('IN PLACE and re-synthesize around {"candidate":"Y","rationale":"dominates"}'))
    assert.equal(new Set(reviews.map(c => c.prompt.match(/write your report to (\S+):/)[1])).size, 3, 'report paths must not collide')
    assert.ok(deep.calls <= 27)
    // standard: no switch, no synth; the alternative is fed back as a major finding
    assert.equal(standard.callList.filter(isSynth).length, 0)
    const designs = standard.callList.filter(c => c.agentType === `${R}backend-architect` && c.opts.phase === 'Design')
    assert.equal(designs.length, 2)
    assert.match(designs[1].prompt, /Better alternative: .*dominates/)
    assert.equal(standard.result.designRounds, 2)
  },
}
