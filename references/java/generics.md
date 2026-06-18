# Generics

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Effective Java 3rd ed, Items 26–33 (https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/).

## No raw types (Item 26)
- Raw `List` defeats compile-time checking. Parameterize, or use `<?>` when the element type is irrelevant.
```java
List<String> names = new ArrayList<>();   // do this
List names = new ArrayList();             // not that (raw, unchecked)
```

## Eliminate unchecked warnings (Item 27)
- Fix every warning you can. When you've *proven* a cast is safe, suppress with the narrowest scope and a comment.
```java
@SuppressWarnings("unchecked")  // safe: array holds only T, see invariant above
T[] result = (T[]) Arrays.copyOf(elements, size, type);
```

## Prefer lists to arrays (Item 28)
- Arrays are covariant + reified; generics are invariant + erased — they mix badly. `new T[]` is illegal; `Object[]` accepts wrong types at runtime.
```java
Object[] a = new Long[1]; a[0] = "x";     // compiles, ArrayStoreException at runtime
List<Object> l = new ArrayList<Long>();   // won't compile — caught early
```
- Prefer `List<E>` fields over `E[]` in generic types.

## PECS — Producer-Extends, Consumer-Super (Item 31)
- Use bounded wildcards to make APIs flexible. A parameter that *produces* T → `extends`; one that *consumes* T → `super`.
```java
void pushAll(Collection<? extends E> src)  { for (E e : src) push(e); }   // producer
void popAll(Collection<? super E> dst)     { while (!empty()) dst.add(pop()); } // consumer
```
- Return types: don't use wildcards in returns (forces wildcards on callers). `Comparable`/`Comparator` are always consumers → `Comparable<? super T>`.

## Generic methods & types (Items 29–30)
- Generify types and static utilities; let the compiler infer type args.
```java
static <E> Set<E> union(Set<E> a, Set<E> b) { ... }
Set<String> s = union(x, y);              // inferred
```
- Use recursive type bounds for "comparable to itself": `<T extends Comparable<T>>`.

## `@SafeVarargs` (Item 32)
- Generic varargs create an unsafe heap-pollution hole. Only annotate `@SafeVarargs` when the method doesn't store into or expose the array. Better: accept `List<T>` instead of `T...`.

## Type-safe heterogeneous containers (Item 33) `[niche]`
- Key a map by `Class<T>` to store mixed types safely.
```java
<T> void put(Class<T> type, T instance);
<T> T get(Class<T> type);
```
