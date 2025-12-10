from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
import time
from selenium.webdriver.common.action_chains import ActionChains
import os
import shutil
from pathlib import Path


import html_handler
import np_handler
import ro_handler
import xr_handler
import CNHvariablelist 

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Headless mode if your container uses it
chrome_options.add_argument("--headless=new")


BASE_DIR = Path(__file__).parent
driver = webdriver.Chrome(options=chrome_options)

# Initialize global variables
nothandledclients = []
notes = []  # Initialize notes as an empty list
cervicalshandled = list()  # Initialize cervicalshandled as an empty list
cervicalshandled_global = []
shortcodes = []
softtissue_global = []
bpartproblem = []
note = [] # Initialize note as an empty list
nothandledclientsdict = {}
    
# Load data from the JSON file
data = {}
with open(BASE_DIR / 'shortcodemapping_saffron.json', 'r') as f:
    data = json.load(f)

# create def for switching facilities
def switch_facilities(driver):
    print("not switching facilities this time")
    # try:
    #     myproviderbutton = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "myProviderName")))
    #     myproviderbutton.click()
    #     print("login myproviderbutton clicked")    
    #     time.sleep(1)

    #     facility = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/section/header/nav/div/div/div[3]/div[5]/ul/li[11]/a")))
    #     facility.click()
    #     print("login facility clicked")
    #     time.sleep(1)

    #     #click on facilityList
    #     facilitylist = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "facilityList")))
    #     facilitylist.click()
    #     print("login facilitylist clicked")
    #     time.sleep(1)

    #     #click on the Riverton Xpath to change facility
    #     riverton = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='facilityList']/option[3]")))
    #     riverton.click()
    #     print("login riverton clicked")   

    #     time.sleep(3)

    # except (TimeoutException, ElementNotInteractableException) as e:
    #     print("Facility switch failed:", e)
    #     return False
    
    # return True
 
def process_comment_text(driver, nothandledclients, dateofservice, patientname, data, text, typeofpatientnote):
    print("process comment text")
    try:
        if text == "":
            print("text is empty")
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "no comment text")
            print(nothandledclients)
            return False

        split = text.split(". ")
        front_text = split[0] if len(split) > 1 else split[0]
        note = split[1] if len(split) > 1 else ""
        print("Front text:", front_text)
        print("Note:", note)

        splitter = front_text.split(": ")
        body_softtissue_text = splitter[0] if len(splitter) > 1 else splitter[0]
        nextvisit = splitter[1] if len(splitter) > 1 else ""

        # if next visit starts with "A" then skip next if statement
        if nextvisit[0] == "A":
            print("Next visit starts with A")
            pass  # continue to handle_type1_patient
        
        elif not nextvisit[0].isdigit():
            print("Next visit does not start with a number")
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "next visit does not start with a number")
            # skip to the next client in the basket
            print("returning to handle_type1_patient")
            return False
        
        if not nextvisit:
            print("Next visit is empty")
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "next visit is empty")
            print("returning to handle_type1_patient")
            return False
        
        print("Body soft tissue text:", body_softtissue_text)
        print("Next visit:", nextvisit)

        softtissuesplit = body_softtissue_text.split("; ")
        shortcodes = softtissuesplit[0] if len(softtissuesplit) > 1 else softtissuesplit[0]
        softtissue = softtissuesplit[1] if len(softtissuesplit) > 1 else ""
        print("Shortcodes:", shortcodes)
        print("Soft tissue:", softtissue)
        # append softtissue to the global softtissue list
        softtissue_global.append(softtissue)

        shortcodes = shortcodes.split(", ")
        for shortcode in shortcodes:
            listing = shortcode.split(" ")
            bpart = listing[0]
            if bpart in data:
                cervicalshandled.append(bpart)
                cervicalshandled_global.append(bpart)
        print("global cervicalshandled:", cervicalshandled_global)
        print()
        
    
    except Exception as e:
        print(f"Error processing comment text: {e}")
        nothandledclients.append((patientname, dateofservice, "error processing comment text"))
        # reset the objective tab
        html_handler.reset_objective(driver)

        return None    

    return cervicalshandled, shortcodes, note, nextvisit, softtissue

