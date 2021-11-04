import argparse
import subprocess
import os

from selenium import webdriver
import time
import schedule
import selenium
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from datetime import datetime
import os
import sys

def doesElemExist(driver, name):
    try:
        driver.find_element(By.CLASS_NAME, name)
    except selenium.common.exceptions.NoSuchElementException:
        return False
    return True

def holdTilFindElems(elem, criteria, name ,maxHold=3):
    for i in range(maxHold * 2):
        try:
            elem.find_element(criteria, name)
        except selenium.common.exceptions.NoSuchElementException:
            time.sleep(0.5)
    return driver.find_elements(criteria, name)

def waitTilBtnClicks(elem, criteria, name, bgColor, maxHold=3):
    # Wait until time select botton is green
    btnToClick = None
    for i in range(maxHold * 2):
        btns = holdTilFindElems(elem, criteria, name, maxHold=3)
        for btn in btns:
            if bgColor == None or btn.value_of_css_property('background-color') == bgColor:
                btnToClick = btn
        if btnToClick != None:
            break
        time.sleep(0.5)
    if btnToClick == None:
        print('Could not find the button')
        return False
    # Wait until time select button clicks
    for i in range(maxHold * 2):
        try:
            btnToClick.click()
            return True
            break
        except:
            time.sleep(0.1)
    return False


def reserveUrl(driver, url):
    # open page
    driver.get(url)

    # Hold (max 3 sec) until calender showing up
    calEx = doesElemExist(driver, 'calendar-date')
    for i in range(6):
        if calEx:
            break
        time.sleep(0.5)
        calEx = doesElemExist(driver, 'calendar-date')
    if not calEx:
        return False

    days = driver.find_elements(By.CLASS_NAME, 'calendar-date')
    for day in days:
        if day.value_of_css_property('background-color') != 'rgba(0, 199, 60, 1)':
            continue

        print('Checking day: {}'.format(day.text))
        day.click()

        bookingElem = holdTilFindElems(driver, By.CLASS_NAME, 'ly_time_booking', maxHold=3)
        bookingElem = bookingElem[0]
        timeListElems = holdTilFindElems(bookingElem, By.CLASS_NAME, 'lst_time')
        for timeList in timeListElems:
            timeSlots = holdTilFindElems(timeList, By.CLASS_NAME, 'time_info_box')
            for slot in timeSlots:
                if slot.value_of_css_property('background-color') != 'rgba(224, 254, 211, 1)':
                    continue
                slot.click()

        # Select time
        timeSelectSucc = waitTilBtnClicks(bookingElem, By.TAG_NAME, 'button', 'rgba(0, 199, 60, 1)', 1)
        if not timeSelectSucc:
            continue
        # To next step
        nextStepSucc = waitTilBtnClicks(driver, By.CLASS_NAME, 'bottom_btn', 'rgba(0, 199, 60, 1)', 1)
        if not nextStepSucc:
            continue

        buttons = holdTilFindElems(driver, By.CLASS_NAME, 'list_summary')       # hold till payment page loads
        payButtonSucc = waitTilBtnClicks(driver, By.CLASS_NAME, 'bottom_btn', None, 1)
        if payButtonSucc:
            return True
    return False

if __name__ == '__main__':
    # Set arguments to get chrome driver path
    parser = argparse.ArgumentParser()
    parser.add_argument('--chrome-driver', required=True, help='Path to the Chrome driver')
    parser.add_argument('--port', default='9222', help='Port the execute chrome debug mode on')
    parser.add_argument('--urls', metavar='URL', nargs='+', help='Urls to try')
    parser.add_argument('--max', type=int, default=5, help='Max try per url')
    args = parser.parse_args()

    # Get Chrome driver
    drvOptions = webdriver.chrome.options.Options()
    drvOptions.add_experimental_option('debuggerAddress', '127.0.0.1:{}'.format(args.port))
    driver = webdriver.Chrome(args.chrome_driver, options=drvOptions)

    for url in args.urls:
        print('# Try to reserve {}'.format(url))
        for trial in range(1, args.max + 1):
            print('## Trial {}'.format(trial))
            res = reserveUrl(driver, url)
            if res:
                break
