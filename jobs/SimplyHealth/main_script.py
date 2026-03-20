print('hi from kyle script')
# kyle.py - CNH main driver inside jobs folder

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from html_handler import setup_driver, login, push_basket_button, has_next_page, go_to_next_page
from patient_page_handler import handle_page_patients
from data import nothandledclientsdict
from utils import print_nothandled_clients
import os


def main():
    # TODO: we will move these into environment variables soon
    z_username = os.getenv("ZHEALTH_USERNAME")
    z_password = os.getenv("ZHEALTH_PASSWORD")

    if not z_username or not z_password:
        raise RuntimeError("ZHEALTH_USERNAME or ZHEALTH_PASSWORD not set in environment")

    # use z_username and z_password in your login code
    # username = "kdurieux"
    # password = "*Sublux1"
    url = "https://www.zhealthehr.com/"

    driver = setup_driver()
    from data import nothandledclientsdict
    nothandledclientsdict.clear()
    print("[startup] cleared nothandledclientsdict")
    
    try:
        login(driver, z_username, z_password, url)
        ok = push_basket_button(driver)
        if not ok:
            print("Failed to find basket button, exiting.")
            return

        while True:
            print("Handling patients on the current page")
            handle_page_patients(driver)

            if has_next_page(driver):
                print("Going to the next page")
                go_to_next_page(driver)
            else:
                print("No more pages to handle")
                break

    except Exception as e:
        print(f"Error in main: {e}")

    finally:
        if driver:
            try:
                print("Closing driver...")
                driver.quit()
            except Exception as close_err:
                print(f"Error while quitting driver: {close_err}")
                
        print("Finished processing.")
        print("Unprocessed patients:")
        print_nothandled_clients(nothandledclientsdict)
        driver.quit()


if __name__ == "__main__":
    main()
