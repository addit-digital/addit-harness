# Testing

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [testing-library.com](https://testing-library.com) (React & React Native), [vitest.dev](https://vitest.dev), [jestjs.io](https://jestjs.io), [mswjs.io](https://mswjs.io), [playwright.dev](https://playwright.dev), [wix.github.io/Detox](https://wix.github.io/Detox/), [maestro.dev](https://maestro.dev), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (react, nextjs, react-native rule sets).

## Runner + Testing Library

- Use the project's runner: **Vitest** (Vite/modern) or **Jest** (CRA/RN/Expo). Pair with **React Testing Library** (web) or **React Native Testing Library**.

## Test behavior, not internals

- Query by what the user perceives — roles, labels, text — not by class names, test ids (last resort), or component internals.
- Don't assert on state/props/private methods; assert on rendered output and effects.

```ts
it("submits the form", async () => {
  render(<Signup onSubmit={onSubmit} />);
  await userEvent.type(screen.getByLabelText(/email/i), "a@b.com");
  await userEvent.click(screen.getByRole("button", { name: /sign up/i }));
  expect(onSubmit).toHaveBeenCalledWith({ email: "a@b.com" });
});
```

- Prefer `findBy*`/`waitFor` for async UI over arbitrary timeouts. Use `userEvent` over `fireEvent` (it models real interaction).

## Mock at boundaries — MSW for network

- Mock the network at the HTTP boundary with **MSW**, not by stubbing `fetch` or your data layer. Tests exercise real request/response handling.

```ts
const server = setupServer(
  http.get("/api/user/:id", () => HttpResponse.json({ id: "1", name: "Ada" })),
);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

- Don't mock internal pure functions — test them directly or through the component that uses them.
- RN: mock native modules at the module boundary; many libraries ship Jest mocks.

## Typed test data

- Type fixtures and factories — no `any` in tests. A typed factory keeps test data valid as types evolve.

```ts
const makeUser = (over: Partial<User> = {}): User => ({ id: "1", name: "Ada", ...over });
```

## E2E

- Web: **Playwright** for critical user flows across real browsers.
- React Native: **Detox** (gray-box, JS-driven) or **Maestro** (black-box, YAML flows) for key journeys on device/simulator.
- Keep E2E suites small and high-value; rely on unit/integration tests for breadth (test pyramid).

## Discipline

- Add a regression test with every bug fix — reproduce first, then fix.
- Keep tests deterministic: control time/randomness, no real network, no shared mutable state between tests.
