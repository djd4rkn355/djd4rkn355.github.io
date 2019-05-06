from selenium import webdriver
from selenium.webdriver.common.by import By
from io import TextIOWrapper
import time
import codecs
import subprocess
import smtplib
import traceback

while True:

    try:

        file = codecs.open("subst.html", "w", "utf-8")
        fileFood = codecs.open("food.html", "w", "utf-8")
        file.truncate()
        fileFood.truncate()
        file.write("<!DOCTYPE HTML>\n<html>\n\t<head>\n\t\t<meta charset=\"utf-8\">\n\t\t<style>\n\t\t\tbody {\n\t\t\t\tfont-family: Arial, Helvetica, sans-serif\n\t\t\t}\n\t\t</style>\n\t</head>\n\t<body>")
        fileFood.write("<!DOCTYPE HTML>\n<html>\n\t<head>\n\t\t<meta charset=\"utf-8\">\n\t\t<style>\n\t\t\tbody {\n\t\t\t\tfont-family: Arial, Helvetica, sans-serif\n\t\t\t}\n\t\t</style>\n\t</head>\n\t<body>")

        # browser = webdriver.Chrome('/Users/kduez/git/raspberryPi/chromedriver') # for Windows 10
        browser = webdriver.Chrome('/usr/bin/chromedriver') # for Raspberry Pi, Chrome 72

        browser.get('http://307.joomla.schule.bremen.de/index.php/component/users/?view=login&Itemid=171')

        username = browser.find_element_by_id("username")
        password = browser.find_element_by_id("password")
        username.send_keys("deniz130")
        password.send_keys("Cinemassacre")
        password.send_keys(u'\ue007') # Unicode 'Enter'

        browser.get('http://307.joomla.schule.bremen.de/index.php/service/sch%C3%BCler')

        planInteger = 0
        sendEmail = True

        for planInteger in range(0, 14):

            try:
                table_id_previous = browser.find_elements_by_tag_name("table")[planInteger]

                table_id = browser.find_elements_by_tag_name("table")[planInteger + 1]
                column_test = table_id.find_elements_by_xpath('.//tbody/tr[1]/th')[5] # throws an exception if the table doesnt exist

                rowCount = table_id.find_elements_by_tag_name("tr")
                intRow = 1
                file.write("\n\t\t<table>")

                for intRow in range(1, len(rowCount)): # iterates through every row (vertically) and skips the first one (header)
                    file.write("\n\t\t\t<tr>")
                    intCol = 0
                    rows = table_id.find_elements_by_tag_name("tr")[intRow]
                    
                    for intCol in range(0, 6): # iterates through every column in a row (horizontally) minus the student groups
                        cols = rows.find_elements_by_xpath('.//td')[intCol]
                        print(cols.text)
                        file.write("\n\t\t\t\t<th>" + cols.text + "</th>")
                        intCol += 1
                        
                    file.write("\n\t\t\t</tr>")
                    intRow += 1

                file.write("\n\t\t</table>")

                # date

                try:
                    dateElement = table_id_previous.find_element_by_xpath('./preceding-sibling::p[2]')
                except:
                    dateElement = table_id_previous.find_element_by_xpath('./preceding-sibling::p[1]')
                

                dateB = dateElement.find_element_by_tag_name("b")
                print(dateB.text)
                file.write("\n\t\t<p>" + dateB.text + "</p>")
                
                # info table
                infoRowCount = table_id_previous.find_elements_by_tag_name("tr")
                ic1 = 0
                for ic1 in range(0, len(infoRowCount)):
                    rowsInfo1 = table_id_previous.find_elements_by_tag_name("tr")[ic1]
                    ic0 = 0
                    infoRowCount12 = rowsInfo1.find_elements_by_tag_name("td")
                    for ic0 in range(0, len(infoRowCount12)):
                        colsInfo1 = rowsInfo1.find_elements_by_tag_name("td")[ic0]
                        print(colsInfo1.text)
                        file.write("\n\t\t<p>" + colsInfo1.text + "</p>")
                        ic0 += 1
                    ic1 += 1

                sendEmail = False
            except:
                print("Error in substitution table " + str(planInteger))
                print(traceback.format_exc())

            planInteger += 1

        # send email if no data could be fetched
        if sendEmail is True:
            print("Error in first informational table")
            smtpUser = 'rpiavhplan@gmail.com'
            smtpPass = 'avhplan307'
            toAdd = 'k.duezgoeren@gmail.com'
            fromAdd = smtpUser
            subject = 'AvH Plan Server Issue'
            header = 'To: ' + toAdd + '\n' + 'From: ' + fromAdd + '\n' + 'Subject: ' + subject
            body = 'Plan could not be fetched. Please review the codebase.'
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(smtpUser, smtpPass)
            s.sendmail(fromAdd, toAdd, header + '\n\n' + body + '\n\n' + traceback.format_exc())
            s.quit()
            print('Email has been sent')

        file.write("\n\t</body>\n</html>")
        file.close()

        browser.get('https://www.schulkantine-gueven.de/speisekarte')

        try:
            fileFood.write("\n\t\t<table>\n\t\t\t<tr>\n\t\t\t\t<th>Für Schüler 3,00€, für Bedienstete 3,50€. Mittagstisch von 11:30 bis 14:30.</th>")
            foodDateOne = browser.find_element_by_xpath('//*[@id="1302648704"]/div[1]/h3')
            fileFood.write("\n\t\t\t\t<th>" + foodDateOne.text + "</th>")
            print(foodDateOne.text)

            foodTableOne = browser.find_elements_by_xpath('//*[@id="1302648704"]/div[1]/div/div[2]/div/div[1]/div[2]/div/p')
            for intFoodOne in range(0, len(foodTableOne) - 3):
                foodCol = browser.find_elements_by_xpath('//*[@id="1302648704"]/div[1]/div/div[2]/div/div[1]/div[2]/div/p')[intFoodOne]
                fileFood.write("\n\t\t\t\t<th>" + foodCol.text + "</th>")
                print(foodCol.text)

            try:
                foodDateTwo = browser.find_element_by_xpath('//*[@id="1302648704"]/div[2]/h3')
                fileFood.write("\n\t\t\t\t<th>" + foodDateTwo.text + "</th>")
                print(foodDateTwo.text)

                foodTableTwo = browser.find_elements_by_xpath('//*[@id="1302648704"]/div[2]/div/div[2]/div/div[1]/div[2]/div/p')
                for intFoodTwo in range(0, len(foodTableTwo) - 5):
                    foodColTwo = browser.find_elements_by_xpath('//*[@id="1302648704"]/div[2]/div/div[2]/div/div[1]/div[2]/div/p')[intFoodTwo]
                    fileFood.write("\n\t\t\t\t<th>" + foodColTwo.text + "</th>")
                    print(foodColTwo.text)
            
            except:
                print("No second food for you huehuehue?")

        except:
            print("No food for you huehuehue!")
        finally:
            fileFood.write("\n\t\t\t</tr>\n\t\t</table>\n\t</body>\n<html>")
            browser.quit()
            fileFood.close()

        def subprocess_cmd(command):
            process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
            proc_stdout = process.communicate()[0].strip()
            print(proc_stdout)

        subprocess_cmd('cd /home/pi/djd4rkn355.github.io; git add --all; git commit -m "Pi Push"; git push')
        print("Success")
    
    except:
        print("Timeout")

    time.sleep(480)
