# React Native

*On-demand reference (not auto-loaded). Part of the TypeScript (React/Next.js/React Native) conventions set; see ../../rules/typescript.md for the always-on essentials.*

Sources: [reactnative.dev](https://reactnative.dev) (Platform, FlatList, Animated/native driver), [reactnavigation.org](https://reactnavigation.org) (typing), [docs.swmansion.com/react-native-reanimated](https://docs.swmansion.com/react-native-reanimated/), [docs.expo.dev](https://docs.expo.dev), [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) (react-native rule set).

## Platform differences

- Branch with `Platform.OS` / `Platform.select`; for larger divergence use `*.ios.tsx` / `*.android.tsx` files (resolved automatically).

```ts
const pad = Platform.select({ ios: 12, android: 16, default: 12 });
```

## Lists: FlatList / SectionList

- Never `ScrollView` + `.map()` for long/unbounded data — it mounts everything. Use `FlatList`/`SectionList` (virtualized).

```tsx
<FlatList
  data={items}
  keyExtractor={(it) => it.id}              // stable key, not index
  renderItem={({ item }) => <Row item={item} />}
  getItemLayout={(_, i) => ({ length: H, offset: H * i, index: i })} // if rows are fixed height
  initialNumToRender={10}
  removeClippedSubviews
/>
```

- Memoize `renderItem` and row components; keep item data references stable to avoid full re-renders.

## Typed navigation

- Type route params centrally so `navigate`/`useRoute` are checked.

```ts
type RootStackParamList = { Home: undefined; Profile: { userId: string } };
const Stack = createNativeStackNavigator<RootStackParamList>();

navigation.navigate("Profile", { userId: "42" }); // ✅ checked
const { userId } = useRoute<RouteProp<RootStackParamList, "Profile">>().params;
```

- For Expo Router, rely on its typed-routes feature; keep `href`s typed.

## Animations on the native thread

- Run animations off the JS thread for 60fps: `useNativeDriver: true` (Animated) or Reanimated worklets. JS-thread jank stalls all animation.

```ts
Animated.timing(opacity, { toValue: 1, duration: 200, useNativeDriver: true }).start();
```

- `useNativeDriver` supports transforms/opacity, not layout props (width/height/top). Animate transforms; avoid animating layout.

## Safe areas, keyboard, back button

- Wrap screens with `SafeAreaProvider` + `useSafeAreaInsets` (or `SafeAreaView`) — don't hardcode notch padding.
- Use `KeyboardAvoidingView` (behavior `padding` on iOS, `height`/none on Android) or a keyboard-aware library for forms.
- Handle Android hardware back with `BackHandler` and clean up the listener on unmount.

```ts
useEffect(() => {
  const sub = BackHandler.addEventListener("hardwareBackPress", onBack);
  return () => sub.remove();
}, [onBack]);
```

## Native modules & Expo

- Access device/native APIs through Expo modules (`expo-camera`, `expo-location`, etc.) or vetted libraries; prefer Expo's managed APIs first.
- Request permissions explicitly, handle denial, and release resources (camera, location watchers, sensors) on unmount.
- Keep heavy synchronous work out of render and gesture handlers to protect the JS thread; offload to native/Reanimated where possible.
