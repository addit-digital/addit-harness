# Performance

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [react.dev](https://react.dev) (Profiler, lazy, Server Components), [nextjs.org/docs](https://nextjs.org/docs) (dynamic import, bundle), [reactnative.dev](https://reactnative.dev) (Performance, JS thread), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (react, nextjs, react-native rule sets).

## Measure first

- Profile before optimizing; fix the actual hot path, not a guess. Use the **React DevTools Profiler** to find what re-renders and why (highlight updates, ranked chart).
- Web: Lighthouse / Web Vitals (LCP, INP, CLS) and the bundle analyzer. RN: the in-app perf monitor, Flipper/Hermes profiler.

## Code-splitting & lazy loading

- Split large or below-the-fold UI so it isn't in the initial bundle.

```tsx
// React
const Chart = lazy(() => import("./Chart"));
<Suspense fallback={<Spinner />}><Chart /></Suspense>

// Next.js (optionally client-only)
const Map = dynamic(() => import("./Map"), { ssr: false, loading: () => <Spinner /> });
```

- Lazy-load heavy dependencies (charts, editors, maps) on demand, not at startup.

## Shrink the client bundle (Next.js)

- Keep logic in **Server Components**; they ship zero JS. Move only the interactive leaf to `"use client"` (see `nextjs.md`).
- Import narrowly (`import { x } from "lib"`, tree-shakeable entry points); avoid pulling whole utility libraries.
- Prefer `next/image` and `next/font` to avoid layout shift and extra requests.

## Virtualize long lists

- Render only what's visible. Web: TanStack Virtual / react-window. RN: `FlatList`/`SectionList` with `getItemLayout` (see `react-native.md`). Never render thousands of rows eagerly.

## React render cost

- Cut wasted re-renders: stabilize props/handlers and `React.memo` hot children — but only where the Profiler shows a cost (see `react.md` on deliberate memoization).
- Keep state local so updates re-render the smallest subtree; select narrowly from stores.

## React Native: protect the JS thread

- The JS thread runs your logic, bridge calls, and gesture/animation callbacks — block it and the UI janks.
- Keep heavy work out of render and gesture handlers; debounce/throttle rapid events; move animations to the native driver / Reanimated worklets.
- Use Hermes; defer non-critical work (`InteractionManager.runAfterInteractions`) until after transitions; lazy-init expensive modules.
