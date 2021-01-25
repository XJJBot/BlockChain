#!/usr/bin/env python
# -*- coding: utf-8 -*-
from login import Ui_login
from signup import Ui_signup
from company import Ui_company
from company_sign import Ui_company_sign
from company_transfer import Ui_company_transfer
from company_finance import Ui_company_finance
from bank import Ui_bank
import os
import sys
import csv
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox,QMainWindow, QTableWidgetItem
from client.contractnote import ContractNote
from client.bcosclient import BcosClient
from client.datatype_parser import DatatypeParser
from client.common.compiler import Compiler
from client.bcoserror import BcosException, BcosError
from client_config import client_config
from eth_utils import to_checksum_address
from eth_utils.hexadecimal import encode_hex
from eth_account.account import Account

client = BcosClient()
# 从文件加载abi定义
abi_file  = "contracts/Account.abi"
data_parser = DatatypeParser()
data_parser.load_abi_file(abi_file)
contract_abi = data_parser.contract_abi
address = '7faff65df217dee1b056d50b27c741a2bbfa2e53'
cur_user = ''

def hex_to_signed(source):
    if not isinstance(source, str):
        raise ValueError("string type required")
    if 0 == len(source):
        raise ValueError("string is empty")
    source = source[2:]
    sign_bit_mask = 1 << (len(source)*4-1)
    other_bits_mask = sign_bit_mask - 1
    value = int(source, 16)
    return -(value & sign_bit_mask) | (value & other_bits_mask)

class login(QMainWindow, Ui_login):
    def __init__(self):
        super(login, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("login")
        self.pushButton_signin.clicked.connect(self.signin_clicked)
        self.pushButton_signup.clicked.connect(self.signup_clicked)

    def signin_clicked(self):
        global cur_user
        cinfo_list = []
        with open('comp_info.csv', 'r', encoding = 'utf-8') as f:
            csv_file = csv.reader(f)
            for item in csv_file:
                cinfo_list.append(item)

        name = self.lineEdit_name.text()
        password = self.lineEdit_pwd.text()
        args = [name]
        ret_tuple = client.call(address, contract_abi, "select_company", args)
        if [name, password] in cinfo_list and ret_tuple[0] == 1:
            cur_user = name
            if name == 'bank':
                bank_window.show()
                bank_window.refresh()
            else:
                company_window.show()
                company_window.refresh()
        else:
            QMessageBox.information(self,'Hint','Wrong user name or password!', QMessageBox.Ok)

    def signup_clicked(self):
        signup_window.show()
        
class signup(QMainWindow, Ui_signup):
    def __init__(self):
        super(signup, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("sign up")
        self.pushButton_signup.clicked.connect(self.signup_clicked)
        self.pushButton_cancel.clicked.connect(self.close)

    def signup_clicked(self):
        name = self.lineEdit_name.text()
        pwd = self.lineEdit_pwd.text()
        args = [name]
        receipt = client.sendRawTransactionGetReceipt(address, contract_abi, "insert_company", args)
        if hex_to_signed(receipt['output']) == 0:
            QMessageBox.information(self,'Error','This company is existed', QMessageBox.Ok)
        elif hex_to_signed(receipt['output']) == 1:
            with open('comp_info.csv', 'a', encoding = 'utf-8') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow([name, pwd])
            QMessageBox.information(self,'Hint','Successfully sign up!', QMessageBox.Ok)
            self.close()
        
class bank(QMainWindow, Ui_bank):
    def __init__(self):
        super(bank, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("bank")
        self.pushButton_confirm.clicked.connect(self.confirm_clicked)
        self.pushButton_refuse.clicked.connect(self.refuse_clicked)
        self.pushButton.clicked.connect(self.refresh)

    def refresh(self):
        global cur_user
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(i)
        self.tableWidget.setRowCount(0)
        args = [cur_user, 1]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))
        args = [cur_user, 2]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))

    def confirm_clicked(self):
        if self.tableWidget.selectionModel().hasSelection():
            QMessageBox.information(self,'Hint','Confirm successfully!', QMessageBox.Ok)
        else:
            QMessageBox.information(self,'Hint','Please select a receipt.', QMessageBox.Ok)
        self.refresh()

    def refuse_clicked(self):
        if self.tableWidget.selectionModel().hasSelection():
            row = self.tableWidget.currentRow()
            from_ = self.tableWidget.item(row, 0).text()
            to = self.tableWidget.item(row, 1).text()
            tot_amount = self.tableWidget.item(row, 2).text()
            cur_amount = self.tableWidget.item(row, 3).text()
            deadline = self.tableWidget.item(row, 4).text()
            args = [from_, to, int(tot_amount), int(cur_amount), deadline]
            receipt = client.sendRawTransactionGetReceipt(address, contract_abi, "remove", args)
            QMessageBox.information(self,'Hint','Refuse successfully!', QMessageBox.Ok)
        else:
            QMessageBox.information(self,'Hint','Please select a receipt.', QMessageBox.Ok)
        self.refresh()
        

