"""
Builds Pedalboard effect chains from StemConfig / BusConfig objects,
plus a few small numpy-based utilities (panning, saturation) that don't
map cleanly onto discrete Pedalboard plugins.
"""
import numpy as np
from pedalboard import (
    Pedalboard, HighpassFilter, LowpassFilter, PeakFilter,
    HighShelfFilter, LowShelfFilter, Compressor, Gain, Limiter, Reverb, Delay,
)


def to_stereo(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        return np.stack([audio, audio])
    if audio.shape[0] == 1:
        return np.vstack([audio, audio])
    return audio


def apply_pan(audio: np.ndarray, pan: float) -> np.ndarray:
    audio = to_stereo(audio)
    angle = (pan + 1) * (np.pi / 4)
    left_gain = np.cos(angle)
    right_gain = np.sin(angle)
    out = audio.copy()
    out[0] *= left_gain * np.sqrt(2)
    out[1] *= right_gain * np.sqrt(2)
    return out


def saturate(audio: np.ndarray, drive: float) -> np.ndarray:
    if drive <= 0:
        return audio
    amount = 1.0 + drive * 9.0
    wet = np.tanh(audio * amount) / np.tanh(amount)
    mix = min(drive * 1.5, 1.0)
    return audio * (1 - mix) + wet * mix


def build_stem_chain(cfg) -> Pedalboard:
    plugins = []
    if cfg.highpass_freq:
        plugins.append(HighpassFilter(cutoff_frequency_hz=cfg.highpass_freq))
    if cfg.lowpass_freq:
        plugins.append(LowpassFilter(cutoff_frequency_hz=cfg.lowpass_freq))
    for band in cfg.eq_bands:
        plugins.append(PeakFilter(cutoff_frequency_hz=band["freq"],
                                   gain_db=band["gain"], q=band.get("q", 1.0)))
    plugins.append(Compressor(
        threshold_db=cfg.comp_threshold, ratio=cfg.comp_ratio,
        attack_ms=cfg.comp_attack_ms, release_ms=cfg.comp_release_ms,
    ))
    plugins.append(Gain(gain_db=cfg.makeup_gain + cfg.volume_db))
    return Pedalboard(plugins)


def build_bus_chain(cfg) -> Pedalboard:
    plugins = [
        Compressor(threshold_db=cfg.comp_threshold, ratio=cfg.comp_ratio,
                   attack_ms=cfg.comp_attack_ms, release_ms=cfg.comp_release_ms),
    ]
    if cfg.shelf_freq:
        plugins.append(HighShelfFilter(cutoff_frequency_hz=cfg.shelf_freq,
                                        gain_db=cfg.shelf_gain))
    plugins.append(Gain(gain_db=cfg.volume_db))
    return Pedalboard(plugins)


def build_reverb_send() -> Pedalboard:
    return Pedalboard([Reverb(room_size=0.6, wet_level=1.0, dry_level=0.0, damping=0.5)])


def build_delay_send(bpm: float = 120.0) -> Pedalboard:
    delay_seconds = 60.0 / bpm / 2
    return Pedalboard([Delay(delay_seconds=delay_seconds, feedback=0.3, mix=1.0)])


def build_master_chain(target_ceiling_db: float) -> Pedalboard:
    return Pedalboard([
        Limiter(threshold_db=target_ceiling_db, release_ms=100),
    ])
