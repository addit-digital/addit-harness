# Data fetching & async

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [tanstack.com/query](https://tanstack.com/query/latest), [react.dev](https://react.dev) (Suspense, error boundaries), [nextjs.org/docs](https://nextjs.org/docs) (server fetching), [reactnative.dev](https://reactnative.dev) (Networking), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (react, nextjs, react-native rule sets).

## Where to fetch

- **Next.js**: fetch on the server in Server Components / route handlers (see `nextjs.md`). Client-side fetching only for interactive, user-triggered data.
- **React Native / SPA**: use a cache library (TanStack Query / SWR) — see `state-management.md`. Don't hand-roll fetch-in-`useEffect`.

## Model loading & error explicitly

Always represent all three states; don't render against possibly-undefined data.

```tsx
const { data, isLoading, error } = useQuery({ queryKey: ["todos"], queryFn: getTodos });
if (isLoading) return <Spinner />;
if (error) return <ErrorView error={error} onRetry={refetch} />;
return <List items={data} />; // data is defined here
```

- Discriminated unions make this airtight (see `type-safety.md`). Avoid rendering with `data?.x` everywhere.

## Caching

- Let the library cache by query key; configure `staleTime`/`revalidate` deliberately rather than refetching on every mount.
- Server-rendered data (Next.js): use `fetch` cache/`revalidate` semantics; hydrate the client cache with prefetched data to avoid a second fetch.

## Error boundaries (web) / error states (RN)

- Wrap risky UI subtrees in an error boundary so one failed widget doesn't blank the page; show a recoverable fallback.

```tsx
<ErrorBoundary fallback={<Failed onRetry={reset} />}>
  <Dashboard />
</ErrorBoundary>
```

- Error boundaries catch render errors, not async rejections — surface fetch errors through the query `error` state (or throw in a Suspense+boundary setup).
- React Native has no DOM error UI: render an explicit error component with a retry action.

## Async hygiene

- `async/await`; never leave a floating promise — `await` it, `return` it, or `void` it intentionally. Enable `@typescript-eslint/no-floating-promises`.

```ts
// ❌ floating: errors vanish, ordering unclear
doThing();
// ✅
await doThing();         // or: void doThing();  (fire-and-forget, deliberate)
```

- Parallelize independent work; don't await in series.

```ts
// ❌ sequential
const user = await getUser(id);
const posts = await getPosts(id);
// ✅ concurrent
const [user, posts] = await Promise.all([getUser(id), getPosts(id)]);
```

- Use `Promise.allSettled` when partial failure is acceptable. Cancel stale requests with `AbortController` (or let the query lib handle cancellation on key change).
- Throw `Error` subclasses with a message and `cause`; preserve the original error.

```ts
catch (e) { throw new FetchError("failed to load user", { cause: e }); }
```
