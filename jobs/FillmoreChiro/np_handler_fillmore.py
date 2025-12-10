
#from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time
import json
import os
import shutil
from selenium.common.exceptions import NoSuchElementException
import html_handler
import CNHvariablelist
from CNH_FillmoreChiropractic_V1 import nothandledclients
from CNH_FillmoreChiropractic_V1 import shortcodes
from CNH_FillmoreChiropractic_V1 import softtissue_global
from CNH_FillmoreChiropractic_V1 import bpartproblem
from CNH_FillmoreChiropractic_V1 import cervicalshandled_global



def exam_note_plan(driver, cervicalshandled, data, nextvisit, patientname, dateofservice, typeofpatientnote):

    print()
    print("start handling plan")
    print()

    if nextvisit == "":
        print("HANDLE_PLAN, no next visit")
        html_handler.clear_findings(driver)
        # add patient to not handled list
        nothandledclients.append(patientname)
        nothandledclients.append(dateofservice)
        nothandledclients.append(typeofpatientnote)
        nothandledclients.append("no next visit")
        # skip to next client
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
        print(f"Error handling plan: {e}")



def exam_note(driver, cervicalshandled_global, softtissue_global, bpartproblem):
    print("exam_note, cervicalshandled: ",cervicalshandled_global)
    print("exam_note, softtissue: ",softtissue_global)
    print()

    try:
        open_the_exam_tab(driver)
        visual_inspection_tab(driver)
        subluxation_complexes_tab(driver, cervicalshandled_global)
        softtissue_write(driver, softtissue_global)
        orthopedic_tab(driver)
        cervical_exam_tab(driver, bpartproblem)
        lumbar_exam_tab(driver, cervicalshandled_global)
        joint_palpation_tab(driver, cervicalshandled_global)
        muscle_palpation_tab(driver, cervicalshandled_global)
        print('Exam note completed')
        return True
    
    except NoSuchElementException as e:
        print('Exam note not completed', e)
        return False
    

def open_the_exam_tab(driver):
    try:
        html_handler.click_element(driver, CNHvariablelist.examtab)
        print('Exam tab opened')
        return True
    
    except NoSuchElementException:
        print('Exam tab not found')
        return False
def click_subluxation_checkboxes(driver, code_list, mapping_file_path):
    # Load the code-to-labels mapping
    with open('examsubluxationcomplexeslist.json', 'r') as f:
        mapping = json.load(f)

    # Flatten the list of target labels from the input codes
    target_labels = set()
    for code in code_list:
        labels = mapping.get(code)
        if labels:
            target_labels.update(labels)
        else:
            print(f"Warning: Code '{code}' not found in mapping file.")

    # Find and click matching checkboxes by label text
    for label_text in target_labels:
        try:
            label_element = driver.find_element(By.XPATH, f"//label[text()='{label_text}']")
            input_element = label_element.find_element(By.XPATH, "./preceding-sibling::input[@type='checkbox']")
            if not input_element.is_selected():
                input_element.click()
                print(f"Checked: {label_text}")
            else:
                print(f"Already checked: {label_text}")
                
        except NoSuchElementException:
            print(f"Checkbox for label '{label_text}' not found.")
            # clear findings(driver)
            html_handler.clear_findings(driver)
            return False
        

def visual_inspection_tab(driver):
    try:
        html_handler.click_element(driver, CNHvariablelist.visulainspectiontab)
        #click on active appearance button
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[3]/div[2]/div/div[1]/div/div/div/div[2]/span/input[1]")
        # click on communicates drop down and select "satisfactory"
        html_handler.click_element(driver,"/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[3]/div[2]/div/div[1]/div/div/div/div[3]/div[2]/span/select")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[3]/div[2]/div/div[1]/div/div/div/div[3]/div[2]/span/select/option[2]")
        
        # click on communicates drop down and select "satisfactory"
        html_handler.click_element(driver,"/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[3]/div[2]/div/div[1]/div/div/div/div[3]/div[2]/span/select")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[3]/div[2]/div/div[1]/div/div/div/div[3]/div[2]/span/select/option[2]")

        print('Visual Inspection tab opened')
        return True
    
    except NoSuchElementException:
        print('Visual Inspection tab not found')
        return False
    
