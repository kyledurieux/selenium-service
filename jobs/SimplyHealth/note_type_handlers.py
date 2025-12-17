
from data import notes, nothandledclientsdict, cervicalshandled, shortcodes, cervicalshandled_global, softtissue_global, bpartproblem, shortcodemapping
from utils import add_to_not_handled_dict, addto_data
import html_handler
from html_handler import get_comment_text, click_homebutton, push_basket_button, clear_findings
from selenium import webdriver
from selenium.webdriver.common.by import By
import np_handler
import ro_handler
import xr_handler
from objective_softtissue import handle_notes
import time

from objective_softtissue import objective, handle_soft_tissue, clear_handle_addprocedure
from cervical_assessment_plan import handle_cervical_listings, handle_assessment, handle_plan
from invoice_payment_diag import handle_diag_cpt, handle_payment
from utils import DEFAULT_DATA_FILE

import pathlib
BASE_DIR = pathlib.Path(__file__).parent


# This function handles the abort logic for any step that fails
def _abort(driver, patientname, dateofservice, typeofpatientnote, step):
    print(f"❌ {step} not handled")
    add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"{step} failed")
    click_homebutton(driver)
    push_basket_button(driver)
    return False

def handle_type1_patient(driver, patientname, dateofservice, typeofpatientnote):
    print(f"\nHandling FE/FU for: {patientname} - {dateofservice}")

    try:
        text = get_comment_text(driver)

        # Process comment text
        from objective_softtissue import process_comment_text  # Lazy import to avoid circular issues
        result = process_comment_text(driver, nothandledclientsdict, dateofservice, patientname, shortcodemapping, text, typeofpatientnote)
        if result is False:
            add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Error in process_comment_text")
            # click_homebutton(driver)
            # push_basket_button(driver)
            return False

        cervicalshandled_local, shortcodes_local, note, nextvisit, softtissue = result

        if objective(driver, patientname, dateofservice, typeofpatientnote, shortcodemapping, shortcodes_local, cervicalshandled_local, nothandledclientsdict) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Objective")

        if handle_soft_tissue(driver, softtissue) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Soft tissue")

        if handle_cervical_listings(driver, cervicalshandled_local) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Cervical listings")

        if handle_assessment(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Assessment")

        if note:
            notes.append(note)
        from objective_softtissue import handle_notes
        if handle_notes(driver, note) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Notes")

        if handle_plan(driver, cervicalshandled_local, shortcodemapping, nextvisit, patientname, dateofservice, typeofpatientnote) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Plan")

        if handle_diag_cpt(driver, cervicalshandled_local, shortcodemapping, patientname, dateofservice, typeofpatientnote) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Diagnosis/CPT")

        if handle_payment(driver, patientname, dateofservice, typeofpatientnote) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Payment")

        sign_note()
        addto_data(patientname, dateofservice, typeofpatientnote)

        print(f"✅ Completed {patientname} - {dateofservice}")

    except Exception as e:
        print(f"Exception in handle_type1_patient: {e}")
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"Exception: {e}")
        clear_findings(driver)
        return False

    return True


def handle_type2_patient(driver, patientname, dateofservice, typeofpatientnote):
    print(f"\nHandling NP for: {patientname} - {dateofservice}")

    try:
        # If patient was previously marked not-handled for XR, clean them
        if patientname in nothandledclientsdict:
            for record in nothandledclientsdict[patientname]:
                if record["typeofpatientnote"] == "XR":
                    nothandledclientsdict[patientname].remove(record)
            if not nothandledclientsdict[patientname]:
                del nothandledclientsdict[patientname]

        text = html_handler.get_comment_text(driver)

        from objective_softtissue import process_comment_text
        result = process_comment_text(driver, nothandledclientsdict, dateofservice, patientname, shortcodemapping, text, typeofpatientnote)
        if result is False:
            add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Error in NP comment text")
            html_handler.push_basket_button(driver)
            return False

        cervicalshandled_local, shortcodes_local, note, nextvisit, softtissue = result

        if objective(driver, patientname, dateofservice, typeofpatientnote, shortcodemapping, shortcodes_local, cervicalshandled_local, nothandledclientsdict) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Objective")

        if handle_soft_tissue(driver, softtissue) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Soft Tissue")

        if handle_cervical_listings(driver, cervicalshandled_local) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Cervicals")

        if note:
            notes.append(note)
            
        if handle_notes(driver, note) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Notes")

        if np_handler.exam_note_plan(driver, cervicalshandled_local, shortcodemapping, nextvisit, patientname, dateofservice, typeofpatientnote) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "NP plan")

        if np_handler.exam_note(driver, cervicalshandled_global, softtissue_global, bpartproblem, patientname, dateofservice, typeofpatientnote) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "NP exam")

        if np_handler.exam_handle_diag(driver, cervicalshandled_local, shortcodemapping) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "NP diag")

        if np_handler.exam_handle_cpt(driver, cervicalshandled_local) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "NP CPT")

        if np_handler.exam_handle_payment(driver, patientname, dateofservice, typeofpatientnote, nothandledclientsdict) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "NP payment")

        sign_note()
        addto_data(patientname, dateofservice, typeofpatientnote)
        print(f"✅ Completed NP: {patientname}")

    except Exception as e:
        print(f"Exception in NP handler: {e}")
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"NP crash: {e}")
        html_handler.clear_findings(driver)
        return False

    return True


