# Android Kivy App (MVP + Parity Shell)

## Run Local MVP

1. Install dependencies:
   - `python -m pip install kivy kivymd`
2. Launch from project root:
   - `python android_app/main.py`

## Implemented

- Kivy app shell with `ScreenManager`.
- App service facade over reusable core engine.
- Android save abstraction (`json` container + pickle bridge).
- MVP screens:
  - team selection
  - fixtures
  - standings
  - player list/profile lite
- Direct in-app simulation view:
  - no subprocess/Tk launcher dependency in Android path.
- Full parity migration placeholders for active desktop screens/dialogs.

## Notes

- Desktop PyQt/Tk flow remains unchanged.
- Android path is additive and independent of desktop launcher.