def objective(driver, patientname, dateofservice, typeofpatientnote, data, shortcodes, cervicalshandled, nothandledclients):
    
    objectivetab_xpath = CNHvariablelist.objectivetab
    print("objective function")

    # # First, try to close any Bootbox modal that might be covering the page (there is no bootbox to close)
    # try:
    #     html_handler.close_bootbox_if_present(driver)
    # except Exception as e:
    #     # Don't let modal-close issues crash the script
    #     print(f"Error while trying to close bootbox before opening objective tab: {e}")

    # Try clicking the Objective tab
    try:
        html_handler.click_element(driver, objectivetab_xpath)
        print("objective tab opened")
        return True

    except ElementClickInterceptedException as e:
        # Specific case: something (usually a modal) is blocking the click — try to clear it and retry once
        print(f"Objective tab click intercepted, trying to close bootbox and retry: {e}")
        try:
            html_handler.close_bootbox_if_present(driver)
        except Exception as e2:
            print(f"Error while trying to close bootbox after interception: {e2}")

        # Retry once
        try:
            html_handler.click_element(driver, objectivetab_xpath)
            print("objective tab opened (after retry)")
            return True
        except Exception as e3:
            print(f"Objective tab still failed to open after retry: {e3}")
            nothandledclients.append((patientname, dateofservice, typeofpatientnote, "error opening objective tab"))
            print(nothandledclients)
            return False

    except Exception as e:
        # Any other error (not specifically click interception)
        print(f"Error opening objective tab: {e}")
        nothandledclients.append((patientname, dateofservice, typeofpatientnote, "error opening objective tab"))
        print(nothandledclients)
        return False
    # objectivetab_xpath = CNHvariablelist.objectivetab
    # print("objective function")
    # # open the objective tab
    # try:
    #     html_handler.click_element(driver, objectivetab_xpath)
    #     print("objective tab opened")
    # except Exception as e:
    #     print(f"Error opening objective tab: {e}")
    #     nothandledclients.append((patientname, dateofservice, typeofpatientnote, "error opening objective tab"))
    #     print(nothandledclients)
        
    #     return False
    
    print("shortcodes:", shortcodes)# append shortcodes into the global shortcodes list
    shortcodes = ", ".join(shortcodes)

    # check if shortcodes is empty
    if len(shortcodes) == 0:
        return

    shortcodes = shortcodes.split (", ")
    for shortcode in shortcodes:
        listing = shortcode.split (" ")
        bpart = listing [0]
        bpartproblem = listing[1:]
        #append bpartproblem to the global bpartproblem list
        bpartproblem.append(bpartproblem)
        bpartdatafind = data.keys()
        if bpart in bpartdatafind:
            # pass
            bpartdata = data[bpart]
            listings = bpartdata['listings']
            print ("bpart:", bpart)
            #print ("bpartdata:", bpartdata)
            cervicalshandled.append(bpart)

            if bpart == "RETRACING" or bpart == "N/A":
                print ("retracing or na")
                pass

            else:
                # open corrrect tab for bpart lising
                bparttab = driver.find_element(By.ID, bpartdata['htmlId'])
                bparttab.click()
                time.sleep(1)

                # create a list to store the clicked buttons
                handledlistings = set()
                handledshortcodes = set()
                handledshortcodemappings = set()
                handledroots = set()
                itfactorloop = 0

                    # click on the problem listed
                for problem in listing[1:]:
                    # clear itfactorlist
                    # itfactorlist = []
                    for listing in listings.keys():
                        listingdata = listings[listing]
                        root = listingdata['root']
                        problems = listingdata['problems']
                        shortcodemappings = listingdata['shortcodemappings']

                        #check the listing in the data
                        if problem in problems:
                            print ("problem:", problem)
                            problemHtmlId = root + problem
                            if problem in shortcodemappings:
                                thenewproblem = shortcodemappings[problem]
                                problemHtmlId = root + thenewproblem

                                upperproblem = str.upper(thenewproblem)
                                handledshortcodemappings.add(upperproblem)
                                handledroots.add(root)

                                time.sleep(1)      
                                problembox = driver.find_element(By.ID, problemHtmlId)
                                problembox.click()

                                print("problemHtmlId:", problemHtmlId)
                                time.sleep(2)

                            else:
                                print("problem not found")
                                print("problem:", problem)
                                # add client name and issue to the nothandledclients list
                                nothandledclients.append(patientname) 
                                nothandledclients.append(dateofservice)
                                nothandledclients.append(" problem not found")
                                print(nothandledclients) 
                                
                                html_handler.reset_objective(driver)

                                # skip to the next client in the basket
                                break
                        
                            handledlistings.add(problemHtmlId)
                            handledshortcodes.add(shortcode)
                            

                            # print(handledroots)
                            print("handledshortcodes:", handledshortcodes)
                            # print(handledlistings)
                            # print(handledshortcodemappings)
                            print()
                            time.sleep(1)

                # handle defaults for bpart in the json file
                defaults = bpartdata["defaults"]
                listings = bpartdata["listings"]
                
                for default in defaults:
                    disfault = listings[default]["default"]
                    ddfault = str.upper(disfault)
                    shortcodemappings = listings[default]["shortcodemappings"]
                    problems = listings[default]["problems"]

                    # handledproblems = list(handledshortcodemappings)
                    shortcodesplit = shortcode.split(" ")
                    theitfactor = shortcodesplit[-1]

                    print(shortcode)
                    print(theitfactor)
                    print(problems)
                    print()

                    # for theitfactor in handledproblems:
                    if theitfactor in problems:
                        print("tenderness listed")
                        print()
                        continue
                    
                    print("default tenderness activated")
                    # find the root for default
                    root = listings[default]["root"]
                    # combine the root and the default to create the htmlid listing
                    defaultHtmlId = root + disfault
                    print(defaultHtmlId)
                    # click on the default button  
                    try:
                        defaultbox = driver.find_element(By.ID, defaultHtmlId)
                        defaultbox.click()
                        time.sleep(1)
                    except:
                        print("no pain threshold found using default")
                        continue

                    time.sleep(1)
                    print()

        # if the body part code is not in the data add client to the nothandledclients list 
        else:
            print()
            print("The body part code'" + bpart + "' was not found in the data")
            # add client name and issue to the nothandledclients list
            nothandledclients.append(patientname) 
            nothandledclients.append(dateofservice)
            nothandledclients.append(typeofpatientnote)
            nothandledclients.append(f"{bpart} code not found")
            #nothandledclients.append(bpart," code not found")
            print(nothandledclients)
            print()
            #reset objective tab    
            html_handler.reset_objective(driver)
            # skip to the next client in the basket
            return False
          

    print("OBJECTIVE, completed body part codes")
    return                 

def handle_soft_tissue(driver, softtissue): 
    print()
    print("start hanlding soft tissue")         
    print("soft tissue codes: ", softtissue)

    softtissuetab_id = CNHvariablelist.muscleorsofttissuetab
    print ("softtissuetab:", softtissuetab_id)
    ObjMusRecordNote_id = "kpi_dailyNoteObjMusKylePNRecordNote"

    if softtissue == "":
        print ("no soft tissue... moving on")
        return 
    
    try:
        # Wait until present to Open the soft tissue tab
        #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, softtissuetab_id)))
        html_handler.click_element(driver, CNHvariablelist.muscleorsofttissuetab)
        print("opened soft tissue tab")

    except: 
        print("soft tissue tab not found")
        return False
        
    try:
        with open(BASE_DIR / 'softtissuemapping_saffron.json') as h:
            softtissuemapping = json.load(h)
        
        softtissuemap = softtissuemapping['shortcodemappings']
        musclecodemap = softtissuemapping['tissue']
        # softtissue = text.split("; ")[1] if "; " in text else ""
        softtissue = softtissue.split(", ")

        handledproblems, handledmuscles = [], []
        for listing in softtissue:
            print("listing:", listing)
            problems = listing.split(" ")
            problemtext = problems[:-2] if len(problems) > 1 else ""
            musclecode = problems[-2:] if len(problems) > 1 else ""
            print ("problemtext:", problemtext)
            print ("musclecode:", musclecode)

            for problem in problemtext:
                if problem in softtissuemap:
                    handledproblems.append(softtissuemap[problem])
            for muscle in musclecode:
                if muscle in musclecodemap:
                    handledmuscles.append(musclecodemap[muscle])

            if handledmuscles or handledproblems:
                softtissuetext = "Patient presents with a " + " ".join(handledproblems) + " " + " ".join(handledmuscles) + " that is tender upon palpation and has a decreased range of motion. "
                html_handler.send_keys_by_id(driver, ObjMusRecordNote_id, softtissuetext, sleep_time=2)

    except Exception as e:
        print(f"Error handling soft tissue: {e}") 

