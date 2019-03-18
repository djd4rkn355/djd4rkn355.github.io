from selenium import webdriver
from selenium.webdriver.common.by import By
from io import TextIOWrapper
import time
import codecs

while True:
    file = codecs.open("index.html", "w", "utf-8")
    file.truncate()
    file.write("<!DOCTYPE HTML>\n<html>\n\t<head>\n\t\t<meta charset=\"utf-8\">\n\t\t<style>\n\t\t\tbody {\n\t\t\t\tfont-family: Arial, Helvetica, sans-serif\n\t\t\t}\n\t\t</style>\n\t</head>\n\t<body>\n\t\t<table>")

    # browser = webdriver.Chrome('/Users/kduez/git/raspberryPi/chromedriver') # for Windows 10
    browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver') # for Raspberry Pi

    browser.get('http://307.joomla.schule.bremen.de/index.php/component/users/?view=login&Itemid=171')

    username = browser.find_element_by_id("username")
    password = browser.find_element_by_id("password")
    username.send_keys("deniz130")
    password.send_keys("Cinemassacre")
    password.send_keys(u'\ue007') # Unicode 'Enter'

    browser.get('http://307.joomla.schule.bremen.de/index.php/service/sch%C3%BCler')

    table_id = browser.find_element(By.CLASS_NAME, 'subst')
    rowCount = table_id.find_elements_by_tag_name("tr")
    intRow = 1

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
    file.write("\n\t\t</table>\n\t</body>\n</html>")
    browser.quit()
    file.close()
