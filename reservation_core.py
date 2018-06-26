# -*- coding: utf-8 -*-

from selenium import webdriver

driver = webdriver.PhantomJS(executable_path=".\phantomjs.exe")
import datetime
from splinter import Browser

import json
import jalali
from PyQt4.QtCore import *
import os, sys, subprocess


class WorkerThread(QThread):
    def __init__(self, nameOfList, username, password, weeksToReserve,form_data_version, parent=None):
        QThread.__init__(self, parent)

        self.username = username
        self.password = password
        self.nameOfList = nameOfList
        self.weeks_to_reserve = weeksToReserve
        self.form_data_version = form_data_version
        print form_data_version

        # self.reserve = Reserve()


        # QThread.__init__(self)

    def stop_thread(self):
        self.quit()

    def run(self):
        foods, rests_and_day_numbers_of_week ,user_list_version= self.decode_database(self.nameOfList)  # decode database
        # self.reserve.login(self.username,self.password)
        #check userlist version
        if user_list_version != self.form_data_version:
            print user_list_version
            self.emit(SIGNAL("showQuestion()"))
            self.emit(SIGNAL("removeThread(QString)"), self.username)
            return self.stop_thread()
        try:
            self.emit(SIGNAL("log(QString)"), self.username + u": رزرو شروع شد")
            # print self.username,": reservaion started"
            self.login(self.username, self.password)  # login to website

        except AttributeError:
            self.emit(SIGNAL("Error(QString,QString)"), u"خطای ورود",
                      u"نام کاربری یا پسورد شما اشتباه است :" + self.username)
            self.emit(SIGNAL("log(QString)"), self.username + ":" + u" رزرو ناموفق- نام کاربری یا پسورد شما اشتباه است")

            self.emit(SIGNAL("removeThread(QString)"), self.username)
            return self.stop_thread()
        except Exception as e:
            self.emit(SIGNAL("Error(QString,QString)"), u"خطا", u"متاسفانه خطایی رخ داد ")
            # print e

            self.emit(SIGNAL("removeThread(QString)"), self.username)
            return self.stop_thread()

        this_week_available_days, next_week_available_days = self.collect_available_days()  # find the available days


        if "this" in self.weeks_to_reserve:
            if this_week_available_days :
                self.reserve_for_a_week(rests_and_day_numbers_of_week=rests_and_day_numbers_of_week,
                                available_days=this_week_available_days, foods=foods)

        if "next" in self.weeks_to_reserve:
            if next_week_available_days:
                self.reserve_for_a_week(rests_and_day_numbers_of_week=rests_and_day_numbers_of_week,
                                available_days=next_week_available_days, foods=foods)
            else:
                self.emit(SIGNAL("log(QString)"), self.username + ":" + '\n' + u" رزرو برای هفته ی بعد هنوز باز نشده است بعدا امتحان کنید ")





        self.take_screenshot(self.username, self.nameOfList)
        self.open_screenshot(self.username, self.nameOfList)
        self.emit(SIGNAL("reservation(QString,QString)"), u"انجام شد", u"رزرو برای  " + self.username + u" انجام شد ")
        self.emit(SIGNAL("removeThread(QString)"), self.username)
        self.emit(SIGNAL("log(QString)"), u" رزرو برای " + self.username + u" انجام شد ")

    def reserve_for_a_week(self, rests_and_day_numbers_of_week, available_days, foods):
        day_mapping = [u"شنبه", u"1شنبه", u"2شنبه", u"3شنبه", u"4شنبه", u"5شنبه", u"جمعه"]
        meal_mapping = [u"صبحانه", u"ناهار", u"شام"]
        # reserv for a week
        for rests_and_day_number_of_each_day in rests_and_day_numbers_of_week:
            check_credit = self.check_credit()
            if (check_credit != True):
                self.emit(SIGNAL("log(QString)"),
                          self.username + ":" + '\n' + u" اعتبار شما کافی نیست  " + str(check_credit) + "-")
                break
            meal = 0
            selected_day = rests_and_day_number_of_each_day['day']
            if (str(selected_day) in available_days.keys()):  #avilable_days.keys == day number of available days
                for rest in rests_and_day_number_of_each_day['rests']:
                    if rest == "":
                        self.emit(SIGNAL("log(QString)"),
                                  self.username + ":" + '\n' + u" روز  " + day_mapping[selected_day] + u" " + meal_mapping[
                                      meal] + u" انتخاب نکرده اید ")
                        meal += 1
                        continue
                    foods_of_meal = foods[meal]
                    try:
                        reserved = self.reserve_this(available_days[str(selected_day)], rest, str(meal),
                                                             foods_of_meal)
                        if (reserved == True):
                            self.emit(SIGNAL("log(QString)"),
                                      self.username + ":" + '\n' + u" روز  " + day_mapping[selected_day] + u" " +
                                      meal_mapping[meal] + u" رزرو شد ")
                    except:
                        self.emit(SIGNAL("log(QString)"),self.username+":" + '\n' +  meal_mapping[meal]+u" روز  "+ day_mapping[selected_day]+u" قبلا رزرو شده یا این وعده سرو نمی شود")
                    else:
                        if reserved == False:
                            self.emit(SIGNAL("log(QString)"),
                                      self.username + ":" + '\n' + meal_mapping[meal] + u" روز  " + day_mapping[
                                          selected_day] + u" هیچ یک از انتخاب های شما سرو نمی شود ")

                    meal += 1

            else:
               self.emit(SIGNAL("log(QString)"),self.username+ ":" + '\n' + u" همه ی وعده های روز " +day_mapping[selected_day]+u" قبلا رزرو شده یا سلف تعطیل است ")


    def decode_database(self, name_of_database):
        json_file = open('./foodlists/' + name_of_database, 'r')
        json_decoded = json.load(json_file)
        foods = json_decoded['foods']  # export foods
        rests_and_day_numbers_of_week = json_decoded['restsOfEachDay']  # export days
        user_list_version = json_decoded['version']
        return (foods, rests_and_day_numbers_of_week,user_list_version)


    def login(self, username, password):
        self.browser = Browser('phantomjs')
        self.browser.driver.set_window_size(800, 371)
        self.wait_time = 2
        self.browser.visit("http://sups.shirazu.ac.ir/sfxweb/Gate/Login.aspx")
        self.browser.is_element_not_present_by_id('edId', self.wait_time)  # wait until see the element
        self.browser.find_by_id('edId').fill(username)
        self.browser.find_by_id('edPass').fill(password)
        self.browser.find_by_id('edWebApp').select(1)
        self.browser.find_by_id('edEnter').click()
        self.browser.find_by_css('ul.active:nth-child(3) > li:nth-child(2)').click()


    def reserve_this(self, selected_date, selected_rest, selected_meal, foods_of_meal):
        # select restaurant
        rest = self.browser.find_by_id('edRestaurant')
        self.browser.select('edRestaurant', selected_rest)

        #select date
        self.browser.is_element_not_present_by_id("edDate", self.wait_time)  #wait until see the element
        self.browser.select('edDate', selected_date)

        #select meal
        self.browser.is_element_not_present_by_id("edMeal", self.wait_time)  #wait until see the element
        meal = self.browser.find_by_id('edMeal')
        meal.select(selected_meal)

        #collect serving foods
        serving_foods = []
        self.browser.is_element_not_present_by_id("Food", self.wait_time)  #wait until see the element
        number_of_foods = len(self.browser.find_by_css("#Food li"))
        for nth in range(1, number_of_foods + 1):
            value = self.browser.find_by_css('#Food > li:nth-child(' + str(nth) + ') > input:nth-child(1)').value
            serving_foods.append(value)

        #select food and reserv
        reserved = False
        for food in foods_of_meal:  #select food of that meal
            if str(food) in serving_foods:
                self.browser.choose('Food', str(food))
                self.browser.find_by_id('btnBuyChip').click()
                reserved = True
                break

        return reserved

    def date_of_this_friday(self):
        today = datetime.date.today()
        week_day_of_today_gre = today.weekday();
        week_day_of_today_per = week_day_of_today_gre + 2 if week_day_of_today_gre < 5 else  week_day_of_today_gre - 5
        days_to_friday = datetime.timedelta(days=6 - week_day_of_today_per)
        this_friday = today + days_to_friday
        return this_friday


    def collect_available_days(self):
        dates = self.collect_available_dates()  # find the available dates
        this_friday = self.date_of_this_friday()
        next_saturday = this_friday + datetime.timedelta(days=1)

        this_week_available_days={}
        next_week_available_days={}

        for date in dates:
            year = int(date[0:4])
            month = int(date[4:6])
            day = int(date[6:8])
            gre_date = jalali.Persian(year, month, day).gregorian_datetime()
            weekday = gre_date.weekday()
            day_number = weekday + 2 if weekday < 5 else  weekday - 5
            if gre_date > this_friday:
                next_week_available_days[str(day_number)] = date
            if gre_date < next_saturday :
                this_week_available_days[str(day_number)] = date
        return (this_week_available_days,next_week_available_days)

    def collect_available_dates(self):
        rest = self.browser.find_by_id('edRestaurant')
        self.browser.select('edRestaurant', '8')
        dates = []
        number_of_dates = len(self.browser.find_by_css('#edDate >option'))
        for nth in range(2, number_of_dates + 1):
            value = self.browser.find_by_css('#edDate > option:nth-child(' + str(nth) + ')').value
            dates.append(value)
        return dates

    def take_screenshot(self, username, nameOfList):
        # self.browser.back()
        # self.browser.find_by_css('ul.active:nth-child(3) > li:nth-child(1)').click()
        self.browser.driver.save_screenshot('./screenshots/' + username + nameOfList[0:-5] + '.png')

    def open_screenshot(self, username, nameOfList):
        filename = os.getcwd() + '/screenshots/' + username + nameOfList[0:-5] + '.png'
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    def check_credit(self):
        string_credit = self.browser.find_by_id("lblCredit")
        int_credit = int(string_credit.text.replace(',', ''))
        if (int_credit < -1500):
            return int_credit
        return True