def handle_cervical_listings(driver, cervicalshandled):
    print()
    print("start handling cervical listings")
    print("cervicalshandled:", cervicalshandled)
    print()

    commoncervicalstab_id = CNHvariablelist.scanandlegchecktab
    ADL_changeimp_id = "KylObjADLImp"
    SCAN_nopattern_id = "KylObjScanNPatrn"
    LLI_balanced_id = "KylObjLegLSBal"
    try:
        # open the scan and leg check tab tab
        html_handler.click_element(driver, commoncervicalstab_id)
        print("opened scan and leg check tab")
    except Exception as e:
        print(f"Error opening scan and leg check tab: {e}")
        pass

    try:
        with open(BASE_DIR / 'cervicallegcheckmapping_saffron.json') as f:
            cervicallegcheckmapping = json.load(f)
        
        legcheck1 = cervicallegcheckmapping['legchecks']['legcheck']
        cervicals = cervicallegcheckmapping['legchecks']['cervicals']
        commoncervicals = list(set(cervicals) & set(cervicalshandled))
        print("commoncervicals:", commoncervicals)
        time.sleep(3)

        if len(commoncervicals) > 0:
            print("commoncervicals found")
            #html_handler.click_element(driver, commoncervicalstab_id)
            html_handler.click_element_by_id(driver, ADL_changeimp_id)
            html_handler.click_element_by_id(driver, SCAN_nopattern_id)
            html_handler.click_element_by_id(driver, LLI_balanced_id)
            for cervical in commoncervicals:
                legcheck = legcheck1[cervical]
                # wait for the leg check text box to be clickable
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "KylObjOthTxtA")))
                html_handler.send_keys_by_id(driver, "KylObjOthTxtA", f"{legcheck} modified Prill leg check shows a reading of unbalanced. All other Prill checks balanced.")
            
        if len(commoncervicals) < 1:
            print("commoncervicals not found clicking on defaults")
            #html_handler.click_element(driver, commoncervicalstab_id)
            html_handler.click_element_by_id(driver, ADL_changeimp_id)
            html_handler.click_element_by_id(driver, SCAN_nopattern_id)
            html_handler.click_element_by_id(driver, LLI_balanced_id)
            html_handler.click_element_by_id(driver, "KylObjVertLgBal")
            html_handler.click_element_by_id(driver, "KylObjRotLgBal")
            html_handler.click_element_by_id(driver, "KylObjMedLgBal")
            html_handler.click_element_by_id(driver, "KylObjLatLgBal")
        
        time.sleep(1)

    except Exception as e:
        print(f"Error handling cervical listings: {e}")
        html_handler.reset_objective(driver)
        
def handle_assessment(driver):
    
    assessmenttab = CNHvariablelist.assessmenttab

    try:
        # wait until the assessment tab is clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, assessmenttab)))
        # click on the assessment tab
        html_handler.click_element(driver, assessmenttab)
        print("clicked on the assessment tab")

        # wait for the improvment and client progress buttons to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "KylAsesImp")))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "KylAsesClintPrg")))

        # click on the improvment and client progress buttons
        html_handler.click_element_by_id(driver, "KylAsesImp")
        html_handler.click_element_by_id(driver, "KylAsesClintPrg")
        #html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[1]/ul/li[3]")

    except Exception as e:
        print(f"Error handling assessment: {e}")

def handle_notes(driver, note):
    try:
        if note:
            print("Notes: ", note)
            
            html_handler.click_element(driver, CNHvariablelist.additionaltab)
            html_handler.click_element(driver, '//textarea[@id="specialNotes"]')
            html_handler.clear_text_box(driver, '//textarea[@id="specialNotes"]')
            html_handler.send_keys_by_id(driver, '//textarea[@id="specialNotes"]', note +'. ', sleep_time=2)

            print("HANDLE_NOTES, notes added")

    except Exception as e:

        print(f"Error handling notes: {e}")
        # clear the notes
        html_handler.clear_findings(driver)

        return False

def handle_plan(driver, cervicalshandled, data, nextvisit, patientname, dateofservice, typeofpatientnote):
    
    print()
    print("start handling plan")
    print()

    plantab = CNHvariablelist.plantab
    plantab_id = "NotezHealthSoapSuUs29TreatmentPlanPresentation"
    nextvisit_AS = "KylPlnAsc"
    nextvisit_schednextvisit = "KylPlnSnv"
    nextvisit_id = "KylPLnSnv1Left"
    nextvisittime_id = "KylPLnSnv2Left"
    NMR_button = "KylPlnNeuro"
    NMR_cranial_button = "KylPlnNeuroCran"
    NMR_cervical_button = "KylPlnNeuroCerv"
    NMR_thoracic_button = "KylPlnNeuroObjNote"

    # open plan tab
    try:
        # wait until the plan tab is clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, plantab)))
        # click on the plan tab
        openplantab = html_handler.click_element(driver, plantab)
        print("opened plan tab")

    except Exception as e:
        openplantab = html_handler.click_element_by_id(driver, plantab_id)
        openplantab.click()
        print("opened plan tab")

    plancodelist = list()
    time.sleep(2) 

    if nextvisit == "":
        print("HANDLE_PLAN, no next visit")
        html_handler.clear_findings(driver)
        # add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "no next visit")
        # skip to next client
        return False
    
    elif nextvisit == "AS":
        print("HANDLE_PLAN, next visit is AS")
        # wait for the next visit button to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, nextvisit_AS)))
        html_handler.click_element_by_id(driver, nextvisit_AS)

    else:
        print()
        print("entering next visit:", nextvisit)
        html_handler.click_element_by_id(driver, nextvisit_schednextvisit)
        nextvisitnum, nextvisittime = nextvisit[0], nextvisit[1]
        # wait for the next visit number and time to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, nextvisit_id))) 
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, nextvisittime_id)))         
        html_handler.send_keys_by_id(driver, nextvisit_id, nextvisitnum)
        html_handler.send_keys_by_id(driver, nextvisittime_id, nextvisittime, sleep_time=1)

    # remove duplicates from cervicalshandled
    cervicalshandled = list(set(cervicalshandled))

    try:    
        # iterate over cervicalshandled
        for parts in cervicalshandled:

            print(parts)
            plancode = data[parts]['plancode']
            print(plancode)
            newlist = [item for item in plancode]
            for item in newlist:
                if item == "":
                    pass
                else:
                    print (item)
                    time.sleep(1)

                    # click on each item button
                    button = driver.find_element(By.ID, item).click()

                    # add each plancode to the plancodelist
                    plancodelist.append(item)
                    print(plancodelist)
                    time.sleep(1)

        commoncervicals = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7']
        for cervicals in commoncervicals:
            if cervicals in cervicalshandled:
                break
        else:
            #wait for the NMR button to be clickable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, NMR_button)))
            html_handler.click_element_by_id(driver, NMR_button)
            #wait for the cranial, cervical and thoracic buttons to be clickable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, NMR_cranial_button)))
            html_handler.click_element_by_id(driver, NMR_cranial_button)
            #wait for the cervical and thoracic buttons to be clickable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, NMR_cervical_button)))
            html_handler.click_element_by_id(driver, NMR_cervical_button)
            #wait for the thoracic button to be clickable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, NMR_thoracic_button)))
            html_handler.click_element_by_id(driver, NMR_thoracic_button)

    except Exception as e:
        print(f"Error handling plan: {e}")

