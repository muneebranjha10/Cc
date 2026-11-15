# Combine CC v6 — Frame pacing and smoother closing

**Experimental. Not yet tested on a Samsung device. Not guaranteed 60/120 FPS.**

## Diagnosis
The user's recovered module already schedules its motion clock through Android `Choreographer.postFrameCallback`, using frame timestamps. Therefore a simple “force 120 FPS” flag cannot fix dropped frames; the actual bottleneck may be blur, backdrop capture, GPU render/sync, invalidation, or SystemUI view layout.

## Guarded changes (exact uploaded APK only)
- Carry v5 anti-shrink: press-scale 8% → zero
- Carry v5 anti-blink: individual tile close fade → constant 1.0 (panel-wide fading unchanged)
- Physics: max spring integration step 1/240 s → 1/120 s, reducing repeated CPU integration work per frame
- Transition blur radius: 24dp → 16dp; trades some blur intensity for possible performance gain
- Gentler tile closing/opening: horizontal 22dp → 8dp; header 16dp → 6dp; row stagger 12dp → 4dp; vertical base 36dp → 12dp
- Original liquid glass shader and Xposed entry retained; full liquid-glass appearance still depends on active backdrop/rendering hooks

## GitHub APK build
`v6/patch.py` uses `v5/patch.py` and verifies the exact original SHA-256 `d731fb16db3fee293148731fee962a49432c484dfc5490fea9c8ac94bcd8694c`.

For redistribution safety, **copy the workflow and both patch scripts to a PRIVATE repository** and place the original user-supplied `Combine-CC-Geometry-Experimental.apk` in `input/Combine-CC-Geometry-Experimental.apk`. Run `Actions → Build Combine CC v6 experimental → Run workflow`. GitHub Action uses official Android `zipalign`, `apksigner`, verification and uploads test APK artifact.

Do not publish the original or repacked third-party compiled APK publicly unless you have permission.

## Compatibility
Android 16 / One UI 8 and Android 17 / One UI 9 can meet the manifest's SDK requirements, but Samsung SystemUI hooks remain untested on both releases. Changes to shader contents or a signed APK alone do NOT prove compatibility.

## Before installation
A newly signed APK will conflict with the currently installed version if they use different signing keys. Back up the existing module and prepare a safe LSPosed rollback before attempting an uninstall or test.

**Verification pending:** actual frame times at 120Hz, slow close/drag reversal, flicker, SystemUI crashes and background refresh. If physics looks unstable at 120Hz/60Hz, revert to v5.
