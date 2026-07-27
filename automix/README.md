# AutoMix — Standalone Stem Mixing & Mastering

Drop in a folder of WAV stems exported from Cubase (or any DAW), pick a genre,
and get back a mixed, bus-processed, mastered stereo WAV.

## What it does

1. **Classifies stems** by filename (falls back to spectral analysis if the
   name doesn't match a known pattern)
2. **Per-stem processing**: high-pass/low-pass, parametric EQ, compression,
   saturation, panning, effect sends — tuned per genre
3. **Bus routing**: drums / bass / music / vocals / fx, each with its own
   glue compression, and kick→bass sidechain ducking
4. **Mix bus glue** compression before mastering
5. **Mastering chain**: tonal shelving EQ, mid/side stereo width, closed-loop
   LUFS loudness targeting, true-peak-safe limiting

## Install (Windows)

**Two ways to get `AutoMix.exe`:**

**Option A — no Python, ever, on your machine (recommended).**
GitHub builds the real Windows binary for you in the cloud. Takes about
5 minutes of one-time setup, zero local installs. See
**`GETTING_THE_EXE.md`**.

**Option B — build it locally (needs Python once, just for the build).**
1. Install Python 3.10, 3.11, 3.12, or 3.13 (64-bit) — check **"Add
   python.exe to PATH"** during install.
2. Double-click **`INSTALL.bat`**.

Either way, the resulting `AutoMix.exe` is a genuine standalone binary —
it bundles its own Python interpreter and every library inside it, so it
never needs Python installed to *run*, only (in Option B) to build.
Option B downloads the audio libraries from PyPI during that one-time
build (needs internet then; the finished `.exe` doesn't).

`INSTALL.bat` (Option B) also:
- Verifies every library actually imports before building anything, so
  a bad install fails fast with a clear message instead of a mysterious
  crash later
- Builds a real standalone `AutoMix.exe`
- Creates a Desktop shortcut

If anything goes wrong, `INSTALL.bat` writes `install_log.txt`, and
`AutoMix.exe` writes `automix_error.log` next to itself if it ever fails
to start. See **`TROUBLESHOOTING.md`** for the common causes (missing
VC++ Redistributable, 32-bit Python, antivirus quarantine) and fixes.

## Install (macOS / Linux)

```bash
cd automix
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Usage

### GUI (recommended)

Windows: double-click the AutoMix desktop shortcut.

macOS/Linux:
```bash
python automix_gui.py
```

Browse to your stems folder, pick a genre, hit **PROCESS**.

### Command line

```bash
python automix_cli.py ./MySong_Stems -g modern_pop -o MySong_Mixed.wav
python automix_cli.py --list-genres
```

## Stem naming convention

The classifier matches on filename first (case-insensitive substring match):

```
01_Kick.wav        07_Bass.wav          11_Vox_Lead.wav
02_Snare.wav       08_Synth_Lead.wav    12_Vox_Backing.wav
03_Clap.wav        09_Synth_Pad.wav     13_Vox_Adlibs.wav
04_Hats.wav        10_Guitar_Elec.wav   14_FX_Rise.wav
05_Toms.wav                             15_FX_Impact.wav
06_Overheads.wav
```

Anything unrecognized gets classified by spectral analysis (crest factor,
spectral centroid, low-frequency energy) instead.

## Genre presets

| Key | Genre | Target loudness |
|---|---|---|
| `modern_pop` | Modern Pop | -14 LUFS |
| `hip_hop` | Hip-Hop | -9 LUFS |
| `rnb` | R&B | -12 LUFS |
| `afrobeats` | Afrobeats | -11 LUFS |
| `amapiano` | Amapiano | -11.5 LUFS |
| `gospel` | Gospel | -13 LUFS |

## Tuning it to your ear

Every parameter lives in `presets.py` as plain, readable dataclasses.
Edit a preset directly, or copy a block in `GENRE_PRESETS` to make a new
one using `overrides_stem` for just what differs from the defaults.

## Design

The GUI has a mastering-rack visual identity (charcoal panel, hairline
dividers, segmented LED meter) rather than stock `tkinter`. Full token
system in `DESIGN.md`.

## Known limitations

- Sidechain ducking is a simplified envelope follower, not a true
  sidechain compressor.
- No vocal-phrase-aware automation — everything is static per-stem/bus
  processing.
- Reverb/delay are basic algorithmic sends, not convolution.
- Stems at different sample rates are not resampled — keep all stems at
  the same sample rate on export.

## Project layout

```
automix/
├── INSTALL.bat            # One-click offline Windows installer
├── TROUBLESHOOTING.md       # Common install/run problems and fixes
├── DESIGN.md                 # Visual identity: palette, type, layout tokens
├── pyproject.toml              # pip-installable package definition
├── automix_gui.py                # Desktop GUI (crash-safe startup, see code comments)
├── automix_cli.py                  # Command-line entry point
├── engine.py                         # Core pipeline: load → process → bus → master
├── dsp.py                              # Pedalboard chain builders + pan/saturation
├── presets.py                            # Genre presets & per-stem/bus DSP defaults
├── stem_types.py                           # Filename + spectral stem classification
├── make_icon.py                              # Generates assets/automix.ico + icon.png
├── make_test_stems.py                          # Generates synthetic test stems (dev use)
├── assets/                                       # App icon
└── requirements.txt
```

## Roadmap to a VST3/AU plugin

`dsp.py` / `engine.py` is the actual DSP spec for a native plugin —
porting means re-implementing each Pedalboard chain in JUCE's C++ DSP
module using the same tuned parameters, plus a `juce::AudioProcessor`
around it for real-time block processing.
