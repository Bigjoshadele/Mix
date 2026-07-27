"""
Stem classification: figures out what instrument a WAV file contains,
first by filename, falling back to basic spectral analysis if the name
is ambiguous.
"""
import re
import numpy as np
from enum import Enum


class StemType(str, Enum):
    KICK = "kick"
    SNARE = "snare"
    CLAP = "clap"
    HATS = "hats"
    TOMS = "toms"
    OVERHEADS = "overheads"
    PERC = "perc"
    BASS = "bass"
    SYNTH_LEAD = "synth_lead"
    SYNTH_PAD = "synth_pad"
    GUITAR = "guitar"
    KEYS = "keys"
    VOX_LEAD = "vox_lead"
    VOX_BACKING = "vox_backing"
    VOX_ADLIB = "vox_adlib"
    FX = "fx"
    OTHER = "other"


FILENAME_PATTERNS = [
    (StemType.KICK, r"kick|bd|bassdrum"),
    (StemType.SNARE, r"snare|sd\b"),
    (StemType.CLAP, r"clap"),
    (StemType.HATS, r"hat|hh|hi[-_]?hat"),
    (StemType.TOMS, r"tom"),
    (StemType.OVERHEADS, r"overhead|oh\b|room"),
    (StemType.PERC, r"perc|shaker|tamb|conga|bongo"),
    (StemType.BASS, r"bass(?!drum)|808|sub"),
    (StemType.VOX_LEAD, r"vox[_-]?lead|lead[_-]?vox|vocal[_-]?lead|lead[_-]?vocal"),
    (StemType.VOX_ADLIB, r"adlib|ad[_-]?lib"),
    (StemType.VOX_BACKING, r"vox[_-]?back|back[_-]?vox|bgv|harmony|vox[_-]?bv"),
    (StemType.SYNTH_LEAD, r"synth[_-]?lead|lead[_-]?synth"),
    (StemType.SYNTH_PAD, r"pad\b|synth[_-]?pad"),
    (StemType.GUITAR, r"guitar|gtr"),
    (StemType.KEYS, r"key|piano|rhodes|organ"),
    (StemType.FX, r"\bfx\b|riser|impact|sweep|whoosh"),
    (StemType.VOX_LEAD, r"vox|vocal"),
]


def classify_by_filename(filename: str) -> StemType:
    name = filename.lower()
    for stem_type, pattern in FILENAME_PATTERNS:
        if re.search(pattern, name):
            return stem_type
    return StemType.OTHER


def classify_by_audio(audio: np.ndarray, sr: int) -> StemType:
    if audio.ndim > 1:
        mono = audio.mean(axis=0)
    else:
        mono = audio

    if len(mono) == 0 or np.allclose(mono, 0):
        return StemType.OTHER

    spectrum = np.abs(np.fft.rfft(mono))
    freqs = np.fft.rfftfreq(len(mono), 1 / sr)
    centroid = float(np.sum(freqs * spectrum) / (np.sum(spectrum) + 1e-9))

    low_mask = freqs < 120
    low_energy = float(np.sum(spectrum[low_mask] ** 2))
    total_energy = float(np.sum(spectrum ** 2)) + 1e-9
    low_ratio = low_energy / total_energy

    peak = float(np.max(np.abs(mono)) + 1e-9)
    rms = float(np.sqrt(np.mean(mono ** 2)) + 1e-9)
    crest = peak / rms

    if low_ratio > 0.5 and centroid < 200:
        return StemType.BASS
    if crest > 8 and centroid < 2000:
        return StemType.KICK
    if crest > 6 and centroid > 3000:
        return StemType.HATS
    if 200 < centroid < 4000 and crest < 6:
        return StemType.VOX_LEAD
    return StemType.OTHER
