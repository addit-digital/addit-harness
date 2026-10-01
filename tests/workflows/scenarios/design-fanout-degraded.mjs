import assert from 'node:assert/strict'

const R = 'addit-harness:'
const isExplorer = c => /role: explorer/.test(c.prompt)
const base = { slug: 'abc', track: 'backend', repo: '/r', request: 'x', needsUX: false, investigate: false, tier: 'deep' }
// Run 0: one explorer throws -> synthesize from the two that returned. Run 1: all explorers fail -> single design pass.
// Run 2: standard never fans out.
export default {
  argsList: [base, base, { ...base, tier: 'standard' }],
  respond: (call, state) => {
    if (isExplorer(call)) {
      if (state.run === 1 || call.opts.label === 'explorer 2') throw new Error('boom')
      return { summary: 's', priorArt: [], preMortem: [], typicality: 0.5 }
    }
    if (call.agentType === `${R}architect-reviewer` && call.opts.schema) return { findings: [] }
    return 'text'
  },
  expect: ({ runs: [partial, none, standard] }) => {
    assert.equal(partial.error, null)
    const synth = partial.callList.find(c => /role: synthesizer/.test(c.prompt))
    assert.equal(JSON.parse(synth.prompt.match(/Candidates: (\[.*\]) Write the result/)[1]).map(c => c.label).join(''), 'XY')
    assert.equal(partial.calls, 3 + 1 + 1 + 2) // 3 explorers, synth, review, plan, plan review
    assert.equal(none.error, null)
    assert.equal(none.callList.filter(c => /role: synthesizer/.test(c.prompt)).length, 0)
    assert.ok(none.logs.some(l => /no explorer returned/.test(l)))
    assert.equal(none.calls, 3 + 1 + 1 + 2) // 3 failed explorers, one plain design pass, review, plan, plan review
    assert.equal(standard.callList.filter(isExplorer).length, 0)
    assert.equal(standard.calls, 4)
  },
}
