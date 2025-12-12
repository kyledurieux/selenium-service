from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import shutil
import CNHvariablelist
from selenium.common.exceptions import NoSuchElementException
import subprocess


# Create a function for setting up the driver
def setup_driver():
    # Clear WebDriver cache

    try:
        cache_dir = os.path.join(os.path.expanduser("~"), ".wdm")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("WebDriver cache cleared.")
    except Exception as e:
        print(f"Error clearing cache: {e}")

    kill_old_chrome()
    
    try:
        """
        Create a Chrome WebDriver that works inside the Docker container.
        """
        print("[html_handler] setup_driver: starting headless Chrome inside Docker")

        # 👇 NEW: read HEADLESS env (default = "1" = headless)
        headless_env = os.environ.get("HEADLESS", "1")
        headless = (headless_env == "1")

        chrome_options = Options()
        if headless:
            print("[html_handler] HEADLESS=1, running in headless mode")
            chrome_options.add_argument("--headless=new")
        else:
            print("[html_handler] HEADLESS=0, running WITHOUT headless (visible window if environment supports it)")


        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")

                # This uses the ChromeDriver baked into the docker image
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"[html_handler] First Chrome start failed (headless={headless}): {e}")
            # If we were trying NON-headless and it failed (e.g. in a headless EC2 container),
            # fall back to headless mode automatically.
            if not headless:
                print("[html_handler] Falling back to headless mode inside container...")
                chrome_options.add_argument("--headless=new")
                driver = webdriver.Chrome(options=chrome_options)
                return driver
            # If we were already headless, just re-raise
            raise


       
    except Exception as e:
        print(f"Error setting up the driver: {e}")
        raise

# Create a function for login
def login(driver, username, password, url):

    driver.get(url)
    
    try:
        username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='navbarNavAltMarkup']/div/ul/div/div[1]/form/li[1]/input")))
        password_field = driver.find_element(By.XPATH, "//*[@id='navbarNavAltMarkup']/div/ul/div/div[1]/form/li[2]/input")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        print("login username and password entered")
         
        time.sleep(3)
      
    except (TimeoutException, ElementNotInteractableException) as e:
        print("login def, Login failed:", e)
        return False
    
    return True

def click_homebutton(driver):
    try:
        home_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='homeBtn']")))
        home_button.click()
        time.sleep(2)
        print("Home button clicked")
        return True
    except TimeoutException:
        print("Home button not found")
        return False
    
def click_the_diag_buttons(driver, count): # edited 5.8.2025
    
    # Find all <a> elements with onclick calling updateDiagnosisBillingResolvedDate
    buttons = driver.find_elements(By.XPATH, '//a[contains(@onclick, "updateDiagnosisBillingResolvedDate(")]')

    # Optional: wait for page readiness (if dynamic loading is involved)
    wait = WebDriverWait(driver, 10)

    for i, btn in enumerate(buttons):
        try:
            # Scroll to the element (optional, helps with visibility issues)
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            
            # Wait until clickable
            wait.until(EC.element_to_be_clickable(btn))
            
            # Click the element
            btn.click()

            # Optional: wait or handle any popups before continuing
            # time.sleep(0.5)

        except Exception as e:
            print(f"Could not click button #{i}: {e}")

    # This is the original working code that was commented out
    # loop the number of times of the count above and click the buttons adding the count to the xpath each time
    # for i in range(count):
    #     try:
    #         print(i)
    #         buttonroot = '/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li['
    #         buttonend = ']/div[3]/a[2]'
    #         button = click_element(driver, buttonroot + str(i+1) + buttonend)

    #     except Exception as e:
    #         print(f"Error clicking the diag buttons: {e}")


#create def for pushing the basket button
def push_basket_button(driver):
    try:
        basket_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, CNHvariablelist.mybasket)))
                                                                                                  #//*[@id="MyBasket"]
        basket_button.click()
        print("Basket button clicked")
        time.sleep(2)   
        return True  
                                                                   
    except TimeoutException:
        print("Basket button not found")
        driver.quit()
        return False 

