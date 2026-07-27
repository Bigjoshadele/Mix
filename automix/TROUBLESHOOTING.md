# Troubleshooting

If something goes wrong, check these two files first — they usually say
exactly what happened:

- **`install_log.txt`** (in the AutoMix folder) — full output from
  `INSTALL.bat`, every step.
- **`automix_error.log`** (appears next to `AutoMix.exe` after a failed
  run) — if the app crashes or won't open, this has the real Python
  traceback. As of this build, AutoMix always writes this file and shows
  an error dialog instead of silently closing — if you saw the app just
  flash and disappear with no message, you have an older build; rerun
  `INSTALL.bat` to rebuild with the current version.

## "Python was not found"

Install Python 3.10, 3.11, 3.12, or 3.13 (64-bit) from
https://python.org/downloads/ and make sure to check **"Add python.exe
to PATH"** on the first install screen. Then run `INSTALL.bat` again.

## "Your Python is 32-bit"

AutoMix's audio libraries (pedalboard, numpy, scipy) only ship 64-bit
Windows builds (this covers the overwhelming majority of Windows
machines from the last decade). Reinstall Python using the "Windows
installer (64-bit)" link on python.org.

## "A required library failed to import" / anything mentioning "DLL load failed"

This is the most common install-time failure, and it's not really an
AutoMix problem — `pedalboard`, `numpy`, and `scipy` all include compiled
C++ components that need the **Microsoft Visual C++ Redistributable
(x64)** to run, and a lot of Windows machines don't have a recent one
installed.

Install it (free, from Microsoft): https://aka.ms/vs/17/release/vc_redist.x64.exe

Then run `INSTALL.bat` again.

## AutoMix.exe opens then immediately closes, or never appears

Look for `automix_error.log` next to `AutoMix.exe`. It will contain the
exact Python traceback. The most likely causes, in order:

1. Missing VC++ Redistributable (see above) — look for "DLL load failed"
   in the log.
2. Windows Defender / antivirus quarantined the freshly-built `.exe`
   because it's unsigned and not yet "reputable." Check your antivirus's
   quarantine list, or right-click `AutoMix.exe` → Properties → and look
   for an "Unblock" checkbox near the bottom.
3. The `.exe` was moved out of the `dist` folder on its own, away from
   files it expects nearby. Keep `AutoMix.exe` in place and only use the
   Desktop shortcut, or move the whole `dist` folder together.

## SmartScreen says "Windows protected your PC"

Expected the first time you run a freshly built, unsigned executable.
Click **"More info"** → **"Run anyway."** This is a one-time prompt.

## The install seems to hang on "Installing dependencies"

That step downloads `pedalboard`, `numpy`, and `scipy` from PyPI, which
can take a few minutes on a slow connection (numpy/scipy alone are
tens of MB). If it seems truly stuck rather than just slow, check
`install_log.txt` for the exact pip error — a corporate firewall or
proxy blocking PyPI is the usual cause.

## Mixing runs but the output sounds wrong / too quiet / too loud

That's not a crash — it's a tuning issue. Open `presets.py` and adjust
the genre preset's `target_lufs`, `comp_ratio`, or per-stem settings; see
the "Tuning it to your ear" section in `README.md`.

## Still stuck

Copy the contents of `automix_error.log` (or the last ~15 lines of
`install_log.txt`) — that's the fastest way to pin down what's actually
failing.
