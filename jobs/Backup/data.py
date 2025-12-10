# data.py

import json

# Shared global variables
nothandledclients = []
nothandledclientsdict = {}

notes = []
cervicalshandled = []
cervicalshandled_global = []
shortcodes = []
softtissue_global = []
bpartproblem = []

# Load shared mapping data
try:
    with open('shortcodemapping.json', 'r') as f:
        shortcodemapping = json.load(f)
except Exception as e:
    print(f"Error loading shortcodemapping.json: {e}")
    shortcodemapping = {}

# Utility note: other files like softtissuemapping.json, theorder.json, etc.
# can also be loaded here and reused in other scripts if needed.