# utility function to clear the text box
def clear_text_box(driver, element_id, sleep_time=2):
    try:
        text_box = driver.find_element(By.XPATH, element_id)
        text_box.clear()
        time.sleep(sleep_time)
        # print("Text box cleared")
    except Exception as e:
        print(f"Error clearing text box: {e}")

# Utility function to click an element by its XPath
def click_element(driver, xpath, sleep_time=2):
    # Wait until the element is clickable
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    #element = driver.find_element(By.XPATH, xpath)
    element.click()
    time.sleep(sleep_time)

def click_element_by_id(driver, element_id, sleep_time=2):
    # Wait until the element is clickable
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, element_id)))
    #element = driver.find_element(By.ID, element_id)
    element.click()
    time.sleep(sleep_time)

# Utility function to send keys to an element by its ID
def send_keys_by_id(driver, element_id, keys, sleep_time=1):
    try:
        element = driver.find_element(By.ID, element_id)
        element.send_keys(keys)
        time.sleep(sleep_time)
    except:
        element = driver.find_element(By.XPATH, element_id)
        element.send_keys(keys)
        time.sleep(sleep_time)


def is_element_in_iframe(driver, element_id):
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    for iframe in iframes:
        driver.switch_to.frame(iframe)
        try:
            element = driver.find_element(By.ID, element_id)
            driver.switch_to.default_content()  # Switch back to the main content
            return True
        except NoSuchElementException:
            driver.switch_to.default_content()  # Switch back to the main content and continue
    return False

def click_optional_ok_button(driver, timeout=3):
    try:
        ok_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-bb-handler="ok" and text()="OK"]'))
        )
        ok_button.click()
        print("OK button clicked.")
    except (TimeoutException, NoSuchElementException):
        print("OK button not found — continuing.")



def get_comment_text(driver):
    
    try:
        #see if the ok button is present
        click_optional_ok_button(driver)

        # Wait for the text box to be clickable
        text_box = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'noteComments')))
        print("Text box found first try")
        time.sleep(2)
    
    except:
        try:
            # click the ENTER key to close the pop up box
            actions = ActionChains(driver)
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(2)
            text_box = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'noteComments')))
            print("Text box found second try")

        except:
            print("Text box not found")
            return False
                
    try:
        # Check if element is in an iframe
        if is_element_in_iframe(driver, 'noteComments'):
            # Switch to the iframe containing the element
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                driver.switch_to.frame(iframe)
                try:
                    text_box = driver.find_element(By.ID, 'noteComments')
                    break  # Exit the loop if the element is found
                except NoSuchElementException:
                    driver.switch_to.default_content()
            else:
                print("Element not found in any iframe")
                return None
        else:
            # Element is not in an iframe
            print("Element is not in an iframe")
            text_box = driver.find_element(By.ID, 'noteComments')        

    except NoSuchElementException:
        print("Text box not found in iframe")
        return None

    # Retrieve the text from the text box
    text = text_box.get_attribute('value')
    print("Comment text box found")
    print("Comment text:", text)
    return text
    

def go_back_to_basket(driver):
    try:
        click_element(driver, CNHvariablelist.homebutton, sleep_time=4)
        click_element(driver, CNHvariablelist.mybasket, sleep_time=2)
        click_element(driver, CNHvariablelist.mybasket, sleep_time=4)
                  
    except Exception as e:
        print(f"Error going back to basket: {e}")



