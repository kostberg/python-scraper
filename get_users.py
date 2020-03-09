from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
import time
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random
import json
import urllib.request
import os
import configparser


class InstaBot:

    def __init__(self, username=None, password=None):
        """"
        Creates an instance of InstaBot class.

        Args:
            username:str: The username of the user, if not specified, read from configuration.
            password:str: The password of the user, if not specified, read from configuration.
        """

        self.Config = configparser.ConfigParser()
        self.Config.read("config.ini")
        
        self.user = input('Log in as Veeti or David? ')
        self.user = self.user.capitalize()
        if self.user.lower() == 'veeti':
            self.username = self.Config.get('IG_AUTH', 'Veeti_user')
            self.password = self.Config.get('IG_AUTH', 'Veeti_pwd')
        elif self.user.lower() == 'david':
            self.username = 'dasd'
            self.password = 'asdsa'
        else:
            raise NameError('User does not exist')

        self.login_url = "https://www.instagram.com/accounts/login/"
        self.nav_user_url = "https://www.instagram.com/{}/"
        self.get_tag_url = "https://www.instagram.com/explore/tags/{}/"

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument('disable-infobars')
        options.add_argument('--lang=en')
        headless = input('Headless mode? (Yes/No) ')
        if headless.capitalize() == 'Yes':
            options.add_argument('headless')
        else:
            pass
        self.driver = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')

        self.logged_in = False

    # tools
    def random_time(self, amount=2):
        if amount == 1:
            return round((random.random() + 1), 2)
        elif amount == 2:
            return round((random.random() + 2), 2)
        elif amount == 3:
            return round((random.random() + 3), 2)
        elif amount == 4:
            return round((random.random() + 4), 2)

    def remove_popup(self):
        if self.does_element_exist('//div[@role="presentation"]'):
            self.driver.find_element_by_xpath('//button[contains(text(), "Not Now")]').click()
        else:
            pass

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

    def nav_user(self, user):
        url = self.nav_user_url.format(user)
        self.driver.get(url)

    def nav_stats(self, nav):
        self.nav_user(self.username)
        time.sleep(self.random_time())
        href_url = "/" + str(self.username) + "/" + str(nav) + "/"
        follow = self.driver.find_element_by_xpath('//a[@href="' + str(href_url) + '"]')
        follow.click()

    def nav_trending(self):
        self.driver.find_element_by_xpath('//a[@href="/explore/"]').click()

    def nav_tags(self, tag):
        "https://www.instagram.com/explore/tags/{}/".format(tag)

    def bad_follows(self):
        followers = self.get_followers()
        following = self.get_following()
        return set(following).difference(followers)

    def does_json_exist(self, file):
        try:
            f = open(file)
            f.close()
            return True
        except IOError:
            print("Success, {} doesn't exist".format(file))
            return False

    # actions

    def login(self):
        """
        Logs a user into Instagram via the web portal
        """

        self.driver.get(self.login_url)
        time.sleep(self.random_time())
        login_btn = self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]')

        username_input = self.driver.find_element_by_name('username')
        password_input = self.driver.find_element_by_name('password')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        login_btn.click()

        # wait for homepage to load
        self.wait_for_element('//a[@href="/explore/"]')  # random element to wait for
        time.sleep(self.random_time(1))

        # check for popup + remove it
        self.remove_popup()
        time.sleep(self.random_time(2))

    def scroll_stats(self, type):
        if type == "followers":
            element = """document.querySelector('[role="dialog"]').childNodes[1]"""
        elif type == "following":
            element = """document.querySelector('[role="dialog"]').childNodes[2]"""
        query = "return {}.scrollHeight".format(element)

        last_height = self.driver.execute_script(query)
        self.driver.execute_script("{}.scrollTo(0, {}.scrollHeight)".format(element, element))
        time.sleep(self.random_time(1))
        new_height = self.driver.execute_script(query)

        if new_height == last_height:
            return True

        last_height = new_height
        return False

    def get_user_stats(self, type):
        time.sleep(self.random_time())
        followers = self.driver.find_elements_by_xpath('/html/body/div[4]/div/div[2]/ul/div/li')
        followers_len = len(followers)
        if type == "followers":
            path = "/html/body/div[4]/div/div[2]/ul/div/li[{}]/div/div[2]"
        elif type == "following":
            path = "/html/body/div[4]/div/div[2]/ul/div/li[{}]/div/div[1]/div[2]/div[1]/a"
        i = 1
        list = []
        while i <= followers_len:
            xpath = path.format(i)
            a = self.driver.find_element_by_xpath(xpath)
            list.append(a.get_attribute("innerHTML"))
            i += 1
        return list

    def unfollow_bad(self):
        set = self.bad_follows()
        time.sleep(self.random_time(1))
        condition = False
        while not condition:
            condition = self.scroll_stats("following")
        for index, i in enumerate(set, start=1):
            print("{}\nIndex of {} is {}".format(set, i, index))
            time.sleep(self.random_time(3))
            self.driver.find_element_by_xpath('//a[contains(text(), "{}")]/../../../../..//button'.format(i)).click()
            time.sleep(self.random_time())
            self.driver.find_element_by_xpath('//button[contains(text(), "Unfollow")]').click()
            time.sleep(self.random_time())
            if index % 10 == 0:
                self.driver.find_element_by_xpath('//div[@role="dialog"]/div/div/div/button').click()
                time.sleep(self.random_time(4))
                self.driver.find_element_by_xpath('//a[@href="/veeti_seppanen2000/following/"]').click()
                self.wait_for_element('//a[contains(text(), "{}")]/../../../../..//button')
        print(index)

    def get_explore_posts(self, object, get_average_likes=False):
        self.wait_for_element('//textarea[@placeholder="Add a comment…"]')
        time.sleep(self.random_time())
        username = self.driver.find_element_by_xpath("//article/header/div[2]/div/div/h2/a").get_attribute('title')

        # check if post is video and then continues to next loop
        if self.does_element_exist('//textarea[@placeholder="Add a comment…"]/../../../../section/div/div/button/span'):
            likes = self.driver.find_element_by_xpath(
                '//textarea[@placeholder="Add a comment…"]/../../../../section/div/div/button/span').get_attribute(
                'innerHTML')

            # get followers in new tab
            profiles = self.driver.find_elements_by_xpath("//canvas/../a/img")[0]
            ActionChains(self.driver) \
                .key_down(Keys.CONTROL) \
                .click(profiles) \
                .key_up(Keys.CONTROL) \
                .perform()
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.wait_for_element('//*[@id="react-root"]/section//section/ul/li[2]/a/span')
            followers = self.driver.find_element_by_xpath(
                '//*[@id="react-root"]/section//section/ul/li[2]/a/span').get_attribute("title")
            if get_average_likes:
                average_likes = int(self.calc_average_likes(3))     # int representing num of posts to check
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

            # minimum follower limit
            if int(followers.replace(',', '')) < 5000:
                pass
            else:
                object[username] = {}
                object[username]['post_likes'] = likes
                if get_average_likes:
                    object[username]['average_likes'] = average_likes
                object[username]['followers'] = followers
                print(str(object[username]) + " {}".format(username))

            # continue to next post
            self.wait_for_element('//a[contains(text(), "Next")]')
            self.driver.find_element_by_xpath('//a[contains(text(), "Next")]').click()
            time.sleep(self.random_time())

        else:
            object[username] = {}
            object[username]['post_is_video'] = 'True'
            print(str(object[username]) + " {}".format(username))
            # continue to next post
            self.wait_for_element('//a[contains(text(), "Next")]')
            self.driver.find_element_by_xpath('//a[contains(text(), "Next")]').click()
            time.sleep(self.random_time())

    def get_average_likes(self, object):
        self.wait_for_element('//textarea[@placeholder="Add a comment…"]')
        time.sleep(self.random_time())
        if self.does_element_exist('//textarea[@placeholder="Add a comment…"]/../../../../section/div/div/button/span'):
            likes = self.driver.find_element_by_xpath(
                '//textarea[@placeholder="Add a comment…"]/../../../../section/div/div/button/span').get_attribute(
                'innerHTML')
            post_id = str(self.driver.current_url).replace('https://www.instagram.com/p/', '').replace('/', '')
            object[post_id] = likes

            # continue to next post
            self.wait_for_element('//a[contains(text(), "Next")]')
            self.driver.find_element_by_xpath('//a[contains(text(), "Next")]').click()
            time.sleep(self.random_time())

        else:
            # continue to next post
            self.wait_for_element('//a[contains(text(), "Next")]')
            self.driver.find_element_by_xpath('//a[contains(text(), "Next")]').click()
            time.sleep(self.random_time())

    def loop_through_posts(self, accounts, func):
        # first post on page
        self.wait_for_element('//article/div[1]/div/div[1]/div[1]/a')
        time.sleep(self.random_time())
        self.driver.find_element_by_xpath("//article/div[1]/div/div[1]/div[1]/a").click()

        variable = {} # always an object

        i = 0
        # start of loop
        while i < accounts:
            try:
                func(variable)
                i += 1
                if i % 5 == 0:
                    if i % 50 == 0:
                        print('Iterator (Posts: {}) has gone through 50 accounts, pausing for a hour'.format(i))
                        time.sleep(3600) # sleep for an hour
                    else:
                        print('Iterator (Posts: {}) has gone through 5 accounts, refreshing page'.format(i))

                        self.wait_for_element('//button[contains(text(), "Close")]')
                        self.driver.find_element_by_xpath('//button[contains(text(), "Close")]').click()
                        self.wait_for_element('//article/div[1]/div/div[1]/div[1]/a')
                        time.sleep(self.random_time())
                        self.driver.refresh()
                        self.wait_for_element('//article/div[1]/div/div[1]/div[1]/a')
                        time.sleep(self.random_time())
                        self.driver.find_element_by_xpath("//article/div[1]/div/div[1]/div[1]/a").click()
            except NoSuchElementException:
                print('ERROR. Trying to save current data...')
                return variable


        # end of loop
        return variable

    def msg_accounts(self, user):
        # navigate to the user from homepage
        self.nav_user(self.username)
        self.wait_for_element('//input[@placeholder="Search"]')
        self.driver.find_element_by_xpath('//input[@placeholder="Search"]').send_keys(user)

        profile = '//a[@href="/{}/"]'.format(user)
        self.wait_for_element(profile)
        self.driver.find_element_by_xpath(profile).click()

        self.wait_for_element('//span[@aria-label="Options"]/../../../div[1]/span/span[1]/button')
        follow_btn = self.driver.find_element_by_xpath(
            '//span[@aria-label="Options"]/../../../div[1]/span/span[1]/button')

        if follow_btn.get_attribute('innerHTML') == 'Follow':
            follow_btn.click()
        else:
            pass

    # actions invokers
    def calc_average_likes(self, accounts):
        post_likes = self.loop_through_posts(accounts, self.get_average_likes)
        total_likes = 0
        for posts in post_likes:
            likes = int(post_likes[posts].replace(',', ''))
            total_likes += likes

        return int(total_likes / accounts)

    def run(self):
        accounts = int(input('How many accounts do you want to iterate over? (Under 250 recommended) '))
        new_folder = input('Do you want to create a new folder? (Yes/No) ')
        if new_folder.capitalize() == 'Yes':
            path = input('Enter the name of your folder: ')
            try:
                os.mkdir('./JSON_folders/{}/{}'.format(self.user, path))
            except OSError:
                print("Creation of the directory %s failed, start over" % path)
            else:
                print("Successfully created the directory %s " % path)
                use_folder = input('Do you want to use this folder? (Yes/No) ')
                if use_folder.capitalize() == 'Yes':
                    directory = './JSON_folders/{}/{}'.format(self.user, path)
                else:
                    directory = input('Enter the path to your folder: ')
        else:
            directory = input('Enter the path to your folder: ')

        file_name = input("Enter your filename (will be timestamped): ")
        today = datetime.date.today()
        if file_name.endswith('.json'):
            file_name.replace('.json', '_{}.json'.format(today))
        else:
            file_name = file_name + '_{}.json'.format(today)

        # noinspection PyUnboundLocalVariable
        if directory.endswith('/'):
            pass
        else:
            directory = '{0}/'.format(directory)

        file_path = directory + file_name
        if self.does_json_exist(file_path):
            print('Filename already exists, start over')
        else:
            self.nav_trending()
            json_object = self.loop_through_posts(accounts, self.get_explore_posts)
            with open(file_path, 'w') as ftp:
                json.dump(json_object, ftp)
            print("File saved as {}".format(file_name))

    def get_followers(self):
        self.nav_stats("followers")
        time.sleep(self.random_time())
        condition = False
        while not condition:
            condition = self.scroll_stats("followers")
        return self.get_user_stats("followers")

    def get_following(self):
        self.nav_stats("following")
        time.sleep(self.random_time())
        condition = False
        while not condition:
            condition = self.scroll_stats("following")
        return self.get_user_stats("following")


if __name__ == '__main__':
    bot = InstaBot()
    bot.login()
    bot.run()