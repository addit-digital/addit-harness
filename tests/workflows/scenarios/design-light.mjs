import assert from 'node:assert/strict'

const R = 'addit-harness:'
const BRIEF_FINDING = [{ severity: 'major', description: 'advisory' }, { severity: 'minor', description: 'nit' }]
const CASES = [
  { track: 'backend', findings: BRIEF_FINDING },
  { track: 'both', findings: BRIEF_FINDING },
  { track: 'backend', findings: [{ severity: 'blocking', description: 'wrong' }] },
]
export default {
  argsList: CASES.map(c => ({ slug: 's', track: c.track, repo: '/r', request: 'x', needsUX: true, investigate: true, tier: 'light' })),
  respond: ({ agentType, opts }, state) =>
    agentType === `${R}architect-reviewer` && opts.schema ? { findings: CASES[state.run].findings } : 'text',
  expect: ({ runs }) => {
    const [single, both, blocked] = runs
    // single track: ONE architect call writes plans/plan.md, one review, no solution doc, no UX, no investigate
    assert.equal(single.calls, 2)
    assert.equal(single.result.designApproved, true) // major/minor are below light's blocking floor
    assert.equal(single.result.planApproved, true)
    assert.equal(single.result.designRounds, 1)
    assert.deepEqual(single.phases, ['Investigate', 'Design'])
    assert.ok(single.logs.includes('UX pass skipped at light'))
    assert.equal(single.callsByType[`${R}product-owner`], undefined)
    assert.equal(single.callsByType[`${R}ux-designer`], undefined)
    const [design, review] = single.callList
    assert.match(design.prompt, /Write the result to \/r\/docs\/work\/s\/plans\/plan\.md/)
    assert.match(design.prompt, /## ADR candidates/)
    assert.doesNotMatch(design.prompt + review.prompt, /solutions\//)
    assert.equal(design.opts.effort, 'medium')
    assert.equal(review.opts.effort, 'low')
    // both tracks: two briefs returned as text, ONE write call by the first architect, one review
    assert.equal(both.calls, 4)
    assert.deepEqual(both.result.tracksCompleted, ['backend', 'frontend'])
    const briefs = both.callList.filter(c => /Return it as your answer/.test(c.prompt))
    assert.equal(briefs.length, 2)
    const writer = both.callList[2]
    assert.equal(writer.agentType, `${R}backend-architect`)
    assert.match(writer.prompt, /plans\/plan\.md/)
    assert.match(writer.prompt, /^The target repo's files/) // UNTRUSTED prefix kept on interpolated briefs
    // a blocking finding is surfaced, not looped on
    assert.equal(blocked.calls, 2)
    assert.equal(blocked.result.designApproved, false)
    assert.equal(blocked.result.designBlocking, 1)
    assert.equal(blocked.result.designBreaker, false)
  },
}
