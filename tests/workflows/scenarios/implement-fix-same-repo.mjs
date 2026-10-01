import assert from 'node:assert/strict'

const R = 'addit-harness:'
const base = { slug: 's', track: 'both', planSha256: 'a'.repeat(64), tier: 'standard' }
// One-branch policy: developers sharing a repo must never run concurrently, in the implement phase or in either fix round.
const CASES = [
  { name: 'same repo', args: { repo: '/r' }, maxInFlight: 1 },
  { name: 'two repos', args: { repo: '/r', secondaryRepo: '/f' }, maxInFlight: 2 },
]
const inFlight = [0, 0], peak = [0, 0], reviews = [0, 0], qas = [0, 0], fixCalls = [0, 0]
const tick = () => new Promise(r => setTimeout(r, 5))
export default {
  argsList: CASES.map(c => ({ ...base, ...c.args })),
  respond: async ({ agentType, opts }, state) => {
    const i = state.run
    if (agentType === `${R}qa-engineer`) return { passed: qas[i]++ > 0, findings: ['x'], evidence: [] }
    if (agentType.endsWith('code-reviewer')) return { findings: reviews[i]++ === 0 ? [{ severity: 'blocking', description: 'bug' }] : [], touchedFiles: ['a.js'] }
    if (agentType.startsWith('pr-review-toolkit:')) throw new Error('unknown agent type')
    inFlight[i]++; peak[i] = Math.max(peak[i], inFlight[i])
    if (opts.phase !== 'Implement') fixCalls[i]++
    await tick()
    inFlight[i]--
    return 'done'
  },
  expect: ({ runs }) => {
    CASES.forEach((c, i) => {
      assert.equal(runs[i].error, null, c.name)
      assert.equal(fixCalls[i], 4, `${c.name}: review fix + QA fix, one per track`)
      assert.equal(peak[i], c.maxInFlight, `${c.name}: peak concurrent developers`)
    })
  },
}
