# -*- coding: utf-8 -*-
import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
import json
import qtui
import reservation_core
import urllib
import atexit
import os

class Main(QMainWindow, qtui.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        QFontDatabase.addApplicationFont(".\data\BKOODB.TTF")

        self.tabWidget.setCurrentIndex(0)  # set the main tab to main page
        self.TABnewList.setCurrentIndex(0)
        self.CHKBXthis.setChecked(True)
        self.CHKBXnext.setChecked(True)
        self.fill_forms()  # get the list from json file and fill the uis list widget
        self.fill_list_of_listname()
        # add functionality to move left, right ,down,up buttons
        #########################################################
        self.BTNmvRBreak.clicked.connect(self.move_right)
        self.BTNmvRLunch.clicked.connect(self.move_right)
        self.BTNmvRDinner.clicked.connect(self.move_right)

        self.BTNmvLBreak.clicked.connect(self.move_left)
        self.BTNmvLLunch.clicked.connect(self.move_left)
        self.BTNmvLDinner.clicked.connect(self.move_left)

        self.BTNmvUBreak.clicked.connect(self.move_up)
        self.BTNmvULunch.clicked.connect(self.move_up)
        self.BTNmvUDinner.clicked.connect(self.move_up)

        self.BTNmvDBreak.clicked.connect(self.move_down)
        self.BTNmvDLunch.clicked.connect(self.move_down)
        self.BTNmvDDinner.clicked.connect(self.move_down)
        #########################################################

        self.BTNreserv.clicked.connect(self.reserve)
        self.BTNsaveList.clicked.connect(self.saveList)
        self.BTNsaveList.setEnabled(False)  #remove after fixing ui
        self.BTNreserv.setEnabled(False)  #remove after fixing ui

        self.CMBXlists.currentIndexChanged.connect(self.check_btnreserv)
        self.LNEDTusername.textChanged.connect(self.check_btnreserv)
        self.LNEDTpassword.textChanged.connect(self.check_btnreserv)
        self.CHKBXthis.stateChanged.connect(self.check_btnreserv)
        self.CHKBXnext.stateChanged.connect(self.check_btnreserv)


        self.CHKBXshowPassword.stateChanged.connect(self.show_password)


        self.LNEDTlistName.textChanged.connect(self.check_btnsaveList)

        self.CMBXeditLists.currentIndexChanged.connect(self.loadTheList)

        self.BTNrmvlst.clicked.connect(self.removee_list)
        self.BTNupdate.clicked.connect(self.update_formdata)
        self.threadlist={}



    #
    # def qstring_to_string(self,qstring):
    #     return unicode(qstring.toUtf8(), encoding="UTF-8")
    def update_formdata(self):
        question =u"برای انجام این کار برنامه نیاز به ریستارت دارد\nآیا موافقید؟"
        flags = QMessageBox.Yes
        flags |= QMessageBox.No
        response = QMessageBox.question(self, "Question",
                                              question,
                                              flags)
        if response == QMessageBox.Yes:
            try:
                url = "https://www.dropbox.com/s/cqgbwsxgkgw1ey5/_formdata?dl=1"
                urllib.urlretrieve (url, "_formdata")
                json_file = open('_formdata', 'r')
                json_decoded = json.load(json_file)
                user_list_version = json_decoded['version']  # export foods
                if(user_list_version != self.form_data_version):
                    atexit.register(os.execl, "update.bat", "update.bat")
                    sys.exit()
                else:
                    self.showInfoMessage(u"بروز رسانی",u"شما قبلا آخرین نسخه را دارید.")
            except Exception as e :
                print e
                self.show_error_message(u"خطای بروزرسانی",u"بروز رسانی ناموفق بعدا امتحان کنید")

    def show_password(self):
        if self.CHKBXshowPassword.checkState():
            self.LNEDTpassword.setEchoMode(QLineEdit.Normal)
        else:
            self.LNEDTpassword.setEchoMode(QLineEdit.Password)
    def show_error_message(self,title,bodyText):
        QMessageBox.critical(self,title,bodyText)
    def log(self,text):
        self.QPTXTEDTlogs.appendPlainText(text)
    def showInfoMessage(self,title,bodyText):
        QMessageBox.information(self,title,bodyText)
        #self.

    def fill_list_of_listname(self):
        datas_file = open('./data/_lisnamedata')
        datas_decoded = json.load(datas_file)
        listNames = datas_decoded["listNames"]
        self.CMBXlists.clear()
        self.CMBXeditLists.clear()
        self.CMBXlists.addItems(listNames)
        self.CMBXeditLists.addItems(listNames)

    def check_btnsaveList(self, text):
        if text:
            self.BTNsaveList.setEnabled(True)
        else:
            self.BTNsaveList.setEnabled(False)

    def check_btnreserv(self):
        if self.CMBXlists.currentText() and self.LNEDTpassword.text() and self.LNEDTusername.text():
            if (self.CHKBXnext.checkState() or self.CHKBXthis.checkState()):
                self.BTNreserv.setEnabled(True)
            else:
                self.BTNreserv.setEnabled(False)
        else:
            self.BTNreserv.setEnabled(False)

    def clear_food_restaurant(self):
        self.LSTWGallBreak.clear()
        self.LSTWGallLunch.clear()
        self.LSTWGallDinner.clear()

        self.LSTWGselectedBreak.clear()
        self.LSTWGselectedLunch.clear()
        self.LSTWGselectedDinner.clear()
    def load_data_file_to_obj(self):
        foodsFile = open("./data/_formdata", "r")
        datasEncoded = json.load(foodsFile)
        foodsFile.close()
        # get the each meals food
        self.breakfastFoods = datasEncoded["breakfastFoods"]
        self.lunchFoods = datasEncoded['lunchFoods']
        self.dinnerFoods = datasEncoded['dinnerFoods']
        self.restaurants = datasEncoded["restaurants"]
        self.restMapping = datasEncoded['restMapping']
        self.form_data_version = datasEncoded['version']
        # print self.form_data_version

    def fill_forms(self):
        self.load_data_file_to_obj()
        self.clear_food_restaurant()

        self.LSTWGallBreak.addItems(self.breakfastFoods.keys())
        self.LSTWGallLunch.addItems(self.lunchFoods.keys())
        self.LSTWGallDinner.addItems(self.dinnerFoods.keys())

        allRestObjects = [[self.CMBbreak0, self.CMBlunch0, self.CMBdinner0],
                          [self.CMBbreak1, self.CMBlunch1, self.CMBdinner1],
                          [self.CMBbreak2, self.CMBlunch2, self.CMBdinner2],
                          [self.CMBbreak3, self.CMBlunch3, self.CMBdinner3],
                          [self.CMBbreak4, self.CMBlunch4, self.CMBdinner4],
                          [self.CMBbreak5, self.CMBlunch5, self.CMBdinner5],
                          [self.CMBbreak6, self.CMBlunch6, self.CMBdinner6]]
        for thisDayRests in allRestObjects:
            for rest in thisDayRests:
                rest.clear()
                rest.addItems(self.restaurants)

    def show_question(self):
        """
        Show the question message
        """
        question=u"فهرست غذا ها و رستوران ها تغییر کرده است\n و با لیست انتخابی شما همخوانی ندارد\n ایا می خواهید لیست را حذف کنید؟"
        flags = QMessageBox.Yes
        flags |= QMessageBox.No
        response = QMessageBox.question(self, "Question",
                                              question,
                                              flags)
        if response == QMessageBox.Yes:
            self.removee_list()
        elif response== QMessageBox.No:
            self.CMBXeditLists.setCurrentIndex(0)
    def loadTheList(self):
        self.clear_food_restaurant()
        nameOfList=self.CMBXeditLists.currentText()
        currentIndex = self.CMBXeditLists.currentIndex()
        self.CMBXlists.setCurrentIndex(currentIndex)
        if nameOfList == "":
            self.fill_forms()
            return
        listFile = open("./foodlists/"+nameOfList+'.json', "r")
        datasEncoded = json.load(listFile)
        listFile.close()
        #check version
        user_list_version = datasEncoded["version"]
        if(user_list_version != self.form_data_version):

            self.show_question()
            return
        # get the each meals food
        breakfastFoods = datasEncoded["foods"][0]
        lunchFoods = datasEncoded['foods'][1]
        dinnerFoods = datasEncoded['foods'][2]
        restsOfEachDay=datasEncoded['restsOfEachDay']
        restaurants=[dic['rests'] for dic in restsOfEachDay]

        breakAll,breakSelected = self.getStringOf(self.breakfastFoods,breakfastFoods)
        lunchAll,lunchSelected = self.getStringOf(self.lunchFoods,lunchFoods)
        dinnerAll , dinnerSelected = self.getStringOf(self.dinnerFoods,dinnerFoods)



        self.LSTWGallBreak.addItems(breakAll)
        self.LSTWGallLunch.addItems(lunchAll)
        self.LSTWGallDinner.addItems(dinnerAll)

        # for food in dinnerSelected:
        #     self.LSTWGselectedDinner.addItem(food)

        self.LSTWGselectedBreak.addItems(breakSelected)
        self.LSTWGselectedLunch.addItems(lunchSelected)
        self.LSTWGselectedDinner.addItems(dinnerSelected)

        allRestObjects = [[self.CMBbreak0, self.CMBlunch0, self.CMBdinner0],
                          [self.CMBbreak1, self.CMBlunch1, self.CMBdinner1],
                          [self.CMBbreak2, self.CMBlunch2, self.CMBdinner2],
                          [self.CMBbreak3, self.CMBlunch3, self.CMBdinner3],
                          [self.CMBbreak4, self.CMBlunch4, self.CMBdinner4],
                          [self.CMBbreak5, self.CMBlunch5, self.CMBdinner5],
                          [self.CMBbreak6, self.CMBlunch6, self.CMBdinner6]]

        for thisDayRests, thisDaySelectedRest  in zip(allRestObjects,restaurants):
            for rest, selectedRest in zip(thisDayRests,thisDaySelectedRest):
                rest.setCurrentIndex(self.restMapping.index(selectedRest))

    def getStringOf(self,dicOfItems,valueOfitems):
        copyOfDicItems = dicOfItems.copy()
        selected=[]
        all=[]

        for theValue in valueOfitems:
            for theKey in copyOfDicItems.keys():
                if theValue in copyOfDicItems[theKey]:
                    selected.append(theKey)
                    del copyOfDicItems[theKey]
                    break

        all=copyOfDicItems.keys()

        return (all,selected)
    def move_right(self):
        listsDic = {"BTNmvRBreak": (self.LSTWGallBreak, self.LSTWGselectedBreak),
                    "BTNmvRLunch": (self.LSTWGallLunch, self.LSTWGselectedLunch),
                    "BTNmvRDinner": (self.LSTWGallDinner, self.LSTWGselectedDinner)}
        # detect to move from which list
        sender_button = self.sender().objectName()
        lstWgtOfAll = listsDic[sender_button][0]
        lsWgtOfSelect = listsDic[sender_button][1]

        selectedItems = lstWgtOfAll.selectedItems()
        for item in selectedItems:
            row = lstWgtOfAll.row(item)
            lsWgtOfSelect.addItem(lstWgtOfAll.takeItem(row))

    def move_left(self):
        listsDic = {"BTNmvLBreak": (self.LSTWGallBreak, self.LSTWGselectedBreak),
                    "BTNmvLLunch": (self.LSTWGallLunch, self.LSTWGselectedLunch),
                    "BTNmvLDinner": (self.LSTWGallDinner, self.LSTWGselectedDinner)}
        sender_button = self.sender().objectName()
        lstWgtOfAll = listsDic[sender_button][0]
        lsWgtOfSelect = listsDic[sender_button][1]

        selectedItems = lsWgtOfSelect.selectedItems()
        for item in selectedItems:
            row = lsWgtOfSelect.row(item)
            lstWgtOfAll.addItem(lsWgtOfSelect.takeItem(row))


    def move_up(self):
        listsDic = {"BTNmvUBreak": self.LSTWGselectedBreak,
                    "BTNmvULunch": self.LSTWGselectedLunch,
                    "BTNmvUDinner": self.LSTWGselectedDinner}
        sender_button = self.sender().objectName()
        lisWgOfSelect = listsDic[sender_button]

        length = lisWgOfSelect.count()
        self.currentRow = lisWgOfSelect.currentRow()

        if self.currentRow > 0:
            currentItem = lisWgOfSelect.takeItem(self.currentRow)
            lisWgOfSelect.insertItem(self.currentRow - 1, currentItem)
            lisWgOfSelect.setCurrentRow(self.currentRow - 1)


    def move_down(self):
        listsDic = {"BTNmvDBreak": self.LSTWGselectedBreak,
                    "BTNmvDLunch": self.LSTWGselectedLunch,
                    "BTNmvDDinner": self.LSTWGselectedDinner}
        sender_button = self.sender().objectName()
        lisWgOfSelect = listsDic[sender_button]

        length = lisWgOfSelect.count()
        self.currentRow = lisWgOfSelect.currentRow()

        if self.currentRow < length - 1:
            currentItem = lisWgOfSelect.takeItem(self.currentRow)
            lisWgOfSelect.insertItem(self.currentRow + 1, currentItem)
            lisWgOfSelect.setCurrentRow(self.currentRow + 1)


    def reserve(self):
        weeks_to_reserve=[]
        if self.CHKBXthis.checkState():
            weeks_to_reserve.append("this")
        if self.CHKBXnext.checkState():
            weeks_to_reserve.append("next")

        username = self.LNEDTusername.text()
        if username not in self.threadlist:
            self.workerThread = reservation_core.WorkerThread(username=self.LNEDTusername.text()
                                                             , password=self.LNEDTpassword.text()
                                                             , nameOfList=self.CMBXlists.currentText() + '.json'
                                                             ,weeksToReserve = weeks_to_reserve
                                                             ,form_data_version=self.form_data_version)


            self.threadlist[username]= self.workerThread        #prevent from
            self.workerThread.start()
        else:
            self.showInfoMessage(u"ارور",u" درحال رزرو برای " + username)
            return


        self.connect(self.workerThread,SIGNAL("Error(QString,QString)"),self.show_error_message)
        self.connect(self.workerThread,SIGNAL("reservation(QString,QString)"),self.showInfoMessage)
        self.connect(self.workerThread,SIGNAL("log(QString)"),self.log)
        self.connect(self.workerThread,SIGNAL("removeThread(QString)"),self.removeThredRef)
        self.connect(self.workerThread,SIGNAL("showQuestion()"),self.show_question)


    def removeThredRef(self,username):
        del self.threadlist[username]

    def saveList(self):
        nameOfList = self.LNEDTlistName.text()
        restsOfEachDay = self.collect_restaurants()
        foods = self.collect_foods()
        pyJson = {}
        pyJson["version"]=self.form_data_version
        pyJson["restsOfEachDay"] = restsOfEachDay
        pyJson["foods"] = foods
        # write json file
        json_file = json.dumps(pyJson)
        file = open('./foodlists/' + nameOfList + '.json', 'w')
        file.write(json_file)  #write database to file
        file.close()

        json_file = open('./foodlists/' + nameOfList + ".json", "r")
        json_decoded = json.load(json_file)
        json_file.close()

        datas_file = open('./data/_lisnamedata', "r+")
        datas_decoded = json.load(datas_file)
        if nameOfList.upper() not in (name.upper() for name in datas_decoded["listNames"]):
            datas_decoded["listNames"].append(nameOfList)
            # self.CMBXlists.addItem(nameOfList)
            # self.CMBXeditLists.addItem(nameOfList)

        datas_file.seek(0, 0)  #go to begining of file
        datas_file.write(json.dumps(datas_decoded))
        datas_file.close()
        self.fill_list_of_listname()
        self.showInfoMessage(u" لیست جدید",nameOfList+u" ذخیره شد ")
    def removee_list(self):
        list_name = self.CMBXlists.currentText()
        if(list_name == ""):
            return
        current_index = self.CMBXeditLists.currentIndex()
        in_cmbxlists = self.CMBXlists.findText(list_name)

        datas_file = open('./data/_lisnamedata', "r")
        datas_decoded = json.load(datas_file)
        datas_decoded["listNames"].remove(list_name)
        datas_file.close();
        datas_file = open('./data/_lisnamedata', "w")
        datas_file.write(json.dumps(datas_decoded))
        datas_file.close()
        self.fill_list_of_listname()
        # self.CMBXeditLists.removeItem(current_index)
        # self.CMBXlists.removeItem(in_cmbxlists)

    def collect_restaurants(self):
        allRestObjects = [[self.CMBbreak0, self.CMBlunch0, self.CMBdinner0],
                          [self.CMBbreak1, self.CMBlunch1, self.CMBdinner1],
                          [self.CMBbreak2, self.CMBlunch2, self.CMBdinner2],
                          [self.CMBbreak3, self.CMBlunch3, self.CMBdinner3],
                          [self.CMBbreak4, self.CMBlunch4, self.CMBdinner4],
                          [self.CMBbreak5, self.CMBlunch5, self.CMBdinner5],
                          [self.CMBbreak6, self.CMBlunch6, self.CMBdinner6]]

        restsOfWeek = []
        day = 0
        for thisDaysRests in allRestObjects:
            myObj = {}
            todaySelectedRests = []

            for rest in thisDaysRests:
                todaySelectedRests.append(self.restMapping[rest.currentIndex()])
            myObj["rests"] = todaySelectedRests
            myObj["day"] = day
            day += 1
            restsOfWeek.append(myObj)
        return restsOfWeek

    def collect_foods(self):
        breakFastSelected = []
        lunchSelected = []
        dinnerSelected = []

        for i in range(self.LSTWGselectedBreak.count()):
            breakFastSelected.extend(self.breakfastFoods[self.LSTWGselectedBreak.item(i).text()])
        for i in range(self.LSTWGselectedLunch.count()):
            lunchSelected.extend(self.lunchFoods[self.LSTWGselectedLunch.item(i).text()])
        for i in range(self.LSTWGselectedDinner.count()):
            dinnerSelected.extend(self.dinnerFoods[self.LSTWGselectedDinner.item(i).text()])

        foods = []
        foods.append(breakFastSelected)
        foods.append(lunchSelected)
        foods.append(dinnerSelected)

        return foods


app = QApplication(sys.argv)
mainWindow = Main()
mainWindow.show()
app.exec_()