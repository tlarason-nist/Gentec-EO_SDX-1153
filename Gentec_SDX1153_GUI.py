import sys
import os
from gentec.gentec1153utils import ScanSerialPorts
from GUI_SDX1153.compiled_SDX1153 import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui


class SDX1153GUI(QtWidgets.QMainWindow):
    """
    Object for GUI interacting with Gentec_EO SDX-1153 and SDX-1226 current-to-voltage converters (amplifiers).
    Contains commonly used commands, e.g. get instrument ID, setting/reading gain range, etc.

    Note: in manual mode the amp puts the current gain and resistance in the output buffer and "Auto Gain" when switched to REMOTE.
    If you switch the gain manually several times there will be a gain and resistance for every switch,
    so the buffer is cleared first before reading the gain.
    """

    def __init__(self):
        super().__init__()
        self.ampDict = {}
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.closeEvent = self.quit
        self.ui.actionQuit.triggered.connect(self.quit)
        self.ui.actionHelp.triggered.connect(self.help)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.scanButton.clicked.connect(self.scan)
        self.ui.sendButton.clicked.connect(self.send)
        self.ui.connectedAmps.itemClicked.connect(self.ampID)

        self.IssuesMsgBox = QtWidgets.QMessageBox()
        self.IssuesMsgBox.setIcon(QtWidgets.QMessageBox.Critical)
        self.IssuesMsgBox.setWindowTitle("COM port error.")
        self.IssuesMsgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.infoMsgBox = QtWidgets.QMessageBox()
        self.infoMsgBox.setIcon(QtWidgets.QMessageBox.NoIcon)
        self.infoMsgBox.setWindowTitle("Information")
        self.infoMsgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        iconPath = scriptDir + os.path.sep + "/icons/amp_icon_301.png"
        self.setWindowIcon(QtGui.QIcon(iconPath))

    def quit(self, *args):  # BUG: runs twice if quit is selected from menu.
        """Stop GUI program execution. Also, closes any open amplifier comm ports."""
        print("quit")
        # Make sure comm ports are closed.
        if bool(self.ampDict):
            # Closes without error if Quit selected before scanning ports.
            for guiCOM_sn in list(self.ampDict.keys()):
                print("Close amp " + str(guiCOM_sn) + " port")
                self.ampDict[guiCOM_sn]["Amp Serial Interface"].Close()
        self.close()

    def help(self):
        print("help")  # Display Help window.
        helpText = "1. Click 'Scan'. (All SDX-1153/1226 amps found will be listed in 'Connected Amplifiers'.)\n2. Select amplifier command.\n3. Click 'Send Command'.\n4. Click on amplifier SN in 'Connected Amplifiers' to see amp ID information."
        self.infoMsgBox.setText(helpText)
        self.infoMsgBox.show()

    def about(self):
        print("about")  # Display About window.
        aboutText = "This program was developed by the National Institute of Standards and Technology (NIST) to control the gain range of Gentec-EO SDX-1153/1226 amplifiers.\n\nThe source code for this program, including documentation, is located at https://github.com/tlarason-nist/Gentec-EO_SDX-1153.git. \n\nTo get help or suggest feedback, send an email to thomas.larason@nist.gov."
        self.infoMsgBox.setText(aboutText)
        self.infoMsgBox.show()

    def scan(self):
        """Clear UI inputs, scan serial ports and build dictionary of SDX-1153/1226 amplifiers."""
        self.ui.connectedAmps.clear()
        self.ui.selectAmp.clear()
        print("scan ports")
        self.ampDict = ScanSerialPorts()
        self.ui.connectedAmps.addItems(list(self.ampDict.keys()))
        self.ui.selectAmp.addItems(list(self.ampDict.keys()))

    def send(self):
        """Send the selected command to the selected amplifier."""
        if bool(self.ampDict):  # Check if port scan and been done (ampDict not empty)
            print("send command")
            guiampIndex = self.ui.selectAmp.currentIndex()
            guiampText = self.ui.selectAmp.currentText()
            if guiampIndex == -1:
                print("No amplifiers have been found.")
            # print(guiampIndex, guiampText)  # for testing
            self.ampDict[guiampText]["Amp Serial Interface"].Amp_Connect()
            self.ampDict[guiampText]["Amp Serial Interface"].Amp_Default()
            guiampCommand = self.ui.commandsBox.currentText()  # Get command text
            print(guiampCommand)
            if "Read Gain" in guiampCommand:
                amp_response = self.ampDict[guiampText][
                    "Amp Serial Interface"
                ].Read_Gain()
                print(amp_response)
                self.ui.ampGain.clear()
                self.ui.ampGain.insert(str(amp_response))
            elif "Set Gain" in guiampCommand:
                gain_range = self.ui.setGain.value()
                amp_response = self.ampDict[guiampText][
                    "Amp Serial Interface"
                ].Set_Gain(int(gain_range))
                # Read amp gain after setting the gain to verify change.
                amp_response = self.ampDict[guiampText][
                    "Amp Serial Interface"
                ].Read_Gain()
                print(amp_response)
                self.ui.ampGain.clear()
                self.ui.ampGain.insert(str(amp_response))
            elif "Amp Init" in guiampCommand:
                amp_response = self.ampDict[guiampText][
                    "Amp Serial Interface"
                ].Amp_Init()
                print(guiampText + " " + amp_response)
                self.ui.ampInitmessage.clear()
                self.ui.ampInitmessage.setPlainText(
                    str(guiampText + " " + amp_response)
                )
            self.ampDict[guiampText]["Amp Serial Interface"].Close()
        else:
            self.IssuesMsgBox.setText("Select Scan first.")
            self.IssuesMsgBox.show()

    def ampID(self):
        """Look up Amp ID information from ampDict using 'Connected Amplifiers' control on GUI to select the amplifier."""
        guiampText2 = self.ui.connectedAmps.currentItem().text()
        print(guiampText2)
        ampID = self.ampDict[guiampText2]["Amp ID Information"].split("\n")[0:4]
        print(ampID)
        self.ui.ampIDinfo.clear()
        self.ui.ampIDinfo.addItems(ampID)

    # Connect to all the amplifiers found in scan (ampDict.keys). Not used.
    # Not used because of complications with possibly trying to open connections twice.
    def connect_all(self):
        """Connect to ALL the amplifiers found and listed in the ampDict."""
        for guiCOM_sn in list(self.ampDict.keys()):  # Connecting by amp sn.
            self.ampDict[guiCOM_sn]["Amp Serial Interface"].Amp_Connect()


# Code needed to start GUI execution.
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SDX1153GUI()
    window.show()
    app.exec()