def subluxation_complexes_tab(driver, cervicalshandled):
    
    # print("exam - cervicals handled:", cervicalshandled_global)    
    # cervicalshandled = cervicalshandled_global
    
    print("cervicalshandled:", cervicalshandled)
    shortcodes = cervicalshandled

    with open(r'G:\My Drive\My folder\kyle-python\New Button Scrape\plannotesublux.json') as p:
            plannotesublux = json.load(p)

    try:
        #open the subluxation complexes tab
        html_handler.click_element_by_id(driver, 'soapcategory_660949')
        print('Subluxation Complexes tab opened')

        subluxes = plannotesublux['subluxes']
        bone = subluxes['bone']
        singleboxcode = subluxes['singleboxcode']
        doubleboxcode = subluxes['doubleboxcode']
        #remove duplicates from shortcodes
        shortcodes = list(set(shortcodes))

        print("exam shortcodes to click: ", shortcodes)

         # using text from shortcodes, find the segments correlating to the checkboxes to click
        for bone in shortcodes:
            print("bone refence to click: ", bone)
            splitbone = bone.split(" ")
            bone = splitbone[0]
            print(bone)


            if bone.startswith("B"):
                print("doublebox code")
                clickmybox = doubleboxcode[bone]
                print(clickmybox)
                # extract the items in the clickmybox list and turn them both into strings
                item1 = str(clickmybox[0])
                item2 = str(clickmybox[1])
                # create the xpath for the first item in the list
                item1xpath = "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[4]/div[2]/div/div[1]/div/div/div/div"+item1+"/label/input"
                print(item1xpath)
                html_handler.click_element(driver, item1xpath)
                
                # create the xpath for the second item in the list
                item2xpath = "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[4]/div[2]/div/div[1]/div/div/div/div"+item2+"/label/input"
                print(item2xpath)
                html_handler.click_element(driver, item2xpath)
                

            else:
                clickmybox = singleboxcode[bone]
                print("singlebox code")
                print(clickmybox)
                itemxpath = "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[4]/div[2]/div/div[1]/div/div/div/div"+clickmybox+"/label/input"
                print(itemxpath)
                html_handler.click_element(driver, itemxpath)
                print("single box: ", bone," clicked")

        return True
    
    except NoSuchElementException:
        print('Subluxation Complexes tab not found')
        return False

def softtissue_write(driver, softtissue_global):
    print("softtissue_write, opening other exam tab")

    with open(r'G:\My Drive\My folder\kyle-python\New Button Scrape\softtissuemapping.json') as s:
        softtissuemaping = json.load(s)

    #open the other exam tab
    try:
        html_handler.click_element_by_id(driver, 'soapcategory_660948')
        print('Other Exam tab opened')
    
    except NoSuchElementException as e:
        print('Other Exam tab not found', e)        
        return False
    
    print()
    print("softtissue_write, softtissue_global: ", softtissue_global)
    softtissue = list(set(softtissue_global))
    print("softtissue_write, softtissue: ", softtissue)
    print()
    

    problem = softtissuemaping['problems']
    problemcode = softtissuemaping['shortcodemappings']
    tissue = softtissuemaping['tissue']
    thephrase = []
    
    softtissue = softtissue.split(", ")
    print("exam, softtissue_write, softtissue: ", softtissue)    
    
    for listing in softtissue:
        print("exam, softtissue_write, listing: ", listing)

        if listing == "":
            return False
        
        #split the first word and find the code in problemcode
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

        html_handler.click_element_by_id(driver, 'kpi_dailyOthrNotPNRecordNote')
        # send the phrase to the comment box
        html_handler.send_keys_by_id(driver, 'kpi_dailyOthrNotPNRecordNote', phrase)
        # send a period to the comment box
        html_handler.send_keys_by_id(driver, 'kpi_dailyOthrNotPNRecordNote', ".")
        time.sleep(1)

