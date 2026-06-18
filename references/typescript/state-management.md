# State management

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [tanstack.com/query](https://tanstack.com/query/latest) (server-state philosophy), [swr.vercel.app](https://swr.vercel.app), [docs.pmnd.rs/zustand](https://docs.pmnd.rs/zustand/getting-started/introduction), [redux-toolkit.js.org](https://redux-toolkit.js.org), [react.dev](https://react.dev) (state), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (react rule set).

## Server state ≠ client state

The single most important distinction. They have different needs; don't manage them with the same tool.

- **Server/remote state**: lives on a server, you only hold a cached copy, can go stale, needs dedup/refetch/retry. → a data-fetching cache (TanStack Query / SWR / RTK Query).
- **Client/UI state**: owned entirely by the app (modals open, form drafts, selected tab, theme). → `useState`/`useReducer` locally; a store only if genuinely shared.

```ts
// ❌ server state hand-rolled in useEffect: no cache, no dedup, races, stale
useEffect(() => { fetch(url).then(setData); }, [url]);

// ✅ let the cache library own it
const { data, isLoading, error } = useQuery({ queryKey: ["user", id], queryFn: () => getUser(id) });
```

## Server state: TanStack Query / SWR

- Stable, serializable query keys; the key is the cache identity.
- Tune `staleTime` (how long data is "fresh") vs `gcTime`; rely on built-in dedup, background refetch, retry.
- Mutations: `useMutation`, then `invalidateQueries` (or optimistic update + rollback) — don't manually patch unrelated caches.

```ts
const m = useMutation({
  mutationFn: updateUser,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ["user", id] }),
});
```

## Client state: Zustand / Redux Toolkit

- Reach for a store only when state is genuinely shared across distant components and `useState` + Context becomes painful. Most apps need less global state than they think.
- **Zustand** for lightweight global state; **Redux Toolkit** when you need its ecosystem (devtools, middleware, strict patterns) on a large app.
- Keep stores slim and domain-focused; don't dump server data into them.

```ts
const useCart = create<CartState>((set) => ({
  items: [],
  add: (i) => set((s) => ({ items: [...s.items, i] })),
}));
```

## Selectors & over-rendering

- Subscribe narrowly. Select the smallest slice you use, not the whole store — broad selection re-renders on unrelated changes.

```ts
// ❌ re-renders on any cart change
const cart = useCart();
// ✅ re-renders only when count changes
const count = useCart((s) => s.items.length);
```

- For object/array selections, use a shallow-equality comparator (`useShallow` in Zustand, `createSelector`/memoized selectors in Redux) to avoid new-reference churn.
- Context has no selector — splitting one Context into several (or pairing with a store) avoids re-rendering all consumers on every change.