def handle_diag_cpt(driver, cervicalshandled, data, patientname, dateofservice, typeofpatientnote): 
    print()
    print("start handling invoicing")
    print()

    # remove duplicates from cervicalshandled
    cervicalshandled = list(set(cervicalshandled)) 
    print("cervicalshandled list:", cervicalshandled)
    commoncervicals = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7']

    try:
        print("click on the invoicing tab")
        html_handler.click_element(driver, CNHvariablelist.invoicetab)
        print("clicked on the invoicing tab")
        
        with open(BASE_DIR /'theorder.json') as o:
            order = json.load(o)

        listofdiaghandled = list()
        diaglist2 = data.keys()

        # check if 'RETRACING' or 'N/A' is in cervicalshandled
        if 'RETRACING' in cervicalshandled:
            print(cervicalshandled)
            print("Only RETRACING found")
            
            cervdiag = "M54.2"
            nmrdiag = ["M79.12", "M62.838"]
            try:
                    
                if cervdiag not in listofdiaghandled:
                    # add cervdiag to nmrdiag
                    nmrdiag.append(cervdiag)
                    print("Adding to diagnosis list:", nmrdiag)
                    for eachnmrdiag in nmrdiag:
                        # enter the diagnosis code
                        html_handler.send_keys_by_id(driver, CNHvariablelist.diagnosisline, eachnmrdiag)
                        #hit the enter button to enter the diagnosis code                                      
                        html_handler.send_keys_by_id(driver, CNHvariablelist.diagnosisline , Keys.ENTER, sleep_time=1)
                        #click the diagnosis button to add the diagnosis code to the list
                        try:
                            #wait for the diagnosis button to be clickable
                            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, CNHvariablelist.diagnosisbutton)))    

                            #try clicking the diagnosisbutton_xpath
                            html_handler.click_element(driver, CNHvariablelist.diagnosisbutton, sleep_time=1)
                            print("diagnosis button clicked")
                        
                        except:
                            print("could not find / click the ADD diagnosis button")


                        html_handler.clear_text_box(driver, CNHvariablelist.diagnosisline, sleep_time = 1)
                        listofdiaghandled.append(eachnmrdiag)  

            except Exception as e:
                print(f"handle_diag_cpt cpt code entering error: {e}")
                # open the plan tab
                try:

                    html_handler.click_element(driver, CNHvariablelist.plantab, sleep_time=1)
                    html_handler.clear_findings(driver)
                    # add patient to not handled list
                    add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RETRACING diagnosis not handled")
                    # skip to next client

                except Exception as e:
                    print("cannot locate the clear plan tab:", e)

                return False


        elif 'N/A' in cervicalshandled:
            print("Only N/A found")

            cervdiag = "M54.2"
            nmrdiag = ["M79.12", "M62.838"]
            try:
                        
                    if cervdiag not in listofdiaghandled:
                        # add cervdiag to nmrdiag
                        nmrdiag.append(cervdiag)
                        print("Adding to diagnosis list:", nmrdiag)
                        for eachnmrdiag in nmrdiag:
                            html_handler.send_keys_by_id(driver, CNHvariablelist.diagnosisline, eachnmrdiag)
                            html_handler.send_keys_by_id(driver, CNHvariablelist.diagnosisline , Keys.ENTER, sleep_time=1)
                        
                            try:
                                #try clicking the diagnosisbutton_xpath
                                html_handler.click_element(driver, CNHvariablelist.diagnosisbutton, sleep_time=1)
                            except:
                                html_handler.click_element(driver, CNHvariablelist.diagnosisbutton, sleep_time=1)

                            html_handler.clear_text_box(driver, CNHvariablelist.diagnosisline, sleep_time=1)
                            listofdiaghandled.append(eachnmrdiag)

            except Exception as e:
                print(f"handle_diag_cpt cpt code entering error: {e}")
                # open the plan tab
                html_handler.click_element(driver, CNHvariablelist.plantab, sleep_time=1)
                html_handler.clear_findings(driver)
                # add patient to not handled list
                add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "N/A not handled")
                # skip to next client
                return False

        else:
            print("RETRACING or N/A not found or both found")
            try:
                
                cervicalshandled = sorted(cervicalshandled, key=lambda x: order[x])
                print("cervicalshandled:", cervicalshandled)

                for part in cervicalshandled:
                    if part in diaglist2:
                        diagcode = data[part]['diagcode']
                        print("Diagnosis code:", diagcode)

                        for eachdiagcode in diagcode:
                            listofdiaghandled.append(eachdiagcode)

                # remove duplicates from listofdiaghandled
                listofdiaghandled = list(set(listofdiaghandled))
                print("List of diagnosis codes:", listofdiaghandled)

                for everydiagcode in listofdiaghandled:
                    print("Entering diagnosis code: ", everydiagcode)
                    html_handler.send_keys_by_id(driver, CNHvariablelist.diagnosisline, everydiagcode, sleep_time=1)
                    html_handler.send_keys_by_id(driver, CNHvariablelist.diagnosisline, Keys.ENTER, sleep_time=1)

                    try:
                        #try clicking the diagnosisbutton_xpath
                        html_handler.click_element(driver, CNHvariablelist.diagnosisbutton, sleep_time=1)
                    except:
                        html_handler.click_element(driver, CNHvariablelist.diagnosisbutton, sleep_time=1)

                    html_handler.clear_text_box(driver, CNHvariablelist.diagnosisline, sleep_time=1)

            except Exception as e:
                print(f"handle_diag_cpt cpt code entering error: {e}")
                # open the plan tab
                html_handler.click_element_by_id(driver, "NotezHealthSoapSuUs29TreatmentPlanPresentation", sleep_time=1)
                html_handler.clear_findings(driver)
                # add patient to not handled list
                add_to_not_handled_list.append(patientname, dateofservice, typeofpatientnote, "error entering diagnosis codes")
                # skip to next client
                return False

            try:
                cervdiag = "M54.2"
                nmrdiag = ["M79.12", "M62.838"]
                invoicediagcommentbox = CNHvariablelist.diagnosisline
                invoicediagcommentbutton = CNHvariablelist.diagnosisbutton
                                            
                if cervdiag not in listofdiaghandled:
                    # add cervdiag to nmrdiag
                    nmrdiag.append(cervdiag)
                    for eachnmrdiag in nmrdiag:
                        html_handler.send_keys_by_id(driver, invoicediagcommentbox, eachnmrdiag, sleep_time=1)
                        html_handler.send_keys_by_id(driver, invoicediagcommentbox, Keys.ENTER, sleep_time=1)

                        try:
                            #try clicking the diagnosisbutton_xpath
                            html_handler.click_element(driver, CNHvariablelist.diagnosisbutton, sleep_time=1)
                        except:
                            html_handler.click_element(driver, CNHvariablelist.diagnosisbutton, sleep_time=1)

                        html_handler.clear_text_box(driver, invoicediagcommentbox, sleep_time=1)
                        listofdiaghandled.append(eachnmrdiag)

            except Exception as e:
                print(f"handle_diag_cpt nmr entering error: {e}")
                # open the plan tab
                html_handler.click_element(driver, CNHvariablelist.plantab, sleep_time=1)
                html_handler.clear_findings(driver)
                # add patient to not handled list
                add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "error entering NMR diagnosis codes")
                # skip to next client
                return False
            
        print()
        print("Locating diagnosis button container")
        print()
        try:

            # Locate the container
            container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='diagnosisBillingListSortable']")))

            # Find all buttons or <a> elements with an onclick attribute containing 'updateDiagnosisBillingResolvedDate'
            buttons = container.find_elements(By.XPATH, ".//a[contains(@onclick, 'updateDiagnosisBillingResolvedDate')]")

            # Click each button
            for i, button in enumerate(buttons):
                try:
                    # Scroll the button into view before clicking
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    button.click()
                    print(f"Successfully clicked button {i + 1}")
                except Exception as e:
                    print(f"Error clicking button {i + 1}: {e}")
   

        except Exception as e:
            print(f"Error locating diagnosis container: {e}")
            return False

        # handle cpt codes
        # add wellness CPT code
        html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, "S8990", sleep_time=3)
        html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=2)
        try:
            html_handler.click_element(driver, CNHvariablelist.cptbutton)
        except:
            html_handler.click_element(driver, CNHvariablelist.cptbutton)
        html_handler.clear_text_box(driver, CNHvariablelist.cptline)

        unique_codes = list(set(listofdiaghandled))
        # add other CPT codes
        count = len([code for code in unique_codes if code >='M99.11' and code <= 'M99.15'])
        if "M99.08" in unique_codes and "M99.12" not in unique_codes:
            count += 1

        try:
            if count < 1:
                html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, "99212", sleep_time=1)
                html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=1)
                try:
                    html_handler.click_element(driver, CNHvariablelist.cptbutton)
                except:
                    html_handler.click_element(driver, CNHvariablelist.cptbutton)
                html_handler.clear_text_box(driver, CNHvariablelist.cptline)
                html_handler.clear_text_box(driver, CNHvariablelist.cptline)
            elif count in [1, 2]:
                html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, "98940", sleep_time=1)
                html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=1)
                try:
                    html_handler.click_element(driver, CNHvariablelist.cptbutton)
                except:
                    html_handler.click_element(driver, CNHvariablelist.cptbutton)
                html_handler.clear_text_box(driver, CNHvariablelist.cptline)
                html_handler.clear_text_box(driver, CNHvariablelist.cptline)
            elif count in [3, 4]:
                html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, "98941", sleep_time=1)
                html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=1)
                try:
                    html_handler.click_element(driver, CNHvariablelist.cptbutton)
                except:
                    html_handler.click_element(driver, CNHvariablelist.cptbutton)
                html_handler.clear_text_box(driver, CNHvariablelist.cptline)
                html_handler.clear_text_box(driver, CNHvariablelist.cptline)
            elif count == 5:
                html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, "98942", sleep_time=1)
                html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=1)
                try:
                    html_handler.click_element(driver, CNHvariablelist.cptbutton)
                except:
                    html_handler.click_element(driver, CNHvariablelist.cptbutton)
                html_handler.clear_text_box(driver, CNHvariablelist.cptline)
                html_handler.clear_text_box(driver, CNHvariablelist.cptline)

        except Exception as e:
            print(f"Error handling additional diagnoses: {e}")
            #open the plan tab
            html_handler.click_element_by_id(driver, "NotezHealthSoapSuUs29TreatmentPlanPresentation", sleep_time=1)
            html_handler.clear_findings(driver)
            # add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "error entering common CPT codes")
            # skip to next client
            return False

        if "M99.06" in unique_codes or "M99.07" in unique_codes:
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, "98943", sleep_time=1)
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=1)
            try:
                html_handler.click_element(driver, CNHvariablelist.cptbutton)
            except:
                html_handler.click_element(driver, CNHvariablelist.cptbutton)
            html_handler.clear_text_box(driver, CNHvariablelist.cptline)
            html_handler.clear_text_box(driver, CNHvariablelist.cptline)

        if "TPT" in typeofpatientnote or "PBTPT" in typeofpatientnote or "OVTPT" in typeofpatientnote:
            print("type of patient note: ", typeofpatientnote)
            print("TPT is type of patient, entering 97140")
            
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, "97140", sleep_time=1)
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=1)
            try:
                html_handler.click_element(driver, CNHvariablelist.cptbutton)
            except:
                html_handler.click_element(driver, CNHvariablelist.cptbutton)
            html_handler.clear_text_box(driver, CNHvariablelist.cptline)
            html_handler.clear_text_box(driver, CNHvariablelist.cptline)
        
        if "N/A" in cervicalshandled:
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, "97140", sleep_time=1)
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=1)
            try:
                html_handler.click_element(driver, CNHvariablelist.cptbutton)
            except:
                html_handler.click_element(driver, CNHvariablelist.cptbutton)
            html_handler.clear_text_box(driver, CNHvariablelist.cptline)
            html_handler.clear_text_box(driver, CNHvariablelist.cptline)

        if "RETRACING" in cervicalshandled:
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, "97140", sleep_time=1)
            html_handler.send_keys_by_id(driver, CNHvariablelist.cptline, Keys.ENTER, sleep_time=1)
            try:
                html_handler.click_element(driver, CNHvariablelist.cptbutton)
            except:
                html_handler.click_element(driver, CNHvariablelist.cptbutton)
            html_handler.clear_text_box(driver, CNHvariablelist.cptline)
            html_handler.clear_text_box(driver, CNHvariablelist.cptline)

    except Exception as e:
        print(f"Error handling additional diagnoses: {e}")
        #open the plan tab
        html_handler.click_element(driver, CNHvariablelist.plantab, sleep_time=1)
        html_handler.clear_findings(driver)
        # add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "general error entering CPT codes")
        # skip to next client
        return False
    
    return True