def orthopedic_tab(driver):
    try:
        html_handler.click_element_by_id(driver, 'soapcategory_660933')
        print('Orthopedic tab opened')

        #click standard orthopedic exam buttons
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[5]/div[2]/div/div[1]/div/div/div/div[3]/div[2]/label[1]/input")   
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[5]/div[2]/div/div[1]/div/div/div/div[6]/div[3]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[5]/div[2]/div/div[1]/div/div/div/div[6]/div[5]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[5]/div[2]/div/div[1]/div/div/div/div[7]/div[3]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[5]/div[2]/div/div[1]/div/div/div/div[7]/div[5]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[5]/div[2]/div/div[1]/div/div/div/div[8]/div[3]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[5]/div[2]/div/div[1]/div/div/div/div[8]/div[5]/label[1]/input")
        
        print("standard orthopedic buttons clicked")
        print()
        return True

    except NoSuchElementException:
        print('Orthopedic tab not found')
        return False
    
def cervical_exam_tab(driver, bpartproblem):
    
    try:
        # open the cervical tab
        html_handler.click_element_by_id(driver, 'soapcategory_660934')
        print('Cervical Exam tab opened')

        # open the cervical active ROM tab
        html_handler.click_element_by_id(driver, 'soapsubcategory_660935')
        print('Cervical Active ROM tab opened')

        # click on the standard cervical active ROM buttons
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[3]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[4]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[5]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[6]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[7]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[8]/div[4]/label[1]/input")
        print('standard cervical active ROM buttons clicked')

        # for the bpartproblem in listing, click the corresponding checkbox
        for problem in bpartproblem:
            print("problem:", problem)
            #if problem ends with "R" or "L" then click the correlating button
            if problem.endswith("R"):
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[6]/div[4]/label[3]/input")
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[8]/div[4]/label[3]/input")
                print("right rotation buttons clicked")
                time.sleep(1)
            elif problem.endswith("L"):
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[5]/div[4]/label[3]/input")
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[7]/div[4]/label[3]/input")
                print("left rotation buttons clicked")
                time.sleep(1)

        # open the cervical passive ROM tab
        html_handler.click_element_by_id(driver, 'soapsubcategory_660936')
        print('Cervical Passive ROM tab opened')

        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[2]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[3]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[4]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[5]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[6]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[7]/div[4]/label[1]/input")
        print('standard cervical passive ROM buttons clicked')

        # for the bpartproblem in listing, click the correlating buttons
        for problem in bpartproblem:
            print("problem:", problem)
            if problem.endswith("R"):
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[5]/div[4]/label[3]/input")
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[7]/div[4]/label[3]/input")    
                print("right rotation buttons clicked")

            elif problem.endswith("L"):
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[4]/div[4]/label[3]/input")
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[6]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/div[6]/div[4]/label[3]/input")
                print("left rotation buttons clicked")
            
        return True
    
    except NoSuchElementException:
        print('Cervical Exam tab not found')
        return False
    
