from selenium import webdriver
from selenium.webdriver.common.by import By
from io import TextIOWrapper
import time as delay
import codecs
import subprocess
import smtplib
import traceback # use 'print(traceback.format_exc())' in an except-block to print a stack trace
import json
from datetime import datetime
from shutil import copyfile

import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials

from fancy_page_maker import make_page
from fancy_page_maker import assign_ranking
from fancy_page_maker import Substitution

# used for pushing changes to GitHub via terminal
def push_changes():
    process = subprocess.Popen('cd /home/pi/djd4rkn355.github.io; git add --all; git commit -m "Pi Push"; git push', stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print(proc_stdout)

# sends notifications to viable clients using Firebase Cloud Messaging
def send_notifications():
    # message for development clients before users are notified of any changes
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
    
    # as GitHub takes around a minute to deploy changes to GitHub Pages, introduce a delay of two minutes
    delay.sleep(120)
    
    # data message for Android clients that locally refreshes the plan and notifies of any changes
    topic_android = 'substitutions-android'
    message_android = messaging.Message(
        data={},
        topic=topic_android,
    )
    response_android = messaging.send(message_android)
    print('Successfully sent message to Android clients: ', response_android)

    # text notification for iOS clients that notifies about changes without any further local processing
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

# sends an email if an error occurred during the fetch
# I may have just copied this code from the internet, but it works, so don't change anything except the strings
def send_email(currentTime, body):
    try:
        print("Sending email")
        smtpUser = 'rpiavhplan@gmail.com'
        smtpPass = 'subst307plan_bydeniz'
        toAddress = 'k.duezgoeren@gmail.com'
        fromAddress = smtpUser
        subject = 'AvH Plan Server Issue'
        header = 'To: ' + toAddress + '\n' + 'From: ' + fromAddress + '\n' + 'Subject: ' + subject # don't change this string
        s = smtplib.SMTP('smtp.gmail.com', 587) # don't change the string in this
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(smtpUser, smtpPass)
        s.sendmail(fromAddress, toAddress, header + '\n\n' + body + '\n\nFetch started at: ' + currentTime)
        s.quit()
        print('Email has been sent')
    except: # fail-safe in case the fetch was unsuccessful due to an internet disconnect
        print('Email failed to send')

def writeInfoText(element):
    # p tag for Android app version 2.3.3 and below
    writeSubstText("\n\t\t<p>" + element.text + "</p>")

    # h2 tag for Android app version 2.3.4+
    # this allows for removing html tags without the need of deploying a new app version
    # I've added all HTML formatting tags that I found on an article on w3schools.com
    # aren't online programming resources just delightful?
    textToWrite = element.get_attribute('innerHTML') \
        .replace('<b>', '') \
        .replace('</b>', '') \
        .replace('&nbsp;', '') \
        .replace('<i>', '') \
        .replace('<strong>', '') \
        .replace('<em>', '') \
        .replace('<mark>', '') \
        .replace('<small>', '') \
        .replace('<del>', '') \
        .replace('<ins>', '') \
        .replace('<sub>', '') \
        .replace('<sup>', '')
    writeSubstText("\n\t\t<h6>" + textToWrite + "</h6>")

# these two functions allow for changing the way the script writes the required HTML files
# this can be useful if, for example, an identical copy of the substitution plan file is required 
def writeSubstText(text):
    substitutionFile.write(text)

def writeFoodText(text):
    foodMenuFile.write(text)
        

cred = credentials.Certificate("/home/pi/Desktop/avh-plan-firebase-adminsdk-5iy97-2a377ca3d3.json")
firebase_admin.initialize_app(cred)

while True:

    try:

        currentTime = datetime.now().strftime('%d.%m.%Y, %H:%M')
        print("----- " + currentTime + " -----")
        header = "<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<meta charset=\"utf-8\">\n\t\t<style>\n\t\t\tbody {\n\t\t\t\tfont-family: Arial, Helvetica, sans-serif\n\t\t\t}\n\t\t</style>\n\t</head>\n\t<body>\n<h1>" + currentTime + "</h1>"

        # initialise the substitution table file and the food menu file with some HTML
        substitutionFile = codecs.open("avh_substitutions.html", "w", "utf-8")
        substitutionFile.truncate()
        writeSubstText(header)
        foodMenuFile = codecs.open("food.html", "w", "utf-8")
        foodMenuFile.truncate()
        writeFoodText(header)
        
        # this right here is an instance of Selenium, a library made for prototyping quick web scraping tools. As I found it to be very useful
        # for fetching any data required, as well as being able to log in without sending a POST request (the possible complexity of which in
        # this case is described a few lines below), I have kept it in this script. Since it is not headless, it requires more resources than
        # a headless library. A Raspberry Pi 3B with 512 MB of RAM, which has been used to develop this script, has proven, at least in my
        # experience, to freeze occasionally, unless its page file is increased. I recommend at least a Raspberry Pi 3B+ for future deployments
        # 
        # a driver is required for this library, for which I have been using a Chromedriver. Place it anywhere on the deployment machine
        # and include its path as a string here. Make sure the driver's version matches the version of the web browser
        browser = webdriver.Chrome('/usr/bin/chromedriver') # for Raspberry Pi, Chrome 72

        # use this for testing on another PC and change the directory string accordingly
        # browser = webdriver.Chrome('/Users/kduez/git/raspberryPi/chromedriver') # for Windows 10

        # using this URL instead of /users/?view=login&Itemid=171 significantly speeds up the login process,
        # as it contains much fewer images that have to be loaded, since Selenium waits until the page finished loading
        # it also keeps the script from timing out on my slow-as-molasses internet connection
        browser.get('http://307.joomla.schule.bremen.de/index.php/component/users/#top')

        # finds the username and password text fields on the website and sends the corresponsing data
        # this is advantageous over a POST request, as the school website generates tokens on login for security reasons,
        # which cannot easily be included in a POST request, if at all
        username = browser.find_element_by_id("username")
        password = browser.find_element_by_id("password")
        username.send_keys("deniz130")
        password.send_keys("Cinemassacre")
        password.send_keys(u'\ue007') # Unicode 'Enter'

        browser.get('http://307.joomla.schule.bremen.de/index.php/service/sch%C3%BCler')
        print("Fetching of the substitution plan starts now.")

        sendEmail = True

        # PSA feature
        # uncomment this and edit only the fields that contain text
        # do not remove the "psa" string in the second <th> tag
        # you may append a link without a space between "psa" and the link

##        writeSubstText(
##                "\n\t\t<table>" +
##                "\n\t\t\t<tr>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t\t<th>psa</th>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t\t<th>Ein Update wird in den kommenden Tagen verfügbar sein; alte Versionen der App werden ab dem 30.09. nicht mehr funktionieren.</th>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t\t<th></th>" + 
##                "\n\t\t\t</tr>" + 
##                "\n\t\t</table>")

        # start iterating through HTML substitution tables

        for planInteger in range(0, 14):

            try:
                table_id_previous = browser.find_elements_by_tag_name("table")[planInteger]

                # start info table fetch

                try:
                    try:
                        dateElement = table_id_previous.find_element_by_xpath('./preceding-sibling::p[1]')
                        dateB = dateElement.find_element_by_tag_name("b")
                    except:
                        dateElement = table_id_previous.find_element_by_xpath('./preceding-sibling::p[2]')
                        dateB = dateElement.find_element_by_tag_name("b")

                    # info table
                    infoRows = table_id_previous.find_elements_by_tag_name("tr")
                    try:
                        column_test = table_id_previous.find_elements_by_xpath('.//tbody/tr[1]/th')[5] # throws an exception if the table is not a substitution table
                        isInfoTable = False
                    except:
                        info_test = infoRows[1]
                        writeInfoText(dateB)
                        
                        for infoRowInt in range(0, len(infoRows)):
                            rowsInfo = infoRows[infoRowInt]
                            infoCols = rowsInfo.find_elements_by_tag_name("td")

                            for infoColInt in range(0, len(infoCols)):
                                writeInfoText(infoCols[infoColInt])
                                
                except:
                    pass

                # end info table fetch
                # start substitution table fetch
                
                table_id = browser.find_elements_by_tag_name("table")[planInteger]

                # throws an exception if the table doesnt exist or is not a substitution table and skips it
                column_test = table_id.find_elements_by_xpath('.//tbody/tr[1]/th')[5]
                print("Table " + str(planInteger) + " has been found")

                writeSubstText("\n\t\t<table>")
                
                substitutions = []

                groupColInt = -1
                courseColInt = -1
                additionalColInt = -1
                dateColInt = -1
                timeColInt = -1
                roomColInt = -1
                teacherColInt = -1
                typeColInt = -1

                # collect indexes for the substitution table's columns
                # this is useful, as it makes the order of the columns on the website irrelevant
                # TODO change this to something more pleasant than a cascade of if-else's
                firstRow = table_id.find_elements_by_tag_name("tr")[0]
                columns = firstRow.find_elements_by_xpath('.//th')
                for i in range(0, len(columns)):
                    col = columns[i]
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
                    elif col.text == "Art":
                        typeColInt = i

                tableRows = table_id.find_elements_by_tag_name("tr")

                for intRow in range(1, len(tableRows)): # iterates through every row (vertically) and skips the first one (header)
                    try:
                        row = tableRows[intRow]
                        substs = row.find_elements_by_xpath('.//td')

                        substitutionIndexes = [groupColInt, dateColInt, timeColInt, courseColInt, roomColInt, additionalColInt, teacherColInt, typeColInt]

                        writeSubstText("\n\t\t\t<tr>")
                        subst_list = []
                        for i in range(0, len(substitutionIndexes)):
                            if substitutionIndexes[i] == -1:
                                t = ""
                            else:
                                try: # if an incomplete row exists, as to not crash the script
                                    t = substs[substitutionIndexes[i]].text
                                except:
                                    t = ""
                            writeSubstText("\n\t\t\t\t<th>" + t + "</th>")
                            subst_list.append(t)
                            
                        writeSubstText("\n\t\t\t</tr>")
                        substitutions.append(Substitution(subst_list[0], subst_list[3], subst_list[4], subst_list[1], subst_list[5], subst_list[2], assign_ranking(subst_list[0])))
                        
                    except:
                        pass

                writeSubstText("\n\t\t</table>")
                sendEmail = False

                # end substitution table fetch

            except:
                pass

        # end iterating through HTML substitution tables

        # send email if no substitution tables have been found
        if sendEmail == True:
            try:
                mainPage = browser.find_element_by_class_name('item-page')
                mainPageItems = mainPage.find_elements_by_tag_name('p')
                sendEmail = False
                for i in range(0, len(mainPageItems)):
                    writeInfoText(mainPageItems[i])
            except:
                send_email(currentTime, 'Plan could not be fetched; no substitution tables were found. No changes have been made to the GitHub repository. Please review the script as soon as possible.')
                sendEmail = True

        writeSubstText("\n\t</body>\n</html>")
        substitutionFile.close()

        # only continue if the substitution plan was fetched successfully
        if sendEmail == False:
            try:
                browser.get('https://www.schulkantine-gueven.de/speisekarte')
                writeFoodText("\n\t\t<table>\n\t\t\t<tr>\n\t\t\t\t<th>Für Schüler 3,00€, für Bedienstete 3,50€. Mittagstisch von 11:30 bis 14:30.</th>")
                
                i = browser.find_elements_by_class_name('richText')
                
                for a in range(0, len(i)):
                    d = browser.find_elements_by_class_name('menuCategroyTitle')[a]
                    if 'Speiseplan' in d.text:
                        break
                    writeFoodText("\n\t\t\t\t<th>" + d.text + "</th>")
                    p = i[a].find_elements_by_tag_name('p')

                    for a2 in range(0, len(p)):
                        if 'FÜR SCHÜLER' in p[a2].text:
                            break
                        writeFoodText("\n\t\t\t\t<th>" + p[a2].text + "</th>")

            except:
                print("Food menu fetch unsuccessful")
            finally:
                writeFoodText("\n\t\t\t</tr>\n\t\t</table>\n\t</body>\n<html>")
                foodMenuFile.close()
                browser.quit()

            # compares the newly-created substitution table file with a pre-existing file to check for any changes
            # make sure that the file 'subst_check.html' exists and contains some text, or else the check will fail
            substFileNew = open("avh_substitutions.html", "r")
            substFileCheck = open("avh_substitutions_check.html", "r")
            sameFiles = True
            for line1 in substFileNew:
                for line2 in substFileCheck:
                    if line1 != line2:
                        if line1[0:4] == "<h1>": # ignores any lines with data that may change on any iteration (e.g. starting time of fetch)
                            print("Line ignored")
                        else:
                            sameFiles = False
                    break
            substFileNew.close()
            substFileCheck.close()
            print('Substitution files the same: ' + str(sameFiles))

            # compares the newly-created food menu file with a pre-existing file to check for any changes
            # make sure that the file 'food_check.html' exists and contains some text, or else the check will fail
            foodFileNew = open("food.html", "r")
            foodFileCheck = open("food_check.html", "r")
            sameFoodFiles = True
            for line1 in foodFileNew:
                for line2 in foodFileCheck:
                    if line1 != line2:
                        if line1[0:4] == "<h1>": # ignores any lines with data that may change on any iteration (e.g. starting time of fetch)
                            print("Line ignored")
                        else:
                            sameFoodFiles = False
                    break
            foodFileNew.close()
            foodFileCheck.close()
            print('Food menu files the same: ' + str(sameFoodFiles))

            if sameFiles == True:
                # updates the new file with the data from the check file to copy its fetch time
                # as such, users will not be able to refresh the plan with an equal copy
                copyfile("avh_substitutions_check.html", "avh_substitutions.html")
            else: # sameFiles == False
                # in this case, an update to the substitution plan has been published; send notifications to all users
                # copies the contents of the newly created file to the check file. By keeping the new file, its fetch time is preserved
                # and users will be able to refresh the plan
                copyfile("avh_substitutions.html", "avh_substitutions_check.html")
            make_page(substitutions)

            if sameFoodFiles == True:
                # updates the new file with the data from the check file to copy its fetch time
                # as such, users will not be able to refresh the food menu with an equal copy
                copyfile("food_check.html", "food.html")
            else: # sameFoodFiles == False
                # copies the contents of the newly created file to the check file. By keeping the new file, its fetch time is preserved
                # and users will be able to refresh the food menu
                copyfile("food.html", "food_check.html")

            push_changes()
            print("Script successfully executed. Repository is up-to-date.")

            # if changes to the substitution table have occurred, send notifications to all users
            # this does not trigger if only the food menu has been updated in order to prevent some duplicate notifications
            if sameFiles == False:
                print("Notifications will be prepared.")
                send_notifications()
            else:
                print("No notifications will be sent.")

        elif sendEmail == True:
            print("Fetch has been unsuccessful. Changes have not been pushed to GitHub.")
    
    # fail-safe in case a website could not be collected (e.g. intermittent internet outage)
    except:
        print("The connection has timed out.")
        substitutionFile.close()
        foodMenuFile.close()
        browser.quit()

        # sends an email with a stack trace for recognising exceptions without remoting into the server
        send_email(currentTime, 'The connection likely has timed out. Please check the status of the school website as well as the script.\n\n' + traceback.format_exc())

    # waits eight minutes until the next fetch. A successful fetch will likely take around two minutes, not including the notification delay,
    # which will result in a refreshing time of around every ten minutes
    delay.sleep(360)
