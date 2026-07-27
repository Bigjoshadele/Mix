"""Generates synthetic-but-realistic stems (with transients & dynamics) for testing."""
import numpy as np
import soundfile as sf
import os

SR = 44100
DUR = 8.0
BPM = 100
BEAT = 60 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(42)


def env(n, attack, decay):
    t = np.arange(n) / SR
    e = np.where(t < attack, t / attack, np.exp(-(t - attack) / decay))
    return e


def click_train(interval_beats, decay=0.15, freq=100, noise=False, dur=DUR):
    n = int(SR * dur)
    sig = np.zeros(n)
    step = int(interval_beats * BEAT * SR)
    for start in range(0, n, step):
        length = min(int(SR * 0.3), n - start)
        e = env(length, 0.001, decay)
        if noise:
            tone = rng.standard_normal(length)
        else:
            t = np.arange(length) / SR
            tone = np.sin(2 * np.pi * freq * t) * np.exp(-t * 20)
        sig[start:start + length] += tone[:length] * e[:length]
    return sig / (np.max(np.abs(sig)) + 1e-9)


def sustained_tone(freq, dur=DUR, harmonics=3):
    t = np.arange(int(SR * dur)) / SR
    sig = np.zeros_like(t)
    for h in range(1, harmonics + 1):
        sig += np.sin(2 * np.pi * freq * h * t) / h
    lfo = 1 + 0.05 * np.sin(2 * np.pi * 0.2 * t)
    return sig * lfo / (np.max(np.abs(sig)) + 1e-9)


def vocal_like(freq=220, dur=DUR):
    t = np.arange(int(SR * dur)) / SR
    vibrato = np.sin(2 * np.pi * 5 * t) * 3
    sig = np.sin(2 * np.pi * (freq + vibrato) * t)
    sig += 0.3 * np.sin(2 * np.pi * (freq * 2 + vibrato) * t)
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t) ** 2
    breath = rng.standard_normal(len(t)) * 0.02
    return (sig * envelope + breath) / (np.max(np.abs(sig)) + 1e-9)


def write(name, sig, outdir):
    stereo = np.stack([sig, sig])
    stereo += rng.standard_normal(stereo.shape) * 0.001
    sf.write(os.path.join(outdir, name), stereo.T, SR, subtype="PCM_24")


def generate(outdir):
    os.makedirs(outdir, exist_ok=True)
    write("01_Kick.wav", click_train(1, decay=0.2, freq=60) * 0.9, outdir)
    write("02_Snare.wav", click_train(2, decay=0.15, freq=200, noise=True) * 0.7, outdir)
    write("04_Hats.wav", click_train(0.5, decay=0.05, freq=8000, noise=True) * 0.4, outdir)
    write("07_Bass.wav", sustained_tone(55, harmonics=4) * 0.6, outdir)
    write("08_Synth_Lead.wav", sustained_tone(440, harmonics=5) * 0.4, outdir)
    write("09_Synth_Pad.wav", sustained_tone(220, harmonics=2) * 0.3, outdir)
    write("11_Vox_Lead.wav", vocal_like(220) * 0.7, outdir)
    write("12_Vox_Backing.wav", vocal_like(330) * 0.4, outdir)
    print(f"Generated test stems in {outdir}")


if __name__ == "__main__":
    generate("test_stems")
