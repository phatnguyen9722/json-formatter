#!/usr/bin/env python3
"""
JSON Formatter Launcher
This is the entry point for PyInstaller builds
"""
import sys
import os

# Add the current directory to the path so app module can be found
if getattr(sys, "frozen", False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)

# Now import and run the app
from app.main import main

if __name__ == "__main__":
    main()
