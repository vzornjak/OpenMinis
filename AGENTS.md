# OpenMinis fork maintenance

- Upstream is https://github.com/OpenMinis/OpenMinis; origin is the owner's fork.
- Keep main identical to upstream/main. Development lives on ios-hr-apple.
- Keep Croatian localization, Apple provider, and build/maintenance changes in separate commits.
- Prefer new files in Providers/Apple and scripts/fork over rewriting upstream logic.
- Preserve the upstream tool executor, permission prompts, persistence, terminal and browser.
- Never add an automatic local-to-cloud switch. Apple PCC is opt-in and requires Apple's entitlement.
- Build this fork with Xcode 27 on macOS. All DerivedData, caches, logs and generated source belong in .build/.
- scripts/fork/build.py generates separate bundle IDs and App Group/iCloud IDs in .build/ios-source; do not manually edit the generated copy.
- Use source-pinned iSH/proot submodules, not their latest branch tips.
- After an upstream merge, run localization validation, provider tests, a device build, then device smoke checks documented in FORK.md. A clean merge alone is not validation.
- Preserve GPLv3 and third-party license files.
