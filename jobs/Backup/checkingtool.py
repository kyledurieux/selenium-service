import pandas as pd

def check_for_patient():
    try:
        # Open schdata.csv
        df = pd.read_csv('shcdata.csv')
    except FileNotFoundError:
        print("The file 'shcdata.csv' was not found.")
        return

    # Ask for input of patient name
    patient_name = input("Enter patient name: ")
    # Ask for input of date of service
    date_of_service = input("Enter date of service (mm/dd/yyyy): ")
    # Ask for input of type of patient
    patient_type = input("Enter type of patient (ALL CAPS): ")

    # Find the patient record
    mask = (df['Patient Name'] == patient_name) & \
           (df['Date of Service'] == date_of_service) & \
           (df['Patient Type'] == patient_type)

    if mask.any():
        #if patient is found, print the patient's information
        print(df[mask])
        
    else:
        print("Patient not found")

def main():
    check_for_patient()
    quit()

if __name__ == "__main__":
    main()