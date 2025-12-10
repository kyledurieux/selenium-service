

#The Basket XPath Variable 
mybasket = '//a[@id="MyBasket"]'
homebutton = '//a[@id="homeBtn"]'

# Main Soap Note tab variables
objectivetab = "//a[text()='Objective']"
subjectivetab = "//a[text()='Subjective']"
assessmenttab = "//a[text()='Assessment']"
plantab = "//a[text()='Plan']"
examtab = "//a[text()='Exam']"
additionaltab = "//a[text()='Additional']"
invoicetab = "//a[text()='Invoice']"
reviewandsigntab = "//a[text()='Review & Sign']"

#Objective tab variables
scanandlegchecktab = '//a[normalize-space(text())="SCAN AND LEG CHECK"]'
cervicaltab = '//a[normalize-space(text())="CERVICAL SPINE"]'
thoracictab = '//a[normalize-space(text())="THORACIC SPINE"]'
lumbartab = '//a[normalize-space(text())="LUMBAR SPINE"]'
sacrumtab = '//a[normalize-space(text())="SACRUM"]'
upperextremitytab = '//a[normalize-space(text())="UPPER EXTREMITIES"]'
lowerextremitytab = '//a[normalize-space(text())="LOWER EXTREMITIES"]'
muscleorsofttissuetab = '//a[normalize-space(text())="MUSCLE OR SOFT TISSUE"]'
skullandtmjtab = '//a[normalize-space(text())="SKULL AND TMJ"]'

#Additional tab variables
specialnotetextarea = '//textarea[@name="specialNotes"]'


#Exam tab variables
vitalstab = '//a[normalize-space(text())="VITALS"]'
visiontab = '//a[normalize-space(text())="VISION"]'
visualinspectiontab = '//a[normalize-space(text())="VISUAL INSPECTION"]'
subluxationcomplexestab = '//a[normalize-space(text())="SUBLUXATION COMPLEXES"]'
orthopedictab = '//a[normalize-space(text())="ORTHOPEDIC"]'
cervicalromtab = '//a[normalize-space(text())="CERVICAL ROM"]'
lumbarromtab = '//a[normalize-space(text())="LUMBAR ROM"]'
motortab = '//a[normalize-space(text())="MOTOR"]'
reflextab = '//a[normalize-space(text())="REFLEX"]'
sensorytab = '//a[normalize-space(text())="SENSORY"]'
jointpalpationtab = '//a[normalize-space(text())="JOINT PALPATION"]'
musclepalpationtab = '//a[normalize-space(text())="MUSCLE PALPATION"]'
supinetab = '//a[normalize-space(text())="SUPINE"]'
proneteststab = '//a[normalize-space(text())="PRONE TESTS"]'
sidelyingtab = '//a[normalize-space(text())="SIDE LYING"]'
otherexamtab = '//a[normalize-space(text())="OTHER EXAM"]'
posturalinspectiontab = '//a[normalize-space(text())="POSTURAL INSPECTION"]'
examnotestab = '//a[normalize-space(text())="EXAM NOTES"]'
cervicalactiveromtab = '//a[normalize-space(text())="CERVICAL ACTIVE ROM"]'
cervicalpassiveromtab = '//a[normalize-space(text())="CERVICAL PASSIVE ROM"]'
lumbaractiveromtab = '//a[normalize-space(text())="LUMBAR ACTIVE ROM"]'
lumbarpassiveromtab = '//a[normalize-space(text())="LUMBAR PASSIVE ROM"]'

#invoice tab variables
diagnosisline = '//input[@id="diagnosisBillingCode.icdWithDiagnosisCode"]'
cptline = '//input[@id="cptBillingCode.cptCodeWithDesc"]'
diagnosisbutton = '//button[@onclick="addDiagnosisBilling();"]'
cptbutton = '//a[contains(@href, "addCPTBilling()")]'

#clearing tabs
clearfindingsbutton = '//button[text()="Clear Findings"]'
