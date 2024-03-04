from gentec.gentec1153utils import ScanSerialPorts


# Find all Gentec E-O SDX-1153 or SDX-1226 amplifiers and build ampDictionary.
ampDict = ScanSerialPorts()
# print(str(ampDict) + "\n")  # Print the ampDict
print("Amplifer SN found: " + str(list(ampDict.keys())))

# Connect to an amplifer (ask operator)
comm_satisfied = True
while comm_satisfied:
    COM_sn = input("Enter Amp serial # or Q to quit: ")
    print(COM_sn)
    if "Q" in COM_sn or "q" in COM_sn:
        comm_satisfied = False
        keep_running = False

    else:
        if str(COM_sn) in str(list(ampDict.keys())):
            amp_ser_port = ampDict[COM_sn]["Amp Serial Interface"]
            amp_ser_port.Amp_Connect()
            comm_satisfied = False
            keep_running = True


# Loop waiting for operator to select commands.
while keep_running:
    command = input(
        "Enter command RG (Read Gain), SG (Set Gain), ID (Amp ID), AI (Amp Init), SMfg (Set Manufacturer), SSN (Set SN), or Q to quit: "
    ).upper()
    if "Q" in command:
        amp_ser_port.Close()  # Close comm port
        keep_running = False  # Stop loop (and program) execution
    if "RG" in command:
        amp_response = amp_ser_port.Read_Gain()
        print(amp_response)
    elif "SG" in command:
        gain_range = input("Enter gain range (4-9): ")
        amp_response = amp_ser_port.Set_Gain(int(gain_range))
    elif "ID" in command:
        amp_response = amp_ser_port.Amp_ID()
        print(amp_response)
    elif "AI" in command:
        amp_response = amp_ser_port.Amp_Init()
        print(amp_response)
    elif "SMFG" in command:
        print(
            "WARNING!! Use this command carefully! The manufacturer is not set at the factory.\nUse this command to set the manufacturer to 'Gentec-EO yyyy-mm'. The date is useful to identify the age of the amplifier."
        )
        mfg_date = input("Enter manufacture date (yyyy-mm): ")
        amp_response = amp_ser_port.Set_Mfg(mfg_date)
        print(amp_response)
    elif "SSN" in command:
        print(
            "WARNING!! Use this command carefully! The serial number is not set at the factory.\nUse this command to set the serial number."
        )
        serialnumb = input("Enter serial number (number on the amp label): ")
        amp_response = amp_ser_port.Set_SN(serialnumb)
        print(amp_response)

print("Goodbye.\n")
