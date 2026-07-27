#!/usr/bin/env python3
"""AutoMix CLI — standalone stem-to-master processor."""
import argparse
import sys
from presets import GENRE_PRESETS
from engine import AutoMixEngine


def main():
    parser = argparse.ArgumentParser(description="AutoMix: automated stem mixing & mastering")
    parser.add_argument("stems_folder", nargs="?", help="Folder containing .wav stems")
    parser.add_argument("-g", "--genre", default="modern_pop",
                         choices=list(GENRE_PRESETS.keys()),
                         help="Genre preset to apply")
    parser.add_argument("-o", "--output", default="mixed_master.wav",
                         help="Output WAV file path")
    parser.add_argument("--list-genres", action="store_true",
                         help="List available genre presets and exit")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress logs")
    args = parser.parse_args()

    if args.list_genres:
        print("Available genre presets:")
        for key, preset in GENRE_PRESETS.items():
            print(f"  {key:12s} -> {preset.name} (target {preset.master.target_lufs} LUFS)")
        return 0

    if not args.stems_folder:
        parser.print_help()
        return 1

    preset = GENRE_PRESETS[args.genre]
    engine = AutoMixEngine(preset, verbose=not args.quiet)
    engine.run(args.stems_folder, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
