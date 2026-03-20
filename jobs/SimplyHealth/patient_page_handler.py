# patient_page_handler.py

from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from utils import already_in_not_handled_dict
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from data import cervicalshandled, cervicalshandled_global, shortcodes, notes, softtissue_global, bpartproblem, nothandledclientsdict
from utils import check_patientdate_exists, add_to_not_handled_dict
from html_handler import click_homebutton, push_basket_button, click_edit_button

from note_type_handlers import handle_type1_patient, handle_type2_patient, handle_type3_patient, handle_type4_patient, handle_type5_patient
import time
import traceback



def handle_page_patients(driver):
    print("FUNCTION - handle_page_patients")

    while True:
        driver.switch_to.default_content()

        try:
            print("Looking for myBasketDraftList...")
            table_body = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "myBasketDraftList"))
            )
            print("Found myBasketDraftList")

            rows = table_body.find_elements(By.TAG_NAME, "tr")
            print(f"Found {len(rows)} patients")

        except Exception as e:
            print(f"Top-level error in handle_page_patients: {e}")
            traceback.print_exc()
            return False

        found_actionable_patient = False

        for index in range(1, len(rows) + 1):
            patientname = "<unknown>"
            dateofservice = "<unknown>"
            typeofpatientnote = "<unknown>"

            try:
                driver.switch_to.default_content()

                table_body = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "myBasketDraftList"))
                )
                current_rows = table_body.find_elements(By.TAG_NAME, "tr")

                if index > len(current_rows):
                    print(f"Row {index} no longer exists after refresh. Skipping.")
                    continue

                row = current_rows[index - 1]

                dateofservice = row.find_element(By.XPATH, "./td[1]").text.strip()
                patientname = row.find_element(By.XPATH, "./td[2]").text.strip()
                typeofpatientnote = row.find_element(By.XPATH, "./td[3]/strong").text.strip()

                print(f"\nRow {index} - {patientname}, DOS: {dateofservice}, Type: {typeofpatientnote}")

                # Clear global state for new patient
                cervicalshandled.clear()
                cervicalshandled_global.clear()
                shortcodes.clear()
                notes.clear()
                softtissue_global.clear()
                bpartproblem.clear()

                if check_patientdate_exists(patientname, dateofservice, typeofpatientnote):
                    print("Patient already handled")
                    continue

                if already_in_not_handled_dict(patientname, dateofservice, typeofpatientnote):
                    print(f"Patient already in not handled list: {patientname} - {dateofservice} ({typeofpatientnote})")
                    print("____________________________\n")
                    print(f"Skipping patient: {patientname}\n____________________________\n")
                    continue

                found_actionable_patient = True

                success = handle_patient_files(
                    driver,
                    patientname,
                    dateofservice,
                    typeofpatientnote,
                    index
                )

                if not success:
                    print(f"handle_patient_files returned False for {patientname}")
                    _refresh_basket(driver)
                    break

                print(f"Successfully handled {patientname}")
                _refresh_basket(driver)
                break

            except Exception as e:
                print(f"Error processing patient row: {e}")
                traceback.print_exc()

                add_to_not_handled_dict(
                    patientname,
                    dateofservice,
                    typeofpatientnote,
                    f"Exception in patient row loop: {type(e).__name__}: {e}"
                )

                try:
                    print(f"DEBUG: current_url = {driver.current_url}")
                    print(f"DEBUG: page title = {driver.title}")
                    print("DEBUG: first 500 chars of page:")
                    print(driver.page_source[:500])
                except Exception as debug_err:
                    print(f"DEBUG collection failed: {type(debug_err).__name__}: {debug_err}")

                try:
                    _refresh_basket(driver)
                except Exception as nav_error:
                    print(f"Recovery navigation failed: {type(nav_error).__name__}: {nav_error}")
                    traceback.print_exc()
                    return False

                break

        else:
            print("All patients handled on this page.")
            return True

        if not found_actionable_patient:
            print("No actionable patients found.")
            return True


def _refresh_basket(driver):
    print("Recovery: clicking home button")
    driver.switch_to.default_content()
    click_homebutton(driver)
    time.sleep(2)

    print("Recovery: clicking basket button")
    push_basket_button(driver)
    time.sleep(2)

    driver.switch_to.default_content()

    print("Recovery: waiting for refreshed basket")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "myBasketDraftList"))
    )
    print("Recovery: basket refreshed")



def handle_patient_files(driver, patientname, dateofservice, typeofpatientnote, index):
    print(f"Routing {patientname} - Type: {typeofpatientnote}")

    note_handlers = {
        "FE": handle_type1_patient,
        "FU": handle_type1_patient,
        "NP": handle_type2_patient,
        "RO": handle_type4_patient,
        "MG": handle_type3_patient,
        "XR": handle_type5_patient
    }

    if typeofpatientnote in note_handlers:
        #click_edit_button(driver, index)
        from utils import click_correct_edit_button

        if not click_correct_edit_button(driver, patientname, dateofservice, typeofpatientnote):
            add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Edit button not found")
            return False

        return note_handlers[typeofpatientnote](driver, patientname, dateofservice, typeofpatientnote)

    print("Unknown note type. Skipping.")
    add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Unknown patient note type")
    return False
