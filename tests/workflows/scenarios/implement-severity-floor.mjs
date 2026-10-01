import assert from 'node:assert/strict'

const R = 'addit-harness:'
const F = { minor: [{ severity: 'minor', description: 'm' }], major: [{ severity: 'major', description: 'M' }] }
const CASES = [
  ['light', 'minor', true], ['standard', 'minor', true], ['deep', 'minor', false],
  ['light', 'major', true], ['standard', 'major', false], ['deep', 'major', false],
]
export default {
  argsList: CASES.map(([tier]) => ({ slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier })),
  respond: ({ agentType }, state) => {
    if (agentType === `${R}qa-engineer`) return { passed: true, findings: [], evidence: [] }
    if (agentType.endsWith('code-reviewer') || agentType.startsWith('pr-review-toolkit:'))
      return { clean: false, findings: F[CASES[state.run][1]], touchedFiles: [{ repo: '/r', path: 'a.js' }] } // the reviewer's own `clean` is ignored
    return 'done'
  },
  expect: ({ runs }) => {
    CASES.forEach(([tier, sev, want], i) => assert.equal(runs[i].result.clean, want, `${tier} with only ${sev} findings`))
    assert.equal(runs[0].result.fixRounds, 0)
  },
}
