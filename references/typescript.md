# TypeScript — extensive conventions & patterns (React / Next.js / React Native)

On-demand reference (not auto-loaded). Read this for substantial frontend/mobile
work. The always-on essentials live in `rules/typescript.md`. Focus: React,
Next.js (App Router), React Native. Adapted from the React/Next.js docs and
[awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)
(react, nextjs, react-native rule sets).

## Type safety (shared)
- `strict: true`. Treat compiler errors as bugs, not annoyances.
- Validate anything from the network/storage at the boundary; don't trust shapes:
  ```ts
  const UserSchema = z.object({ id: z.string(), name: z.string() });
  type User = z.infer<typeof UserSchema>;
  const user = UserSchema.parse(await res.json());
  ```
- Discriminated unions for state; exhaustive handling:
  ```ts
  type Remote<T> =
    | { status: "loading" }
    | { status: "error"; error: Error }
    | { status: "ok"; data: T };
  function render<T>(r: Remote<T>) {
    switch (r.status) {
      case "loading": return spinner();
      case "error":   return errorView(r.error);
      case "ok":      return view(r.data);
      default: { const _x: never = r; return _x; }
    }
  }
  ```
- Prefer precise prop types; avoid `React.FC` (implicit children); type props
  explicitly:
  ```ts
  type ButtonProps = { label: string; onPress: () => void; disabled?: boolean };
  function Button({ label, onPress, disabled = false }: ButtonProps) { ... }
  ```

## React component patterns
- Function components + hooks only. Keep components small and composable; extract
  custom hooks for reusable stateful logic (`useDebounce`, `useUser`).
- **Rules of hooks:** call hooks unconditionally at top level; never in
  loops/conditions. Lint with `eslint-plugin-react-hooks`.
- **`useEffect`:** complete dependency arrays; effects are for *synchronizing with
  external systems*, not for deriving state. Derive during render instead:
  ```ts
  // ❌ effect to compute derived value
  // ✅ compute in render (memoize only if expensive)
  const fullName = `${first} ${last}`;
  ```
  Clean up subscriptions/timers in the effect's return.
- **Keys:** stable ids, never array index for dynamic lists.
- **Memoization is deliberate, not reflexive.** Reach for `useMemo`/`useCallback`/
  `React.memo` when you've identified a real re-render cost or referential-equality
  need — not by default.
- **State placement:** keep state as local as possible; lift only to the nearest
  common ancestor. Avoid prop-drilling deep trees — use context for truly global,
  low-churn values (theme, auth), not high-frequency state.

## State management
- Server/remote state ≠ client state. Use a data-fetching library
  (TanStack Query / RTK Query / SWR) for server state: caching, dedup,
  background refetch — don't hand-roll in `useEffect`.
- Client/UI state: `useState`/`useReducer` locally; a store (Zustand/Redux
  Toolkit) only when state is genuinely shared and complex. Keep stores slim;
  select narrowly to avoid over-rendering.
- Forms: a library (React Hook Form) + schema validation (zod) over manual state.

## Next.js (App Router)
- **Server Components by default.** Add `"use client"` only when you need state,
  effects, event handlers, or browser APIs. Push client boundaries as far down
  the tree as possible (a small interactive leaf, not the whole page).
- Fetch data on the server (in Server Components / route handlers / server
  actions); colocate fetching with the component that needs it. Use the built-in
  `fetch` caching/revalidation semantics deliberately (`revalidate`, `no-store`).
- **Never** put secrets or server-only logic in client components; use server
  actions or route handlers (`app/api/.../route.ts`) for mutations.
- Use `loading.tsx`/`error.tsx`/`not-found.tsx` for streaming and error UX.
  Stream with Suspense for slow data.
- Images via `next/image`; fonts via `next/font`; metadata via the metadata API.
- Keep `'use server'` actions validated and authorized — treat them like API
  endpoints.

## React Native (mobile)
- Mind platform differences: `Platform.OS` / `Platform.select`, and `*.ios.tsx` /
  `*.android.tsx` files for divergent implementations.
- Keep the JS thread free: avoid heavy synchronous work in render or handlers;
  use `FlatList`/`SectionList` (with `keyExtractor`, `getItemLayout` where
  possible) for long lists, not `ScrollView` + `map`.
- Use the project's navigation library consistently (React Navigation / Expo
  Router); type the route params.
- Animations on the native driver (`useNativeDriver: true`) or Reanimated for
  60fps; avoid animating layout on the JS thread.
- Handle safe areas, keyboard avoidance, and back-button (Android) explicitly.
- Access native/device APIs through Expo modules or vetted libraries; clean up
  listeners/permissions.

## Async & errors
- `async/await`; never leave a floating promise (await, return, or `void` it).
- Parallelize independent work: `await Promise.all([...])`, not sequential awaits.
- Throw `Error` subclasses with messages and `cause`; surface user-facing errors
  through error boundaries (web) / error states (RN).
- Wrap risky UI subtrees in an error boundary; show a recoverable fallback.

## Testing
- Use the project's runner (Jest/Vitest) + React Testing Library (or RN Testing
  Library). Test behavior the user observes (roles, text, interactions), not
  implementation details:
  ```ts
  it("submits the form", async () => {
    render(<Signup onSubmit={onSubmit} />);
    await userEvent.type(screen.getByLabelText(/email/i), "a@b.com");
    await userEvent.click(screen.getByRole("button", { name: /sign up/i }));
    expect(onSubmit).toHaveBeenCalledWith({ email: "a@b.com" });
  });
  ```
- Mock at boundaries (network via MSW, native modules), not internal pure
  functions. Type test data (no `any`).
- E2E with Playwright (web) / Detox or Maestro (RN) for critical flows.
- Add a regression test with every bug fix.

## Performance
- Web: code-split (dynamic `import`), lazy-load below-the-fold, avoid large client
  bundles (keep logic in Server Components), virtualize long lists.
- Profile with React DevTools Profiler before optimizing; fix the actual hot path.
