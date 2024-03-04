import serial
import serial.tools.list_ports


def ScanSerialPorts():
    """Find all available serial ports with devices. Then tries to connect to each port and
    test if the device is a Gentec E-O SDX-1153 or SDX-1226 amplifier.

    Returns:
        ampDict with either the amplifiers found listed by serial number or an empty dictionary if no amps are found.

    """
    available_ports = list(serial.tools.list_ports.comports())
    ampDict = {}
    if not available_ports:
        print("No COM ports available")
    else:
        for port_obj in available_ports:
            port = port_obj.device
            amp_ser_port = SDX1153(port)
            amp_ser_port.Connect()
            amp_info, serialnumber = amp_ser_port.Amp_ID()
            # Amp_ID returns amp_info (manf, model, serial number, version) and serial number to build dictionary.
            good_reply = (
                "SDX-1226" in amp_info or "SDX-1153" in amp_info or "ERR" in amp_info
            )
            if good_reply:
                inittest = amp_ser_port.Amp_Init()  # Initialize the amp
                # print(inittest)  # Here for testing.
                # print(amp_info) # Here for testing.
                # This adds a good_reply to ampDict.
                ampDict[serialnumber] = {
                    "Com Port": port,
                    "Amp ID Information": amp_info,
                    "Amp Serial Interface": amp_ser_port,
                }
            amp_ser_port.Close()
    return ampDict


