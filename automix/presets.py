"""
Genre presets: default DSP parameters per stem type, per bus, and for
the mastering chain.
"""
from dataclasses import dataclass, field
from typing import Optional
from stem_types import StemType


@dataclass
class StemConfig:
    highpass_freq: Optional[float] = None
    lowpass_freq: Optional[float] = None
    eq_bands: list = field(default_factory=list)
    comp_threshold: float = -18.0
    comp_ratio: float = 2.5
    comp_attack_ms: float = 10.0
    comp_release_ms: float = 100.0
    makeup_gain: float = 0.0
    saturation: float = 0.0
    pan: float = 0.0
    volume_db: float = 0.0
    reverb_send: float = 0.0
    delay_send: float = 0.0


@dataclass
class BusConfig:
    comp_threshold: float = -12.0
    comp_ratio: float = 2.0
    comp_attack_ms: float = 20.0
    comp_release_ms: float = 150.0
    saturation: float = 0.0
    shelf_freq: Optional[float] = None
    shelf_gain: float = 0.0
    volume_db: float = 0.0
    sidechain_from: Optional[str] = None
    sidechain_amount: float = 0.0


@dataclass
class MasterConfig:
    target_lufs: float = -14.0
    limiter_ceiling_db: float = -1.0
    stereo_width: float = 1.1
    low_shelf_gain: float = 0.0
    high_shelf_gain: float = 0.5


@dataclass
class GenrePreset:
    name: str
    stems: dict
    buses: dict
    master: MasterConfig


def _base_stem_defaults():
    return {
        StemType.KICK: StemConfig(
            highpass_freq=30, eq_bands=[{"freq": 60, "gain": 2.5, "q": 1.0},
                                         {"freq": 3000, "gain": 1.5, "q": 1.2}],
            comp_threshold=-10, comp_ratio=4.0, comp_attack_ms=5, comp_release_ms=80,
            makeup_gain=3.0, pan=0.0, volume_db=0.0,
        ),
        StemType.SNARE: StemConfig(
            highpass_freq=100, eq_bands=[{"freq": 200, "gain": -1.5, "q": 1.0},
                                          {"freq": 5000, "gain": 2.5, "q": 1.0}],
            comp_threshold=-14, comp_ratio=3.5, comp_attack_ms=3, comp_release_ms=100,
            makeup_gain=2.5, pan=0.0, volume_db=-1.0,
        ),
        StemType.CLAP: StemConfig(
            highpass_freq=200, eq_bands=[{"freq": 2000, "gain": 2.0, "q": 1.0}],
            comp_threshold=-16, comp_ratio=3.0, makeup_gain=2.0, pan=0.05, volume_db=-3.0,
        ),
        StemType.HATS: StemConfig(
            highpass_freq=400, eq_bands=[{"freq": 9000, "gain": 1.5, "q": 0.8}],
            comp_threshold=-20, comp_ratio=2.0, makeup_gain=1.0, pan=0.3, volume_db=-6.0,
        ),
        StemType.TOMS: StemConfig(
            highpass_freq=60, eq_bands=[{"freq": 250, "gain": 2.0, "q": 1.0}],
            comp_threshold=-14, comp_ratio=3.0, makeup_gain=2.0, pan=-0.15, volume_db=-4.0,
        ),
        StemType.OVERHEADS: StemConfig(
            highpass_freq=150, comp_threshold=-18, comp_ratio=2.0,
            makeup_gain=1.5, pan=0.0, volume_db=-7.0,
        ),
        StemType.PERC: StemConfig(
            highpass_freq=200, comp_threshold=-18, comp_ratio=2.5,
            makeup_gain=1.5, pan=0.4, volume_db=-8.0, reverb_send=0.15,
        ),
        StemType.BASS: StemConfig(
            highpass_freq=25, eq_bands=[{"freq": 700, "gain": -2.0, "q": 1.2}],
            comp_threshold=-16, comp_ratio=3.0, comp_attack_ms=8, comp_release_ms=120,
            makeup_gain=2.5, pan=0.0, volume_db=-2.0, saturation=0.15,
        ),
        StemType.SYNTH_LEAD: StemConfig(
            highpass_freq=150, eq_bands=[{"freq": 3000, "gain": 1.5, "q": 1.0}],
            comp_threshold=-18, comp_ratio=2.5, makeup_gain=1.5,
            pan=-0.1, volume_db=-6.0, reverb_send=0.2,
        ),
        StemType.SYNTH_PAD: StemConfig(
            highpass_freq=200, lowpass_freq=12000,
            comp_threshold=-20, comp_ratio=1.8, makeup_gain=1.0,
            pan=0.1, volume_db=-10.0, reverb_send=0.35,
        ),
        StemType.GUITAR: StemConfig(
            highpass_freq=100, eq_bands=[{"freq": 3500, "gain": 1.5, "q": 1.0}],
            comp_threshold=-16, comp_ratio=2.5, makeup_gain=1.5,
            pan=-0.25, volume_db=-6.0, reverb_send=0.15,
        ),
        StemType.KEYS: StemConfig(
            highpass_freq=100, comp_threshold=-18, comp_ratio=2.0,
            makeup_gain=1.5, pan=0.25, volume_db=-7.0, reverb_send=0.2,
        ),
        StemType.VOX_LEAD: StemConfig(
            highpass_freq=100,
            eq_bands=[{"freq": 300, "gain": -1.5, "q": 1.2},
                      {"freq": 3000, "gain": -1.5, "q": 2.5},
                      {"freq": 12000, "gain": 2.5, "q": 0.8}],
            comp_threshold=-18, comp_ratio=3.0, comp_attack_ms=5, comp_release_ms=90,
            makeup_gain=4.0, pan=0.0, volume_db=0.0, saturation=0.2,
            reverb_send=0.15, delay_send=0.08,
        ),
        StemType.VOX_BACKING: StemConfig(
            highpass_freq=120, eq_bands=[{"freq": 12000, "gain": 1.5, "q": 0.8}],
            comp_threshold=-20, comp_ratio=2.5, makeup_gain=2.5,
            pan=0.4, volume_db=-8.0, reverb_send=0.25,
        ),
        StemType.VOX_ADLIB: StemConfig(
            highpass_freq=150, comp_threshold=-20, comp_ratio=3.0,
            makeup_gain=2.0, pan=-0.35, volume_db=-9.0, reverb_send=0.3, delay_send=0.2,
        ),
        StemType.FX: StemConfig(
            highpass_freq=80, comp_threshold=-20, comp_ratio=1.5,
            makeup_gain=0.5, pan=0.0, volume_db=-8.0, reverb_send=0.3,
        ),
        StemType.OTHER: StemConfig(
            highpass_freq=60, comp_threshold=-18, comp_ratio=2.0,
            makeup_gain=1.0, pan=0.0, volume_db=-8.0,
        ),
    }


