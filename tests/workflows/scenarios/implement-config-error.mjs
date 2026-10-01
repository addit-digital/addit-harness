import assert from 'node:assert/strict'

export default {
  args: { slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: 'standard' },
  respond: () => { throw new Error('schema contradiction: required field is forbidden') },
  expect: out => {
    assert.equal(out.result.haltedBy, 'config-error')
    assert.equal(out.calls, 1)
  },
}
