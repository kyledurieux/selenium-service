print('hi from kyle script')
# kyle.py - CNH main driver inside jobs folder

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from html_handler import setup_driver, login, push_basket_button, has_next_page, go_to_next_page
from patient_page_handler import handle_page_patients
from data import nothandledclientsdict
from utils import print_nothandled_clients


def main():
    # TODO: we will move these into environment variables soon
    username = "kdurieux"
    password = "*Sublux1"
    url = "https://www.zhealthehr.com/"

    driver = setup_driver()

    try:
        login(driver, username, password, url)
        push_basket_button(driver)

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
        print("Finished processing.")
        print("Unprocessed patients:")
        print_nothandled_clients(nothandledclientsdict)
        driver.quit()


if __name__ == "__main__":
    main()
