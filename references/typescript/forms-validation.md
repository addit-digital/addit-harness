# Forms & validation

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [react-hook-form.com](https://react-hook-form.com), [zod](https://zod.dev), [react.dev](https://react.dev) (controlled/uncontrolled inputs), [react-hook-form.com/get-started#ReactNative](https://react-hook-form.com/get-started#ReactNative), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (react, react-native rule sets).

## React Hook Form + zod

- Prefer a form library over hand-rolled `useState` per field — fewer re-renders, built-in validation wiring, less boilerplate.
- Define the schema once with zod; derive the form type; wire it with the resolver. One source of truth for shape + validation.

```tsx
const SignupSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});
type SignupValues = z.infer<typeof SignupSchema>;

function Signup() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<SignupValues>({ resolver: zodResolver(SignupSchema) });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <label htmlFor="email">Email</label>
      <input id="email" type="email" {...register("email")} aria-invalid={!!errors.email} />
      {errors.email && <p role="alert">{errors.email.message}</p>}
      <button disabled={isSubmitting}>Sign up</button>
    </form>
  );
}
```

- Reuse the same zod schema on the server (Server Action / route handler) so client and server validation can't diverge.

## Controlled vs uncontrolled

- RHF is **uncontrolled by default** (`register`) — the DOM holds the value; this is the performant path, minimal re-renders.
- Use `Controller` only for components that don't expose a ref / native input (custom selects, date pickers, most RN inputs).

```tsx
<Controller
  control={control}
  name="country"
  render={({ field }) => <CountrySelect value={field.value} onChange={field.onChange} />}
/>
```

- Don't mix: a field is controlled or uncontrolled, not both (avoids the "changing from uncontrolled to controlled" warning).

## React Native

- RN `TextInput` has no `register` ref API — wrap every field in `Controller`, mapping `onChangeText` → `field.onChange` and `value` → `field.value`.

```tsx
<Controller control={control} name="email" render={({ field }) => (
  <TextInput value={field.value} onChangeText={field.onChange} keyboardType="email-address" />
)} />
```

## Accessibility basics

- Every input has an associated label (`<label htmlFor>` or `aria-label`); placeholders are not labels.
- Mark invalid fields with `aria-invalid` and link the message via `aria-describedby`; render errors in a `role="alert"` region so they're announced.
- Keep focus order logical; move focus to the first error on failed submit.
- RN: set `accessibilityLabel`, `accessibilityHint`, and appropriate `accessibilityRole`/keyboard type on inputs.
