"""
DAiW CLI Entry Point
"""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="DAiW - Digital Audio Intimate Workstation")
    parser.add_argument("command", nargs="?", choices=["therapy", "generate"], help="Command to run")

    # We don't actually do anything yet; this is a placeholder.
    # args = parser.parse_args()

    print("DAiW CLI is installed. Use 'python launcher.py' for the full GUI.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
