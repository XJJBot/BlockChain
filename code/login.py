import os,sys,json,glob
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox,QMainWindow, QTableWidgetItem

class Ui_login(object):
    def setupUi(self, login):
        login.setObjectName("login")
        login.resize(400, 300)
        self.pushButton_signup = QtWidgets.QPushButton(login)
        self.pushButton_signup.setGeometry(QtCore.QRect(230, 200, 93, 28))
        self.pushButton_signup.setObjectName("pushButton_signup")
        self.pushButton_signin = QtWidgets.QPushButton(login)
        self.pushButton_signin.setGeometry(QtCore.QRect(90, 200, 93, 28))
        self.pushButton_signin.setObjectName("pushButton_signin")
        self.lineEdit_name = QtWidgets.QLineEdit(login)
        self.lineEdit_name.setGeometry(QtCore.QRect(180, 80, 113, 21))
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.lineEdit_pwd = QtWidgets.QLineEdit(login)
        self.lineEdit_pwd.setGeometry(QtCore.QRect(180, 120, 113, 21))
        self.lineEdit_pwd.setObjectName("lineEdit_pwd")
        self.label_name = QtWidgets.QLabel(login)
        self.label_name.setGeometry(QtCore.QRect(110, 80, 72, 15))
        self.label_name.setObjectName("label_name")
        self.label_pwd = QtWidgets.QLabel(login)
        self.label_pwd.setGeometry(QtCore.QRect(100, 120, 72, 15))
        self.label_pwd.setObjectName("label_pwd")

        self.retranslateUi(login)
        QtCore.QMetaObject.connectSlotsByName(login)

    def retranslateUi(self, login):
        _translate = QtCore.QCoreApplication.translate
        login.setWindowTitle(_translate("login", "Form"))
        self.pushButton_signup.setText(_translate("login", "sign up"))
        self.pushButton_signin.setText(_translate("login", "sign in"))
        self.label_name.setText(_translate("login", "name"))
        self.label_pwd.setText(_translate("login", "password"))



class login(QMainWindow, Ui_login):
    def __init__(self):
        super(login, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("login")
        self.pushButton_signin.clicked.connect(self.signin_clicked)
        self.pushButton_signup.clicked.connect(self.signup_clicked)

    def signin_clicked(self):
        name = self.lineEdit_name.text()
        password = self.lineEdit_pwd.text()
        print(name)
        print(password)

    def signup_clicked(self):
        pass
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = login()
    login_window.show()
    app.exec_()