def _base_buses():
    return {
        "drums": BusConfig(comp_threshold=-10, comp_ratio=2.0, comp_attack_ms=15,
                            comp_release_ms=120, saturation=0.15, volume_db=0.0),
        "bass": BusConfig(comp_threshold=-14, comp_ratio=1.8, volume_db=0.0),
        "music": BusConfig(comp_threshold=-16, comp_ratio=1.6, shelf_freq=8000,
                            shelf_gain=1.0, volume_db=0.0,
                            sidechain_from="kick", sidechain_amount=0.15),
        "vocals": BusConfig(comp_threshold=-14, comp_ratio=2.2, shelf_freq=10000,
                             shelf_gain=1.0, volume_db=0.0),
        "fx": BusConfig(comp_threshold=-20, comp_ratio=1.5, volume_db=0.0),
    }


def _make_preset(name, target_lufs, overrides_stem=None, overrides_bus=None,
                  sidechain_amount=0.15, stereo_width=1.1, high_shelf=0.5):
    stems = _base_stem_defaults()
    if overrides_stem:
        for stem_type, kwargs in overrides_stem.items():
            for k, v in kwargs.items():
                setattr(stems[stem_type], k, v)
    buses = _base_buses()
    buses["music"].sidechain_amount = sidechain_amount
    if overrides_bus:
        for bus_name, kwargs in overrides_bus.items():
            for k, v in kwargs.items():
                setattr(buses[bus_name], k, v)
    master = MasterConfig(target_lufs=target_lufs, stereo_width=stereo_width,
                           high_shelf_gain=high_shelf)
    return GenrePreset(name=name, stems=stems, buses=buses, master=master)


GENRE_PRESETS = {
    "modern_pop": _make_preset(
        "Modern Pop", target_lufs=-14.0, sidechain_amount=0.15, stereo_width=1.1,
    ),
    "hip_hop": _make_preset(
        "Hip-Hop", target_lufs=-9.0, sidechain_amount=0.35, stereo_width=1.05,
        overrides_stem={
            StemType.KICK: dict(eq_bands=[{"freq": 50, "gain": 4.0, "q": 1.0}],
                                 comp_ratio=5.0),
            StemType.BASS: dict(comp_ratio=4.0, saturation=0.3),
        },
    ),
    "rnb": _make_preset(
        "R&B", target_lufs=-12.0, sidechain_amount=0.2, stereo_width=1.15,
        overrides_stem={
            StemType.VOX_LEAD: dict(saturation=0.3, reverb_send=0.25),
        },
    ),
    "afrobeats": _make_preset(
        "Afrobeats", target_lufs=-11.0, sidechain_amount=0.25, stereo_width=1.2,
        overrides_stem={
            StemType.PERC: dict(volume_db=-4.0, pan=0.5),
        },
    ),
    "amapiano": _make_preset(
        "Amapiano", target_lufs=-11.5, sidechain_amount=0.2, stereo_width=1.15,
        overrides_stem={
            StemType.BASS: dict(comp_ratio=2.2, saturation=0.1),
        },
    ),
    "gospel": _make_preset(
        "Gospel", target_lufs=-13.0, sidechain_amount=0.1, stereo_width=1.1,
        overrides_stem={
            StemType.VOX_LEAD: dict(reverb_send=0.3),
            StemType.VOX_BACKING: dict(volume_db=-6.0, reverb_send=0.35),
        },
    ),
}
