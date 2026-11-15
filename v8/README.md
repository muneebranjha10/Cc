# Combine CC v8 — Smooth full-panel fade (experimental)

This version builds on v7 and is meant to reproduce the **simple blur + whole-panel fade** animation chosen in the reference recording `130845.mp4`. It does **not** attempt liquid-glass morphing or per-icon spring movement.

## The actual modifications

- **Closing:** `Panel.update()` previously used `clamp(4 * progress)` for the complete sheet/player opacity, keeping the panel opaque for most of a swipe and causing a late abrupt disappearance. Change it to `clamp(progress)` for continuous, gesture-following fading.
- **Opening:** when not closing, `Panel.update()` previously forced sheet/player opacity to 1.0. Use the same progress value for fade-in.
- **Icons:** preserve the v7 changes to keep tiles at their original size with no independent horizontal/vertical stagger.
- **Renderer:** unchanged. No claim that background capture, FPS or pixel-exact visuals have been fixed.
- **Version:** `0.99.v8` (versionCode 159), to distinguish installed APKs.

The bytecode patch verifies the exact v7 input hash and instruction layout and updates DEX checksums. GitHub Actions uses official Android `zipalign` and `apksigner` and performs signature validation.

## GitHub APK

The `Build and publish Combine CC v8 candidate` workflow uses the already-present `releases/CombineCC-v7-UNTESTED.apk`, applies `v8/patch.py`, and pushes `releases/CombineCC-v8-UNTESTED.apk` if signing and validation succeed. If the workflow fails, there is no release APK; examine the workflow logs.

For long-term update installs, provide an Android signing keystore through repository Actions secrets. Otherwise each run creates an independent test signing key and will not install over an existing differently signed package.

## Safety and compatibility

- The original source includes third-party modules; check redistribution permission before public release.
- One UI 8 / Android 16: untested at runtime.
- One UI 9 / Android 17: untested at runtime.
- Back up the installed module and its settings before attempting to uninstall a differently signed version.
- Test slowly dragging up/down, reversing mid-gesture, lockscreen, split QS, rotation, phone calls/notifications, and SystemUI restarts. If SystemUI behaves badly, disable this LSPosed module from the manager or recovery and restore the previous version.
- **This is a test candidate, not a verified fix.** Only actual device testing can establish that frame pacing and closing behavior improved.
