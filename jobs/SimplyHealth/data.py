# data.py

import json
import pathlib

# Shared global variables
nothandledclients = []
nothandledclientsdict = {}

notes = []
cervicalshandled = []
cervicalshandled_global = []
shortcodes = []
softtissue_global = []
bpartproblem = []
BASE_DIR = pathlib.Path(__file__).resolve().parent


# Load shared mapping data
try:
    with open(BASE_DIR / 'shortcodemapping.json', 'r') as f:
        shortcodemapping = json.load(f)
except Exception as e:
    print(f"Error loading shortcodemapping.json: {e}")
    shortcodemapping = {}
except FileNotFoundError as e:
    print(f"shortcodemapping.json not found in {BASE_DIR}: {e}")
    shortcodemapping = {}


# Utility note: other files like softtissuemapping.json, theorder.json, etc.
# can also be loaded here and reused in other scripts if needed.
