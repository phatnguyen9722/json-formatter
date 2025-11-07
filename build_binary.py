"""
Build script for creating standalone executable
Usage: python build_binary.py
"""

import os
import sys
import subprocess


def build_executable():
    """Build standalone executable using PyInstaller"""

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=JSON-Formatter",
        "--windowed",  # No console window
        "--onefile",  # Single executable file
        "--clean",  # Clean build
        "--noconfirm",  # Overwrite without asking
        # Add icon if you have one (optional)
        # "--icon=icon.ico",
        "launcher.py",
    ]

    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 60)
        print("✅ Build successful!")
        print("=" * 60)
        print(f"\nExecutable location:")
        print(f"  → dist/JSON-Formatter.exe (Windows)")
        print(f"  → dist/JSON-Formatter (Linux/Mac)")
        print("\nYou can now distribute this single file!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
