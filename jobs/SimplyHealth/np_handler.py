from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
import time
import json
import os
import shutil
from selenium.common.exceptions import NoSuchElementException
import html_handler
import CNHvariablelist
from utils import add_to_not_handled_dict
import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent

# Define a prefix for logging messages
PREFIX = "NP Module → "
def log(message):
    print(f"{PREFIX}{message}")



def exam_note_plan(driver, cervicalshandled, data, nextvisit, patientname, dateofservice, typeofpatientnote):

    print()
    print("start handling plan")
    print()

    if nextvisit == "":
        print("HANDLE_PLAN, no next visit")
        return False
    

    # open plan tab
    openplantab = html_handler.click_element(driver, CNHvariablelist.plantab, sleep_time = 1)
    print("opened plan tab")

    plancodelist = list()

    try:
        print()
        print("entering next visit:", nextvisit)
        html_handler.click_element_by_id(driver, "KylPlnAsc", sleep_time=2)
        
        # # remove duplicates from cervicalshandled
        # cervicalshandled = list(set(cervicalshandled))
        
        # # iterate over cervicalshandled
        # for parts in cervicalshandled:

        #     print(parts)
        #     plancode = data[parts]['plancode']
        #     print(plancode)
        #     newlist = [item for item in plancode]
        #     for item in newlist:
        #         if item == "":
        #             pass
        #         else:
        #             print (item)
        #             time.sleep(1)

        #             # click on each item button
        #             button = driver.find_element(By.ID, item).click()

        #             # add each plancode to the plancodelist
        #             plancodelist.append(item)
        #             print(plancodelist)
        #             time.sleep(1)

        # commoncervicals = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7']
        # for cervicals in commoncervicals:
        #     if cervicals in cervicalshandled:
        #         break
        # else:
        #     html_handler.click_element_by_id(driver, 'KylPlnNeuro', sleep_time=1)
        #     html_handler.click_element_by_id(driver, 'KylPlnNeuroCran', sleep_time=1)
        #     html_handler.click_element_by_id(driver, 'KylPlnNeuroCerv', sleep_time=1)
        #     html_handler.click_element_by_id(driver, 'KylPlnNeuroObjNote', sleep_time=2)

    except Exception as e:
        log(f"Error handling plan: {e}")
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Error handling plan: " + str(e))



