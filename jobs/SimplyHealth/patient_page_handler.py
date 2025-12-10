# patient_page_handler.py

from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from utils import already_in_not_handled_dict

from data import cervicalshandled, cervicalshandled_global, shortcodes, notes, softtissue_global, bpartproblem, nothandledclientsdict
from utils import check_patientdate_exists, add_to_not_handled_dict
from html_handler import click_homebutton, push_basket_button, click_edit_button

from note_type_handlers import handle_type1_patient, handle_type2_patient, handle_type3_patient, handle_type4_patient, handle_type5_patient

def handle_page_patients(driver):
    print("FUNCTION - handle_page_patients")

    try:
        table_body = driver.find_element(By.ID, "myBasketDraftList")
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(rows)} patients")

        for index, row in enumerate(rows, start=1):
            try:
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
                    continue

                

                if already_in_not_handled_dict(patientname, dateofservice, typeofpatientnote):
                    print(f"Patient already in not handled list: {patientname} - {dateofservice} ({typeofpatientnote})")
                    print("____________________________\n")
                    print(f"Skipping patient: {patientname}\n____________________________\n")
                    continue
    
                # skip_patient = False
                # if patientname in nothandledclientsdict:
                #     print("Patient found in not handled dictionary:", patientname)
                #     # check if the date of service and type of patient note match
                #     for record in nothandledclientsdict[patientname]:
                #         print("checking date of service:", record ['dateofservice'])
                #         print("checking type of patient note:", record ['typeofpatientnote'])
                #         print(dateofservice, typeofpatientnote)

                #         if (record['dateofservice'] == dateofservice and 
                #             record['typeofpatientnote'] == typeofpatientnote):
                #             print("Patient already in not handled list")
                #             print("____________________________")
                #             print()
                #             skip_patient = True
                #             break                            
                # if skip_patient:
                #     print("Skipping patient:", patientname)
                #     print("____________________________")
                #     print()
                #     continue   

                if not handle_patient_files(driver, patientname, dateofservice, typeofpatientnote, index):
                    continue

                click_homebutton(driver)
                push_basket_button(driver)
                return handle_page_patients(driver)

            # except StaleElementReferenceException:
            #     print("Stale row; retrying")
            #     push_basket_button(driver)
            #     return handle_page_patients(driver)

            except Exception as e:
                print(f"Error processing patient row: {e}")
                add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Exception in patient row loop")
                click_homebutton(driver)
                push_basket_button(driver)
                return handle_page_patients(driver)

        print("All patients handled on this page.")
        return True

    except Exception as e:
        print(f"Top-level error in handle_page_patients: {e}")
        return False

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
