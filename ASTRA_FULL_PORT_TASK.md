# ASTRA FULL-PORT MISSION: ColorCC + ControlCenter 1.4 Liquid Glass

This is the **real implementation target**, NOT the shader-only v3 experiment in the rest of this repository.

## Goal
Produce **one ColorCC APK** for rooted Samsung Galaxy S23, One UI 9, Android 17, KernelSU/LSPosed. Keep **ColorCC's existing UI/layout, tiles, brightness/volume sliders, gestures, options and SystemUI hooks**. Integrate the glass rendering from ControlCenter 1.4 (or recreate equivalent effects where direct integration is impossible): backdrop refraction, RGB spectral dispersion, edge glints, blur/depth, pressed lens bulge, spring motion, merging/morphing glass when feasible. No module selector or second panel.

## Get the inputs
The user has the original `ColorCC (1).apk` (sha256 `58666f0b9ead768ab0be584520e2e43ad7d6814deb77049618ebde76e47bdeae`) and `ControlCenter-1.4 (1).apk` (sha256 `41d4d423e3d9ada372bc048a39ed2bc2b506e3b8aa1a058272f14bf8395ed5c8`). **Do not commit third-party APKs to this PUBLIC repository**; move to a private working repo if you need to store the binaries.

ColorCC's Xposed entry point: `dev.colorcc.Hook`; ControlCenter's entry point: `dev.flexy.controlcenter.Entry`. Both hook Samsung `com.android.systemui`. The earlier APK only modified one AGSL shader string and failed the user's visual and installation tests. Do not claim it is the finished port.

## Implementation checklist
1. Diagnose Android `App not installed` from the user's actual PackageManager failure code, including possible signature mismatch, malformed APK, or profile conflict.
2. Decode and inspect BOTH originals using jadx and Apktool 3.0.3. Map SystemUI view hooks, glass AGSL uniforms, backdrop capture, render passes, touch and spring animation.
3. Reconstruct/edit the **ColorCC implementation**; retain its Xposed entry point and controls; add genuine rendering and animation updates wired to its active view tree. Do not paste an unrelated shader into dormant code.
4. Make renderer compatible with Galaxy S23 and graceful on missing backdrop/state; instrument logs and test shader compilation.
5. GitHub Actions must build reproducibly, align using zipalign, sign with Android SDK apksigner, verify signatures, upload candidate APK. Use a stable signing key in Actions Secrets for subsequent versions; no original developer key is available.
6. Install the result on the Galaxy S23, enable the LSPosed SystemUI scope, test all toggles, sliders, motion, memory/performance, and record proof. Offer rollback directions.
7. Report which effects work, which don't, the exact artifact link, build log, and the PackageManager error if installation still fails.

**Never mark a successful signed baseline APK as a complete glass port. The full port requires actual visual proof on the target device.**

The user has a separate ZIP named `ColorCC-Astra-FullPort-Starter.zip` with original APKs, a fuller `ASTRA_TASK.md`, decode scripts and CI diagnostic/full-candidate workflow. Use it as the main project when available.

## Astra instruction
Read this file and implement, not just outline. If implementation is blocked, state precisely which class/hook/compiler or device test is blocking instead of fabricating a working APK.
