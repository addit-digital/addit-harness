---
paths: ["**/*.tsx", "**/{components,features,hooks,app,screens}/**/*.ts"]
---

# Frontend (React / Next.js / React Native)

<!-- frontend-contract:start -->
## Frontend Implementation Contract (React / Next.js / React Native)

Hard limits. A project's ESLint config or CLAUDE.md may tighten a number, never loosen it.
"Lines" means non-blank lines (grep -cv '^[[:space:]]*$'). The limits are deliberately
stricter than ESLint defaults. A limit may be exceeded only with a one-line reason in
your final report ("FC-2 exceeded in data-table.tsx: column config is declarative").

| ID | Rule | Limit |
|----|------|-------|
| FC-1 | Lines per component/hook file | ≤ 150 (never > 250) |
| FC-2 | Lines per component function incl. JSX | ≤ 80 |
| FC-3 | JSX nesting depth within one component | ≤ 4 levels (`react/jsx-max-depth` max 4); extract a named child beyond that |
| FC-4 | Declared props per component (spread native attributes excluded) | ≤ 7; beyond that use composition (children/slots) or split. ≤ 2 boolean style flags; otherwise a `variant` union |
| FC-5 | Cognitive complexity per function | ≤ 10 (`sonarjs/cognitive-complexity`; measured only where configured); no nested ternaries in JSX |
| FC-6 | Hooks in one component | ≤ 3 state/effect hooks, else extract a custom hook named for its one job (`useCartTotals`, not `useCartLogic`). `useEffect` only to sync with an external system, never for derived state or data fetching |
| FC-7 | Layering | Components never call `fetch`/axios/SDKs directly. Server Components (Next.js page/layout) may await a feature api/ function. Server data goes through the feature's `api/` hooks (the project's server-cache lib). Presentational components get data via props and emit events via callbacks. Routes/screens/pages only compose |
| FC-8 | Boundaries | Feature code lives in `features/<name>/{api,components,hooks,utils,types}` (only the folders needed). No cross-feature imports; compose at app/route level. Import direction: shared → features → app. No barrel files |
| FC-9 | One component per file | No `renderX()` helpers or components defined inside components. A private child ≤ 30 lines may share its parent's file |
| FC-10 | Reuse and tokens | Never re-implement something the reuse inventory found. Promote to shared (`components/`, `hooks/`, `utils/`) only with ≥ 2 real consumers now. No raw hex/px/ms literals or arbitrary Tailwind `[...]` values where a token exists |

Conflict resolution: match the existing project first. In greenfield, follow
bulletproof-react (`references/typescript/react/`; full conflict table in
`references/typescript/README.md`): kebab-case filenames, named exports. Default
exports only where the framework requires them (Next.js
`page`/`layout`/`template`/`loading`/`error`/`not-found`, expo-router screens, tool
config files; `route.ts` uses named `GET`/`POST`). The sanjeed5 guides are lookup
material; bulletproof wins where they disagree.

Figma/design-to-code output is a visual spec, not code to paste. Map every
region to an existing component first, split the frame per FC-1 to FC-9, and
replace literal values with tokens (FC-10).
<!-- frontend-contract:end -->

## Visual design
- `.claude/design-conventions.md` exists: follow it (`/design-conventions` refreshes it).
- Absent but UI exists: derive tokens and scales from the Tailwind config, token
  files and existing screens before writing a component.
- Greenfield: `@frontend-architect` writes the file before substantial implementation.
