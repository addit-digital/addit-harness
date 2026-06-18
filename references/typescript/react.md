# React

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [react.dev](https://react.dev) (Rules of Hooks, You Might Not Need an Effect, useMemo/useCallback), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (react rule set).

## Components & hooks

- Function components + hooks only. Keep components small and composable.
- Extract reusable stateful logic into custom hooks (`useDebounce`, `useUser`); a hook is just a function whose name starts with `use` and that calls other hooks.
- Keep components pure: no side effects during render; same props → same output.

## Rules of hooks

- Call hooks unconditionally, at the top level — never in loops, conditions, or after an early return.
- Call them only from components or other hooks. Enforce with `eslint-plugin-react-hooks`.

```tsx
// ❌ conditional hook
if (open) { const [x] = useState(0); }
// ✅ hook first, branch on the value
const [x, setX] = useState(0);
if (open) { /* use x */ }
```

## useEffect — synchronize, don't derive

Effects are for synchronizing with external systems (subscriptions, DOM, network, timers). They are not for computing values from props/state.

```tsx
// ❌ effect to compute derived state
const [fullName, setFullName] = useState("");
useEffect(() => setFullName(`${first} ${last}`), [first, last]);

// ✅ derive during render (memoize only if measurably expensive)
const fullName = `${first} ${last}`;
```

- Complete dependency arrays — never lie to the linter. If a dep "shouldn't" rerun the effect, the design is usually wrong (move it to a ref, an event handler, or derive it).
- Always clean up subscriptions/timers/listeners in the returned function.
- Don't use effects to respond to user events — put that logic in the event handler.

```tsx
useEffect(() => {
  const id = setInterval(tick, 1000);
  return () => clearInterval(id); // cleanup
}, []);
```

## Keys

- Stable, unique ids from your data. Never the array index for dynamic/reorderable lists (causes state bleaking between rows and subtle bugs).

```tsx
{items.map((it) => <Row key={it.id} item={it} />)}
```

## Memoization is deliberate

Reach for `useMemo`/`useCallback`/`React.memo` only when you've identified a real re-render cost or need referential stability (e.g. a dependency of an effect, or props to a memoized child). Default to none — premature memoization adds noise and its own cost.

```tsx
const sorted = useMemo(() => expensiveSort(items), [items]); // ✅ expensive + stable input
const onPick = useCallback((id: string) => select(id), []);   // ✅ passed to memoized child
```

## State placement

- Keep state as local as possible; lift only to the nearest common ancestor that needs it.
- Avoid prop-drilling deep trees — use Context for truly global, low-churn values (theme, auth, locale), not high-frequency state (it re-renders all consumers).
- Don't duplicate state you can derive; don't mirror props into state.

## Composition

- Prefer composition (children, render-as-slot, component injection) over configuration-by-boolean-flags.

```tsx
// ✅ slots over prop explosion
<Card header={<Title />} footer={<Actions />}>{body}</Card>
```

- Split a component when it does two jobs, or when a `&&`/ternary in JSX gets hard to read.