class company(QMainWindow, Ui_company):
    def __init__(self):
        super(company, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("company")
        self.pushButton_sign.clicked.connect(self.sign_clicked)
        self.pushButton_transfer.clicked.connect(self.transfer_clicked)
        self.pushButton_finance.clicked.connect(self.finance_clicked)
        self.pushButton_pay.clicked.connect(self.pay_clicked)
        self.pushButton.clicked.connect(self.refresh)
        self.refresh()

    def refresh(self):
        global cur_user
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(i)
        self.tableWidget.setRowCount(0)
        args = [cur_user, 1]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))
        args = [cur_user, 2]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))

    def sign_clicked(self):
        company_sign_window.show()
        company_sign_window.refresh()
        self.refresh()

    def transfer_clicked(self):
        company_transfer_window.show()
        company_transfer_window.refresh()
        self.refresh()

    def finance_clicked(self):
        company_finance_window.show()
        company_finance_window.refresh()

    def pay_clicked(self):
        if self.tableWidget.selectionModel().hasSelection():
            row = self.tableWidget.currentRow()
            from_ = self.tableWidget.item(row, 0).text()
            to = self.tableWidget.item(row, 1).text()
            tot_amount = self.tableWidget.item(row, 2).text()
            cur_amount = self.tableWidget.item(row, 3).text()
            deadline = self.tableWidget.item(row, 4).text()
            args = [from_, to, int(tot_amount), int(cur_amount), deadline]
            receipt = client.sendRawTransactionGetReceipt(address, contract_abi, "pay", args)
            QMessageBox.information(self,'Hint','Pay successfully!', QMessageBox.Ok)
        else:
            QMessageBox.information(self,'Hint','Please select a receipt.', QMessageBox.Ok)
        self.refresh()


class company_sign(QMainWindow, Ui_company_sign):
    def __init__(self):
        super(company_sign, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("company_sign")
        self.pushButton_sign.clicked.connect(self.sign_clicked)
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton.clicked.connect(self.refresh)

    def refresh(self):
        global cur_user
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(i)
        self.tableWidget.setRowCount(0)
        args = [cur_user, 1]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))
        args = [cur_user, 2]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))

    def sign_clicked(self):
        global cur_user
        to = self.lineEdit_to.text()
        amount = self.lineEdit_amount.text()
        deadline = self.dateEdit.date().toString('yyyy-MM-dd')
        args = [cur_user, to, int(amount), deadline]
        receipt = client.sendRawTransactionGetReceipt(address, contract_abi, 'sign', args)
        if hex_to_signed(receipt['output']) == 0:
            QMessageBox.information(self,'Error','Fail!', QMessageBox.Ok)
        else:
            QMessageBox.information(self,'Hint','Sign successfully!', QMessageBox.Ok)
        self.close()

class company_transfer(QMainWindow, Ui_company_transfer):
    def __init__(self):
        super(company_transfer, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("company_transfer")
        self.pushButton_transfer.clicked.connect(self.transfer_clicked)
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton.clicked.connect(self.refresh)

    def refresh(self):
        global cur_user
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(i)
        self.tableWidget.setRowCount(0)
        args = [cur_user, 1]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))
        args = [cur_user, 2]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))

    def transfer_clicked(self):
        from_ = self.lineEdit_from.text()
        to = self.lineEdit_to.text()
        tot_a = self.lineEdit_total_a.text()
        cur_a = self.lineEdit_cur_a.text()
        trans_a = self.lineEdit_trans_a.text()
        deadline = self.dateEdit.date().toString('yyyy-MM-dd')
        args = [from_, cur_user, to, int(tot_a), int(cur_a), int(trans_a), deadline]
        receipt = client.sendRawTransactionGetReceipt(address, contract_abi, 'transfer', args)
        if hex_to_signed(receipt['output']) == -1:
            QMessageBox.information(self,'Error','Fail!Transfer_amount is more than cur_amount.', QMessageBox.Ok)
        elif hex_to_signed(receipt['output']) == 0:
            QMessageBox.information(self,'Error','Fail!', QMessageBox.Ok)
        else:
            QMessageBox.information(self,'Hint','Transfer successfully!', QMessageBox.Ok)
        self.close()

class company_finance(QMainWindow, Ui_company_finance):
    def __init__(self):
        super(company_finance, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("company_finance")
        self.pushButton_apply.clicked.connect(self.apply_clicked)
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton.clicked.connect(self.refresh)

    def refresh(self):
        global cur_user
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(i)
        self.tableWidget.setRowCount(0)
        args = [cur_user, 1]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))
        args = [cur_user, 2]
        ret_tuple = client.call(address, contract_abi, "select", args)
        for i in range(len(ret_tuple[0])):
            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(ret_tuple[0][i]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(ret_tuple[1][i]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(ret_tuple[2][i])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(ret_tuple[3][i])))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(ret_tuple[4][i]))

    def apply_clicked(self):
        finance_amount = self.lineEdit.text()
        deadline = self.dateEdit.date().toString('yyyy-MM-dd')
        args = [cur_user, int(finance_amount), deadline]
        receipt = client.sendRawTransactionGetReceipt(address, contract_abi, 'finance', args)
        if hex_to_signed(receipt['output']) == 0:
            QMessageBox.information(self,'Error','Fail!', QMessageBox.Ok)
        else:
            QMessageBox.information(self,'Hint','Apply successfully!', QMessageBox.Ok)
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = login()
    signup_window = signup()
    bank_window = bank()
    company_window = company()
    company_sign_window = company_sign()
    company_transfer_window = company_transfer()
    company_finance_window = company_finance()
    login_window.show()
    app.exec_()
    client.finish()