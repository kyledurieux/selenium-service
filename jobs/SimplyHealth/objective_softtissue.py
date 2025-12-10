# Objective and Soft Tissue Handling Module

import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from data import cervicalshandled, cervicalshandled_global, softtissue_global, bpartproblem
from utils import add_to_not_handled_dict
import html_handler
import CNHvariablelist
import pathlib
BASE_DIR = pathlib.Path(__file__).parent    

def process_comment_text(driver, nothandledclientsdict, dateofservice, patientname, data, text, typeofpatientnote):
    try:
        if text.strip() == "":
            add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "No comment text")
            return False

        split = text.split(". ")
        front_text = split[0] if len(split) > 1 else split[0]
        note = split[1] if len(split) > 1 else ""

        splitter = front_text.split(": ")
        body_softtissue_text = splitter[0] if len(splitter) > 1 else splitter[0]
        nextvisit = splitter[1] if len(splitter) > 1 else ""

        if not nextvisit or (not nextvisit[0].isdigit() and nextvisit[0] != "A"):
            add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Invalid next visit format")
            return False

        softtissuesplit = body_softtissue_text.split("; ")
        shortcodes_raw = softtissuesplit[0]
        softtissue = softtissuesplit[1] if len(softtissuesplit) > 1 else ""
        softtissue_global.append(softtissue)

        shortcodes = shortcodes_raw.split(", ")
        for shortcode in shortcodes:
            bpart = shortcode.split(" ")[0]
            if bpart in data:
                cervicalshandled.append(bpart)
                cervicalshandled_global.append(bpart)

        return cervicalshandled, shortcodes, note, nextvisit, softtissue

    except Exception as e:
        print(f"Error processing comment text: {e}")
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"Error parsing comment text: {e}")
        html_handler.reset_objective(driver)
        return False

def objective(driver, patientname, dateofservice, typeofpatientnote, data, shortcodes, cervicalshandled, nothandledclientsdict):
    try:
        html_handler.click_element(driver, CNHvariablelist.objectivetab)
    except Exception as e:
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"Failed to open objective tab: {e}")
        return False

    for shortcode in shortcodes:
        parts = shortcode.split(" ")
        bpart = parts[0]
        problems = parts[1:]

        if bpart not in data:
            add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"Unknown body part: {bpart}")
            html_handler.reset_objective(driver)
            return False

        cervicalshandled.append(bpart)
        try:
            bparttab = driver.find_element(By.ID, data[bpart]['htmlId'])
            bparttab.click()
            time.sleep(1)
        except:
            if bpart =="RETRACING" or bpart == "N/A":
                continue
            else:
                add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"Missing body part tab for {bpart}")
                continue

        listings = data[bpart]['listings']
        for problem in problems:
            for listing in listings.values():
                root = listing['root']
                if problem in listing.get('problems', []):
                    html_id = root + listing['shortcodemappings'].get(problem, problem)
                    try:
                        driver.find_element(By.ID, html_id).click()
                        time.sleep(1)
                    except:
                        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"Problem button not found: {html_id}")
                        html_handler.reset_objective(driver)
                        return False

        for default in data[bpart].get('defaults', []):
            root = listings[default]['root']
            default_code = listings[default]['default']
            html_id = root + default_code
            try:
                driver.find_element(By.ID, html_id).click()
            except:
                print(f"Default code {html_id} not found")

    return True

def handle_soft_tissue(driver, softtissue):
    if not softtissue:
        return True

    try:
        html_handler.click_element(driver, CNHvariablelist.muscleorsofttissuetab)
        with open(BASE_DIR / 'softtissuemapping.json') as f:
            mapping = json.load(f)

        mappings = mapping['shortcodemappings']
        muscles = mapping['tissue']
        softtissue_entries = softtissue.split(", ")

        for entry in softtissue_entries:
            parts = entry.split(" ")
            problemtext = parts[:-2]
            musclecode = parts[-2:]

            problemdesc = [mappings.get(p, p) for p in problemtext]
            muscledesc = [muscles.get(m, m) for m in musclecode]

            fulltext = f"Patient presents with a {' '.join(problemdesc)} {' '.join(muscledesc)} that is tender upon palpation and has a decreased range of motion."
            html_handler.send_keys_by_id(driver, "kpi_dailyNoteObjMusKylePNRecordNote", fulltext, sleep_time=2)

    except Exception as e:
        print(f"Soft tissue handling error: {e}")
        return False

    return True

def handle_notes(driver, note):
    try:
        if note:
            html_handler.click_element(driver, CNHvariablelist.additionaltab)
            html_handler.click_element_by_id(driver, "specialNotes")
            html_handler.clear_text_box(driver, CNHvariablelist.specialnotetextarea)
            html_handler.send_keys_by_id(driver, "specialNotes", note + ".", sleep_time=2)
            print("Special notes area updated successfully.")

 
    except Exception as e:
        print(f"Error handling notes: {e}")
        return False
    return True

def clear_handle_addprocedure(driver):
    try:
        # clear the additional notes text area
        html_handler.click_element(driver, CNHvariablelist.additionaltab)
        html_handler.clear_text_box(driver, CNHvariablelist.additionalproceduretextarea)
        print("Additional Procedure area cleared successfully.")
        html_handler.click_element(driver, CNHvariablelist.savebutton)
        print("Additional Procedure area updated successfully.")

    except Exception as e:
        print(f"Error clearing or updating additional procedure area: {e}")
        return False