def handle_payment(driver, patientname, dateofservice, typeofpatientnote):

    try:
        amount_due_element = driver.find_element(By.XPATH, '//input[@id="balanceDue"]')
        print("found Blanace Due imput box")

    except:
        try:
            amount_due_element = driver.find_element(By.XPATH, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[2]/div[3]/form/ul/li[13]/div/div/input")
            print("found Balance Due input box by the hard code xpath")                                        
        except:                 
            amount_due_element = driver.find_element(By.XPATH, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[3]/div[3]/form/ul/li[13]/div/div/input")
            print("found the Balance Due input box by the hard code exception xpath")

    try:    
        amount_due1 = float(amount_due_element.get_attribute("value")) 
        
         # if typeofpatientnote is "TPT" then the amount_due is float(amount_due1) - 50
        if typeofpatientnote == "TPT":
            amount_due = float(amount_due1) - 50 # subtract the 50 dollar fee

        # if typeofpatientnote is "OV" then the amount_due is float(amount_due1) - 60
        elif typeofpatientnote == "OV":
            amount_due = float(amount_due1) - 60 # subtract the 60 dollar fee

        # if typeofpatientnote is "OVTPT" then the amount_due is float(amount_due1) - 100
        elif typeofpatientnote == "OVTPT" or typeofpatientnote == "ROF":
            amount_due = float(amount_due1) - 100 # subtract the 100 dollar fee

        # if typeofpatientnote is "NP" then the amount_due is float(amount_due1) - 125
        elif typeofpatientnote == "NP":
            amount_due = float(amount_due1) - 125 # subtract the 125 dollar fee

        # if typeofpatientnote is "PB" then the amount_due is float(amount_due1)
        elif typeofpatientnote == "PB" or typeofpatientnote == "PBTPT" or typeofpatientnote == "PBOV" or typeofpatientnote =="PBNP":
            amount_due = float(amount_due1) # subtract the 0 dollar fee
        
        else:
            amount_due = "1"

        print(amount_due1)
        print()
        
        html_handler.send_keys_by_id(driver, "discount", str(amount_due))
        html_handler.send_keys_by_id(driver, "paymentType", "W")
        html_handler.send_keys_by_id(driver, "paymentType", Keys.ENTER)
        html_handler.click_element_by_id(driver, "addInvoicePaymentBtn")

    except Exception as e:
        print(f"Error handling payment: {e}")
        # add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "error handling payment")
        # skip to next client
        return False
    
    return True

def sign_note():
    print("Sign Note")
    print("_________________________________________________________")  

def handle_page_patients(driver): #edited to work take out hard coded xpath in table
    print("FUNCTION - handle_page_patients")
    
    try:
        # Locate the tbody by ID (much better than full absolute path)
        table_body = driver.find_element(By.ID, "myBasketDraftList")
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(rows)} patients")

        for index, row in enumerate(rows, start=1):
            try:
                dateofservice = row.find_element(By.XPATH, "./td[1]").text.strip()
                patientname = row.find_element(By.XPATH, "./td[2]").text.strip()
                typeofpatientnote = row.find_element(By.XPATH, "./td[3]/strong").text.strip()

                print(f"\nRow {index}")
                print(f"Name: {patientname}")
                print(f"Date of Service: {dateofservice}")
                print(f"Type: {typeofpatientnote}")
    # try:
    #     rows = driver.find_elements(By.XPATH, "/html/body/section/section[1]/div/div[2]/div[1]/section/article/div/div/div[1]/table/tbody/tr")
    #                                           #/html/body/section/section[1]/div/div[2]/div[1]/section/article/div/div/div[1]/table/tbody/tr[1]
    #     print(f"Found {len(rows)} patients")

    #     try:
    #         for index, row in enumerate(rows, start=1):
    #             patientname = row.find_element(By.XPATH, "./td[2]").text
    #             dateofservice = row.find_element(By.XPATH, "./td[1]").text
    #             typeofpatientnote = row.find_element(By.XPATH, "./td[3]/strong").text
                
    #             print()
    #             print(f"{patientname} found")
    #             print(dateofservice)
    #             print(typeofpatientnote)
    #             print()

                # clear global variables
                cervicalshandled.clear()
                cervicalshandled_global.clear()
                shortcodes.clear()
                notes.clear()
                softtissue_global.clear()
                bpartproblem.clear()

                # if the patient in the csv file has already been handled, skip to the next patient
                if check_patientdate_exists(driver, patientname, dateofservice, typeofpatientnote):
                    continue
                
                # if patient name and consecutive date are in nothandledclients list, skip to the next patient
                if (patientname) in nothandledclients:
                    if (dateofservice) in nothandledclients:
                        if (typeofpatientnote) in nothandledclients:
                   
                            print("Patient already in not handled list")
                            print("____________________________")
                            print()
                            continue
                    

                # handle patient files
                if not handle_patient_files(driver, patientname, dateofservice, typeofpatientnote, index, note):
                    continue                    

                # click on home button
                html_handler.click_homebutton(driver)        
                html_handler.push_basket_button(driver)
                return handle_page_patients(driver)
 
            except StaleElementReferenceException as e:
                print("StaleElementReferenceException:", e)
                print("Retrying...")
                html_handler.push_basket_button(driver)
                row = driver.find_elements(By.XPATH, "/html/body/section/section[1]/div/div[2]/div[1]/section/article/div/div/div[1]/table/tbody/tr")[index-1]
                return handle_page_patients(driver)
                

            except Exception as e:
                print(f"HANDLE_PATIENT DATA, Error processing patient row: {e}")
                # Log the error but don't break the loop; try the next patient
                add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "handle_page_patients, error processing patient row")
                return False

        else:
            print("All patients handled")
            print("____________________________")
            print()
      
    except:
        print("HANDLE_PATIENT_DATA, Failed to process patients", e)
        return False
    
    return True

