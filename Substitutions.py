from selenium import webdriver
from selenium.webdriver.common.by import By
from io import TextIOWrapper
import time as timeImport
import codecs
import subprocess
import smtplib
import traceback
import json
from datetime import datetime
from shutil import copyfile

import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials

def subprocess_cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print(proc_stdout)

def send_notifications():
    topic_debug = 'substitutions-debug'
    message_debug = messaging.Message(
        notification=messaging.Notification(
            title='Push successful',
            body='Committed changes to GitHub.',
        ),
        topic=topic_debug,
    )
    response_debug = messaging.send(message_debug)
    print('Successfully sent message to development clients: ', response_debug)
    
    timeImport.sleep(120)
    
    topic_android = 'substitutions-android'
    message_android = messaging.Message(
        data={},
        topic=topic_android,
    )
    response_android = messaging.send(message_android)
    print('Successfully sent message to Android clients: ', response_android)

    topic_ios = 'substitutions-ios'
    message_ios = messaging.Message(
        notification=messaging.Notification(
            title='AvH-Vertretungsplan',
            body='Der Plan wurde aktualisiert.',
        ),
        topic=topic_ios,
    )
    response_ios = messaging.send(message_ios)
    print('Successfully sent message to iOS clients: ', response_ios)

def send_email(currentTime, body):
    print("Sending email.")
    smtpUser = 'rpiavhplan@gmail.com'
    smtpPass = 'avhplan307'
    toAdd = 'k.duezgoeren@gmail.com'
    fromAdd = smtpUser
    subject = 'AvH Plan Server Issue'
    header = 'To: ' + toAdd + '\n' + 'From: ' + fromAdd + '\n' + 'Subject: ' + subject
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(smtpUser, smtpPass)
    s.sendmail(fromAdd, toAdd, header + '\n\n' + body + '\n\nFetch started at: ' + currentTime)
    s.quit()
    print('Email has been sent.')

cred = credentials.Certificate("/home/pi/Desktop/avh-plan-firebase-adminsdk-5iy97-2a377ca3d3.json")
firebase_admin.initialize_app(cred)

while True:

    try:

        file = codecs.open("subst.html", "w", "utf-8")
        fileFood = codecs.open("food.html", "w", "utf-8")
        file.truncate()
        fileFood.truncate()
        file.write("<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<meta charset=\"utf-8\">\n\t\t<style>\n\t\t\tbody {\n\t\t\t\tfont-family: Arial, Helvetica, sans-serif\n\t\t\t}\n\t\t</style>\n\t</head>\n\t<body>")
        fileFood.write("<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<meta charset=\"utf-8\">\n\t\t<style>\n\t\t\tbody {\n\t\t\t\tfont-family: Arial, Helvetica, sans-serif\n\t\t\t}\n\t\t</style>\n\t</head>\n\t<body>")
        currentTime = datetime.now().strftime('%Y-%m-%d, %H:%M')
        timeHeader = "\n\t\t<h1>" + currentTime + "</h1>"
        file.write(timeHeader)
        fileFood.write(timeHeader)

        # browser = webdriver.Chrome('/Users/kduez/git/raspberryPi/chromedriver') # for Windows 10
        browser = webdriver.Chrome('/usr/bin/chromedriver') # for Raspberry Pi, Chrome 72

        browser.get('http://307.joomla.schule.bremen.de/index.php/component/users/?view=login&Itemid=171')

        username = browser.find_element_by_id("username")
        password = browser.find_element_by_id("password")
        username.send_keys("deniz130")
        password.send_keys("Cinemassacre")
        password.send_keys(u'\ue007') # Unicode 'Enter'

        browser.get('http://307.joomla.schule.bremen.de/index.php/service/sch%C3%BCler')
        print("Fetching of the substitution plan starts now.")

        planInteger = 0
        sendEmail = True

        # PSA feature
        # uncomment this and edit only the fields that contain text
        # do not remove the "psa" string in the second <th> tag
        # you may append a link without a space between "psa" and the link