def lumbar_exam_tab(driver, cervicalshandled):
    
    try:
        # open the lumbar tab
        html_handler.click_element_by_id(driver, 'soapsubcategory_660937')
        print('Lumbar Exam tab opened')

        # open the lumbar active ROM tab
        html_handler.click_element_by_id(driver, 'soapsubcategory_660938')
        print('Lumbar Active ROM tab opened')

        # click on the standard lumbar active ROM buttons
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[3]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[4]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[5]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[6]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[7]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[8]/div[4]/label[1]/input")   
        print('standard lumbar active ROM buttons clicked')

        # for the bpartproblem in listing, click the correlating buttons
        for problem in cervicalshandled:
            print("problem:", problem)

            if problem.endswith("R"):
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[6]/div[4]/label[3]/input")
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[8]/div[4]/label[3]/input")
                print("right rotation buttons clicked")

            elif problem.endswith("L"):
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[5]/div[4]/label[3]/input")
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/div[7]/div[4]/label[3]/input")
                print("left rotation buttons clicked")

        # open the lumbar passive ROM tab
        html_handler.click_element_by_id(driver, 'soapcategory_660939')
        print('Lumbar Passive ROM tab opened')

        # click on the standard lumbar passive ROM buttons
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[2]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[3]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[4]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[5]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[6]/div[4]/label[1]/input")
        html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[7]/div[4]/label[1]/input")
        print('standard lumbar passive ROM buttons clicked')

        # for the bpartproblem in listing, click the correlating buttons
        for problem in cervicalshandled:
            print("problem:", problem)
            if problem.endswith("R"):
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[5]/div[4]/label[3]/input")
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[7]/div[4]/label[3]/input")
                print("right rotation buttons clicked")

            elif problem.endswith("L"):
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[4]/div[4]/label[3]/input")
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[6]/div[1]/div[3]/div[7]/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[6]/div[4]/label[3]/input")
                print("left rotation buttons clicked")

        return True
    
    except NoSuchElementException as e:
        print('Lumbar Exam tab not found', e)
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
        html_handler.click_element_by_id(driver, 'soapcategory_660943')
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
        print('Joint Palpation tab not found', e)
        return False    
    