def check_patientdate_exists(driver, patientname, dateofservice, typeofpatientnote):
    print("Checking if patient has been handled")

    try:
        #using fillmoredata.csv file to store patient data and check if patient has been handled
        shcdata = pd.read_csv(BASE_DIR / 'fillmoredata.csv')
        patient_exists = False

        for index, row in shcdata.iterrows():
            if row['Patient Name'] == patientname:
                print(f"The date in shcdata doc is: {row['Date of Service']}")
                if row['Date of Service']== dateofservice and row['Patient Type'] == typeofpatientnote:
                    patient_exists = True
                    date_format = "%m/%d/%Y"  # Adjust the format based on your date format
                    dateofservice1 = datetime.strptime(row['Date of Service'], date_format) if isinstance(row['Date of Service'], str) else row['Date of Service']
                    current_date = datetime.now()
                    
                    # Calculate six months ago
                    six_months_ago = current_date - timedelta(days=30 * 6)

                    # Check if dateofservice is six months older than the current date
                    if dateofservice1 < six_months_ago:
                        print("Deleting outdated patient records")
                        shcdata.drop(index, inplace=True)
                        shcdata.to_csv('fillmoredata.csv', index=False)


        if patient_exists:
            print("Patient file already handled")
            print("____________________________")
            print()
            
            return True
        
        return False    

    except KeyError as e:
        print(f"Error checking if patient has been handled: {e}. Please check the CSV file column names.")
        return False
    
    except Exception as e:
        print(f"Error checking if patient has been handled: {e}")
        return False                            

