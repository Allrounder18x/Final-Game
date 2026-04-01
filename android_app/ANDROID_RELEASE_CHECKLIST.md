# Android Release Checklist

## Buildozer Pipeline

- Install Linux/WSL dependencies for Buildozer and Android SDK/NDK.
- From `android_app`, run:
  - `python -m pip install -r requirements-android.txt`
  - `buildozer android debug`
- Validate generated debug APK on real device.

## Save Migration Validation

- Test fresh game save/load via JSON slot (`autosave.json`).
- Test loading legacy pickle save from desktop branch.
- Verify season/year/user-team continuity after migration load.

## Device QA Matrix

- Low-end Android (3-4 GB RAM): app start, team select, one match sim.
- Mid-range Android (6-8 GB RAM): full season chunk simulation.
- High-end Android: stress test save/reload loops.
- Validate lifecycle:
  - background -> resume
  - rotation (if enabled)
  - force-stop -> relaunch -> load last save

## Signing and Release

- Generate keystore:
  - `keytool -genkey -v -keystore release.keystore -alias cricket-release -keyalg RSA -keysize 2048 -validity 10000`
- Configure `buildozer.spec` release signing keys/alias.
- Build release artifact:
  - `buildozer android release`
- Align and sign APK/AAB per Play Console requirements.

## Rollout Checklist

- Smoke-test release build on minimum API level device.
- Prepare migration notes for legacy pickle saves.
- Upload internal testing track build.
- Resolve QA issues and tag release candidate.
- Publish staged rollout (5% -> 20% -> 100%) with crash monitoring.
