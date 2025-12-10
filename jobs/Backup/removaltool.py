import pandas as pd

def remove_patient():
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
    #patient_type = input("Enter type of patient (ALL CAPS): ")

    # Find and remove the patient record
    mask = (df['Patient Name'] == patient_name) & \
           (df['Date of Service'] == date_of_service) #& \
           #(df['Patient Type'] == patient_type)

    if mask.any():
        df = df.drop(df[mask].index)
        df.to_csv('shcdata.csv', index=False)
        print("Patient removed from schedule")
    else:
        print("Patient not found")
    # Ask if the user wants to remove another patient
    while True:
        another = input("Do you want to remove another patient? (y/n): ").strip().lower()
        if another == 'y':
            remove_patient()
            break
        elif another == 'n':
            print("Exiting the program.")
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def main():
    remove_patient()
    quit()

if __name__ == "__main__":
    main()
