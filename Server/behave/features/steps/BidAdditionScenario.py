import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import allure
from behave import then, when, given
from allure_behave.hooks import allure_report

import time

@given(u'I am on the "Stock" page')
def step1(context):
    # Open browser
    context.driver = webdriver.Chrome()
    # Open URL
    context.driver.get("http://localhost:5173/stocks")

@when(u'I log in')
def step2(context):
    # Store the main window handle so we can switch to the popup
    main_window_handle = None

    # Click the Google Login button
    context.driver.find_element(By.ID, "login-button").click()

    signin_window_handle = None
    # Login popup should be launched at this point, find its handle
    while not signin_window_handle:
        for handle in context.driver.window_handles:
            if handle != main_window_handle:
                signin_window_handle = handle
                break
    context.driver.switch_to.window(signin_window_handle)

    # Enter login info (email box)
    context.driver.find_element(By.ID, "whsOnd zHQkBf").send_keys("paeljojy@student.jyu.fi")
    # Press next button
    context.driver.find_element(By.CLASS_NAME, "VfPpkd-Jh9lGc").click()

    # Enter username into jyu username box
    context.driver.find_element(By.ID, "username").send_keys("paeljojy")
    # Enter password into jyu password box
    context.driver.find_element(By.ID, "password").send_keys("**********")

    # Press submit button
    context.driver.find_element(By.CLASS_NAME, "submit").click()

@when(u'I fill in "Amount" with "20"')
def step3(context):
    # Fill in bid amount
    context.driver.find_element(By.ID, "bid-amount-input").send_keys("20")

@when(u'I fill in "Price" with "100"')
def step4(context):
    # Fill in bid price 
    context.driver.find_element(By.ID, "bid-price-input").send_keys("100")

@when(u'I press "Add Bid"')
def step5(context):
    context.driver.find_element(By.ID, "bid-submit").click()

@then(u'I should see "Bid was successfully added"')
def step6(context):
    if not context.driver.find_element(By.ID, "bid-submit").click():
        raise Exception("Bid was not successfully added")
    else:
        print("Bid was successfully added")

# Check that the bid was added to the user's bids list
@then(u'I should see "20"')
def step7(context):
    pass
@then(u'I should see "100"')
def step8(context):
    pass

