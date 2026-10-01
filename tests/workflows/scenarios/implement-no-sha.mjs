import assert from 'node:assert/strict'

export default {
  args: { slug: 's', track: 'backend', repo: '/r' },
  respond: () => { throw new Error('no agent may run') },
  expect: out => {
    assert.match(out.error, /planSha256 missing or malformed\. Do not compute this yourself; ask the user/)
    assert.equal(out.calls, 0)
  },
}
