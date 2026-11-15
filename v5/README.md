# Combine CC v5 — experimental anti-blink and anti-shrink patch

**Use the project ZIP from ChatGPT for the complete local-build scripts and original APK.** This public repository contains the reproducible DEX patch and GitHub Actions build instructions, **not the third-party original binary**.

## Changes to the actual uploaded Combine CC APK

- Tile press compression: 8% → **0%**
- Per-tile closing fade: close-progress alpha → **constant 1.0** (addresses disappearing/blinking icons during slow gestures)
- Reduced opening movement carried from v4: lateral 22→12dp, header 16→10dp, row 12→8dp, base 36→22dp
- Leaves original ColorCC controls, LSPosed entry `dev.colorcc.Hook`, existing liquid-glass shaders and SystemUI hooks unchanged
- Works with exact input APK SHA-256 `d731fb16db3fee293148731fee962a49432c484dfc5490fea9c8ac94bcd8694c`. Fails closed if a different APK is used

## Android compatibility

The **original** APK declares `minSdkVersion=33`, `targetSdkVersion=36`, so it is *installable in principle* on Android 16 / One UI 8 and Android 17 / One UI 9. Actual Samsung SystemUI hook compatibility and visual behavior have **not** been tested on either OS. One UI 8 support must not be called confirmed until device testing.

## Reproducible GitHub build

Copy this patcher and workflow into a **private repository** and include your `input/Combine-CC-Geometry-Experimental.apk`. Use Actions → **Build Combine CC v5 candidate**. GitHub builds with official Android SDK `zipalign` and `apksigner` and uploads the APK as a workflow artifact.

Do **not** upload other developers' compiled APKs into a public repository without redistribution permission.

**Caution:** This candidate has a different signature from the original installed app and cannot be installed as an update without uninstalling the older signed package. Back up the working APK/settings and have an LSPosed rollback path before testing. This is not a fully tested glass port.