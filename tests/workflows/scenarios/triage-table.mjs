import assert from 'node:assert/strict'

// The thirteen evidence rows of the 08-25 design (solution-backend.md §3.4) must score to exactly the
// table's S, R, tier. Rows after the table exercise overrides, the user override and the failure paths.
const files = (n, dirs = ['src'], newCount = 0) =>
  Array.from({ length: n }, (_, i) => ({ path: `${dirs[i % dirs.length]}/f${i}.js`, exists: i >= n - newCount ? false : true }))
const base = {
  changeShape: 'logic', introducesNewModule: false, touchesPublicContract: false, touchesSecuritySurface: false,
  touchesDataPersistence: false, addsDependency: false, bumpsDependency: false, riskPaths: [], reversibility: 'revert',
  runtimeSurface: 'none', existingPatternPrecedent: true, unknowns: [], checks: { build: 'make', test: 'make test', lint: null },
  stack: {}, confidence: 'high',
}
const row = (name, track, ev, want) => ({ name, track, needsUX: false, ev: { ...base, ...ev }, want })
const ROWS = [
  row('docs fix', 'frontend', { filesToChange: files(5, ['site'], 1), unknowns: ['mermaid lexer?'] }, { S: 2, R: 1, tier: 'light' }),
  row('auth tweak', 'backend', { filesToChange: files(1), touchesSecuritySurface: true }, { S: 1, R: 3, tier: 'standard' }),
  row('40-file rename, cross-module', 'backend', { filesToChange: files(40, ['a', 'b']) }, { S: 7, R: 0, tier: 'deep' }),
  row('40-file rename, one module', 'backend', { filesToChange: files(40) }, { S: 5, R: 0, tier: 'standard' }),
  row('two-file typo', 'backend', { filesToChange: files(2), changeShape: 'content' }, { S: 0, R: 0, tier: 'light' }),
  row('contract alone', 'backend', { filesToChange: files(1), touchesPublicContract: true }, { S: 1, R: 3, tier: 'standard' }),
  row('adds dependency alone', 'backend', { filesToChange: files(1), addsDependency: true }, { S: 1, R: 3, tier: 'standard' }),
  row('bumps dependency alone', 'backend', { filesToChange: files(1), changeShape: 'config', bumpsDependency: true }, { S: 0, R: 1, tier: 'light' }),
  row('new service', 'backend', { filesToChange: files(15, ['a', 'b', 'c'], 8), introducesNewModule: true, touchesPublicContract: true, existingPatternPrecedent: false }, { S: 11, R: 4, tier: 'deep' }),
  row('new module', 'backend', { filesToChange: files(4, ['a', 'b'], 3), introducesNewModule: true, existingPatternPrecedent: false }, { S: 8, R: 1, tier: 'deep' }),
  row('8 files api+web, both', 'both', { filesToChange: files(8, ['api', 'web']), unknowns: ['one'] }, { S: 6, R: 1, tier: 'standard' }),
  row('schema migration', 'backend', { filesToChange: files(3, ['db', 'src']), touchesDataPersistence: true, reversibility: 'not-revertible' }, { S: 4, R: 6, tier: 'standard' }),
  row('migration plus unknown', 'backend', { filesToChange: files(3, ['db', 'src']), touchesDataPersistence: true, reversibility: 'not-revertible', unknowns: ['one'] }, { S: 4, R: 7, tier: 'deep' }),
]
const EXTRA = [
  { name: 'two root-level files are one directory, not a spread', track: 'backend', needsUX: false, ev: { ...base, filesToChange: [{ path: 'README.md', exists: true }, { path: 'LICENSE', exists: true }], changeShape: 'content' }, want: { S: 0, R: 0, tier: 'light' } },
  { name: 'needsUX floors to standard', track: 'frontend', needsUX: true, ev: { ...base, filesToChange: files(1), changeShape: 'content' }, want: { S: 0, R: 0, tier: 'standard', overrides: ['needs-ux'] } },
  { name: 'low confidence floors to standard', track: 'backend', needsUX: false, ev: { ...base, filesToChange: files(1), changeShape: 'content', confidence: 'low' }, want: { S: 0, R: 0, tier: 'standard', overrides: ['low-confidence'] } },
  { name: 'user override is exact (down)', track: 'backend', needsUX: false, userTier: 'light', ev: { ...base, filesToChange: files(1), touchesSecuritySurface: true }, want: { S: 1, R: 3, tier: 'light', overrides: ['security-or-persistence', 'user'] } },
  { name: 'invalid paths are dropped, none left floors to standard', track: 'backend', needsUX: false, ev: { ...base, filesToChange: [{ path: '../etc/passwd', exists: true }, { path: '/abs', exists: true }], changeShape: 'content' }, want: { S: 0, tier: 'standard', overrides: ['no-files'], plannedFiles: [] } },
  { name: 'triage failure defaults to standard', track: 'backend', needsUX: false, ev: null, want: { tier: 'standard', triageFailed: true } },
]
const CASES = [...ROWS, ...EXTRA]

export default {
  argsList: CASES.map(c => ({ slug: 's', track: c.track, needsUX: c.needsUX, repo: '/r', request: 'x', userTier: c.userTier })),
  respond: (_call, state) => CASES[state.run].ev,
  expect: ({ runs }) => {
    CASES.forEach((c, i) => {
      const r = runs[i]
      assert.equal(r.error, null, c.name)
      for (const [k, v] of Object.entries(c.want)) assert.deepEqual(r.result[k], v, `${c.name}: ${k}`)
      assert.equal(r.result.haltedBy, null, c.name)
      assert.equal(r.calls, 1, c.name)
    })
    const call = runs[0].callList[0]
    assert.equal(call.agentType, 'addit-harness:task-triager')
    assert.equal(call.opts.effort, 'low')
    assert.match(call.prompt, /^The target repo's files/) // UNTRUSTED prefix kept
  },
}
