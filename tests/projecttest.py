import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import unittest

basedir = os.path.abspath(os.path.dirname(__file__))

os.environ['DATABASE_URL'] = 'sqlite://'

class ProjectTest(unittest.TestCase):
    def setUp(self):
        # Could not get webdriver to find the website normally
        self.flask_process = subprocess.Popen(["flask", "run"])
        self.driver = webdriver.Chrome("./chromedriver")
        self.driver.get("http://localhost:5000/index")

    def tearDown(self):
        self.driver.quit()
        self.flask_process.terminate()

    def test_navigation(self):
        # Test logo click
        button = self.driver.find_element(By.CLASS_NAME, 'logo')
        button.click()
        expectedURL = 'http://localhost:5000/index'
        assert self.driver.current_url == expectedURL
