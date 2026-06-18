# Next.js (App Router)

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [nextjs.org/docs](https://nextjs.org/docs) (App Router, Server/Client Components, data fetching & caching, server actions, file conventions, next/image, next/font), [react.dev](https://react.dev) (Server Components, Suspense), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (nextjs rule set).

## Server vs Client Components

- **Server Components by default.** They run on the server, can be `async`, fetch data directly, and ship zero JS to the client.
- Add `"use client"` only when you need state, effects, event handlers, refs, or browser APIs. The directive marks an entry into the client tree — everything imported below it is client too.
- Push the client boundary as far down as possible: a small interactive leaf, not the whole page. Pass Server Components into client ones as `children` to keep them server-rendered.

```tsx
// app/page.tsx — Server Component (no directive)
export default async function Page() {
  const products = await getProducts();        // runs on server
  return <ProductList products={products} />;   // list can be server; only the leaf is client
}
```

```tsx
// components/like-button.tsx
"use client";
export function LikeButton() {
  const [liked, setLiked] = useState(false);   // needs state → client
  return <button onClick={() => setLiked(v => !v)}>{liked ? "♥" : "♡"}</button>;
}
```

## Data fetching, caching, revalidation

- Fetch on the server, colocated with the component that needs it. Independent fetches in parallel (`Promise.all`) to avoid waterfalls.
- Control caching deliberately with `fetch` options or route segment config.

```ts
await fetch(url, { cache: "force-cache" });          // static (default-ish), cached
await fetch(url, { next: { revalidate: 60 } });      // ISR: revalidate every 60s
await fetch(url, { cache: "no-store" });             // always dynamic, per-request
export const revalidate = 3600;                       // segment-level default
```

- Use `revalidatePath` / `revalidateTag` after a mutation to refresh cached data.

## Server actions & route handlers

- Mutations via Server Actions (`"use server"`) or route handlers (`app/api/.../route.ts`). Treat both like public API endpoints: validate input (zod) and authorize every call.

```ts
"use server";
export async function createPost(formData: FormData) {
  const data = PostSchema.parse(Object.fromEntries(formData)); // validate
  await requireUser();                                          // authorize
  await db.post.create({ data });
  revalidatePath("/posts");
}
```

## loading / error / not-found

- `loading.tsx` → instant Suspense fallback while the segment streams.
- `error.tsx` → error boundary for the segment (must be a Client Component; gets `reset()`).
- `not-found.tsx` → 404 UI; trigger with `notFound()`.
- Wrap slow sub-trees in `<Suspense>` to stream the fast parts first.

## Assets, fonts, metadata

- Images via `next/image` (auto sizing, lazy-load, format negotiation); always set `width`/`height` or `fill` + `sizes`.
- Fonts via `next/font` (self-hosted, zero layout shift, no external request).
- SEO via the Metadata API (`export const metadata` / `generateMetadata`), not manual `<head>` tags.

## Secrets boundary

- **Never** put secrets or server-only logic in a Client Component — anything in the client bundle is public.
- Only `NEXT_PUBLIC_*` env vars reach the browser; keep everything else server-side.
- Use `import "server-only"` to make a module fail the build if imported into client code.
