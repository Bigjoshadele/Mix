"""
AutoMix Engine: takes a folder of stem WAVs and a genre preset, and
renders a fully mixed + mastered stereo WAV.
"""
import os
import glob
import numpy as np
import soundfile as sf
import pyloudnorm as pyln

from stem_types import StemType, classify_by_filename, classify_by_audio
from presets import GenrePreset
import dsp

STEM_TO_BUS = {
    StemType.KICK: "drums", StemType.SNARE: "drums", StemType.CLAP: "drums",
    StemType.HATS: "drums", StemType.TOMS: "drums", StemType.OVERHEADS: "drums",
    StemType.PERC: "drums",
    StemType.BASS: "bass",
    StemType.SYNTH_LEAD: "music", StemType.SYNTH_PAD: "music",
    StemType.GUITAR: "music", StemType.KEYS: "music",
    StemType.VOX_LEAD: "vocals", StemType.VOX_BACKING: "vocals",
    StemType.VOX_ADLIB: "vocals",
    StemType.FX: "fx", StemType.OTHER: "music",
}

TARGET_SR = 44100


class AutoMixEngine:
    def __init__(self, preset: GenrePreset, verbose: bool = True):
        self.preset = preset
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(f"[automix] {msg}")

    def load_stems(self, folder: str):
        wav_paths = sorted(glob.glob(os.path.join(folder, "*.wav")) +
                            glob.glob(os.path.join(folder, "*.WAV")))
        if not wav_paths:
            raise FileNotFoundError(f"No .wav files found in {folder}")

        stems = []
        max_len = 0
        sr_ref = None
        for path in wav_paths:
            audio, sr = sf.read(path, always_2d=False)
            audio = audio.T if audio.ndim == 2 else audio
            if sr_ref is None:
                sr_ref = sr
            elif sr != sr_ref:
                self.log(f"WARNING: {os.path.basename(path)} sample rate {sr} "
                          f"differs from reference {sr_ref}; resampling not yet "
                          f"implemented, results may be affected.")

            stem_type = classify_by_filename(os.path.basename(path))
            if stem_type == StemType.OTHER:
                stem_type = classify_by_audio(np.atleast_2d(audio), sr)
                self.log(f"  {os.path.basename(path)}: filename ambiguous, "
                         f"classified by audio as {stem_type.value}")
            else:
                self.log(f"  {os.path.basename(path)}: classified as {stem_type.value}")

            stems.append({"path": path, "audio": dsp.to_stereo(np.atleast_2d(audio)),
                          "type": stem_type, "sr": sr})
            max_len = max(max_len, stems[-1]["audio"].shape[1])

        for s in stems:
            pad = max_len - s["audio"].shape[1]
            if pad > 0:
                s["audio"] = np.pad(s["audio"], ((0, 0), (0, pad)))

        self.sr = sr_ref
        self.max_len = max_len
        return stems

    def normalize_input(self, audio, target_peak_db=-6.0):
        peak = np.max(np.abs(audio)) + 1e-9
        target_peak = 10 ** (target_peak_db / 20)
        gain = target_peak / peak
        return audio * gain

    def process_stem(self, stem):
        cfg = self.preset.stems.get(stem["type"], self.preset.stems[StemType.OTHER])
        audio = self.normalize_input(stem["audio"])
        chain = dsp.build_stem_chain(cfg)
        processed = chain(audio, self.sr)
        if cfg.saturation > 0:
            processed = dsp.saturate(processed, cfg.saturation)
        processed = dsp.apply_pan(processed, cfg.pan)

        sends = {}
        if cfg.reverb_send > 0:
            sends["reverb"] = processed * cfg.reverb_send
        if cfg.delay_send > 0:
            sends["delay"] = processed * cfg.delay_send

        return processed, sends, cfg

    def build_buses(self, processed_stems):
        buses = {name: np.zeros((2, self.max_len)) for name in
                  ["drums", "bass", "music", "vocals", "fx"]}
        reverb_sum = np.zeros((2, self.max_len))
        delay_sum = np.zeros((2, self.max_len))
        kick_signal = np.zeros((2, self.max_len))

        for stem_type, audio, sends in processed_stems:
            bus_name = STEM_TO_BUS.get(stem_type, "music")
            buses[bus_name][:, :audio.shape[1]] += audio
            if stem_type == StemType.KICK:
                kick_signal[:, :audio.shape[1]] += audio
            if "reverb" in sends:
                reverb_sum[:, :sends["reverb"].shape[1]] += sends["reverb"]
            if "delay" in sends:
                delay_sum[:, :sends["delay"].shape[1]] += sends["delay"]

        if np.any(reverb_sum):
            reverb_out = dsp.build_reverb_send()(reverb_sum, self.sr) * 0.6
            buses["fx"] += reverb_out[:, :self.max_len]
        if np.any(delay_sum):
            delay_out = dsp.build_delay_send()(delay_sum, self.sr) * 0.5
            buses["fx"] += delay_out[:, :self.max_len]

        return buses, kick_signal

    def apply_sidechain_duck(self, signal, kick_signal, amount):
        if amount <= 0 or not np.any(kick_signal):
            return signal
        env = np.abs(kick_signal).mean(axis=0)
        alpha = 0.003
        smoothed = np.zeros_like(env)
        for i in range(1, len(env)):
            smoothed[i] = alpha * env[i] + (1 - alpha) * smoothed[i - 1]
        smoothed = smoothed / (smoothed.max() + 1e-9)
        duck_curve = 1.0 - amount * smoothed
        return signal * duck_curve

    def process_buses(self, buses, kick_signal):
        processed = {}
        for name, audio in buses.items():
            cfg = self.preset.buses.get(name)
            if cfg is None:
                processed[name] = audio
                continue
            if cfg.sidechain_from == "kick" and cfg.sidechain_amount > 0:
                audio = self.apply_sidechain_duck(audio, kick_signal, cfg.sidechain_amount)
            chain = dsp.build_bus_chain(cfg)
            processed[name] = chain(audio, self.sr)
            if cfg.saturation > 0:
                processed[name] = dsp.saturate(processed[name], cfg.saturation)
        return processed

    def sum_mix_bus(self, buses):
        mix = np.zeros((2, self.max_len))
        for audio in buses.values():
            mix[:, :audio.shape[1]] += audio[:, :self.max_len]
        return mix

    def apply_glue_compression(self, mix):
        from pedalboard import Compressor
        board = dsp.Pedalboard([Compressor(threshold_db=-6.0, ratio=1.5,
                                            attack_ms=15, release_ms=200)])
        return board(mix, self.sr)

    def master(self, mix):
        mcfg = self.preset.master
        from pedalboard import HighShelfFilter, LowShelfFilter
        pre = dsp.Pedalboard([
            LowShelfFilter(cutoff_frequency_hz=100, gain_db=mcfg.low_shelf_gain),
            HighShelfFilter(cutoff_frequency_hz=10000, gain_db=mcfg.high_shelf_gain),
        ])
        mix = pre(mix, self.sr)

        mid = (mix[0] + mix[1]) / 2
        side = (mix[0] - mix[1]) / 2
        side *= mcfg.stereo_width
        mix = np.stack([mid + side, mid - side])

        limiter = dsp.build_master_chain(mcfg.limiter_ceiling_db)
        try:
            meter = pyln.Meter(self.sr)
            pre_loudness = meter.integrated_loudness(mix.T)
            if not np.isfinite(pre_loudness):
                self.log("Loudness measurement was silence/invalid; skipping LUFS normalization")
                return limiter(mix, self.sr)

            gain_db = np.clip(mcfg.target_lufs - pre_loudness, -24, 24)
            trial = mix * (10 ** (gain_db / 20))
            limited = limiter(trial, self.sr)

            for _ in range(3):
                measured = meter.integrated_loudness(limited.T)
                if not np.isfinite(measured):
                    break
                error_db = mcfg.target_lufs - measured
                if abs(error_db) < 0.3:
                    break
                gain_db += error_db * 0.8
                trial = mix * (10 ** (gain_db / 20))
                limited = limiter(trial, self.sr)

            final_lufs = meter.integrated_loudness(limited.T)
            self.log(f"Loudness: {pre_loudness:.1f} LUFS pre-limit -> "
                     f"{final_lufs:.1f} LUFS final (target {mcfg.target_lufs})")
            return limited
        except Exception as e:
            self.log(f"LUFS normalization skipped ({e})")
            return limiter(mix, self.sr)

    def run(self, input_folder: str, output_path: str):
        self.log(f"Loading stems from {input_folder} ...")
        stems = self.load_stems(input_folder)

        self.log("Processing individual stems ...")
        processed_stems = []
        for stem in stems:
            audio, sends, cfg = self.process_stem(stem)
            processed_stems.append((stem["type"], audio, sends))

        self.log("Building buses ...")
        buses, kick_signal = self.build_buses(processed_stems)

        self.log("Processing buses (compression, sidechain, glue) ...")
        buses = self.process_buses(buses, kick_signal)

        mix = self.sum_mix_bus(buses)
        mix = self.apply_glue_compression(mix)

        self.log(f"Mastering to {self.preset.master.target_lufs} LUFS ...")
        mastered = self.master(mix)

        peak = np.max(np.abs(mastered))
        if peak > 0.999:
            mastered = mastered / peak * 0.999

        sf.write(output_path, mastered.T, self.sr, subtype="PCM_24")
        self.log(f"Wrote {output_path}")
        return output_path
