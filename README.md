# Gentec_SDX1153
## Table of Contents
- [Gentec\_SDX1153](#gentec_sdx1153)
  - [Table of Contents](#table-of-contents)
  - [About ](#about-)
  - [Python requirements ](#python-requirements-)
  - [How to use](#how-to-use)
    - [How to launch GUI with executable ](#how-to-launch-gui-with-executable-)
    - [How to launch GUI with Python script ](#how-to-launch-gui-with-python-script-)
    - [How to import and use library (no GUI) ](#how-to-import-and-use-library-no-gui-)
  - [General guidance for amplifier operation ](#general-guidance-for-amplifier-operation-)

## About <a class="anchor" id=about></a>
Gentec_SDX1153 is a Python program for interacting with Gentec-EO SDX-1153 and SDX-1226 current-to-voltage converters (referred to here as amplifiers or amps).  Contains a few commonly used commands, e.g., setting/reading gain range, get instrument ID, etc.

This project was written at NIST by Thomas Larason (thomas.larason@nist.gov) with lots of help from Michael Braine.

The Gentec-EO SDX-1153 and SDX-1226 devices come from the factory without the manufacturer or serial number programed into the units. The command "IDN" returns the model number (SDX-1153 or SDX-1226). This is different from the SCPI command "*IDN?" which returns the manufacturer, model, serial number, and firmware version of the device. An equivalent result is obtained with the function _Amp_ID_ built into the functions library.

To set the manufacturer to 'Gentec-EO' use the function _Set_Mfg_. This function asks for a manufacture date in the format yyyy-mm. This is optional, but recommended. Use the _Set_SN_ function to set the serial number. This function will ask for the amplifier's serial number. Typically use the number on the amp label. These functions are not available with the GUI.


## Python requirements <a class="anchor" id=python-requirements></a>
Gentec-EO SDX-1153 requires Python >= 3.12.1 and the following libraries with their dependencies:
* PySerial >= 3.5

To use the GUI, additional libraries and their dependencies are required:
* PyQT5 >= 5.15.10

The virtual environment file, `Gentec_SDX1153.yaml`, will specifiy all required libraries for use of the GUI.

**Note:** older versions of these libraries and Python may work, but are untested.

## How to use<a class="anchor" id=howToUse></a>
There are three ways to use Gentec-EO SDX-1153: [with the GUI using the compiled executable](#how-to-launch-gui-with-executable), [with the GUI using the Python script](#how-to-launch-gui-with-python-script), or [directly with the functions library](#how-to-import-and-use-library-no-gui)

### How to launch GUI with executable <a class="anchor" id=how-to-launch-gui-with-executable></a>
The executable is available from the publicly available GitHub repository. On the Releases page, the latest executable can be downloaded for Windows 10 machines: https://github.com/tlarason-nist/Gentec-EO_SDX-1153.git. Simply download the .exe and run it.

The first operation after the GUI opens is to click on the **Scan** button. This will scan the serial ports (i.e., USB) for Gentec-EO SDX-1153 and SDX-1226 amps. The serial numbers of the amplifiers found will be listed in the **Connected Amplifiers** box and the **Amplifier** dropdown. Figure 1 is an image of the GUI after the **Scan** button has been clicked. Two SDX-1153's have been found connected to the host computer.

<p align="center">
    <img src=images/ampGUIscanned1.png>
    <figcaption><b>Figure 1: </b>Gentec-EO SDX-1153 GUI after scanning host computer ports and finding two devices, serial numbers 507007 and 501946.</figcaption>
</p>


Selecting one of the SN listed in the **Connected Amplifiers** box will show the Amplifier ID (manufacturer, model, sn, and firmware version) in the **Amplifier ID Information** box. The ID information for an 507007 is shown in Figure 2.

<p align="center">
    <img src=images/ampGUIscanned2.png>
    <figcaption><b>Figure 2: </b>ID information for Gentec-EO SDX-1153 sn 507007.</figcaption>
</p>


To read or set the gain range (10<sup>x</sup>) of an amplifier, select the sn from the **Amplifier** dropdown box. Then select the command operation (Read Gain or Set Gain) from the **Amplifier Command** dropdown. If reading the gain range (GUI default), click the **Send Command** button. The current gain range of the selected amp will be displayed in the **Amp Gain** box. Figure 3 shows the GUI after the Read Gain command was sent to amp 507007.

<p align="center">
    <img src=images/ampGUIreadgain.png>
    <figcaption><b>Figure 3: </b><b>AMP Gain</b> box shows the current gain range of 5 for Gentec-EO SDX-1153 sn 507007.</figcaption>
</p>


If setting the gain, select the **Set Gain** command and use the **Set Gain input box** to select the gain range. Then click the **Send Command** button. The new gain range will be displayed in the **Amp Gain** box. Setting the gain range of amp 507007 to 6 is shown in Figure 4.

<p align="center">
    <img src=images/ampGUIsetgain.png>
    <figcaption><b>Figure 4: </b><b>AMP Gain</b> box shows the current gain range of 6 for Gentec-EO SDX-1153 sn 507007.</figcaption>
</p>


To reset an amplifier to the "power on" state, select **Amp Init**, then click the **Send Command** button. If the reinit is sucessful, a message "serial# Amplifier Reinitialized" will be shown in the **Amp Reinitialized** box.
Note: This is not typically needed since the reinit process is run during the scanning process when an SDX-1153 or SDX-1226 is found. Figure 5 shows the GUI after the **Amp Init** command is sent.

<p align="center">
    <img src=images/ampGUIampinit.png>
    <figcaption><b>Figure 5: </b><b>AMP Reinitialized</b> box shows the amp sn (507007) and the text "Amplifier Reinitialized".</figcaption>
</p>


To quit the program and exit the GUI, click on the **Main** menu item in the top left of the GUI window, then select **Quit** from the dropdown list. This is shown in Figure 6.

<p align="center">
    <img src=images/ampGUIquit.png>
    <figcaption><b>Figure 6: </b>Quitting the program.</figcaption>
</p>


The the **Main** menu item also has selections for **Help** and **About**. See Figure 7. **Help** will give a short list of typical operations. **About** displays basic information about this program.

<p align="center">
    <img src=images/ampGUImenu.png>
    <figcaption><b>Figure 7: </b>Selecting <b>Help</b> will show typical operation steps. <b>About</b> will show information about this program.</figcaption>
</p>

### How to launch GUI with Python script <a class="anchor" id=how-to-launch-gui-with-python-script></a>
With `src` as the root folder in a terminal and gentec_SDX1153 as the active environment, use `python Gentec_SDX1153_GUI.py` to launch the GUI.

### How to import and use library (no GUI) <a class="anchor" id=how-to-import-and-use-library-no-gui></a>
With `src` as the root folder, use `import gentec.gentec1153utils`. Inside this module is the Gentec instrument library, _SDX1153_, and _ScanSerialPorts_ function which tries to connect to each serial port and test if the device is a Gentec E-O SDX-1153 or SDX-1226 amplifier. The _ScanSerialPorts_ function returns a dictionary, **ampDict**, with either the amplifiers found listed by serial number (dictionary key) or an empty dictionary if no amps are found. The dictionary contains the com port, amp ID information (manufacturer, model, serial number, and firmware version), and amp serial interface (see the class _SDX1153_ in the Gentec instrument library).

An example program, `Gentec_SDX1153.py`, illustrates how the _ScanSerialPorts_ function and the Gentec instrument library is used.

 ## General guidance for amplifier operation <a class="anchor" id=general-guidance-for-amplifier-operation></a>
This program works with Gentec-EO SDX-1153 and SDX-1226 devices. The devices come from the factory without the manufacturer or serial number programed into the units. Use the _Set_Mfg_ and _Set_SN_ functions to program the manufacturer and serial number of a new amplifer. This only needs to be done once. These functions are not available with the GUI.

In manual mode the amplifier puts the current gain and resistance in the output buffer and "Auto Gain" when switched to REMOTE. If you switch the gain manually several times there will be a gain and resistance for every switch,  so clear the buffer first before reading the gain. The functions in the library are written to handle this situation.