class SDX1153:
    """
    Object for interacting with Gentec_EO SDX-1153 and SDX-1226 current-to-voltage converters (amplifiers).
    Contains commonly used commands, e.g. get instrument ID, setting/reading gain range, etc.

    Note: in manual mode the amp puts the current gain and resistance in the output buffer and "Auto Gain" when switched to REMOTE.
    If you switch the gain manually several times there will be a gain and resistance for every switch,
    so clear the buffer first before reading the gain.
    """

    def __init__(self, port, baudrate=9600, timeout=0.5):
        self.__ser__ = serial.Serial()
        self.__ser__.port = port
        self.__ser__.baudrate = baudrate
        self.__ser__.timeout = timeout
        self.__ser__.status = False

    def Connect(self):
        """Connects (opens) to a port with current settings.
        Has some error checking.
        """
        try:
            self.__ser__.open()
            # print(self.__ser__.port + " Connected!")  # Here for testing.
            self.__ser__.status = True
        except serial.SerialException as err:
            if "PermissionError(13, 'Access is denied.', None, 5)" in str(err):
                print("Check if port is in use somewhere else.")
            elif (
                "FileNotFoundError(2, 'The system cannot find the file specified.', None, 2)"
                in str(err)
            ):
                print("Nothing connected to this port.")
            else:
                raise err

    def IsConnected(self):
        # print(self.__ser__.status)
        return self.__ser__.status

    def Close(self):
        self.__ser__.close()
        print(self.__ser__.port + " Disconnected!\n")  # Here for testing.
        self.__ser__.status = False

    def Write(self, cmd):
        cmdstring = cmd + "\r\n"
        self.__ser__.write(cmdstring.encode())

    def Read(self):
        return self.__ser__.readline().decode().split("\r")[0]

    def Query(self, cmd):
        self.Write(cmd)
        return self.Read()

    def Amp_ID(self):
        """Identify device/instrument (amplifier) manufacturer, model, serial number, and firmware version.
        Gentec amplifiers do not use typical *IDN? command, must use individual commands to build ID info.
        The MFG and SNM values are blank when delivered from the factory. They must be added to RAM by the user.
        The MFG and SNM commands are not documented in the gentec users manual.

        Returns:
            string: Returns tuple manufacturer, model, serial number, and firmware version on four separte lines and serial number by itself. Typically used in a header file.
        """
        self.Write("MFG")  # ask for instrument manufacturer
        mfg = self.Read()
        self.Write("IDN")  # ask for instrument model number
        model = self.Read()
        self.Write("SNM")  # ask for instrument serial number
        sn = self.Read()
        self.Write("VER")  # ask for instrument firmware version
        frmwr = self.Read()
        # build all ID info string
        id_info = (
            "Manufacturer:,"
            + mfg
            + "\nModel:,"
            + model
            + "\nSerialNumber:,"
            + sn
            + "\nFirmware:,"
            + frmwr
            + "\n"
        )
        return id_info, sn

    def Clear_Buffer(self):
        """Clear amplifier output buffer.
        Clear the amp output buffer before setting or reading the amp gain.
        """
        # print("clear buffer") # here for testing
        satisfied = False
        # loopcount = 0  # for testing
        while not satisfied:  # loop waiting to empty buffer
            # print(str(loopcount))# here for testing
            buffout = self.__ser__.readline().decode()
            if buffout == "":
                satisfied = True  # end loop
                # else:
                #   print(str(buffout))# here for testing
                # loopcount = loopcount + 1

    def Set_Gain(self, gain):
        """Set amplifier gain range.

        Args:
            gain (int): value between 4-9.

        Returns:
            string: OK, ERR, Invalid Gain, or Must be in Auto Mode.
            'OK' if the command executed correctly;
            'ERR' if the command could not be executed;
            'Invalid Gain' if gain input not between 4-9;
            'Must be in Auto Mode' if not in REMOTE.
        """
        self.Clear_Buffer()
        gain_in = str(
            gain - 4
        )  # subtract 4 from the gain range to get gain range command value
        gaincmd = "TIA%s" % (gain_in)
        self.Write(gaincmd)  # set the amplifier gain range
        gi_response = self.__ser__.readline().decode()

        # Check for set gain error. Responses are: OK, ERR, Invalid Gain, Must be in Auto Mode
        if "OK" not in gi_response:
            if "ERR" in gi_response:
                gi_response = "Error"
            elif "Invalid Gain" in gi_response:
                gi_response = "Invalid Gain"
            elif "Must be in Auto Mode" in gi_response:
                gi_response = "Must be in Auto Mode"
            return gi_response

    def Read_Gain(self):
        """Gain is gain range 10^x, where x = gain (4-9).

        Returns:
            int: Returns gain in both Manual and REMOTE modes or
            string: ERR
        """
        self.Clear_Buffer()
        self.Write("TIA")
        go_response = self.__ser__.readline().decode().split(",")[0]

        ## Check for get (read) gain error. Responses are: gain range (index #) or ERR
        if "ERR" in go_response:
            return go_response
        else:
            gain_out = (
                int(go_response) + 4
            )  # add 4 to the returned value to get gain range
            return gain_out

    def Set_Mfg(self, mfg_date):
        """Sets the amplifier manufacturer to "Gentec-EO". This is not set at the factory. The MFG command are not documented in the gentec users manual.

        Args:
            mfg_date (string): Optionally, the manufacture date (yyyy-mm) can be set. Some applications find this useful. Set mfg_data to "" if not used.

        Returns:
            string: Responses are OK if the command executed correctly or
            ERR if the command could not be executed.
        """
        mfg_in = "MFG%s" % "Gentec-EO " + mfg_date  # date is optional
        self.Write(mfg_in)  # set instrument manufacturer
        mfg_in_response = self.__ser__.readline().decode().strip()
        return mfg_in_response

    def Set_SN(self, snm_in):
        """Sets the amplifier serial number. This is not set at the factory. The SNM commands are not documented in the gentec users manual.

        Args:
            smn_in (string): Typically use the number on the amp label.

        Returns:
            string: Responses are OK if the command executed correctly or
            ERR if the command could not be executed.
        """
        self.Write("SNM" + str(snm_in))  # set instrument serial number
        snm_in_response = self.__ser__.readline().decode().strip()
        return snm_in_response

    def Amp_Connect(self):
        """Connects to amplifer and queries manufacturer, model, serial number, and firmware version.

        Returns:
            string: Returns tuple of manufacturer, model, serial number, firmware version on four separte lines and serial number. Tuple typically used in a header file.
        """
        self.Connect()
        InitID = self.Amp_ID()
        print("Amp " + InitID[1] + " Connected!")
        # print(InitID[0])  # Print ID info string (4 lines)
        # print(InitID[1])  # Print amp serial number.

    def Amp_Reset(self):
        """Reset the amplifier like at power up.
        The following three commands are all performed at power up in the following order:
            RST forces a reset of the current offset DAC
            INI forces an initialization of the current offset DAC
            CAL forces a self-calibration of the current offset DAC
        These commands are not in the SDX-1153 User Manual v2.1, Gentec-EO sent them to me in series of
        emails last dated May 6, 2013, see file Gentec-EO SDX-1153 Commands_undocumented.txt.
        """
        self.Write("RST")  # forces a reset of the current offset DAC
        self.Write("INI")  # forces an initialization of the current offset DAC
        self.Write("CAL")  # forces a self-calibration of the current offset DAC

    def Amp_Default(self):
        """Default Amp Setup
        This turns the Zero Current Relay OFF and sets the Current DAC to a known value that is nominally 0µA or 2^19 = 524287.
        Setting the Current DAC is necessary after the RST, INI, and CAL commands are run.

        The following two commands are sent as default commands to the amplifier whenever the amplifier is initialized:
            RLY - Sets or Clears the Current zero relay independent of the zro command.
                Default: Disconnect a +/- 10 µA current source to the amp inverting input.
            DAC - Sets or queries the Current DAC directly. The argument is in DAC counts,
                where 2^20 (= 1048575) is +10µA, 2^19 (= 524287) is 0µA, and 0 is -10µA.
                Default: DAC counts = 523776 is the power on value for amp SN 501946 and has been used in all the LabVIEW programs.

        Zero Relay: RLY[0,1]\r\n; Returns: Command Status
        Example: From the SDX-1153 User Manual v2.1
            Send RLY1\r\n The SDX-1153 will set the current relay to CONNECT the source to the TIA inverting input.
            The current source value will not be changed. The SDX-1153 will reply OK.
        Example: Default
            Send RLY0\r\n The SDX-1153 will set the current relay to DISCONNECT the source to the TIA inverting input.
            The current source value will not be changed. The SDX-1153 will reply OK.
        Sending RLY with no argument will result in ERR being sent to the host.

        Reads:
            string: Responses are OK if the command executed correctly or
            ERR if the command could not be executed.

        Returns:
            amp_default_error: No errors = False; Error = True
        """
        self.Clear_Buffer()
        amp_default_error = False  # no errors
        self.Write(
            "RLY0"
        )  # Disconnect a +/- 10 µA current source to the amp inverting input.
        rly_response = self.__ser__.readline().decode().strip()
        if "OK" not in rly_response:
            print(rly_response)
            amp_default_error = True
        self.Write(
            "DAC523776"
        )  # Set DAC counts to 523776 is the power on value for amp SN 501946
        dac_response = self.__ser__.readline().decode().strip()
        if "OK" not in dac_response:
            print(dac_response)
            amp_default_error = True
        return amp_default_error

    def Amp_Init(self):
        """Reset the amplifier like at power up and set Defaults.

        Returns:
        string: Amplifier Reinitialized if the command executed correctly
        """
        self.Amp_Reset()
        # print("Reset")
        default_error = self.Amp_Default()
        if default_error == False:
            amp_init_response = "Amplifier Reinitialized"
        else:
            amp_init_response = "Amplifier Error"
        return amp_init_response
