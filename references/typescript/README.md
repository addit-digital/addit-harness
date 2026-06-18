# TypeScript reference (React / Next.js / React Native)

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [react.dev](https://react.dev), [nextjs.org/docs](https://nextjs.org/docs), [reactnative.dev](https://reactnative.dev), [tanstack.com/query](https://tanstack.com/query/latest), [react-hook-form.com](https://react-hook-form.com), [zod](https://zod.dev), [testing-library.com](https://testing-library.com), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (react, nextjs, react-native rule sets).

Tier-2 reference material — read on demand, not auto-loaded. The always-on
essentials live in `../../rules/typescript.md`. Focus: React, Next.js (App
Router), React Native (frontend/mobile, not backend Node). Open only the topic
file you need:

- **[type-safety.md](type-safety.md)** — open for strict-mode config, killing `any`/narrowing `unknown`, zod boundary validation, discriminated unions, and precise prop types.
- **[react.md](react.md)** — open for component/hook patterns: rules of hooks, `useEffect` (synchronize vs derive), keys, deliberate memoization, state placement, composition.
- **[nextjs.md](nextjs.md)** — open for App Router work: Server vs Client Components, server actions/route handlers, fetch caching/revalidation, loading/error/not-found, `next/image` & `next/font`, the secrets boundary.
- **[react-native.md](react-native.md)** — open for mobile: platform differences, FlatList/SectionList, typed navigation, native-driver/Reanimated animations, safe areas/keyboard/back button, Expo modules.
- **[state-management.md](state-management.md)** — open to decide where state lives: server vs client state, TanStack Query/SWR for server state, Zustand/Redux Toolkit for client, selectors to avoid over-rendering.
- **[data-fetching.md](data-fetching.md)** — open for fetch patterns (web & RN), loading/error modeling, caching, error boundaries, and async hygiene (no floating promises, `Promise.all`).
- **[forms-validation.md](forms-validation.md)** — open for forms: React Hook Form + zod, controlled vs uncontrolled, RN inputs, accessibility basics.
- **[testing.md](testing.md)** — open for tests: Jest/Vitest + Testing Library (web & RN), test behavior not internals, MSW for network, Detox/Maestro/Playwright for E2E, typed test data.
- **[performance.md](performance.md)** — open for perf: code-splitting/dynamic import, virtualization, Server Components to shrink bundles, the RN JS thread, the React DevTools Profiler.
