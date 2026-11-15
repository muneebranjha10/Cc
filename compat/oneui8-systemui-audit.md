# One UI 8 SystemUI compatibility audit — Samsung Android 16

**Evidence:** User-uploaded `System UI.apk`, SHA-256 `6ca6fa7659835cfa049932bf7652b6ab5fdb6d1c812e2c0139038d8b98f0a048`. The binary is **not** uploaded to this public GitHub repository.

## APK identifiers

- Manifest package: `com.android.systemui`
- Version code: `36`
- Version name: `16`
- Minimum / target SDK: **36 / 36** (Android 16; consistent with One UI 8)
- Four DEX files: classes.dex (10,294,976), classes2.dex (10,774,660), classes3.dex (10,811,188), classes4.dex (6,120,640)
- ZIP integrity verified, 9,280 entries.
- The manifest does **not** independently identify the exact One UI revision or device model. User reports this as One UI 8.

## Combine CC SystemUI hook compatibility: detected

All the following exact class names in current `dev.colorcc.Hook.install` have matching defined classes in the uploaded SystemUI:

- `com.android.systemui.shade.NotificationPanelViewController`
- `com.android.systemui.qs.QSHostAdapter`
- `com.android.systemui.samsung.quicksetting.SecQSPanelComposeAdapter`
- `com.android.systemui.qs.QSContainerImpl`
- `com.android.systemui.shade.SecPanelSplitHelper`
- `com.android.systemui.qs.animator.PanelTransitionAnimator`
- `com.android.systemui.shade.PanelSlideEventHandler`
- `com.android.systemui.qs.QSFragmentLegacy`
- `com.android.systemui.qs.composefragment.QSFragmentCompose`
- `com.android.systemui.qs.SecQSDetailController`
- `com.android.systemui.qs.QSImpl`

Confirmed **declared** method signatures:

```
PanelTransitionAnimator.slide(float,float,PanelSlideEventHandler.Direction,int): void
PanelSlideEventHandler.createSlideAnimatorAndRun(float,float): void
PanelSlideEventHandler.onPanelExpansionChanged(ShadeExpansionChangeEvent): void
SecPanelSplitHelper.onPanelExpansionChanged(ShadeExpansionChangeEvent): void
SecPanelSplitHelper.slide(float,PanelSlideEventHandler.Direction,boolean): void
QSFragmentLegacy.closeDetail(): void
QSImpl.closeDetail(): void
SecQSDetailController.closeDetail(): void
QSFragmentCompose.closeDetail(): void
```

**Missing method:**
`SecQSPanelComposeAdapter.setLegacyDetailVisible(boolean)` was **not declared or found** in this APK. The current hook's optional path around this name must remain guarded. Do not assume that method exists on One UI 8.

## What this proves and what it does not

**Proves:** The user-provided SystemUI shares major class/method targets with the Combine CC hook implementation. An Android 16 phone can meet Combine CC's minSdkVersion 33 requirement.

**Does NOT prove:** Hooks actually run at boot, all reflected fields and method parameter types match in every branch, glass backdrop capture works, FPS is 60/120, tile-close animation is fixed, or One UI 9 compatibility. No live One UI 8 device was available for execution.

## Recommended implementation/testing

1. Check SDK and actual feature/class presence on module load; never infer compatibility from version string alone.
2. Only install the matching subset of hooks: each optional `findClassIfExists`, `findAndHookMethod` or `hookAllMethods` should use granular guards and log missing targets without preventing module startup.
3. If `setLegacyDetailVisible` is missing, prefer available `closeDetail()` implementations or simply skip that optional hook; avoid blindly invoking non-existent methods.
4. Derive animation geometry from stable measured tile bounds; avoid cumulative transforms for slow drag/reversal.
5. Keep renderer capture work off the main thread, do not force a nominal FPS, profile actual SystemUI frame time.
6. **Test on One UI 8** before saying it works; compare against an actual One UI 9 SystemUI.apk for accurate cross-version adaptation.
7. Use a signed, ZIP-aligned APK with a stable signing certificate, keep original installed version safe and prepare rollback.

This is a **source-level compatibility assessment**, not an APK release or a working on-device certification.
