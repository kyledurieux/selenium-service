# utils.py

import pandas as pd
import csv
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException

from data import nothandledclientsdict
from pathlib import Path

BASE_DIR = Path(__file__).parent


def print_nothandled_clients(nothandledclientsdict):
    """
    Pretty prints the nothandledclientsdict in a readable format grouped by patient.
    """
    print("\n===== ❌ Not Handled Clients Summary =====\n")

    for patient, issues in nothandledclientsdict.items():
        print(f"🧍 {patient}")
        for entry in issues:
            date = entry.get("dateofservice", "Unknown Date")
            note_type = entry.get("typeofpatientnote", "Unknown Type")
            finding = entry.get("findings", "No findings listed")
            print(f"   📅 {date} | 📝 {note_type}")
            print(f"     ➤ {finding}")
        print()  # Blank line between patients

    print("==========================================\n")

def add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, findings):
    entry = {
        'dateofservice': dateofservice,
        'typeofpatientnote': typeofpatientnote,
        'findings': findings
    }
    if patientname in nothandledclientsdict:
        nothandledclientsdict[patientname].append(entry)
    else:
        nothandledclientsdict[patientname] = [entry]

def check_patientdate_exists(patientname, dateofservice, typeofpatientnote, filename='shcdata.csv'):
    filename = BASE_DIR / filename
    print(f"Checking if {patientname} with DOS {dateofservice} is already in {filename}")

    try:
        shcdata = pd.read_csv(filename)

        # Normalize column names (strip spaces, remove BOM, etc.)
        shcdata.columns = [
            col.strip().replace('\ufeff', '') for col in shcdata.columns
        ]
        print("CSV columns detected:", list(shcdata.columns))

        required_cols = ['Patient Name', 'Date of Service', 'Type of Patient Note']
        for col in required_cols:
            if col not in shcdata.columns:
                print(f"Missing expected column '{col}' in {filename}")
                # If the structure isn't what we expect, safely treat as "not found"
                return False

        for index, row in shcdata.iterrows():
            if (
                str(row['Patient Name']).strip() == str(patientname).strip() and
                str(row['Date of Service']).strip() == str(dateofservice).strip() and
                str(row['Type of Patient Note']).strip() == str(typeofpatientnote).strip()
            ):
                date_format = "%m/%d/%Y"
                dateofservice1 = datetime.strptime(row['Date of Service'], date_format)
                current_date = datetime.now()
                six_months_ago = current_date - timedelta(days=30 * 6)

                if dateofservice1 < six_months_ago:
                    print("Deleting outdated patient record")
                    shcdata.drop(index, inplace=True)
                    shcdata.to_csv(filename, index=False)
                    return False

                print("Patient already handled")
                return True

        return False

    except Exception as e:
        print(f"Error checking patient in CSV: {e}")
        return False

# def check_patientdate_exists(patientname, dateofservice, typeofpatientnote, filename='shcdata.csv'):
#     print(f"Checking if {patientname} with DOS {dateofservice} is already in {filename}")

#     try:
#         shcdata = pd.read_csv(filename)
#         patient_exists = False

#         for index, row in shcdata.iterrows():
#             if row['Patient Name'] == patientname and \
#                row['Date of Service'] == dateofservice and \
#                row['Type of Patient Note'] == typeofpatientnote:
                
#                 date_format = "%m/%d/%Y"
#                 dateofservice1 = datetime.strptime(row['Date of Service'], date_format)
#                 current_date = datetime.now()
#                 six_months_ago = current_date - timedelta(days=30 * 6)

#                 if dateofservice1 < six_months_ago:
#                     print("Deleting outdated patient record")
#                     shcdata.drop(index, inplace=True)
#                     shcdata.to_csv(filename, index=False)
#                     return False
                
#                 print("Patient already handled")
#                 return True

#         return False

#     except Exception as e:
#         print(f"Error checking patient in CSV: {e}")
#         return False

def addto_data(patientname, dateofservice, typeofpatientnote, filename='shcdata.csv'):
    filename = BASE_DIR / filename
    try:
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([patientname, dateofservice, typeofpatientnote])
            print()
            print("_________________________________________")
            print("Added to shcdata.csv:", patientname, dateofservice, typeofpatientnote)
            print("_________________________________________")
            print()
    except Exception as e:
        print(f"Error writing to CSV: {e}")


## This is old code that was not used in the recent edits as of 07/20/2025
# def click_correct_edit_button(driver, patientname, dateofservice, typeofpatientnote):
#     """
#     Locates and clicks the edit button for the given patient by matching name and date.
#     This prevents stale index problems after the table reloads.
#     """
#     try:
#         rows = driver.find_elements(By.XPATH, f'//tbody[@id="myBasketDraftList"]/tr')
#         for row in rows:
#             try:
#                 date = row.find_element(By.XPATH, "./td[1]").text.strip()
#                 name = row.find_element(By.XPATH, "./td[2]").text.strip()
#                 type = row.find_element(By.XPATH, "./td[3]/strong").text.strip()

#                 if date == dateofservice and name == patientname and type == typeofpatientnote:
#                     edit_button = row.find_element(By.XPATH, './/button[contains(text(), "Edit")]')
#                     edit_button.click()
#                     print(f"🖱️ Clicked edit button for {name} on {date}")
#                     return True
#             except NoSuchElementException:
#                 continue  # Skip malformed rows
#     except Exception as e:
#         print(f"❌ Error in click_correct_edit_button: {e}")

#     print(f"⚠️ Could not find matching edit button for {patientname} on {dateofservice}")
#     return False


def click_correct_edit_button(driver, patientname, dateofservice, typeofpatientnote, timeout=10):
    """
    Locates and clicks the edit button for the given patient by matching name and date.
    Avoids stale DOM issues by re-querying the rows each time.
    """
    print(f"🔍 Looking for edit button for {patientname} on {dateofservice}")
    
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f'//tbody[@id="myBasketDraftList"]/tr'))
        )

        rows = driver.find_elements(By.XPATH, f'//tbody[@id="myBasketDraftList"]/tr')

        for _ in range(5):  # up to 5 retries to avoid stale state
            try:
                rows = driver.find_elements(By.XPATH, f'//tbody[@id="myBasketDraftList"]/tr')

                for row in rows:
                    try:
                        date = row.find_element(By.XPATH, "./td[1]").text.strip()
                        name = row.find_element(By.XPATH, "./td[2]").text.strip()
                        type = row.find_element(By.XPATH, "./td[3]/strong").text.strip()

                        if date == dateofservice and name == patientname and type == typeofpatientnote:
                            edit_button = row.find_element(By.XPATH, './/button[contains(text(), "Edit")]')
                            edit_button.click()
                            print(f"🖱️ Clicked edit button for {name} on {date}")
                            return True

                    except (StaleElementReferenceException, NoSuchElementException):
                        continue  # One row had trouble; move on

                break  # Exit retry loop if no outer exception

            except StaleElementReferenceException:
                print("⚠️ Retrying row scan due to stale DOM...")
                continue

    except TimeoutException:
        print("❌ Timeout waiting for table to appear.")

    print(f"⚠️ Could not find matching edit button for {patientname} on {dateofservice}")
    return False

def already_in_not_handled_dict(patientname, dateofservice, typeofpatientnote):
    """
    Returns True if a specific (name, date, type) combo already exists in nothandledclientsdict.
    """
    if patientname in nothandledclientsdict:
        for entry in nothandledclientsdict[patientname]:
            if (
                entry.get("dateofservice") == dateofservice and
                entry.get("typeofpatientnote") == typeofpatientnote
            ):
                return True
    return False
