# ColorCC Glass Edition (experimental)

This repository builds a modified **ColorCC 0.99.58** APK for personal testing. It retains ColorCC's existing layout, functions, and LSPosed entry point while adjusting its embedded AGSL shader to add more visible lens refraction, RGB dispersion, and glass highlights.

It is a **partial renderer port**, not a complete copy of the animation, merge/morph, or backdrop systems from ControlCenter 1.4. Device compatibility on Samsung One UI 9 / Android 17 is not yet confirmed.

## GitHub Actions build
1. Upload your original `ColorCC (1).apk` as `input/ColorCC.apk` to a **private copy** of this repository. Do not publish third-party APKs without permission.
2. Open **Actions → Build ColorCC Glass Edition → Run workflow**.
3. After a successful run, download **ColorCC-GlassEdition-Experimental** from the run's **Artifacts**. Extract its APK.

The workflow can also accept a publicly accessible HTTPS `base_apk_url`; avoid passing private URLs in public workflow logs.

The build replaces the existing ColorCC lens shader, validates the APK, and signs it with Android's `apksigner`. Each CI build uses a fresh test certificate; uninstall an older copy first if certificate mismatch occurs.

## Important
* ColorCC version 0.99.58 (`dev.colorcc`), target SDK 36, is the expected base.
* Keep the original APK and know how to disable LSPosed modules in recovery before testing SystemUI hooks.
* Disable the old ColorCC and ControlCenter modules before installing this build.
* The script modifies only shader source, not the original SystemUI hook implementations. No claim is made that every ControlCenter effect is already ported.
* Respect the original module authors' licenses and redistribution rights.