def exam_note(driver, cervicalshandled_global, softtissue_global, bpartproblem, patientname, dateofservice, typeofpatientnote):
    print("exam_note, cervicalshandled: ",cervicalshandled_global)
    print("exam_note, softtissue: ",softtissue_global)
    print("exam_note, bpartproblem: ",bpartproblem)
    print()

    try:
        if open_the_exam_tab(driver) == False:
            log("Exam tab not opened successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list
            add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, "Exam tab not opened successfully.")
            return False
        log("Exam tab opened successfully.")

        # open the visual inspection tab        
        if visual_inspection_tab(driver) == False:
            log("Visual Inspection tab not opened successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list
            html_handler.add_to_nothandledlist(driver)
            return False
        log("Visual Inspection tab opened successfully.")

        # click on the active appearance button
        if subluxation_complexes_tab(driver, cervicalshandled_global) == False:
            log("Subluxation Complexes tab not opened successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list
            html_handler.add_to_nothandledlist(driver)
            return False
        log("Subluxation Complexes tab completed successfully.")
    
        # write the soft tissue findings
        if softtissue_write(driver, softtissue_global) == False:
            log("Soft Tissue tab not opened successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list
            html_handler.add_to_nothandledlist(driver)
            return False
        log("Soft Tissue tab completed successfully.")

        # open the orthopedic tab
        if orthopedic_tab(driver) == False:
            log("Orthopedic tab not opened successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list
            html_handler.add_to_nothandledlist(driver)
            return False
        log("Orthopedic tab opened successfully.")
        
        # open the cervical exam tab
        if cervical_exam_tab(driver, bpartproblem) == False:
            log("Cervical Exam tab not opened successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list
            html_handler.add_to_nothandledlist(driver)
            return False
        log("Cervical Exam tab opened successfully.")

        # open the lumbar exam tab
        if lumbar_exam_tab(driver, bpartproblem) == False:
            log("Lumbar Exam tab not opened successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list
            html_handler.add_to_nothandledlist(driver)
            return False
        log("Lumbar Exam tab opened successfully.")

        # open the joint palpation tab
        if joint_palpation_tab(driver, cervicalshandled_global) == False:
            log("Joint Palpation tab not opened successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list
            html_handler.add_to_nothandledlist(driver)
            return False
        log("Joint Palpation tab opened successfully.")

        # open the muscle palpation tab
        if muscle_palpation_tab(driver, cervicalshandled_global) == False:
            log("Muscle Palpation tab not opened successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list
            html_handler.add_to_nothandledlist(driver)
            return False
        log("Muscle Palpation tab opened successfully.")

        print()
        print('Exam note completed')
        print()
        return True
    
    except NoSuchElementException as e:
        log('Exam note not completed', e)
        return False
    

def open_the_exam_tab(driver):
    try:
        html_handler.click_element(driver, CNHvariablelist.examtab)
        log('Exam tab opened')
        return True
    
    except NoSuchElementException:
        log('Exam tab not found')
        return False
    
def visual_inspection_tab(driver):
    try:
        html_handler.click_element(driver, CNHvariablelist.visualinspectiontab)
        print('Visual Inspection tab opened')
        #click on active appearance button
        html_handler.click_element(driver, '//input[@type="checkbox" and @data-fieldcomments="active"]')
        print('Active Appearance button clicked')
        # click on communicates drop down and select "satisfactory"

        dropdown_element = driver.find_element(By.XPATH,'//select[@id="KyleVisnspComm1"]')
        print('Communicates dropdown opened')
        select = Select(dropdown_element)
        time.sleep(2)

        try:
            select.select_by_visible_text("Satisfactorily")
            print("Satisfactorily option selected in the dropdown")
        except Exception as e1:
            try:
                select.select_by_value("satisfactorily")
                print("Satisfactorily selected by value")
            except Exception as e2:
                log("Satisfactorily option not found in the dropdown")
                log("First error:", e1)
                log("Second error:", e2)
                return False
        #html_handler.click_element(driver, '//*[@id="KyleVisnspComm1"]/option[2]')

        print('Visual Inspection tab opened')
        return True
    
    except:
        log('Visual Inspection tab not handled')
        return False

def click_subluxation_checkboxes(driver, code_list, mapping_file_path):
    # Load the code-to-labels mapping
    print("loaded mapping file: ", mapping_file_path)

    with open(BASE_DIR / mapping_file_path, 'r') as f:
        mapping = json.load(f)

    # Flatten the list of target labels from the input codes
    # Flatten the code_list and remove duplicates
    code_list = list(set(code_list))
    target_labels = set()
    print("click_subluxation_checkboxes, code_list: ", code_list)
    
    print()
    # Iterate through the code list and find corresponding labels
    for code in code_list:
        code_clean = code.strip()
        print(f"Looking up code: '{code_clean}'")
        labels = mapping.get(code_clean)
        print (f"Labels found for code '{code_clean}': {labels}")

        if labels:
            target_labels.update(labels)
        else:
            log(f"Warning: Code '{code}' not found in mapping file.")
            return False
    #
    # # if not using strike out below    
    # label_debug_path = "debug_labels.txt"
    # with open(label_debug_path, "w", encoding="utf-8") as f:
    #     f.write("--- Debug: All label texts on page ---\n")
    #     all_labels = driver.find_elements(By.XPATH, "//label")
    #     for lbl in all_labels:
    #         try:
    #             label_text = lbl.text.strip()
    #             f.write(f"→ Label text: '{label_text}'\n")
    #         except:
    #             continue
    #     f.write("--- End Debug ---\n")
    # print(f"✅ All label text written to {label_debug_path}\n")

    for label_text in target_labels:
        print(f"\n➡️ Searching for label containing: '{label_text}'")

        found = False
        all_labels = driver.find_elements(By.XPATH, "//label")
        for label in all_labels:
            try:
                if label_text.strip().lower() in label.text.strip().lower():
                    print(f"✅ Found match in label: '{label.text.strip()}' — clicking...")
                    # driver.execute_script("arguments[0].scrollIntoView(true);", label)
                    time.sleep(0.3)
                    label.click()
                    found = True
                    break
            except Exception as e:
                log(f"⚠️ Skipping label due to error: {e}")
                continue

        if not found:
            log(f"⚠️ No label found containing '{label_text}'")
            return False

    print("✅ Finished checkbox label clicking")

    # THIS WAS THE DEBUG CODE TO PRINT ALL LABELS
    # Optional debug: print all <label><span> text on the page
    # Save all label texts for debugging
    # with open("debug_labels.txt", "w", encoding="utf-8") as f:
    #     f.write("--- Debug: All label texts on page ---\n")
    #     all_labels = driver.find_elements(By.XPATH, "//label")
    #     for lbl in all_labels:
    #         try:
    #             f.write(f"→ Label text: '{lbl.text.strip()}'\n")
    #         except:
    #             continue
    #     f.write("--- End Debug ---\n")
    # print("✅ All label text written to debug_labels.txt\n")

    # # Click checkboxes based on target_labels using fuzzy match
    # all_labels = driver.find_elements(By.XPATH, "//label")
    # for target in target_labels:
    #     print(f"\n➡️ Searching for label containing: '{target}'")

    #     matched = False
    #     for label in all_labels:
    #         label_text = label.text.strip()
    #         if target.lower() in label_text.lower():
    #             try:
    #                 print(f"✅ Found match in label: '{label_text}' — clicking...")
    #                 driver.execute_script("arguments[0].scrollIntoView(true);", label)
    #                 time.sleep(0.2)
    #                 label.click()
    #                 matched = True
    #                 break
    #             except Exception as e:
    #                 print(f"❌ Error clicking label: {e}")
    #                 break

    #     if not matched:
    #         print(f"⚠️ No label found containing '{target}'")
    #         return False

    # print("✅ Finished checkbox label clicking\n")
            

def subluxation_complexes_tab(driver, cervicalshandled):
    
    # open the subluxation complexes tab
    try:
        html_handler.click_element(driver, CNHvariablelist.subluxationcomplexestab)
        print('Subluxation Complexes tab opened')
    except:
        log('Subluxation Complexes tab not found')
        #clear findings
        html_handler.clear_findings(driver)
        # add patient to not handled list
        html_handler.add_to_nothandledlist(driver)
        return False
    
    # print("exam - cervicals handled:", cervicalshandled_global)    
    # cervicalshandled = cervicalshandled_global
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mapping_file_path = os.path.join(script_dir, 'examsubluxationcomplexeslist.json')
    if not os.path.exists(mapping_file_path):
        log(f"Mapping file not found at {mapping_file_path}. Please check the path.")
        return False
    
    print("cervicalshandled:", cervicalshandled)
    shortcodes = cervicalshandled

    try:
        if click_subluxation_checkboxes(driver, shortcodes, mapping_file_path) == False:
            print("Subluxation Complexes checkboxes not clicked successfully.")
            #clear findings
            html_handler.clear_findings(driver)
            # add patient to not handled list

        print("Subluxation Complexes checkboxes clicked successfully.")


    except NoSuchElementException:
        log('Subluxation Complexes tab not found')
        #clear findings
        html_handler.clear_findings(driver)
        return False
    
    # THIS IS THE OLD CODE THAT WORKED

    # with open(r'G:\My Drive\My folder\kyle-python\New Button Scrape\plannotesublux.json') as p:
    #         plannotesublux = json.load(p)

    # try:
    #     #open the subluxation complexes tab
    #     html_handler.click_element(driver, CNHvariablelist.subluxationcomplexestab)
    #     print('Subluxation Complexes tab opened')

    #     subluxes = plannotesublux['subluxes']
    #     bone = subluxes['bone']
    #     singleboxcode = subluxes['singleboxcode']
    #     doubleboxcode = subluxes['doubleboxcode']
    #     #remove duplicates from shortcodes
    #     shortcodes = list(set(shortcodes))

    #     print("exam shortcodes to click: ", shortcodes)

    #      # using text from shortcodes, find the segments correlating to the checkboxes to click
    #     for bone in shortcodes:
    #         print("bone refence to click: ", bone)
    #         splitbone = bone.split(" ")
    #         bone = splitbone[0]
    #         print(bone)


    #         if bone.startswith("B"):
    #             print("doublebox code")
    #             clickmybox = doubleboxcode[bone]
    #             print(clickmybox)
    #             # extract the items in the clickmybox list and turn them both into strings
    #             item1 = str(clickmybox[0])
    #             item2 = str(clickmybox[1])
    #             # create the xpath for the first item in the list
    #             item1xpath = "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[4]/div[2]/div/div[1]/div/div/div/div"+item1+"/label/input"
    #             print(item1xpath)
    #             html_handler.click_element(driver, item1xpath)
                
    #             # create the xpath for the second item in the list
    #             item2xpath = "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[4]/div[2]/div/div[1]/div/div/div/div"+item2+"/label/input"
    #             print(item2xpath)
    #             html_handler.click_element(driver, item2xpath)
                

    #         else:
    #             clickmybox = singleboxcode[bone]
    #             print("singlebox code")
    #             print(clickmybox)
    #             itemxpath = "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[4]/div[2]/div/div[1]/div/div/div/div"+clickmybox+"/label/input"
    #             print(itemxpath)
    #             html_handler.click_element(driver, itemxpath)
    #             print("single box: ", bone," clicked")

    #     return True
    
    # except NoSuchElementException:
    #     print('Subluxation Complexes tab not found')
    #     return False

def softtissue_write(driver, softtissue_global):
    print()
    print("softtissue_write, opening other exam tab")

    #with open(r'G:\My Drive\My folder\kyle-python\New Button Scrape\softtissuemapping.json') as s:
    with open(BASE_DIR / 'softtissuemapping.json') as s:
        softtissuemaping = json.load(s)

    #open the other exam tab
    try:
        html_handler.click_element(driver, CNHvariablelist.otherexamtab)
        print('Other Exam tab opened')
    
    except NoSuchElementException as e:
        log('Other Exam tab not found', e)        
        return False
    
    print()
    print("softtissue_write, softtissue_global: ", softtissue_global)
    
    problem = softtissuemaping['problems']
    problemcode = softtissuemaping['shortcodemappings']
    tissue = softtissuemaping['tissue']
    thephrase = []

    softtissue = list(set(softtissue_global))
    print("softtissue_write, softtissue: ", softtissue)

    if not softtissue:
        print("There is no soft tissue to write.")
        return True  # No soft tissue entries to process, return True
    
    else:
        # Now separate each phrase within the entries by splitting them
        separated_softtissues = []
        for entry in softtissue:
            separated_softtissues.extend(entry.split(", "))  # Splitting the string by ', '

        print("exam, softtissue_write, separated_softtissues: ", separated_softtissues)

        for listing in separated_softtissues:
            print("exam, softtissue_write, listing: ", listing)

            if listing == "":
                print("exam, softtissue_write, listing is empty, skipping")
                return True

            # The rest of your code will remain the same from this point
            splitwords = listing.split(' ')
            firsttwowords = splitwords[0:2]
            restofproblem = splitwords[2:] 
            print(firsttwowords)
            print(restofproblem)

            for word in firsttwowords:
                print(word)
                #print(problemcode[word])
                firstword = problemcode[word]
                print(firstword)
                #add each word to thephrase list
                thephrase.append(firstword)
                
            # use the rest of the words in the problem to find the tissue codes in tissue
            print(restofproblem)

            # build the phrase from tissue
            for word in restofproblem:
                print(word)
                #print(tissue[word])
                thetissueword = tissue[word]
                print(thetissueword)
                #add each word to thephrase list
                thephrase.append(thetissueword)

            # build the phrase from tissue and firstword in problemcode
            print("the phrase: ", thephrase)
            finalphrase = ' '.join(thephrase)
            print(finalphrase)
            
            phrase = finalphrase #"Patient presents with "+thephrasefirstword+" "+therestofthephrase+". "
            print(phrase)

            try:
                print("exam, softtissue_write, entering phrase")
                html_handler.click_element_by_id(driver, 'kpi_dailyOthrNotPNRecordNote')
                # send the phrase to the comment box
                html_handler.send_keys_by_id(driver, 'kpi_dailyOthrNotPNRecordNote', phrase)
                # send a period to the comment box
                html_handler.send_keys_by_id(driver, 'kpi_dailyOthrNotPNRecordNote', ".")
                time.sleep(1)

            except NoSuchElementException as e:
                log('softtissue_write, phrase not entered', e)
                return False

def orthopedic_tab(driver):
    try:
        html_handler.click_element(driver, CNHvariablelist.orthopedictab)
        print('Orthopedic tab opened')

        # click standard orthopedic exam buttons
        # the negative on the distraction button
        html_handler.click_element_by_id(driver, "KyleOrthoDistrctn1")                                     
        # click on left Negative for Foraminal Compression                                    
        html_handler.click_element_by_id(driver, "KyleOrthoForcomp1")
        # click on right Negative for Foraminal Compression
        html_handler.click_element_by_id(driver, "KyleOrthoForcompRyt1")
        # click on left Jackson's Compression                                   
        html_handler.click_element_by_id(driver, "KyleOrthoJckComp1")
        # click on right Jackson's Compression
        html_handler.click_element_by_id(driver, "KyleOrthoJckCompRyt1")
        # click on Shoulder Depression buttons
        html_handler.click_element_by_id(driver, "KyleOrthoShDep1")
        html_handler.click_element_by_id(driver, "KyleOrthoShDepRyt1")
        
        print("standard orthopedic buttons clicked")
        print()
        return True

    except NoSuchElementException:
        log('Orthopedic tab not found')
        return False
    
def cervical_exam_tab(driver, bpartproblem):
    print()
    print ("exam, cervical_exam_tab, bpartproblem: ", bpartproblem)
    print()
    
    try:
        # open the cervical tab
        html_handler.click_element(driver, CNHvariablelist.cervicalromtab)
        print('Cervical Exam tab opened')

        # open the cervical active ROM tab
        html_handler.click_element(driver, CNHvariablelist.cervicalactiveromtab)
        print('Cervical Active ROM tab opened')

        # click on the standard cervical active ROM buttons
        # click on Normal for Flexion
        html_handler.click_element_by_id(driver, "KyleCervARFlxR1")
        # click on Normal for Extension                                   
        html_handler.click_element_by_id(driver, "KyleCervARExtR1")
        # click on Normal for Lateral Flexion Left
        html_handler.click_element_by_id(driver, "KyleCervARLLFlxR1")
        # click on Normal for Lateral Flexion Right                                  
        html_handler.click_element_by_id(driver, "KyleCervARRLFlxR1")
        # click on Normal for Rotation Left                                 
        html_handler.click_element_by_id(driver, "KyleCervARLrotR1")
        # click on Normal for Rotation Right
        html_handler.click_element_by_id(driver, "KyleCervARRrotR1")
        print('standard cervical active ROM buttons clicked')

        # for the bpartproblem in listing, click the corresponding checkbox
        for problem in bpartproblem:
            print("problem:", problem)
            #if problem ends with "R" or "L" then click the correlating button
            if problem.endswith("R"):
                html_handler.click_element_by_id(driver, "KyleCervARRLFlxR3") #buton for decreaed right flexion
                html_handler.click_element_by_id(driver, "KyleCervARRrotR3") #button for decreased right rotation
                print("right rotation buttons clicked")
                time.sleep(1)
            elif problem.endswith("L"):
                html_handler.click_element_by_id(driver, "KyleCervARLLFlxR3") #button for decreased left flexion
                html_handler.click_element_by_id(driver, "KyleCervARLrotR3") #button for decreased left rotation
                print("left rotation buttons clicked")
                time.sleep(1)

        # open the cervical passive ROM tab
        html_handler.click_element(driver, CNHvariablelist.cervicalpassiveromtab)
        print('Cervical Passive ROM tab opened')
        # click on the standard cervical passive ROM buttons
        html_handler.click_element_by_id(driver, 'KyleCervPasFlxR1') 
        html_handler.click_element_by_id(driver, 'KyleCervPasExtR1')
        html_handler.click_element_by_id(driver, 'KyleCervPasLLFlxR1')
        html_handler.click_element_by_id(driver, 'KyleCervPasRLFlxR1')
        html_handler.click_element_by_id(driver, 'KyleCervPasLrotR1')
        html_handler.click_element_by_id(driver, 'KyleCervPasRrotR1')

        print('standard cervical passive ROM buttons clicked')

        # for the bpartproblem in listing, click the correlating buttons
        for problem in bpartproblem:
            print("problem:", problem)
            if problem.endswith("R"):
                html_handler.click_element_by_id(driver, "KyleCervPasRLFlxR3") #button for decreased right flexion
                html_handler.click_element_by_id(driver, "KyleCervPasRrotR3") #button for decreased right rotation
                print("right rotation buttons clicked")

            elif problem.endswith("L"):
                html_handler.click_element_by_id(driver, "KyleCervPasLLFlxR3") #button for decreased left flexion
                html_handler.click_element_by_id(driver, "KyleCervPasLrotR3") #button for decreased left rotation
                print("left rotation buttons clicked")
            
        return True
    
    except NoSuchElementException:
        log('Cervical Exam tab not found')
        return False
    
def lumbar_exam_tab(driver, bpartproblem):
    print()
    print("exam, lumbar_exam_tab, cervicalshandled: ", bpartproblem)
    print()
    
    try:
        # open the lumbar tab
        html_handler.click_element(driver, CNHvariablelist.lumbarromtab)
        print('Lumbar Exam tab opened')

        # open the lumbar active ROM tab
        html_handler.click_element(driver, CNHvariablelist.lumbaractiveromtab)
        print('Lumbar Active ROM tab opened')

        # click on the standard lumbar active ROM buttons
        html_handler.click_element_by_id(driver, "KyleLumbARFlxR1") # click on Normal for Flexion
        html_handler.click_element_by_id(driver, "KyleLumbARExtR1") # click on Normal for Extension
        html_handler.click_element_by_id(driver, "KyleLumbARLLFlxR1") # click on Normal for Lateral Flexion Left
        html_handler.click_element_by_id(driver, "KyleLumbARRLFlxR1") # click on Normal for Lateral Flexion Right
        html_handler.click_element_by_id(driver, "KyleLumbARLrotR1") # click on Normal for Rotation Left
        html_handler.click_element_by_id(driver, "KyleLumbARRrotR1") # click on Normal for Rotation Right
        print('standard lumbar active ROM buttons clicked')

        # for the bpartproblem in listing, click the correlating buttons
        for problem in bpartproblem:
            print("problem:", problem)

            if problem.endswith("R"):
                html_handler.click_element_by_id(driver, "KyleLumbARRLFlxR3") #button for decreaed right flexion
                html_handler.click_element_by_id(driver, "KyleLumbARRrotR3") #button for decreased right rotation
                print("right rotation buttons clicked")

            elif problem.endswith("L"):
                html_handler.click_element_by_id(driver, "KyleLumbARLLFlxR3") #button for decreased left flexion
                html_handler.click_element_by_id(driver, "KyleLumbARLrotR3") #button for decreased left rotation
                print("left rotation buttons clicked")

        # open the lumbar passive ROM tab
        html_handler.click_element(driver, CNHvariablelist.lumbarpassiveromtab)
        print('Lumbar Passive ROM tab opened')

        # click on the standard lumbar passive ROM buttons
        html_handler.click_element_by_id(driver, 'KyleLumbPasARFlxR1') # click on Normal for Flexion
        html_handler.click_element_by_id(driver, 'KyleLumbPasARExtR1') # click on Normal for Extension
        html_handler.click_element_by_id(driver, 'KyleLumbPasARLLFlxR1') # click on Normal for Lateral Flexion Left
        html_handler.click_element_by_id(driver, 'KyleLumbPasARRLFlxR1') # click on Normal for Lateral Flexion Right
        html_handler.click_element_by_id(driver, 'KyleLumbPasARLrotR1') # click on Normal for Rotation Left
        html_handler.click_element_by_id(driver, 'KyleLumbPasARRrotR1') # click on Normal for Rotation Right
        print('standard lumbar passive ROM buttons clicked')

        # for the bpartproblem in listing, click the correlating buttons
        for problem in bpartproblem:
            print("problem:", problem)
            if problem.endswith("R"):
                html_handler.click_element_by_id(driver, "KyleLumbPasARRLFlxR3") #button for decreaed right flexion
                html_handler.click_element_by_id(driver, "KyleLumbPasARRrotR3") #button for decreased right rotation
                print("right rotation buttons clicked")

            elif problem.endswith("L"):
                html_handler.click_element_by_id(driver, "KyleLumbPasARLLFlxR3") #button for decreased left flexion
                html_handler.click_element_by_id(driver, "KyleLumbPasARLrotR3") #button for decreased left rotation
                print("left rotation buttons clicked")

        return True
    
    except NoSuchElementException as e:
        log('Lumbar Exam tab not found', e)
        return False


def joint_palpation_tab(driver, cervicalshandled):
    
    #remove duplicates from cervicalshandled
    cervicalshandled = list(set(cervicalshandled))
    print("joint palpation cervicalshandled: ", cervicalshandled)
    # split first letter from each problem in cervicalshandled
    cervicalshandled = [problem[0] for problem in cervicalshandled]
    print("joint palpation cervicalshandled: ", cervicalshandled)
    #remove duplicates from cervicalshandled
    cervicalshandled = list(set(cervicalshandled))

    try:
        # open the joint palpation tab
        html_handler.click_element(driver, CNHvariablelist.jointpalpationtab)
        print('Joint Palpation tab opened')

        # click on the areas of decreased joint motions according to the bpartproblem in listing
        for problem in cervicalshandled:
            # if problem starts with "C" then click the correlating button
            if problem.startswith("C"):
                print("cervical joint palpation")
                html_handler.click_element_by_id(driver, "KyleJntPlpCerv1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleJntPlpCervRyt3")
                
            elif problem.startswith("T"):
                print("thoracic joint palpation")
                html_handler.click_element_by_id(driver, "KyleJntPlpThor1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleJntPlpThorRyt3")

            elif problem.startswith("L"):
                print("lumbar joint palpation")
                html_handler.click_element_by_id(driver, "KyleJntPlpLumb1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleJntPlpLumbRyt3")

            elif problem.startswith("S"):
                print("sacral joint palpation")
                html_handler.click_element_by_id(driver, "KyleJntPlpSacr1")  
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleJntPlpSacrRyt3")

            # if the problem has "ELBW" or "WRST" or "SHLD" or "DIG" in it, click the correlating button
            elif "ELBW" or "WRST" or "SHLD" or "DIG" in problem:
                print("extremity joint palpation")
                html_handler.click_element_by_id(driver, "KyleJntPlpUpExt1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleJntPlpUpExtRyt3")

            # if the problem has "HIP" or "KNEE" or "ANKL" or "TOE" in it, click the correlating button
            elif "HIP" or "KNEE" or "ANKL" or "TOE" in problem:
                print("extremity joint palpation")
                html_handler.click_element_by_id(driver, "KyleJntPlpLowExt1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleJntPlpLowExtRyt3")        

        return True

    except NoSuchElementException as e:
        log('Joint Palpation tab not found', e)
        return False    
    
def muscle_palpation_tab(driver, cervicalshandled):
    print()
    print("exam, muscle_palpation_tab, cervicalshandled: ", cervicalshandled)   
    print()

    try:
        # open the muscle palpation tab
        html_handler.click_element(driver, CNHvariablelist.musclepalpationtab)
        print('Muscle Palpation tab opened')
        for problem in cervicalshandled:
            print("problem:", problem)
            # click on the muscle palpation buttons that correspond to the bpartproblem in listing
            if "C" in cervicalshandled:
                print("cervical muscle correlation palpation buttons clicking")
                html_handler.click_element_by_id(driver, "KyleMusPtSOM1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleMusPtSOM3")
                
                html_handler.click_element_by_id(driver, "KyleMusPtStern1")
                html_handler.click_element_by_id(driver, "KyleMusPtStern3")

                html_handler.click_element_by_id(driver, "KyleMusPtCerv1")
                html_handler.click_element_by_id(driver, "KyleMusPtCerv3")

            elif "T" in cervicalshandled:
                print("thoracic muscle correlation palpation buttons clicking")
                html_handler.click_element_by_id(driver, "KyleMusPtParat1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleMusPtParat3")

                html_handler.click_element_by_id(driver, "KyleMusPtTrap1")
                html_handler.click_element_by_id(driver, "KyleMusPtTrap3")

            elif "L" or "S" in cervicalshandled:
                print("lumbar muscle correlation palpation buttons clicking")
                html_handler.click_element_by_id(driver, "KyleMusPtParal1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleMusPtParal3")

                html_handler.click_element_by_id(driver, "KyleMusPtQuadr1")
                html_handler.click_element_by_id(driver, "KyleMusPtQuadr3")

                html_handler.click_element_by_id(driver, "KyleMusPtGlUT1")
                html_handler.click_element_by_id(driver, "KyleMusPtGlUT3")

            elif "ELBW" or "WRST" or "SHLD" or "DIG" in cervicalshandled:
                print("extremity muscle correlation palpation buttons clicking")
                html_handler.click_element_by_id(driver, "KyleMusPtUEM1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleMusPtUEM3")

            elif "HIP" or "KNEE" or "ANKL" or "TOE" in cervicalshandled:
                print("extremity muscle correlation palpation buttons clicking")
                html_handler.click_element_by_id(driver, "KyleMusPtLEM1")
                #click the corresponding tender button
                html_handler.click_element_by_id(driver, "KyleMusPtLEM3")

            return True
    
    except NoSuchElementException as e:
        log('Muscle Palpation tab not found', e)
        return False
    
def exam_handle_diag(driver, cervicalshandled, data):
    print()
    print("start handling invoicing")
    print()

    # remove duplicates from cervicalshandled
    cervicalshandled = list(set(cervicalshandled)) 
    commoncervicals = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7']

    try:
        #open the invoice tab
        html_handler.click_element(driver, CNHvariablelist.invoicetab, sleep_time=2)
        listofdiaghandled = list()
        diaglist2 = data.keys()

        with open(BASE_DIR / 'theorder.json') as o:
            order = json.load(o)

        if "RETRACING" not in cervicalshandled or "N/A" not in cervicalshandled:
            cervicalshandled = sorted(cervicalshandled, key=lambda x: order[x])
            print("cervicalshandled:", cervicalshandled)

            for part in cervicalshandled:
                if part in diaglist2:
                    diagcode = data[part]['diagcode']
                    print(diagcode)

                    for eachdiagcode in diagcode:
                        listofdiaghandled.append(eachdiagcode)

            #remove duplicates from listofdiaghandled
            listofdiaghandled = list(set(listofdiaghandled))
            print(listofdiaghandled)

            for everydiagcode in listofdiaghandled:
                # enter and select the diagnosis code
                html_handler.send_keys_by_id(driver, "diagnosisBillingCode.icdWithDiagnosisCode", everydiagcode, sleep_time=3)
                html_handler.send_keys_by_id(driver, "diagnosisBillingCode.icdWithDiagnosisCode", Keys.ENTER, sleep_time=2)
                # click the add button
                html_handler.click_element(driver, CNHvariablelist.diagnosisbutton, sleep_time=2)
                # clear the text box                                   
                html_handler.clear_text_box(driver, "diagnosisBillingCode.icdWithDiagnosisCode")
                
        cervdiag = "M54.20"
        nmrdiag = ["M79.12", "M62.838"]

        if cervdiag not in listofdiaghandled:
            for eachnmrdiag in nmrdiag:
                # enter and select the diagnosis code
                html_handler.send_keys_by_id(driver, "diagnosisBillingCode.icdWithDiagnosisCode", eachnmrdiag)
                html_handler.send_keys_by_id(driver, "diagnosisBillingCode.icdWithDiagnosisCode", Keys.ENTER, sleep_time=2)
                # click the add button
                html_handler.click_element(driver, CNHvariablelist.diagnosisbutton, sleep_time=2)
                # clear the text box
                #html_handler.clear_text_box(driver, "diagnosisBillingCode.icdWithDiagnosisCode")
                
                listofdiaghandled.append(eachnmrdiag)

        # # Xpath to locate the container (ul) element
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
                    log(f"Error clicking button {i + 1}: {e}")
   

        except Exception as e:
            log(f"Error locating diagnosis container: {e}")
            return False

        return True

    except NoSuchElementException as e:
        log('Diagnosis tab not found', e)
        return False
     

def exam_handle_cpt(driver, cervicalshandled):

    try:
        #open the invoice tab
        #html_handler.click_element_by_id(driver, "NoteInvoicesPresentation", sleep_time=2)

        #handle cpt codes
        unique_codes = list(set(cervicalshandled))
        # add other CPT codes
        count = len([code for code in unique_codes if code >='M99.11' and code <= 'M99.15'])
        if "M99.08" in unique_codes and "M99.12" not in unique_codes:
            count += 1

        if count == 0:
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", "99202", sleep_time=3)
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", Keys.ENTER, sleep_time=2)
            html_handler.click_element(driver, CNHvariablelist.cptbutton)
            html_handler.clear_text_box(driver, "cptBillingCode.cptCodeWithDesc")
        elif count in [1, 2]:
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", "99203", sleep_time=3)
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", Keys.ENTER, sleep_time=2)
            html_handler.click_element(driver, CNHvariablelist.cptbutton)
            html_handler.clear_text_box(driver, "cptBillingCode.cptCodeWithDesc")
        elif count in [3, 4]:
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", "99204", sleep_time=3)
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", Keys.ENTER, sleep_time=2)
            html_handler.click_element(driver, CNHvariablelist.cptbutton)
            html_handler.clear_text_box(driver, "cptBillingCode.cptCodeWithDesc")
        elif count >= 5:
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", "99205", sleep_time=3)
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", Keys.ENTER, sleep_time=2)
            html_handler.click_element(driver, CNHvariablelist.cptbutton)
            html_handler.clear_text_box(driver, "cptBillingCode.cptCodeWithDesc")

    except Exception as e:
        log(f"Error handling additional diagnoses: {e}")

    return True

def exam_handle_payment(driver, patientname, dateofservice, typeofpatientnote, nothandledclientsdict):
    
    try:
        amount_due_element = driver.find_element(By.XPATH, '//input[@id="balanceDue"]')
        amount_due = float(amount_due_element.get_attribute("value")) 
        amount_due = amount_due 

        html_handler.send_keys_by_id(driver, "discount", str(amount_due), sleep_time=1)
        html_handler.send_keys_by_id(driver, "paymentType", "W", sleep_time=1)
        html_handler.send_keys_by_id(driver, "paymentType", Keys.ENTER, sleep_time=1)
        html_handler.click_element_by_id(driver, "addInvoicePaymentBtn", sleep_time=1)

    except Exception as e:
        log(f"Error handling payment: {e}")
        # add patient to not handled list
        add_to_not_handled_dict(patientname, dateofservice, typeofpatientnote, nothandledclientsdict, "payment error")
        # skip to next client
        return False
    
    return True
