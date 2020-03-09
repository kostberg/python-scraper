from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
import time
from utility_methods.utility_methods import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random
import json
import urllib.request
import os


class InstaBot:

    def __init__(self, username=None, password=None, arg1=False):
        """"
        Creates an instance of InstaBot class.

        Args:
            username:str: The username of the user, if not specified, read from configuration.
            password:str: The password of the user, if not specified, read from configuration.
            arg1: boolean: True for launching chrome headless/ False for not
        """

        self.username = 'kasper_ostbergg'
        self.password = 'Money1798'

        self.login_url = config['IG_URLS']['LOGIN']
        self.nav_user_url = config['IG_URLS']['NAV_USER']
        self.get_tag_url = config['IG_URLS']['SEARCH_TAGS']

        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=400,850")
        options.add_argument('disable-infobars')
        options.add_argument('--lang=en')
        mobile_emulation = {"deviceName": "iPhone 7"}
        options.add_experimental_option("mobileEmulation", mobile_emulation)

        if arg1:
            options.add_argument('headless')

        self.driver = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')

        self.logged_in = False

    # tools
    def add_msgd_users(self, msgd_user):
        # load messaged users
        msgd_users = self.data_handling('./messaged_users.json')
        # append user to list
        msgd_users.append(msgd_user)
        # save new list
        with open('./messaged_users.json', 'w') as file:
            json.dump(msgd_users, file)



    def high_value_accounts(self):
        dir_path = input('Enter the path to desired folder to iterate over (either local or absolute): ')
        name = input('Enter the unique name of your refined list: ')
        # iterate over files in dir and create object
        directory = os.fsencode(dir_path)
        master_object = {}
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                json_file = dir_path + "/" + filename
                json_object = self.data_handling(json_file)
                master_object = self.mergeDict(master_object, json_object)

        # handle numbers
        for key, value in master_object.items():
            # check if post is video
            if 'post_is_video' in value:
                pass
            else:
                for innerKey, innerValue in master_object[key].items():
                    if type(innerValue) is int:
                        pass
                    elif type(innerValue) is str:
                        master_object[key][innerKey] = int(innerValue.replace(',', ''))
                    else:
                        pass

        # refine the accounts by a lot of statements
        refined_accounts = {}
        for key, value in master_object.items():
            # check if post is video
            if 'post_is_video' in value:
                # videos always perform well
                refined_accounts.update({key: value})
            else:
                like_ratio = round((value['post_likes'] / value['followers']), 4)

                # refine the accounts by a lot of statements
                if like_ratio > 0.15:
                    refined_accounts.update({key: value})
                if value['post_likes'] > 5000 and value['followers'] < 25000:
                    refined_accounts.update({key: value})
                if value['post_likes'] > 25000 and value['followers'] < 50000:
                    refined_accounts.update({key: value})

        self.save_usernames(refined_accounts, 'refined_list/{}'.format(name))

    def mergeDict(self, dict1, dict2):
        # Merge dictionaries and keep values of common keys in list
        dict3 = {**dict1, **dict2}
        for key, value in dict3.items():
            if key in dict1 and key in dict2:
                if value == dict1[key]:
                    pass
                else:
                    likes = [int(value["post_likes"].replace(',', '')), int(dict1[key]['post_likes'].replace(',', ''))]
                    followers = [int(value["followers"].replace(',', '')),
                                 int(dict1[key]["followers"].replace(',', ''))]
                    dict3[key] = {'post_likes': max(likes), 'followers': max(followers)}

        return dict3

    def does_json_exist(self, filename):
        try:
            f = open('./JSON_lists/{}.json'.format(filename))
            f.close()
            return True
        except IOError:
            print("Success, filename doesn't exist")
            return False

    def data_handling(self, path):
        jsonFile = open(path)
        jsonString = jsonFile.read()
        jsonData = json.loads(jsonString)
        return jsonData

    def save_usernames(self, variable, filename):
        if self.does_json_exist(filename):
            pass
        else:
            with open('./JSON_lists/{}.json'.format(filename), 'w') as ftp:
                json.dump(list(variable.keys()), ftp)

    def random_time(self, amount=2):
        if amount == 1:
            return round((random.random() + 1), 4)
        elif amount == 2:
            return round((random.random() * 5 + 15), 2)
        elif amount == 3:
            return round((random.random() * 10 + 30), 2)
        elif amount == 4:
            return round((random.random() * 20 + 40), 2)

    def wait_for_element(self, xpath):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            print("Wat da hel!")

    def does_element_exist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
            return True
        except NoSuchElementException:
            return False

    def add_to_homescreen(self):
        if self.does_element_exist('//div[@role="presentation"]'):
            self.driver.find_element_by_xpath('//button[contains(text(), "Cancel")]').click()
        else:
            pass

    def remember_me(self):
        if self.does_element_exist('//button[contains(text(), "Not Now")]'):
            self.driver.find_element_by_xpath('//button[contains(text(), "Not Now")]').click()
        else:
            pass

    def activate_notifications(self):
        self.wait_for_element('//div[@role="presentation"]//button[contains(text(), "Not Now")]')
        if self.does_element_exist('//div[@role="presentation"]'):
            self.driver.find_element_by_xpath(
                '//div[@role="presentation"]//button[contains(text(), "Not Now")]').click()
        else:
            pass

    # actions

    def login(self):
        """
        Logs a user into Instagram via the web portal
        """

        self.driver.get(self.login_url)
        time.sleep(self.random_time())
        login_btn = self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/div/div/div/form/div[7]/button')

        username_input = self.driver.find_element_by_name('username')
        password_input = self.driver.find_element_by_name('password')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        login_btn.click()

        # wait for header to load
        self.wait_for_element('//header/div/h1/div')  # random element to wait for
        time.sleep(5.32)

        # check for remember me popup + remove it
        self.remember_me()
        time.sleep(5.7)

        # wait for homepage to load
        self.wait_for_element('//a[@href="/explore/"]')  # random element to wait for
        time.sleep(4.6)

        # check for add to homescreen popup + remove it
        self.add_to_homescreen()
        time.sleep(2.7)

    def msg_users(self, user, message="Hey, would you be interested in selling you account?"):
        print(user)
        time.sleep(self.random_time(3))

        self.wait_for_element('//h1[contains(text(), "Direct")]/../div[2]/button')
        self.driver.find_element_by_xpath('//h1[contains(text(), "Direct")]/../div[2]/button').click()

        time.sleep(self.random_time())
        self.wait_for_element('//input[@placeholder="Search..."]')
        self.driver.find_element_by_xpath('//input[@placeholder="Search..."]').send_keys(user)

        time.sleep(self.random_time())
        self.wait_for_element('//*[@id="react-root"]/section/div[2]/div/div[2]/div[1]')
        element = self.driver.find_elements_by_xpath('//div[contains(text(), "{}")]/../../../..'.format(user))
        element[0].click()

        self.wait_for_element('//h1[contains(text(), "New Message")]/..//button')
        if self.does_element_exist('//h1[contains(text(), "New Message")]/..//button[@disabled]'):
            pass
        elif user not in self.data_handling('messaged_users.json'):
            time.sleep(self.random_time())
            self.wait_for_element('//button[contains(text(), "Next")]')
            self.driver.find_element_by_xpath('//button[contains(text(), "Next")]').click()

            time.sleep(self.random_time())
            self.wait_for_element('//textarea[@placeholder="Message..."]')
            self.driver.find_element_by_xpath('//textarea[@placeholder="Message..."]').send_keys(message)
            time.sleep(self.random_time(1))
            self.wait_for_element('//button[contains(text(), "Send")]')
            self.driver.find_element_by_xpath('//button[contains(text(), "Send")]').click()

            # add to messaged users list to prevent double messaging
            self.add_msgd_users(user)
            time.sleep(self.random_time())
            self.driver.find_element_by_xpath('//a[@href="/direct/new/"]').click()
            time.sleep(1)

            self.wait_for_element('//a[@href="/direct/inbox/"]')
            self.driver.find_element_by_xpath('//a[@href="/direct/inbox/"]').click()
            time.sleep(self.random_time(1))
        else:
            print('Double message prevented. User: {}'.format(user))

    # action invokers
    def start_messaging(self, json_list):
        with open(json_list) as f:
            users = json.load(f)

        # navigate to inbox
        self.wait_for_element('//a[@href="/direct/inbox/"]')
        self.driver.find_element_by_xpath('//a[@href="/direct/inbox/"]').click()
        time.sleep(self.random_time())

        # check for notifications popup + remove it
        self.activate_notifications()

        # load different messages to be sent
        jsonFile = open('./messages.json')
        jsonString = jsonFile.read()
        jsonData = json.loads(jsonString)

        for user in users:
            self.msg_users(user, jsonData[0])


if __name__ == '__main__':
    config_file_path = './config.ini'
    logger_file_path = './bot.log'
    config = init_config(config_file_path)

    bot = InstaBot()
    bot.login()
    bot.start_messaging('./JSON_lists/refined_list/Veeti/sicko_list.json')
