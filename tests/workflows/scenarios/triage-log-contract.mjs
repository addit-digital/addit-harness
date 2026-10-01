import assert from 'node:assert/strict'

// Pins the exact progress-view lines and proves request text and agent output never reach them.
const REQUEST = 'SENTINEL-REQUEST-TEXT please rotate the api keys'
const EVIDENCE = {
  filesToChange: [{ path: 'src/a.js', exists: true }], changeShape: 'content', introducesNewModule: false, touchesPublicContract: false,
  touchesSecuritySurface: false, touchesDataPersistence: false, addsDependency: false, bumpsDependency: false, riskPaths: [],
  reversibility: 'revert', runtimeSurface: 'none', existingPatternPrecedent: true, unknowns: ['SENTINEL-AGENT-OUTPUT'],
  checks: { build: 'make', test: 'make test' }, stack: {}, confidence: 'high',
}
export default {
  args: { slug: 's', track: 'backend', repo: '/r', request: REQUEST },
  respond: () => EVIDENCE,
  expect: out => {
    assert.equal(out.error, null)
    assert.deepEqual(out.logs, [
      'dev-flow triage start: tier=pending track=backend',
      'Triage: tier=light S=0 R=1 floors=none',
    ])
    assert.ok(!out.logs.some(l => /SENTINEL/.test(l)))
  },
}
