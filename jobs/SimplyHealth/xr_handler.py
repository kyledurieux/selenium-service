import html_handler
import CNHvariablelist
from selenium.webdriver.common.keys import Keys

def xr_objective(driver):
    try:
        # open the objective tab
        html_handler.click_element_by_id(driver, "NotezHealthSoapSuUs92ObjectivePresentation")
        # click on the copy previous objuective button
        html_handler.click_element(driver, "//*[@id='facility_zHealthSoapSuUs92Objective_tmpl']/div/div[1]/button")
    except:
        #clear objective tab
        html_handler.reset_objective(driver)
        return False
    return True

def xr_assessment(driver):
    try:
        # open the assessment tab
        html_handler.click_element_by_id(driver, "NotezHealthSoapSuUs91AssessmentPresentation")
        # click on the copy previous assessment button
        html_handler.click_element(driver, "//*[@id='facility_zHealthSoapSuUs91Assessment_tmpl']/div/div[5]/button")
    except:
        return False
    return True

def xr_plan(driver):
    try:
        # open the plan tab
        html_handler.click_element_by_id(driver, "NotezHealthSoapSuUs29TreatmentPlanPresentation")
        # click on the copy previous plan button
        html_handler.click_element(driver, "//*[@id='facility_zHealthSoapSuUs29TreatmentPlan_tmpl']/div/div[1]/button")
    except:
        #clear plan tab and return false
        html_handler.clear_findings(driver)
        return False
    return True

def xr_exam(driver):
    try:
        # open the exam tab
        html_handler.click_element_by_id(driver, "NotezHealthSoapSuUs98ExamPresentation")
        # click on the copy previous exam button
        html_handler.click_element(driver, "//*[@id='facility_zHealthSoapSuUs98Exam_tmpl']/div/div[1]/button")
    except:
        #clear exam tab and return false
        html_handler.click_element(driver, "//*[@id='moveToOldNotezHealthSoapSuUs98Exam']/button")
        html_handler.click_element(driver, "/html/body/div[67]/div/div/div[2]/button[2]")
        html_handler.click_element_by_id(driver, "NotezHealthSoapSuUs29TreatmentPlanPresentation")
        html_handler.clear_findings(driver)
        return False
    
    return True

def xr_addpro(driver):
    try:
        #click on additional tab
        html_handler.click_element_by_id(driver, "NoteAdditionalPresentation")
        #send keys to the additional procedeure text area
        html_handler.send_keys_by_id(driver, "addProcedure", "CBCT image taken as of today's date")

    except:
        print("Error in adding CBCT script to additional procedure line")
        return False
    return True

def xr_invoice_import_previous_diag(driver):
    try:
        #click on the invoice tab
        html_handler.click_element_by_id(driver, "NoteInvoicesPresentation")
        #click on the import previous diagnosis button
        html_handler.click_element(driver, "//*[@id='invoiceIcdDiv']/div[2]/div[1]/div[2]/button[3]")
    except:
        print("Error in importing previous diagnosis")
        return False
    return True

def xr_cptcodes(driver):
    try:
        html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", "70486", sleep_time=3)
    except: 
        print("Error in sending cpt code")
        return False

    try:
        html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", Keys.ENTER, sleep_time=2)
    except:
        print("Error adding cpt code")
        return False    

    try:
        html_handler.click_element(driver, CNHvariablelist.cptbutton)
    except:
        print("Error clicking cpt adding button")
        return False

    try:                                
        html_handler.clear_text_box(driver, "cptBillingCode.cptCodeWithDesc")
    except:
        print("Error clearing cpt code line")
        return False
    return True

