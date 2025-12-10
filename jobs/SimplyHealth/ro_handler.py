import html_handler
from selenium.webdriver.common.by import By

def ro_exam(driver):
    try:
        # click on the clear previous exam button
        html_handler.click_element_by_id(driver, "NotezHealthSoapSuUs98ExamPresentation") 
        html_handler.click_element_by_id(driver, "moveToOldNotezHealthSoapSuUs98Exam")
        
    except:
        print("ro _exam, unalbe to clear previous exam")
        return False
    
    try:
        #click on the button to confirm clear findings
        driver.find_element(By.CSS_SELECTOR, 'button[data-bb-handler="confirm"].btn-danger').click() 
    except:
        try:
            html_handler.click_element(driver, "/html/body/div[69]/div/div/div[2]/button[2]")

        except:
            print("RO click confirm clear button not clickable")
            #clear the note
            html_handler.clear_findings(driver)
            return False
        
    return True





                               