def muscle_palpation_tab(driver, cervicalshandled):

    try:
        # open the muscle palpation tab
        html_handler.click_element_by_id(driver, 'soapcategory_660944')
        print('Muscle Palpation tab opened')

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

        if "T" in cervicalshandled:
            print("thoracic muscle correlation palpation buttons clicking")
            html_handler.click_element_by_id(driver, "KyleMusPtParat1")
            #click the corresponding tender button
            html_handler.click_element_by_id(driver, "KyleMusPtParat3")

            html_handler.click_element_by_id(driver, "KyleMusPtTrap1")
            html_handler.click_element_by_id(driver, "KyleMusPtTrap3")

        if "L" or "S" in cervicalshandled:
            print("lumbar muscle correlation palpation buttons clicking")
            html_handler.click_element_by_id(driver, "KyleMusPtParal1")
            #click the corresponding tender button
            html_handler.click_element_by_id(driver, "KyleMusPtParal3")

            html_handler.click_element_by_id(driver, "KyleMusPtQuadr1")
            html_handler.click_element_by_id(driver, "KyleMusPtQuadr3")

            html_handler.click_element_by_id(driver, "KyleMusPtGlUT1")
            html_handler.click_element_by_id(driver, "KyleMusPtGlUT3")

        if "ELBW" or "WRST" or "SHLD" or "DIG" in cervicalshandled:
            print("extremity muscle correlation palpation buttons clicking")
            html_handler.click_element_by_id(driver, "KyleMusPtUEM1")
            #click the corresponding tender button
            html_handler.click_element_by_id(driver, "KyleMusPtUEM3")

        if "HIP" or "KNEE" or "ANKL" or "TOE" in cervicalshandled:
            print("extremity muscle correlation palpation buttons clicking")
            html_handler.click_element_by_id(driver, "KyleMusPtLEM1")
            #click the corresponding tender button
            html_handler.click_element_by_id(driver, "KyleMusPtLEM3")

        return True
    
    except NoSuchElementException as e:
        print('Muscle Palpation tab not found', e)
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
        html_handler.click_element_by_id(driver, "NoteInvoicesPresentation", sleep_time=2)
        listofdiaghandled = list()
        diaglist2 = data.keys()

        with open('theorder.json') as o:
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
                html_handler.send_keys_by_id(driver, "diagnosisBillingCode.icdWithDiagnosisCode", everydiagcode, sleep_time=3)
                html_handler.send_keys_by_id(driver, "diagnosisBillingCode.icdWithDiagnosisCode", Keys.ENTER, sleep_time=2)
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/button[1]", sleep_time=2)
                html_handler.clear_text_box(driver, "diagnosisBillingCode.icdWithDiagnosisCode")
                
        cervdiag = "M54.20"
        nmrdiag = ["M79.12", "M62.838"]

        if cervdiag not in listofdiaghandled:
            for eachnmrdiag in nmrdiag:
                html_handler.send_keys_by_id(driver, "diagnosisBillingCode.icdWithDiagnosisCode", eachnmrdiag)
                html_handler.send_keys_by_id(driver, "diagnosisBillingCode.icdWithDiagnosisCode", Keys.ENTER, sleep_time=2)
                html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/button[1]", sleep_time=2)
                html_handler.clear_text_box(driver, "diagnosisBillingCode.icdWithDiagnosisCode")
                
                listofdiaghandled.append(eachnmrdiag)

        # # Xpath to locate the container (ul) element
        # container_xpath = "//ul[@id='diagnosisBillingListSortable']"
        # # Find the container element
        # container_element = driver.find_element(By.XPATH, container_xpath)
        # # Xpath to find all the diagnosis items (li) within the container
        # diagnosis_items_xpath = ".//li[contains(@class, 'form-group')]"
        # # Find all the diagnosis items within the container
        # diagnosis_items = container_element.find_elements(By.XPATH, diagnosis_items_xpath)
        # # Get the count of diagnosis items
        # count = len(diagnosis_items)

        # print(count)
        # try:
        #     clickthediagbuttons = html_handler.click_the_diag_buttons(driver, count)
        #     print("clicked the diag buttons")

        # except Exception as e:
        #     print(f"Error handling additional diagnoses: {e}")

        return True

    except NoSuchElementException as e:
        print('Diagnosis tab not found', e)
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
            html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[1]/div[2]/div/form/div[3]/div[9]/a/span")
            html_handler.clear_text_box(driver, "cptBillingCode.cptCodeWithDesc")
        elif count in [1, 2]:
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", "99203", sleep_time=3)
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", Keys.ENTER, sleep_time=2)
            html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[1]/div[2]/div/form/div[3]/div[9]/a/span")
            html_handler.clear_text_box(driver, "cptBillingCode.cptCodeWithDesc")
        elif count in [3, 4]:
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", "99204", sleep_time=3)
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", Keys.ENTER, sleep_time=2)
            html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[1]/div[2]/div/form/div[3]/div[9]/a/span")
            html_handler.clear_text_box(driver, "cptBillingCode.cptCodeWithDesc")
        elif count >= 5:
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", "99205", sleep_time=3)
            html_handler.send_keys_by_id(driver, "cptBillingCode.cptCodeWithDesc", Keys.ENTER, sleep_time=2)
            html_handler.click_element(driver, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[1]/div[2]/div/form/div[3]/div[9]/a/span")
            html_handler.clear_text_box(driver, "cptBillingCode.cptCodeWithDesc")

    except Exception as e:
        print(f"Error handling additional diagnoses: {e}")

    return True

def exam_handle_payment(driver, patientname, nothandledclients):
    
    try:
        amount_due_element = driver.find_element(By.XPATH, "/html/body/section/section[1]/section[2]/div[3]/div[10]/div/div/div[2]/div[8]/div/div[1]/div[2]/div[3]/form/ul/li[13]/div/div/input")
        amount_due = float(amount_due_element.get_attribute("value")) 
        html_handler.send_keys_by_id(driver, "discount", str(amount_due), sleep_time=1)
        html_handler.send_keys_by_id(driver, "paymentType", "W", sleep_time=1)
        html_handler.send_keys_by_id(driver, "paymentType", Keys.ENTER, sleep_time=1)
        html_handler.click_element_by_id(driver, "addInvoicePaymentBtn", sleep_time=1)

    except Exception as e:
        print(f"Error handling payment: {e}")
        # add patient to not handled list
        nothandledclients.append((patientname, "payment error"))
        # skip to next client
        return False
    
    return True