def addto_data(patientname, dateofservice, typeofpatientnote):
    # Add patient information to the fillmoredata.csv file 
    with open(BASE_DIR / 'fillmoredata.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([patientname, dateofservice, typeofpatientnote])
        print("Patient information added to Fillmore data")
        print()
 
# Function for handling patient files based on the type of patient note
def handle_patient_files(driver, patientname, dateofservice, typeofpatientnote, index, note):
    print()
    print(f"Processing files for patient:")
    print(f"{patientname}")
    print(f"Date of Service: {dateofservice}") 
    print(f"Type of Note: {typeofpatientnote}")
    print()
    
    note_handlers = {
        "OV": handle_type1_patient,
        "OVTPT": handle_type1_patient,
        "PBOV": handle_type1_patient,
        "PBTPT": handle_type1_patient,
        "PBOVTPT": handle_type1_patient,
        "TPT": handle_type1_patient,
        "PB": handle_type1_patient,
        "NP": handle_type2_patient,
        "PBNP": handle_type2_patient,
        "RO": handle_type4_patient,
        "MG": handle_type3_patient,
        "XR": handle_type5_patient
    }

    if typeofpatientnote in note_handlers:
        html_handler.click_edit_button(driver, index)
        #handle_type1_patient(driver, patientname, dateofservice, typeofpatientnote)
        note_handlers[typeofpatientnote](driver, patientname, dateofservice, typeofpatientnote, note)

    else:
        print(f"Unknown type of patient note: {typeofpatientnote}")
        print("__________________")
        #add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "Unknown type of patient note")
        #skip to next client
        return False

    return True

# Placeholder function for handling FE and FU patient files
def handle_type1_patient(driver, patientname, dateofservice, typeofpatientnote, note):

    print(f"Handling {typeofpatientnote} for:")
    print(f"{patientname}, DOS: {dateofservice}")

    # if comment box found then process the comment text and continue note processing
    try:
        # process the comment text
        text = html_handler.get_comment_text(driver)

        if process_comment_text(driver, nothandledclients, dateofservice, patientname, data, text, typeofpatientnote) == False:
            print("Process comment text failed, returned to handle_type1_patient")
            #add client name and issue to the nothandledclients list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "FE error processing comment text")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False  # Skip to the next patient  
                      
        cervicalshandled, shortcodes, note, nextvisit, softtissue = process_comment_text(driver, nothandledclients, dateofservice, patientname, data, text, typeofpatientnote)
        
        # print("cervicalshandled:", cervicalshandled)
        # print("shortcodes:", shortcodes)
        # print("note:", note)
        # print("nextvisit:", nextvisit)
        # print("softtissue:", softtissue)

        if objective(driver, patientname, dateofservice, typeofpatientnote, data, shortcodes, cervicalshandled, nothandledclients) == False:
            print("Objective not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False  # Skip to the next patient
        
        if handle_soft_tissue(driver, softtissue) == False:
            print("Soft tissue not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_cervical_listings(driver, cervicalshandled) == False:
            print("Cervical listings not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_assessment(driver) == False:
            print("Assessment not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_notes(driver, note) == False:
            print("Notes not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_plan(driver, cervicalshandled, data, nextvisit, patientname, dateofservice, typeofpatientnote) == False:
            print("Plan not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_diag_cpt(driver, cervicalshandled, data, patientname, dateofservice, typeofpatientnote) == False:
            print("Diagnosis and CPT not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_payment(driver, patientname, dateofservice, typeofpatientnote) == False:
            print("Payment not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        sign_note()
        addto_data(patientname, dateofservice, typeofpatientnote)

        print()
        print("done ",{patientname}," ", {dateofservice})
        print("_________________________________________________________")
        print()

        # click_basket = html_handler.push_basket_button(driver)


    except Exception as e:
        print(f"handle_type1_patient, Error processing patient: {e}")
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, f"handle_type1_patient, Error processing patient: {e}, check exam notes")
        # clear plan and objective tabs
        html_handler.clear_findings
        #skip to next client
        return False
    
    return True

# Placeholder function for handling Type2 patient files: NP
def handle_type2_patient(driver, patientname, dateofservice, typeofpatientnote, note):
    print(f"Handling {typeofpatientnote} for:")
    print(f"{patientname}, DOS: {dateofservice}")

    # # skip this type of patient
    # print("Skipping NP patient")
    # print("_________________________________________________________")
    # # add patient to not handled list
    # add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "NP patient")
    # return True
    

    # if comment box found then process the comment text and continue note processing
    try:
        # process the comment text
        try:
            if html_handler.get_comment_text(driver) == False:
                print("Comment text not found")
                #add patient to not handled list
                add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "NP comment text not found")
                # html_handler.click_homebutton(driver)
                # html_handler.push_basket_button(driver)
                return False    # Skip to the next patient
            
            text = html_handler.get_comment_text(driver)
        except:
            print("Error getting comment text")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "NP error getting comment text")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False  # Skip to the next patient


        if process_comment_text(driver, nothandledclients, dateofservice, patientname, data, text, typeofpatientnote) == False:
            print("Process comment text failed, returned to handle_type1_patient")
            html_handler.push_basket_button(driver)
            return False  # Skip to the next patient  
                      
        cervicalshandled, shortcodes, note, nextvisit, softtissue = process_comment_text(driver, nothandledclients, dateofservice, patientname, data, text, typeofpatientnote)
        
        # print("cervicalshandled:", cervicalshandled)
        # print("shortcodes:", shortcodes)
        # print("note:", note)
        # print("nextvisit:", nextvisit)
        # print("softtissue:", softtissue)


        if objective(driver, patientname, dateofservice, typeofpatientnote, data, shortcodes, cervicalshandled, nothandledclients) == False:
            print("Objective not handled")
            html_handler.push_basket_button(driver)
            return False  # Skip to the next patient
        
        handle_soft_tissue(driver, softtissue)
        handle_cervical_listings(driver, cervicalshandled)
        # #handle_assessment(driver)
        if handle_notes(driver, note) == "False":
            print("Notes not handled")
            html_handler.push_basket_button(driver)
            return False
        
        if np_handler.exam_note_plan(driver, cervicalshandled, data, nextvisit, patientname, dateofservice, typeofpatientnote) == False:
            print("NP Exam Note Plan not handled") 
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "NP exam note plan not handled")
            html_handler.push_basket_button(driver)
            return False
        
        if np_handler.exam_note(driver, cervicalshandled_global, softtissue_global, bpartproblem) == False:
            print("NP Exam Note not handled")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "NP exam note not handled")
            html_handler.push_basket_button(driver)
            return False

        np_handler.exam_handle_diag(driver, cervicalshandled, data)
        np_handler.exam_handle_cpt(driver,cervicalshandled)
        np_handler.exam_handle_payment(driver, patientname, nothandledclients)
        sign_note()
        addto_data(patientname, dateofservice, typeofpatientnote)

        print()
        print("done ",{patientname}," ", {dateofservice})
        print("_________________________________________________________")
        print()

        # click_basket = html_handler.push_basket_button(driver)


    except Exception as e:
        print(f"handle_type2_patient, Error processing patient: {e}")
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, f"handle_type2_patient, Error processing patient: {e}, check exam notes")
        # clear plan and objective tabs
        html_handler.clear_findings(driver)

        return False
    
    return True

# Placeholder function for handling MG (Type3) patient files
def handle_type3_patient(driver, patientname, dateofservice, typeofpatientnote, note):
    
    print(f"Handling MG patient (massage note): {patientname}, Date of Service: {dateofservice}")
    # Skipping the MG patient
    print("Skipping MG patient")
    print("_________________________________________________________")
    # add patient to not handled list
    add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "MG patient")
    return True

# Placeholder function for handling RO (Type4) patient files
def handle_type4_patient(driver, patientname, dateofservice, typeofpatientnote, note):

    print(f"Handling {typeofpatientnote} for:")
    print(f"{patientname}, DOS: {dateofservice}")

    # if comment box found then process the comment text and continue note processing
    try:
        # process the comment text
        text = html_handler.get_comment_text(driver)

        if process_comment_text(driver, nothandledclients, dateofservice, patientname, data, text, typeofpatientnote) == False:
            print("RO Process comment text failed, returned to handle_type1_patient")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO comment text not processed")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False  # Skip to the next patient  
                      
        cervicalshandled, shortcodes, note, nextvisit, softtissue = process_comment_text(driver, nothandledclients, dateofservice, patientname, data, text, typeofpatientnote)
        
        # print("cervicalshandled:", cervicalshandled)
        # print("shortcodes:", shortcodes)
        # print("note:", note)
        # print("nextvisit:", nextvisit)
        # print("softtissue:", softtissue)

        if objective(driver, patientname, dateofservice, typeofpatientnote, data, shortcodes, cervicalshandled, nothandledclients) == False:
            print("RO Objective not handled")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO objective not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False  # Skip to the next patient
        
        if handle_soft_tissue(driver, softtissue) == False:
            print("RO Soft tissue not handled")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO soft tissue not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_cervical_listings(driver, cervicalshandled) == False:
            print("RO Cervical listings not handled")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO cervical listings not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_assessment(driver) == False:
            print("RO Assessment not handled") 
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO assessment not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False 
        
        if handle_notes(driver, notes) == False:
            print("RO Notes not handled")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO notes not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
         
        if handle_plan(driver, cervicalshandled, data, nextvisit, patientname, dateofservice, typeofpatientnote) == False:
            print("RO Plan not handled")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO plan not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if ro_handler.ro_exam(driver) == False:
            print("RO Error Deleting New Client Exam")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO exam not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_diag_cpt(driver, cervicalshandled, data, patientname, dateofservice, typeofpatientnote) == False:
            print("RO Diagnosis and CPT not handled")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO diagnosis and CPT not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        if handle_payment(driver, patientname, dateofservice, typeofpatientnote) == False:
            print("RO Payment not handled")
            #add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "RO payment not handled")
            html_handler.click_homebutton(driver)
            html_handler.push_basket_button(driver)
            return False
        
        sign_note()
        addto_data(patientname, dateofservice, typeofpatientnote)

        print()
        print("done ",{patientname}," ", {dateofservice})
        print("_________________________________________________________")
        print()

        # click_basket = html_handler.push_basket_button(driver)


    except Exception as e:
        print(f"handle_type4_patient, Error processing patient: {e}")
        nothandledclients.append(patientname)
        nothandledclients.append(dateofservice)
        nothandledclients.append("handle_type4_patient, error processing patient")
        return False
    
    return True  

# Placeholder function for handling XR (Type5) patient files
def handle_type5_patient(driver, patientname, dateofservice, typeofpatientnote, note):

    print(f"Handling {typeofpatientnote} for:") 
    print(f"{patientname}, DOS: {dateofservice}")

    # check if np note has been handled in the csv file for the current patient
    try:
        shcdata = pd.read_csv(BASE_DIR / 'fillmoredata.csv')

        # # Debugging: Print the first few rows and column names
        # print("CSV file loaded. Here are the first few rows:")
        # print(shcdata.head())
        # print("CSV file columns:", shcdata.columns)

        patient_exists = False

        # Iterate over each row in the CSV file
        for index, row in shcdata.iterrows():
            csv_patient_name = row['Patient Name']
            csv_type_of_patient_note = row['Type of Patient Note']

            # Compare patient name and type of patient note
            if csv_patient_name == patientname and csv_type_of_patient_note == "NP":
                patient_exists = True
                print(f"Match found for {patientname} with NP note. Continuing...")
                pass

        # If patient not found or NP note not handled
        if not patient_exists:
            print(f"NP note not handled for {patientname}, skipping to next patient...")
            # Add patient to not handled list
            add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "NP note not handled")
            return False
        
    except Exception as e:
        print(f"Error checking if patient has been handled: {e}")
        return False
                        
    if xr_handler.xr_objective(driver) == False:
        print("XR Objective not handled")
        #add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "xr_objective not handled")
        html_handler.click_homebutton(driver)
        html_handler.push_basket_button(driver)
        return False  # Skip to the next patient
    
    if xr_handler.xr_assessment(driver) == False:
        print("XR Assessment not handled")
        #add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "xr_assessment not handled")
        html_handler.click_homebutton(driver)
        html_handler.push_basket_button(driver)
        return False
    
    if xr_handler.xr_plan(driver) == False:
        print("XR Plan not handled")
        #add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "xr_plan not handled")
        html_handler.click_homebutton(driver)
        html_handler.push_basket_button(driver)
        return False
    
    if xr_handler.xr_exam(driver) == False:
        print("XR Exam not handled")
        #add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "xr_exam not handled")
        html_handler.click_homebutton(driver)
        html_handler.push_basket_button(driver)
        return False
    
    if xr_handler.xr_addpro(driver) == False:
        print("XR Add Pro not handled")
        #add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "xr_addpro not handled")
        html_handler.click_homebutton(driver)
        html_handler.push_basket_button(driver)
        return False
    
    if xr_handler.xr_invoice_import_previous_diag(driver) == False:
        print("XR Invoice not handled")
        #add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "xr_invoice_import_previous_diag not handled")
        html_handler.click_homebutton(driver)
        html_handler.push_basket_button(driver)
        return False
    
    if xr_handler.xr_cptcodes(driver) == False:
        print("XR CPT codes not handled")
        #add patient to not handled list
        add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, "xr_cptcodes not handled")
        html_handler.click_homebutton(driver)
        html_handler.push_basket_button(driver)
        return False
    
    sign_note()
    addto_data(patientname, dateofservice, typeofpatientnote)

