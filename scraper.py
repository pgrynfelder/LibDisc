
import os
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DRIVERS_PATH = os.path.abspath('.') + "\drivers\\"
if os.name == "nt":
    phantomdriver_path = DRIVERS_PATH + "phantomjs.exe"
    chromedriver_path = DRIVERS_PATH + "chromedriver.exe"
    geckodriver_path = DRIVERS_PATH + "geckodriver.exe"
else:
    phantomdriver_path = DRIVERS_PATH + "phantomjs"
    chromedriver_path = DRIVERS_PATH + "chromedriver"
    geckodriver_path = DRIVERS_PATH + "geckodriver"


class Message:
    def __init__(self, message_id=0, teacher="", channel="", subject="", url="", date="", text=""):
        self.message_id = message_id
        self.teacher = teacher
        self.subject = subject
        self.url = url
        self.date = date
        self.text = text
        self.channel = channel

    def __repr__(self):
        return (f'Message(\n'
                f'{self.message_id},\n'
                f'"{self.teacher}",\n'
                f'"{self.channel}",\n'
                f'"{self.subject}",\n'
                f'"{self.url}",\n'
                f'"{self.text}",\n'
                f')')


with open("config.json", encoding="utf_8") as f:
    config = json.load(f)
    TEACHERS = config["teachers"]
    REGEX = config["regex"]
    LOGIN = config["register"]["login"]
    PASSWORD = config["register"]["password"]
    del config


class Scraper:
    def __init__(self, driver="phantom"):
        if driver == "phantom":
            self.browser = webdriver.PhantomJS(
                executable_path=phantomdriver_path, service_log_path=os.path.devnull)
        elif driver == "chrome":
            self.browser = webdriver.Chrome(
                executable_path=chromedriver_path, service_log_path=os.path.devnull)
        elif driver == "gecko":
            self.browser = webdriver.Firefox(
                executable_path=geckodriver_path, service_log_path=os.path.devnull)
        else:
            raise Exception(f'Webdriver "{driver}" is not available"')
        self.wait = WebDriverWait(self.browser, 10)
        self.browser.set_window_size(1920, 1080)

    def login(self):
        self.browser.get("https://portal.librus.pl/rodzina/home")
        self.browser.find_element_by_class_name("btn-synergia-top").click()
        self.browser.find_elements_by_class_name(
            "dropdown-item--synergia")[1].click()
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.ID, "caLoginIframe")))
        self.browser.find_element_by_id("Login").send_keys(LOGIN)
        self.browser.find_element_by_id("Pass").send_keys(PASSWORD)
        self.browser.find_element_by_id("LoginBtn").click()
        return True

    def fetch_messages(self):
        self.wait.until(EC.presence_of_element_located(
            (By.ID, "icon-wiadomosci"))).click()
        messages = set()
        inbox = self.browser.find_element_by_css_selector(
            "table.decorated > tbody")
        for listing in inbox.find_elements_by_tag_name("tr"):
            labels = listing.find_elements_by_tag_name("td")
            if labels[2].get_attribute("style") == "font-weight: bold;":
            # if True:
                teacher = ""
                for t in TEACHERS.keys():
                    if t in labels[2].text:
                        teacher = t
                        break
                if teacher:
                    msg = Message(
                        labels[0].find_element_by_tag_name(
                            "input").get_attribute("value"),
                        labels[2].text,
                        TEACHERS[teacher],
                        labels[3].text,
                        labels[3].find_element_by_tag_name(
                            "a").get_attribute("href"),
                        labels[4].text
                    )
                    messages.add(msg)

        matched = set()
        for msg in messages:
            self.browser.get(msg.url)
            msg.text = self.browser.find_element_by_class_name(
                "container-message-content").text
            if re.search(REGEX, msg.text):
                matched.add(msg)
        return matched

    def close(self):
        self.browser.close()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    xd = Scraper()
    xd.login()
    msgs = xd.fetch_messages()
    for x in msgs:
        print(x)
    del xd
