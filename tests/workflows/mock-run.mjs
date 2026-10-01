#!/usr/bin/env node
// Runs a real workflow script body with only the runtime calls stubbed.
// Usage: node tests/workflows/mock-run.mjs <workflows/x.js> <scenario>
// A scenario (tests/workflows/scenarios/<scenario>.mjs) default-exports
// { args, respond(call, state), budget?, expect(out) }. respond() returns the
// agent result (or null) and may throw to simulate an agent error. expect()
// throws on a failed assertion. Prints { result, error, calls, callsByType, logs, phases }.
// A scenario may give argsList instead of args to run the script once per entry
// (state.run is the entry index); expect() then receives { runs: [out, ...] }.
import { readFileSync } from 'node:fs'
import { basename, dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const [scriptPath, scenarioName] = process.argv.slice(2)
if (!scriptPath || !scenarioName) {
  console.error('usage: mock-run.mjs <workflows/x.js> <scenario>')
  process.exit(64)
}
const scenarioFile = resolve(dirname(fileURLToPath(import.meta.url)), 'scenarios', `${basename(scenarioName, '.mjs')}.mjs`)
const scenario = (await import(pathToFileURL(scenarioFile).href)).default

const source = readFileSync(scriptPath, 'utf8')
const metaSrc = source.match(/^export const meta = \{[\s\S]*?^\}/m)?.[0]
if (!metaSrc) throw new Error('script has no top-level `export const meta = {...}` block')
const meta = new Function(`${metaSrc.replace('export ', '')}; return meta`)()
const body = source.replace(/^export const meta =/m, 'const meta =')

const banned = what => () => { throw new Error(`${what} is not allowed in workflow scripts`) }
const ShimDate = class extends Date {
  constructor(...a) { if (a.length === 0) banned('new Date()')(); super(...a) }
  static now = banned('Date.now()')
}
const ShimMath = Object.create(Math, { random: { value: banned('Math.random()') } })
const AsyncFunction = Object.getPrototypeOf(async () => {}).constructor

const runOnce = async (runArgs, index) => {
  const calls = [], logs = [], phases = [], callsByType = {}, state = { calls, run: index }
  const checkPhase = title => {
    if (!meta.phases.some(p => p.title === title)) throw new Error(`phase '${title}' is not declared in meta.phases`)
  }
  const phase = title => { checkPhase(title); phases.push(title) }
  const log = m => { logs.push(String(m)) }
  const agent = async (prompt, opts = {}) => {
    if (opts.phase) checkPhase(opts.phase)
    calls.push({ agentType: opts.agentType, prompt, opts })
    callsByType[opts.agentType] = (callsByType[opts.agentType] ?? 0) + 1
    return scenario.respond(calls.at(-1), state)
  }
  const parallel = thunks => Promise.all(thunks.map(async f => { try { return await f() } catch { return null } }))
  const budget = { total: 0, remaining: () => Infinity, ...scenario.budget }
  const run = new AsyncFunction('agent', 'parallel', 'phase', 'log', 'budget', 'args', 'Date', 'Math', body)
  const out = { result: null, error: null }
  try { out.result = await run(agent, parallel, phase, log, budget, runArgs, ShimDate, ShimMath) }
  catch (e) { out.error = e?.message ?? String(e) }
  return Object.assign(out, { calls: calls.length, callsByType, logs, phases, callList: calls })
}

// A scenario with argsList runs the script once per entry (matrix checks); expect() then gets { runs }.
const runs = []
if (scenario.argsList) for (const [i, a] of scenario.argsList.entries()) runs.push(await runOnce(a, i)) // sequential: scenarios keep module state
const out = scenario.argsList ? { runs } : await runOnce(scenario.args, 0)
console.log(JSON.stringify(out, (k, v) => (k === 'callList' ? undefined : v), 2))
try { scenario.expect(out); console.error(`PASS ${scenarioName}`) }
catch (e) { console.error(`FAIL ${scenarioName}: ${e.message}`); process.exit(1) }