##        file.write(
##                "\n\t\t<table>" +
##                "\n\t\t\t<tr>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t\t<th>psahttps://307.joomla.schule.bremen.de/index.php/service/sch%C3%BCler/informationen-und-downloads</th>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t\t<th>Klick hier, um den Klausurenplan auf der Schulwebsite einzusehen.</th>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t</tr>" + 
##                "\n\t\t</table>")

        for planInteger in range(0, 14):

            try:
                table_id_previous = browser.find_elements_by_tag_name("table")[planInteger]

                try:
                    dateElement = table_id_previous.find_element_by_xpath('./preceding-sibling::p[1]')
                    dateB = dateElement.find_element_by_tag_name("b")
                except:
                    dateElement = table_id_previous.find_element_by_xpath('./preceding-sibling::p[2]')
                    dateB = dateElement.find_element_by_tag_name("b")

                # info table
                infoRowCount = table_id_previous.find_elements_by_tag_name("tr")
                info_test = infoRowCount[1]

                file.write("\n\t\t<p>" + dateB.text + "</p>")

                infoRowInt = 0
                for infoRowInt in range(0, len(infoRowCount)):
                    rowsInfo = table_id_previous.find_elements_by_tag_name("tr")[infoRowInt]
                    infoColInt = 0
                    infoColCount = rowsInfo.find_elements_by_tag_name("td")

                    for infoColInt in range(0, len(infoColCount)):
                        colsInfo1 = rowsInfo.find_elements_by_tag_name("td")[infoColInt]
                        file.write("\n\t\t<p>" + colsInfo1.text + "</p>")
                        infoColInt += 1

                    infoRowInt += 1

                table_id = browser.find_elements_by_tag_name("table")[planInteger + 1]
                column_test = table_id.find_elements_by_xpath('.//tbody/tr[1]/th')[5] # throws an exception if the table doesnt exist

                rowCount = table_id.find_elements_by_tag_name("tr")
                intRow = 1
                file.write("\n\t\t<table>")

                print("Table " + str(planInteger) + " has been found")

                groupColInt = 0
                courseColInt = 0
                additionalColInt = 0
                dateColInt = 0
                timeColInt = 0
                roomColInt = 0
                teacherColInt = -1

                firstRow = table_id.find_elements_by_tag_name("tr")[0]
                for i in range(0, 9):
                    col = firstRow.find_elements_by_xpath('.//th')[i]
                    if col.text == "Klasse(n)":
                        groupColInt = i
                    elif col.text == "Datum":
                        dateColInt = i
                    elif col.text == "Stunde":
                        timeColInt = i
                    elif col.text == "Fach":
                        courseColInt = i
                    elif col.text == "Vertreter":
                        teacherColInt = i
                    elif col.text == "Raum":
                        roomColInt = i
                    elif col.text == "Vertretungs-Text":
                        additionalColInt = i

                for intRow in range(1, len(rowCount)): # iterates through every row (vertically) and skips the first one (header)
                    try:
                        intCol = 0
                        rows = table_id.find_elements_by_tag_name("tr")[intRow]
                        substs = rows.find_elements_by_xpath('.//td')

                        if teacherColInt == -1:
                            teacher = ""
                        else:
                            teacher = substs[teacherColInt].text

                        file.write( "\n\t\t\t<tr>" +
                                    "\n\t\t\t\t<th>" + substs[groupColInt].text + "</th>" + 
                                    "\n\t\t\t\t<th>" + substs[dateColInt].text + "</th>" + 
                                    "\n\t\t\t\t<th>" + substs[timeColInt].text + "</th>" + 
                                    "\n\t\t\t\t<th>" + substs[courseColInt].text + "</th>" + 
                                    "\n\t\t\t\t<th>" + substs[roomColInt].text + "</th>" + 
                                    "\n\t\t\t\t<th>" + substs[additionalColInt].text + "</th>" + 
                                    "\n\t\t\t\t<th>" + teacher + "</th>" +
                                    "\n\t\t\t</tr>")
                        
                        intRow += 1
                    except:
                        pass

                file.write("\n\t\t</table>")

                
                
                

                sendEmail = False
            except:
                print("Table " + str(planInteger) + " not found")
            finally:
                planInteger += 1

        # send email if no data could be fetched
        if sendEmail == True:
            send_email(currentTime, 'Plan could not be fetched; no substitution tables were found. No changes have been made to the GitHub repository. Please review the script as soon as possible.')

        file.write("\n\t</body>\n</html>")
        file.close()

        browser.get('https://www.schulkantine-gueven.de/speisekarte')

        try:
            fileFood.write("\n\t\t<table>\n\t\t\t<tr>\n\t\t\t\t<th>Für Schüler 3,00€, für Bedienstete 3,50€. Mittagstisch von 11:30 bis 14:30.</th>")
            foodDateOne = browser.find_element_by_xpath('//*[@id="1302648704"]/div[1]/h3')
            fileFood.write("\n\t\t\t\t<th>" + foodDateOne.text + "</th>")

            foodTableOne = browser.find_elements_by_xpath('//*[@id="1302648704"]/div[1]/div/div[2]/div/div[1]/div[2]/div/p')
            for intFoodOne in range(0, len(foodTableOne) - 3):
                foodCol = browser.find_elements_by_xpath('//*[@id="1302648704"]/div[1]/div/div[2]/div/div[1]/div[2]/div/p')[intFoodOne]
                fileFood.write("\n\t\t\t\t<th>" + foodCol.text + "</th>")

            try:
                foodDateTwo = browser.find_element_by_xpath('//*[@id="1302648704"]/div[2]/h3')
                fileFood.write("\n\t\t\t\t<th>" + foodDateTwo.text + "</th>")

                foodTableTwo = browser.find_elements_by_xpath('//*[@id="1302648704"]/div[2]/div/div[2]/div/div[1]/div[2]/div/p')
                for intFoodTwo in range(0, len(foodTableTwo) - 5):
                    foodColTwo = browser.find_elements_by_xpath('//*[@id="1302648704"]/div[2]/div/div[2]/div/div[1]/div[2]/div/p')[intFoodTwo]
                    fileFood.write("\n\t\t\t\t<th>" + foodColTwo.text + "</th>")
            
            except:
                print("Food menu fetch unsuccessful")

        except:
            print("Food menu fetch unsuccessful")
        finally:
            fileFood.write("\n\t\t\t</tr>\n\t\t</table>\n\t</body>\n<html>")
            browser.quit()
            fileFood.close()

        f1 = open("subst.html", "r")
        f2 = open("subst_check.html", "r")
        sameFiles = True
        for line1 in f1:
            for line2 in f2:
                if line1 != line2:
                    if line1[0:4] == "<h1>":
                        print("Line ignored")
                    else:
                        sameFiles = False
                break
        f1.close()
        f2.close()
        print(sameFiles)

        ff1 = open("food.html", "r")
        ff2 = open("food_check.html", "r")
        sameFoodFiles = True
        for line1 in ff1:
            for line2 in ff2:
                if line1 != line2:
                    if line1[0:8] == "\t\t<h1>":
                        print("Line ignored")
                    else:
                        sameFoodFiles = False
                break
        ff1.close()
        ff2.close()
        print(sameFoodFiles)

        if sameFiles == True:
            copyfile("subst_check.html", "subst.html")
        else: # sameFiles == False
            # in this case, an update to the substitution plan has been published; send notifications to all users
            copyfile("subst.html", "subst_check.html")

        if sameFoodFiles == True:
            copyfile("food_check.html", "food.html")
        else: # sameFoodFiles == False
            copyfile("food.html", "food_check.html")

        if sendEmail == False:
            subprocess_cmd('cd /home/pi/djd4rkn355.github.io; git add --all; git commit -m "Pi Push"; git push')
            print("Script successfully executed. Repository is up-to-date.")
            if sameFiles == False:
                send_notifications()
        elif sendEmail == True:
            print("Fetch has been unsuccessful. Changes have not been pushed to GitHub.")
    
    except:
        print("The connection has timed out.")
        file.close()
        fileFood.close()
        browser.quit()
        send_email(currentTime, 'The connection appears to have timed out. Please check the status of the school website.\n\n' + traceback.format_exc())

    timeImport.sleep(480)
