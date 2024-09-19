""" author: feezyhendrix

    main function botcore
 """

from time import sleep
from random import randint

import modules.config as config
# importing generated info
import modules.generateaccountinformation as accnt
from modules.storeusername import store
# from .activate_account import get_activation_url
# library import
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys  # and Krates
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

import requests
import re
import logging

import requests
import time
# from fake_useragent import UserAgent

# from pymailutils import Imap

# API Endpoint for Temp Mail
TEMP_MAIL_API = "https://api.tempmail.lol"

class AccountCreator():
    account_created = 0
    def __init__(self, use_custom_proxy, use_local_ip_address):
        self.sockets = []
        self.use_custom_proxy = use_custom_proxy
        self.use_local_ip_address = use_local_ip_address
        self.url = 'https://www.instagram.com/accounts/emailsignup/'
        self.__collect_sockets()


    def __collect_sockets(self):
        r = requests.get("https://www.sslproxies.org/")
        matches = re.findall(r"<td>\d+.\d+.\d+.\d+</td><td>\d+</td>", r.text)
        revised_list = [m1.replace("<td>", "") for m1 in matches]
        for socket_str in revised_list:
            self.sockets.append(socket_str[:-5].replace("</td>", ":"))

    def createaccount(self, proxy=None):
        chrome_options = webdriver.ChromeOptions()
        if proxy != None:
            chrome_options.add_argument('--proxy-server=%s' % proxy)

        # chrome_options.add_argument('headless')
        # ua = UserAgent()
        # user_agent = ua.random
        chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"')
        # chrome_options.add_argument("--incognito")
        chrome_options.add_argument('window-size=1200x600')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print('Opening Browser')
        driver.get(self.url)

        print('Browser Opened')
        sleep(5)




        action_chains = ActionChains(driver)
        sleep(5)
        account_info = accnt.new_account()
      
 
        # fill the email value
        print('Filling email field')
        email_field = driver.find_element('name', 'emailOrPhone')
        print(email_field)
        sleep(1)
        action_chains.move_to_element(email_field)
        print(account_info["email"])
        email_field.send_keys(account_info["email"])

        sleep(2)

        # fill the fullname value
        print('Filling fullname field')
        fullname_field = driver.find_element('name', 'fullName')
        action_chains.move_to_element(fullname_field)
        fullname_field.send_keys(account_info["name"])

        sleep(2)

        # fill username value
        print('Filling username field')
        username_field = driver.find_element('name', 'username')
        action_chains.move_to_element(username_field)
        username_field.send_keys(account_info["username"])

        sleep(2)

        # fill password value
        print('Filling password field')
        password_field = driver.find_element('name', 'password')
        action_chains.move_to_element(password_field)
        passW = account_info["password"]
        print(passW)
        password_field.send_keys(str(passW))
        sleep(1)

        sleep(2)

        submit = driver.find_element('xpath', "//button[@type='submit']")


        action_chains.move_to_element(submit)

        sleep(2)
        submit.click()

        sleep(3)
        try:

            
            month_button = driver.find_element('xpath', '//select[@title="Month:"]')
            month_button.click()
            month_button.send_keys(account_info["birthday"].split(" ")[0])
            sleep(1)
            day_button = driver.find_element('xpath', '//select[@title="Day:"]')
            day_button.click()
            day_button.send_keys(account_info["birthday"].split(" ")[1].replace(",", ""))
            sleep(1)
            year_button = driver.find_element('xpath', '//select[@title="Year:"]')

            # Create a Select object
            year_select = Select(year_button)
            # Extract the year from the account_info and replace any commas
            year_value = account_info["birthday"].split(" ")[2].replace(",", "")

            # Select the year by value
            year_select.select_by_value(year_value)

            sleep(2)
            next_button = driver.find_element('xpath', "//button[text()='Next']")
            next_button.click()

            sleep(4)

            if account_info["email"] and account_info["token"]:
                # Provide this temporary email during sign-up or verification
                print(f"Use this temporary email: {account_info['email']} to sign up")

                # Poll inbox for the verification email
                sender, subject, body = accnt.check_inbox(account_info["token"])
                print(f"Sender: {sender}, Subject: {subject}")
                print(f"Email Body: {body}")

                # Extract verification code
                code = accnt.extract_verification_code(body)

                
                confirmation_code = driver.find_element('name', 'email_confirmation_code')

                if code:
                    print(f"Verification code: {code}")
                    confirmation_code.send_keys(code)
                    time.sleep(2)
                    next_button2 = driver.find_element('xpath', "//div[text()='Next']")
                    next_button2.click()

                else:
                    print("No verification code found.")
            sleep(10)

        except Exception as e :
            print(e.with_traceback)
            pass


        sleep(5)
        # After the first fill save the account account_info
        store(account_info)
        
        """
            Currently buggy code.
        """
        # Activate the account
        # confirm_url = get_activation_url(account_info['email'])
        # logging.info("The confirm url is {}".format(confirm_url))
        # driver.get(confirm_url)

        driver.close()

    def creation_config(self):
        try:
            if self.use_local_ip_address == False:
                if self.use_custom_proxy == False:
                    for i in range(0, config.Config['amount_of_account']):
                        if len(self.sockets) > 0:
                            current_socket = self.sockets.pop(0)
                            try:
                                self.createaccount(current_socket)
                            except Exception as e:
                                print('Error!, Trying another Proxy {}'.format(current_socket))
                                self.createaccount(current_socket)

                else:
                    with open(config.Config['proxy_file_path'], 'r') as file:
                        content = file.read().splitlines()
                        for proxy in content:
                            amount_per_proxy = config.Config['amount_per_proxy']

                            if amount_per_proxy != 0:
                                print("Creating {} amount of users for this proxy".format(str(amount_per_proxy)))
                                for i in range(0, amount_per_proxy):
                                    try:
                                        self.createaccount(proxy)

                                    except Exception as e:
                                        print("An error has occured" + str(e))

                            else:
                                random_number = str(randint(1, 20))
                                print("Creating {} amount of users for this proxy".format(random_number))
                                for i in range(0, random_number):
                                    try:
                                        self.createaccount(proxy)
                                    except Exception as e:
                                        print(str(e))
            else:
                for i in range(0, config.Config['amount_of_account']):
                            try:
                                self.createaccount()
                            except Exception as e:
                                print('Error!, Check its possible your ip might be banned')
                                self.createaccount()


        except Exception as e:
            print(e)


def runbot():
    account = AccountCreator(config.Config['use_custom_proxy'], config.Config['use_local_ip_address'])
    account.creation_config()
