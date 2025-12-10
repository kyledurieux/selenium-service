# tab_navigation.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import html_handler
import CNHvariablelist

def open_tab(driver, xpath, label):
    """Generic tab opener with wait and click"""
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        html_handler.click_element(driver, xpath)
        print(f"✅ Opened {label} tab.")
        return True
    except Exception as e:
        print(f"❌ Failed to open {label} tab: {e}")
        return False

def open_plan_tab(driver):
    return open_tab(driver, CNHvariablelist.plantab, "Plan")

def open_assessment_tab(driver):
    return open_tab(driver, CNHvariablelist.assessmenttab, "Assessment")

def open_notes_tab(driver):
    return open_tab(driver, CNHvariablelist.notestab, "Notes")

def open_invoice_tab(driver):
    return open_tab(driver, CNHvariablelist.invoicetab, "Invoice")
