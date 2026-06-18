# Type safety

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [react.dev](https://react.dev), [TypeScript handbook](https://www.typescriptlang.org/docs/handbook/), [zod](https://zod.dev), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (react, nextjs, react-native rule sets).

## Strict mode

- `strict: true` (non-negotiable). Also enable `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`. Treat compiler errors as bugs, not annoyances.
- No `// @ts-ignore` to silence errors; use `// @ts-expect-error` with a reason, or fix the type.

## Avoid `any`; narrow `unknown`

- `any` disables checking and spreads. Ban it (`@typescript-eslint/no-explicit-any`). Use `unknown` at boundaries, then narrow.

```ts
// ❌ trusts the shape
function handle(x: any) { return x.user.name; }

// ✅ accept unknown, narrow before use
function handle(x: unknown): string {
  if (typeof x === "object" && x !== null && "name" in x) {
    return String((x as { name: unknown }).name);
  }
  throw new Error("unexpected shape");
}
```

- Prefer type guards and `in`/`typeof`/`instanceof` over casts. Reserve `as` for genuinely un-inferable cases.

## Validate at the boundary (zod)

Anything from the network, storage, env, or `JSON.parse` is `unknown`. Parse it; don't trust it.

```ts
const UserSchema = z.object({ id: z.string(), name: z.string(), age: z.number().int().optional() });
type User = z.infer<typeof UserSchema>;

const user = UserSchema.parse(await res.json());        // throws on mismatch
const safe = UserSchema.safeParse(input);               // { success, data | error }
```

- Derive types from schemas (`z.infer`) so the runtime check and the static type can't drift.
- Validate env once at startup; export the typed object, not `process.env`.

## Discriminated unions

Model state as a union with a literal tag; handle exhaustively.

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
    default: { const _x: never = r; return _x; } // compile error if a case is added
  }
}
```

- The `never` assignment forces a compile error when a new variant is added — exhaustiveness for free.
- Avoid the "boolean soup" alternative (`isLoading && isError && ...`) — illegal states become representable.

## Precise prop types

- Type props explicitly; avoid `React.FC` (implicit `children`, awkward generics).

```tsx
type ButtonProps = { label: string; onPress: () => void; disabled?: boolean };
function Button({ label, onPress, disabled = false }: ButtonProps) { /* ... */ }
```

- Make impossible prop combinations unrepresentable with unions instead of many optional booleans.

```ts
// ✅ either a link or a button, never both
type Action =
  | { kind: "link"; href: string }
  | { kind: "button"; onPress: () => void };
```

- Reuse element types: `React.ComponentProps<"button">`, `React.ReactNode` for slots, `PropsWithChildren<T>` only when children are truly arbitrary.
- Prefer `readonly` arrays/props and `as const` for literal config to keep inference tight.
