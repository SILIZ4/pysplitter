from PyQt5 import QtWidgets
qmessage = QtWidgets.QMessageBox


def display_error_dialog(message):
    error_dialog = QtWidgets.QMessageBox()
    error_dialog.setWindowTitle("PySplitter Error")
    error_dialog.setText(message)
    error_dialog.exec_()


def ask_yes_no_dialog(parent, message) -> bool:
    return qmessage.question(
            parent, '', message, qmessage.Yes | qmessage.No
        ) == qmessage.Yes
