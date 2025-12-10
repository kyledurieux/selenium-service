# invoice_payment_diag.py

import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import html_handler
import CNHvariablelist
from utils import add_to_not_handled_dict
from data import nothandledclientsdict
import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent

def handle_diag_cpt(driver, cervicalshandled, data, patientname, dateofservice, typeofpatientnote):
    print("Handling diagnosis and CPT...")

    try:
        html_handler.click_element(driver, CNHvariablelist.invoicetab)
    except Exception as e:
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"Cannot open invoice tab: {e}")
        return False

    try:
        with open(BASE_DIR / 'theorder.json') as f:
            order = json.load(f)
    except Exception as e:
        print(f"Failed to load theorder.json: {e}")
        order = {}

    diagcodes = []
    cervicalshandled = sorted(set(cervicalshandled), key=lambda x: order.get(x, 999))
    for part in cervicalshandled:
        diagcodes.extend(data.get(part, {}).get("diagcode", []))

    # Add standard NMR codes
    base_diags = list(set(diagcodes + ["M54.2", "M79.12", "M62.838"]))

    for code in base_diags:
        try:
            html_handler.send_keys_by_id(driver, CNHvariablelist.diagnosisline, code, sleep_time=1)
            html_handler.send_keys_by_id(driver, CNHvariablelist.diagnosisline, Keys.ENTER, sleep_time=1)
            html_handler.click_element(driver, CNHvariablelist.diagnosisbutton)
            html_handler.clear_text_box(driver, CNHvariablelist.diagnosisline)
        except Exception as e:
            print(f"Error adding diagnosis code {code}: {e}")
            add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"Diag error: {code}")
            return False

    # Attempt to click all diagnosis resolve buttons
    try:
        container = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='diagnosisBillingListSortable']"))
        )
        buttons = container.find_elements(By.XPATH, ".//a[contains(@onclick, 'updateDiagnosisBillingResolvedDate')]")
        for i, btn in enumerate(buttons):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                btn.click()
            except Exception as e:
                print(f"Diag resolve button {i+1} failed: {e}")
    except Exception as e:
        print(f"Could not finalize diagnosis billing: {e}")

    # Now CPT code handling
    unique = set(diagcodes)
    count = len([code for code in unique if "M99.1" in code])

    
    cpt_code = "99212" if count < 1 else "98940" if count <= 2 else "98941" if count <= 4 else "98942"
    cpt_codes = ["S8990", cpt_code]  # always add wellness

    if any(x in unique for x in ["M99.06", "M99.07"]):
        cpt_codes.append("98943")  # extremities

    if any(x in cervicalshandled for x in ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]):
        cpt_codes.append("97140")  # soft tissue work

    try:
        for code in cpt_codes:
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, code, sleep_time=1)
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=1)
            html_handler.click_element(driver, CNHvariablelist.cptbutton)
            html_handler.clear_text_box(driver, CNHvariablelist.cptline)
    except Exception as e:
        print(f"Error applying CPT codes: {e}")
        return False

    return True

def handle_payment(driver, patientname, dateofservice, typeofpatientnote):
    print("Handling payment...")

    try:
        amount_input = driver.find_element(By.XPATH, '//input[@id="balanceDue"]')
        amount = float(amount_input.get_attribute("value")) - 75
    except:
        print("Could not get balance due, skipping discount")
        return True

    try:
        html_handler.send_keys_by_id(driver, "discount", str(amount))
        html_handler.send_keys_by_id(driver, "paymentType", "W")
        html_handler.send_keys_by_id(driver, "paymentType", Keys.ENTER)
        html_handler.click_element_by_id(driver, "addInvoicePaymentBtn")
        
    except Exception as e:
        print(f"Payment entry error: {e}")
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Payment failed")
        return False

    return True