def clear_findings(driver):
    try:
        #clear the plan tab
        click_element(driver, CNHvariablelist.plantab, sleep_time=2)
        try:
            #click_element(driver, CNHvariablelist.clearfindingsbutton, sleep_time=2)
            click_element(driver, CNHvariablelist.clearfindingsbutton, sleep_time=2)
                    
        except:
            print("Clear findings button not found on plan tab")

        try:
            driver.find_element(By.CSS_SELECTOR, 'button[data-bb-handler="confirm"].btn-danger').click()
        except:
            print("No confirmation button found on plan tab")
            return False
        
        #clear the assessment tab
        click_element(driver, CNHvariablelist.assessmenttab, sleep_time=2)
        click_element(driver, CNHvariablelist.clearfindingsbutton, sleep_time=2)
        try:
            driver.find_element(By.CSS_SELECTOR, 'button[data-bb-handler="confirm"].btn-danger').click()
        except:
            print("No confirmation button found on assessment tab")
            return False

        #clear the objective tab    
        click_element(driver, CNHvariablelist.objectivetab, sleep_time=2)
        click_element(driver, CNHvariablelist.clearfindingsbutton, sleep_time=2)
        try:
            driver.find_element(By.CSS_SELECTOR, 'button[data-bb-handler="confirm"].btn-danger').click()
        except:
            print("No confirmation button found on objective tab")
            return False
        
    except Exception as e:
        print(f"CLEAR_FINDINGS, Error clearing findings: {e}")

def click_edit_button(driver, index): #updated click_edit_button to use index instead of xpath 5.13.2025
    try:
        # Locate the specific row using index (1-based for XPath)
        row_xpath = f'//tbody[@id="myBasketDraftList"]/tr[{index}]'
        row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, row_xpath)))

        # Within that row, find the "Edit" button — usually the second button in the last <td>
        edit_button = row.find_element(By.XPATH, './/button[contains(text(), "Edit")]')

        # Wait until the button is clickable and click
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(edit_button))
        edit_button.click()
        print(f"Edit button in row {index} clicked.")

    except Exception as e:
        print(f"Error clicking Edit button in row {index}: {e}")
            
    return True

## old code that was not used in the recent edits as of 07/20/2025
# def click_edit_button(driver, index): # edited 5.8.2025
#     try:
#         #wait until the edit button is clickable
#         edit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "addproblem") and text()="Edit"]')))
#         # Construct the XPath for the edit button using the index                           # '//button[contains(@class, "addproblem") and text()="Edit"]'
#                                                                                             # f"/html/body/section/section[1]/div/div[2]/div[1]/section/article/div/div/div[1]/table/tbody/tr[{index}]/td[4]/button[2]"
#         # Click the edit button
      
#         if edit_button:
#             print("Edit button found, attempting to click...")
#             edit_button[index].click()
#             time.sleep(2)
#             print("Edit button clicked")
#             print()

#         else:
#             print("Edit button not found")
#             print()
#             return False  # Return False if the edit button is not found

#     except Exception as e:
#         print(f"Error clicking edit button: {e}")

#     return True

def reset_objective(driver):
    click_element_by_id(driver, "zHealthSoapSuUs92ObjectiveTab", sleep_time=2)
    click_element_by_id(driver, "moveToOldNotezHealthSoapSuUs92Objective", sleep_time=2)
    try:
        driver.find_element(By.CSS_SELECTOR, 'button[data-bb-handler="confirm"].btn-danger').click()  
    except:
        print("No confirmation button found on objective tab")
        return False
    
    print("Objective tab cleared")
    print()

def kill_old_chrome():
    try:
        subprocess.run(["pkill", "-f", "chrome"], check=False)
        subprocess.run(["pkill", "-f", "chromedriver"], check=False)
        print("Old Chrome processes cleaned.")
    except Exception as e:
        print(f"Error cleaning chrome processes: {e}")

def has_next_page(driver):

    try:
        next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "myBasketDraftListNext")))
        if "paginate_button next disabled" in next_button.get_attribute("class"):
            print("next page disabled. stopping script")
            print()
            return False
        
        return True

    except TimeoutException:
        return False
    except Exception as e:
        print(f"Error checking for next page: {e}")
        return False

def go_to_next_page(driver):
    
    try:
        click_element(driver, '//a[text()="Next"]', sleep_time=2)
        print("Next page button clicked")
        time.sleep(2)  # Wait for the next page to load

    except NoSuchElementException:
        print("No next page button found.")
    except TimeoutException:
        print("Timeout while waiting for the next page button.")
    except ElementNotInteractableException:
        print("Element not interactable. Moving to the next iteration.")
    except Exception as e:
        print(f"Error navigating to the next page: {e}")