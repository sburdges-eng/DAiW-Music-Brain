# music_brain/cli.py
"""
DAiW CLI Entry Point
"""
import argparse


def main():
    parser = argparse.ArgumentParser(description="DAiW - Digital Audio Intimate Workstation")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["therapy", "generate"],
        help="Command stub (use the desktop app for full experience).",
    )
    args = parser.parse_args()

    if args.command is None:
        print("DAiW - Digital Audio Intimate Workstation")
        print("=========================================")
        print("\nDAiW CLI is installed. Use 'python launcher.py' for the full GUI/desktop app.")
        print("\nFor the therapy-to-MIDI pipeline, run:")
        print("  python -m music_brain.structure.comprehensive_engine")
        return 0

    print("DAiW CLI is installed. Use 'python launcher.py' for the full GUI/desktop app.")
    return 0


if __name__ == "__main__":
    main()
