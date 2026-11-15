# Combine CC v7 — stable-close experiment

**Ready-made APK:** [Download v7 directly from GitHub](https://raw.githubusercontent.com/muneebranjha10/Cc/main/releases/CombineCC-v7-UNTESTED.apk)

**APK SHA-256:** `fdad10b92770925cf9d1a0cf8c7f0b6b0e756ce250d21ceda387afd21583e898`  
**Version shown in Android Apps:** `0.99.v7` (versionCode 158).  
**Package:** `dev.colorcc`; LSPosed entry `dev.colorcc.Hook`.  

## What's genuinely changed from v6

- All four per-tile travel/stagger distances reduced to **0dp** during opening/closing, replacing the previous shrink-looking slide with more stable tiles.
- Removed per-tile **hardware-layer promotion** during the transition. Normal RenderNode GPU rendering remains; this is an experiment to reduce transient texture churn and flicker.
- Changed closing sheet fade multiplier **2 → 4** to hold tiles visible longer during slow swipes, with a shorter ending fade.
- Reverted v6's spring calculation substep (1/120s) to the original 1/240s for integration stability. This does **not** set display refresh rate.
- Kept the existing v5/v6 anti-press-shrink and per-tile alpha-1 changes, original glass shaders, ColorCC controls, and all existing hooks.
- Added an identifiable version: **0.99.v7**.

## Tested vs. not tested

Confirmed locally: original Xposed entry, original resources and AGSL shader strings retained, 4-byte aligned resource table, correct DEX hashes, ZIP integrity, independent APK v2 signature, manifest version identification. This APK is uploaded to GitHub as a complete binary (not just a workflow).

**Not confirmed:** an S23 actually installing or loading it; exact One UI 8 or One UI 9 SystemUI runtime-hook compatibility; FPS; visual closing behavior; backdrop capture correctness. The uploaded One UI 8 SystemUI audit in `compat/oneui8-systemui-audit.md` confirms many class/method names but identifies a missing optional method; it does not guarantee full support. One UI 9 has not been reverified against a matching SystemUI binary here.

## Install / rollback

- DO NOT uninstall a stable setup without backing up the original APK and relevant settings first.
- This v7 APK uses a **new test certificate**, so Android cannot update an installed ColorCC/Combine CC with a different signature. An uninstall may be required after you've prepared a backup; app preferences may be erased.
- Disable the old module in LSPosed before testing; scope only the appropriate SystemUI process, reboot, and know how to disable the new module if SystemUI crashes.
- If Android says "App not installed", capture the exact PackageInstaller error before another rebuild.

## Rebuild

The script `v7/patch.py` operates on the exact published v6 APK SHA-256 `0746c5ad0aa2e18f3d79d16d76780f88821535c3cbbf6768475f30a31c465346` and fails if source bytes differ. It produces an **unsigned** APK. Use official Android SDK `zipalign` and `apksigner` for future builds and your own private signing key for updatable releases.

**This is an experimental visual stabilization release, not proof of 120 FPS or full liquid-glass feature parity.**
