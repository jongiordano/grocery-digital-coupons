import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = None

def initialize():
    global browser

    path = os.getenv('GOOGLE_CHROME_SHIM') or None

    options = webdriver.ChromeOptions()
    options.binary_location = path
    if path:
        options.add_argument('headless')

    browser = webdriver.Chrome(executable_path='chromedriver', chrome_options = options)

    print 'Using ' + (path or './chromedriver')

def test(email, password, delay = 10, callback = None, complete = None):
    result = { 'email': email, 'count': 1 }
    return result if not complete else complete(result)

def shoprite(email, password, delay = 10, callback = None, complete = None):
    initialize()

    if callback:
        callback('Navigating to url.', email)

    # Visit the Digital Coupons page
    browser.get('http://coupons.shoprite.com/main.html')

    if callback:
        callback('Logging in.', email)

    # Login
    WebDriverWait(browser, delay).until(
        EC.presence_of_element_located((By.ID, "Email"))
    )
    browser.find_element_by_id('Email').send_keys(email)
    browser.find_element_by_id('Password').send_keys(password)
    browser.find_element_by_id('Password').send_keys(Keys.RETURN)

    if callback:
        callback('Waiting for site to load.', email)

    # Wait until the site loads, find the coupon frame
    WebDriverWait(browser, delay).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '#cpsite, .field-validation-error, .validation-summary-errors'))
    )

    if callback:
        callback('Checking if login succeeded.', email)

    # Check if the login succeeded.
    fields = browser.find_elements_by_xpath("//*[contains(text(), 'incorrect') or contains(text(), 'try again')]")
    if len(fields) > 0:
        # Invalid login?
        count = -1
    else:
        coupons_frame = browser.find_element_by_id('cpsite')

        # Find the coupon link in the coupon frame
        coupons_frame_link = coupons_frame.get_attribute("src")

        # Visit the coupon link, look for the page numbers section
        browser.get(coupons_frame_link)

        WebDriverWait(browser, delay).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'paging'))
        )

        # Click the link to show all coupons
        browser.execute_script('onShowAll()')

        # Click all the buttons to add the coupons to your card
        list_of_coupon_buttons = browser.find_elements_by_class_name('load2crd')

        for count, coupon_button in enumerate(list_of_coupon_buttons, start=1):
            try:
                coupon_button.click()

                if callback:
                    callback('Added', count, 'coupons!', email)

                time.sleep(.250)
            except:
                continue

    screenshot = browser.get_screenshot_as_base64()

    if callback:
        callback('Complete!', email)

    browser.close()

    result = { 'email': email, 'count': count, 'screenshot':  screenshot }
    return result if not complete else complete(result)

def stop_and_shop(email, password, delay = 10, callback = None, complete = None):
    initialize()

    # Get email/password from config file
    email = parser.get('stop and shop', 'email')
    password = parser.get('stop and shop', 'password')

    # Visit the Login page
    browser.get('https://stopandshop.com/login/')

    # Login
    help_element = browser.find_element_by_link_text('help')
    help_element.send_keys(Keys.TAB)
    username_element = browser.switch_to.active_element
    username_element.send_keys(email)
    username_element.send_keys(Keys.TAB)
    password_element = browser.switch_to.active_element
    password_element.send_keys(password)
    password_element.send_keys(Keys.RETURN)

    # Wait until link to go to coupons page is ready
    WebDriverWait(browser, delay).until(
        EC.presence_of_element_located((By.LINK_TEXT, 'coupons'))
    )

    # Go to coupons page
    browser.get('https://stopandshop.com/dashboard/coupons-deals/')

    # Wait until coupons are ready
    WebDriverWait(browser, delay).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'load-to-card'))
    )

    # Click all the buttons to add the coupons to your card
    list_of_coupon_buttons = browser.find_elements_by_class_name('load-to-card')

    for count, coupon_button in enumerate(list_of_coupon_buttons, start=1):
        try:
            coupon_button.click()
            if callback:
                callback('Added', count, 'coupons!', email)
            time.sleep(1)
        except:
            continue

    screenshot = browser.get_screenshot_as_base64()

    if callback:
        callback('Complete!', email)

    browser.close()

    result = { 'email': email, 'count': count, 'screenshot':  screenshot }
    return result if not complete else complete(result)