def handle_type3_patient(driver, patientname, dateofservice, typeofpatientnote):
    print(f"Skipping massage note (MG) for {patientname}")
    add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Skipped massage note")
    return True

def handle_type4_patient(driver, patientname, dateofservice, typeofpatientnote):
    print(f"\nHandling RO for: {patientname} - {dateofservice}")

    try:
        text = html_handler.get_comment_text(driver)

        from objective_softtissue import process_comment_text
        result = process_comment_text(driver, nothandledclientsdict, dateofservice, patientname, shortcodemapping, text, typeofpatientnote)
        if result is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "RO comment")

        cervicalshandled_local, shortcodes_local, note, nextvisit, softtissue = result

        if objective(driver, patientname, dateofservice, typeofpatientnote, shortcodemapping, shortcodes_local, cervicalshandled_local, nothandledclientsdict) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Objective")

        if handle_soft_tissue(driver, softtissue) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Soft Tissue")

        if handle_cervical_listings(driver, cervicalshandled_local) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Cervicals")

        if handle_assessment(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Assessment")

        if handle_notes(driver, note) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Notes")
        
        if clear_handle_addprocedure(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Clear Add Procedure")

        if handle_plan(driver, cervicalshandled_local, shortcodemapping, nextvisit, patientname, dateofservice, typeofpatientnote) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Plan")

        if ro_handler.ro_exam(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "RO exam")

        if handle_diag_cpt(driver, cervicalshandled_local, shortcodemapping, patientname, dateofservice, typeofpatientnote) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Diagnosis/CPT")

        if handle_payment(driver, patientname, dateofservice, typeofpatientnote) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "Payment")

        sign_note()
        addto_data(patientname, dateofservice, typeofpatientnote)
        print(f"✅ Completed RO: {patientname}")

    except Exception as e:
        print(f"Exception in handle_type4_patient: {e}")
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"RO crash: {e}")
        html_handler.clear_findings(driver)
        return False

    return True


def handle_type5_patient(driver, patientname, dateofservice, typeofpatientnote):
    print(f"\nHandling XR for: {patientname} - {dateofservice}")

    # Check that an NP note already exists for this patient
    try:
        import pandas as pd
        shcdata = pd.read_csv(DEFAULT_DATA_FILE)
        np_exists = any(
            (row["Patient Name"] == patientname and row["Type of Patient Note"] == "NP")
            for _, row in shcdata.iterrows()
        )

        if not np_exists:
            print("❌ XR note skipped — no matching NP note found.")
            add_to_not_handled_dict(patientname, dateofservice, "XR", "NP note not yet handled")

            time.sleep(3)
            click_homebutton(driver)
            push_basket_button(driver)
            return False

    except Exception as e:
        print(f"Error checking NP note for XR: {e}")
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Error reading shcdata for NP check")
        return False

    # Continue with XR processing
    try:
        if xr_handler.xr_objective(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "XR objective")

        if xr_handler.xr_assessment(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "XR assessment")

        if xr_handler.xr_plan(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "XR plan")

        if xr_handler.xr_exam(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "XR exam")

        if xr_handler.xr_addpro(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "XR addpro")

        if xr_handler.xr_invoice_import_previous_diag(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "XR diag import")

        if xr_handler.xr_cptcodes(driver) is False:
            return _abort(driver, patientname, dateofservice, typeofpatientnote, "XR CPT")

        sign_note()
        addto_data(patientname, dateofservice, typeofpatientnote)
        print(f"✅ Completed XR: {patientname}")

    except Exception as e:
        print(f"Exception in handle_type5_patient: {e}")
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, f"XR crash: {e}")
        return False

    # Return to the basket so next patient routing starts fresh
    click_homebutton(driver)
    push_basket_button(driver)

    return True


def sign_note():
    print("🖋️ Signing note...")