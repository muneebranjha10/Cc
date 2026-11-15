# Combine CC geometry stabilization — experimental test, NOT a release

## What was found in the user-provided APK

The uploaded **Combine-CC-Geometry-Experimental.apk** contains the original ColorCC Xposed entry point (\`dev.colorcc.Hook\`), ColorCC's own lens shader and the full 7,719-character ControlCenter 1.4 glass shader. The latter is present in \`dev.combinecc.Glass\`, but its presence does not prove it is rendering on the phone. Exact full liquid-glass rendering is still unverified.

In \`Ldev/colorcc/Panel$Body;->apply()V\` the tile view is scaled by a press-motion term and translated horizontally and vertically in response to the opening spring. The changes below mitigate the amount of apparent movement **without altering method size, control handlers, Xposed hooks or the 7,719-character shader.**

## Five guarded constants changed

- Press shrink: 8% to 2%
- Lateral opening travel: 22dp to 12dp
- Header vertical opening travel: 16dp to 10dp
- Per-row vertical travel: 12dp to 8dp
- Base vertical travel: 36dp to 22dp

This is a **bounded motion mitigation**, not a proven bug fix. It does NOT repair the glass backdrop synchronization, morphing/joined shapes, bitmap capture, refraction coordinate mapping, or exact ControlCenter animations. A full port needs a maintained source project and real device testing.

## Build an installable test candidate

The existing repository is **public**. Do NOT publish the original APK here without redistribution permission. Instead, copy these scripts and workflow to a **private** GitHub repository.

1. Place your original user-supplied \`Combine-CC-Geometry-Experimental.apk\` in \`input/Combine-CC-Geometry-Experimental.apk\` inside the private repository.
2. On GitHub, open **Actions → Build Combine CC geometry test → Run workflow**.
3. Download the \`CombineCC-GeometryTest-UNTESTED\` artifact after GitHub successfully runs the official \`zipalign\` and \`apksigner\` checks.
4. Preserve a known-good APK and a rollback plan. The candidate is signed with a **new test certificate** and cannot install over the current APK with a different signature.
5. Test carefully before publishing: opening/closing, gesture reversals, slider interactions, rotation, lockscreen, visually inspect effect against reference, inspect SystemUI logs.
6. If unstable, disable the module in LSPosed and restore the existing version.

**Signing is not visual verification**, and CI cannot confirm runtime compatibility on One UI 9 / Android 17. GitHub's workflow requires the original APK but doesn't store it here.

No public binary release has been created because the build is not device-tested and redistribution rights for the third-party base APK are not established.
