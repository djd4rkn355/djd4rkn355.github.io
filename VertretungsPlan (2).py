from selenium import webdriver
from selenium.webdriver.common.by import By
from io import TextIOWrapper
import time
import codecs
import subprocess

while True:

    file = codecs.open("index.html", "w", "utf-8")
    file.truncate()
    file.write("<!DOCTYPE HTML>\n<html>\n\t<head>\n\t\t<meta charset=\"utf-8\">\n\t\t<style>\n\t\t\tbody {\n\t\t\t\tfont-family: Arial, Helvetica, sans-serif\n\t\t\t}\n\t\t</style>\n\t</head>\n\t<body>")

    # browser = webdriver.Chrome('/Users/kduez/git/raspberryPi/chromedriver') # for Windows 10
    browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver') # for Raspberry Pi

    browser.get('http://307.joomla.schule.bremen.de/index.php/component/users/?view=login&Itemid=171')

    username = browser.find_element_by_id("username")
    password = browser.find_element_by_id("password")
    username.send_keys("deniz130")
    password.send_keys("Cinemassacre")
    password.send_keys(u'\ue007') # Unicode 'Enter'

    browser.get('http://307.joomla.schule.bremen.de/index.php/service/sch%C3%BCler')

    

    try:
        table_id = browser.find_element_by_xpath('//*[@id="vertretung"]/table[2]')
        rowCount = table_id.find_elements_by_tag_name("tr")
        intRow = 1
        file.write("\n\t\t<table>")

        for intRow in range(1, len(rowCount)): # iterates through every row (vertically) and skips the first one (header)
            file.write("\n\t\t\t<tr>")
            intCol = 0
            rows = browser.find_elements_by_xpath('//table[2]/tbody/tr')[intRow]
            
            for intCol in range(0, 6): # iterates through every column in a row (horizontally) minus the student groups
                cols = rows.find_elements_by_xpath('.//td')[intCol]
                print(cols.text)
                file.write("\n\t\t\t\t<th>" + cols.text + "<th>")
                intCol += 1
                
            file.write("\n\t\t\t</tr>")
            intRow += 1

        table_id2 = browser.find_element_by_xpath('//*[@id="vertretung"]/table[4]')
        rowCount2 = table_id2.find_elements_by_tag_name("tr")
        intRow2 = 1

        for intRow2 in range(1, len(rowCount2)): # iterates through every row (vertically) and skips the first one (header)
            file.write("\n\t\t\t<tr>")
            intCol2 = 0
            rows2 = browser.find_elements_by_xpath('//table[4]/tbody/tr')[intRow2]
            
            for intCol2 in range(0, 6): # iterates through every column in a row (horizontally) minus the student groups
                cols2 = rows2.find_elements_by_xpath('.//td')[intCol2]
                print(cols2.text)
                file.write("\n\t\t\t\t<th>" + cols2.text + "<th>")
                intCol2 += 1
                
            file.write("\n\t\t\t</tr>")
            intRow2 += 1
    except:
        print("NullPointerException")
    finally:
        file.write("\n\t\t</table>")


    try: #first info table
        dateDay = browser.find_element_by_xpath('//*[@id="vertretung"]/p[1]/b')
        print(dateDay.text)
        file.write("\n\t\t<p>" + dateDay.text + "</p>")
        
        colsInfo = browser.find_element_by_xpath('//*[@id="vertretung"]/table[1]/tbody')
        infoRowCount = colsInfo.find_elements_by_tag_name("tr")
        ic1 = 0
        for ic1 in range(0, len(infoRowCount)): #len(infoRowCount) //*[@id="vertretung"]/table[1]/tbody/tr[2]/td[2]
            rowsInfo1 = browser.find_elements_by_xpath('//*[@id="vertretung"]/table[1]/tbody/tr')[ic1]
            ic0 = 0
            infoRowCount12 = rowsInfo1.find_elements_by_tag_name("td")
            infoRows12 = browser.find_elements_by_xpath('//*[@id="vertretung"]/table[1]/tbody/tr/td')[ic1]
            for ic0 in range(0, len(infoRowCount12)):
                colsInfo1 = rowsInfo1.find_elements_by_xpath('.//td')[ic0]
                print(colsInfo1.text)
                file.write("\n\t\t<p>" + colsInfo1.text + "</p>")
                ic0 += 1
            ic1 += 1
    except:
        print("fuck mate somethings wrong better fix it")

    try:
        dateDay2 = browser.find_element_by_xpath('//*[@id="vertretung"]/p[2]/b')
        print(dateDay2.text)
        file.write("\n\t\t<p>" + dateDay2.text + "</p>")

        colsInfo2 = browser.find_element_by_xpath('//*[@id="vertretung"]/table[3]/tbody')
        infoRowCount2 = colsInfo2.find_elements_by_tag_name("tr")
        ic12 = 0
        for ic12 in range(0, len(infoRowCount2)): #len(infoRowCount) //*[@id="vertretung"]/table[1]/tbody/tr[2]/td[2]
            rowsInfo12 = browser.find_elements_by_xpath('//*[@id="vertretung"]/table[3]/tbody/tr')[ic12]
            ic02 = 0
            infoRowCount12 = rowsInfo12.find_elements_by_tag_name("td")
            infoRows22 = browser.find_elements_by_xpath('//*[@id="vertretung"]/table[3]/tbody/tr/td')[ic12]
            for ic02 in range(0, len(infoRowCount12)):
                colsInfo12 = rowsInfo12.find_elements_by_xpath('.//td')[ic02]
                print(colsInfo12.text)
                file.write("\n\t\t<p>" + colsInfo12.text + "</p>")
                ic02 += 1
            ic12 += 1
    except:
        print("oi you broke it")

    # try:
    #     substBlock = browser.find_element(By.CLASS_NAME, 'item-page')
    #     elements = substBlock.find_elements_by_tag_name("p")
    #     for elem in elements:
    #         print(elem.text)
    #         file.write("\n\t\t<p>" + elem.text + "</p>")
    # except:
    #     print("NullPointerException")

    file.write("\n\t</body>\n</html>")
    browser.quit()
    file.close()

    def subprocess_cmd(command):
        process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        print(proc_stdout)

    subprocess_cmd('cd /home/pi/djd4rkn355.github.io; git add --all; git commit -m "Pi Push"; git push')
    print("Success")
    time.sleep(480)
