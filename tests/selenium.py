import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from app import app, db

class SongversationTester(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        if not self.driver:
            self.skipTest('Web browser not available')
        else:
            self.app = app.test_client()
            self.driver.maximize_window()
            self.driver.get('http://localhost:5000')

    def tearDown(self):
        if self.driver:
            self.driver.close()

    def test_navigation(self):

        # Test logo click
        button = self.driver.find_element(By.ID, 'logo')
        button.click()
        expectedURL = 'http://localhost:5000/index'
        actualURL = self.driver.current_url
        assert actualURL == expectedURL

        # Test dropdown menu selection
        dropdown = self.driver.find_element(By.ID, 'dropdownMenuButton')
        dropdown.click()
        option = dropdown.select_by_visible_text('Statistics')
        option.click()
        assert self.driver.current_url == 'http://localhost:5000/stats'
        option = dropdown.select_by_visible_text('Friends')
        option.click()
        assert self.driver.current_url == 'http://localhost:5000/friends'

        option = dropdown.select_by_visible_text('Sign Out')
        option.click()
        assert 'Log in with Spotify' in self.driver.page_source
