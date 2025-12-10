# cervical_assessment_plan.py

import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import add_to_not_handled_dict
import html_handler
import CNHvariablelist

def handle_cervical_listings(driver, cervicalshandled):
    print("Handling cervical listings...")

    try:
        with open("cervicallegcheckmapping.json") as f:
            mapping = json.load(f)

        legcheck_map = mapping["legchecks"]["legcheck"]
        cervicals_set = set(mapping["legchecks"]["cervicals"])
        common = list(cervicals_set & set(cervicalshandled))

        html_handler.click_element(driver, CNHvariablelist.scanandlegchecktab)
        html_handler.click_element_by_id(driver, "KylObjADLImp")
        html_handler.click_element_by_id(driver, "KylObjScanNPatrn")
        html_handler.click_element_by_id(driver, "KylObjLegLSBal")

        if common:
            for cervical in common:
                if cervical in legcheck_map:
                    legcheck_text = legcheck_map[cervical]
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "KylObjOthTxtA")))
                    html_handler.send_keys_by_id(driver, "KylObjOthTxtA", f"{legcheck_text} modified Prill leg check shows a reading of unbalanced. All other Prill checks balanced.")
        else:
            # If no known cervical listings, default checkboxes
            for box_id in ["KylObjVertLgBal", "KylObjRotLgBal", "KylObjMedLgBal", "KylObjLatLgBal"]:
                html_handler.click_element_by_id(driver, box_id)

    except Exception as e:
        print(f"Error in handle_cervical_listings: {e}")
        html_handler.reset_objective(driver)
        return False

    return True

def handle_assessment(driver):
    print("Handling assessment tab...")
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, CNHvariablelist.assessmenttab)))
        html_handler.click_element(driver, CNHvariablelist.assessmenttab)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "KylAsesImp")))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "KylAsesClintPrg")))

        html_handler.click_element_by_id(driver, "KylAsesImp")
        html_handler.click_element_by_id(driver, "KylAsesClintPrg")

    except Exception as e:
        print(f"Error in handle_assessment: {e}")
        return False

    return True

def handle_plan(driver, cervicalshandled, data, nextvisit, patientname, dateofservice, typeofpatientnote):
    print("Handling plan tab...")

    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, CNHvariablelist.plantab)))
        html_handler.click_element(driver, CNHvariablelist.plantab)

    except:
        try:
            html_handler.click_element_by_id(driver, "NotezHealthSoapSuUs29TreatmentPlanPresentation")
        except Exception as e:
            add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Failed to open plan tab")
            return False

    if not nextvisit:
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "No next visit provided")
        html_handler.clear_findings(driver)
        return False

    try:
        if nextvisit == "AS":
            html_handler.click_element_by_id(driver, "KylPlnAsc")
        else:
            html_handler.click_element_by_id(driver, "KylPlnSnv")
            html_handler.send_keys_by_id(driver, "KylPLnSnv1Left", nextvisit[0])
            html_handler.send_keys_by_id(driver, "KylPLnSnv2Left", nextvisit[1], sleep_time=1)
    except Exception as e:
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"Error setting next visit: {e}")
        return False

    try:
        plancodes_added = []
        cervicalshandled = list(set(cervicalshandled))
        for part in cervicalshandled:
            if part in data:
                for code in data[part].get("plancode", []):
                    if code:
                        driver.find_element(By.ID, code).click()
                        plancodes_added.append(code)
                        time.sleep(1)
    except Exception as e:
        print(f"Plan code entry error: {e}")

    try:
        commoncervicals = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7']
        if not any(c in cervicalshandled for c in commoncervicals):
            html_handler.click_element_by_id(driver, "KylPlnNeuro")
            html_handler.click_element_by_id(driver, "KylPlnNeuroCran")
            html_handler.click_element_by_id(driver, "KylPlnNeuroCerv")
            html_handler.click_element_by_id(driver, "KylPlnNeuroObjNote")
    except Exception as e:
        print(f"Error clicking NMR codes: {e}")

    return True