# utility function to add patient name, date and type to BOTH:
#  - flat list (legacy)
#  - grouped dict (for pretty summary)
def add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, findings):
    # Keep the original flat list behavior (if you still use it anywhere)
    nothandledclients.append(patientname)
    nothandledclients.append(dateofservice)
    nothandledclients.append(typeofpatientnote)
    nothandledclients.append(findings)

    # New: populate the dict used by print_nothandled_clients
    entry = {
        "dateofservice": dateofservice,
        "typeofpatientnote": typeofpatientnote,
        "findings": findings,
    }

    if patientname in nothandledclientsdict:
        nothandledclientsdict[patientname].append(entry)
    else:
        nothandledclientsdict[patientname] = [entry]

#utility function to add patient name, date and type to the not handled list
# def add_to_not_handled_list(patientname, dateofservice, typeofpatientnote, findings):
#     nothandledclients.append(patientname)
#     nothandledclients.append(dateofservice)
#     nothandledclients.append(typeofpatientnote)
#     nothandledclients.append(findings)

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

# Create main function 
def main():
    username = "drsaffron81"
    password = "ePSj9jdTHBFt5s"
    url = 'https://www.zhealthehr.com/'
    #workbook_path = 'D:\\Documents\\kyle-python\\New Button Scrape\\zHealthfollowupexamnotelist2.xlsx'
    
    driver = html_handler.setup_driver()
    
    
    try:
        html_handler.login(driver, username, password, url)
        html_handler.push_basket_button(driver)

        # Loop while we still have pages, and handle all patients on each page
        while True:
            print("Handling patients on the current page")
            handle_page_patients(driver)
            # time.sleep(2)

            if html_handler.has_next_page(driver):
                print("Going to the next page")
                html_handler.go_to_next_page(driver)
                # time.sleep(5)
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