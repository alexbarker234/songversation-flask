from selenium import webdriver
from webdriver.common.by import By
from webdriver.support import expected_conditions as EC
from webdriver.support.ui import Select
from seleniumbase import BaseCase


class SongversationTester:
  def __init__(self):
      self.driver = webdriver.Chrome()

  def test_navigation():
    driver.get('http://localhost:5000')

    # Test logo click
    button = driver.find_element(By.Class, 'logo')
    button.click()
    expectedURL = 'http://localhost:5000/index'
    actualURL = driver.current_url
    assert actualURL == expectedURL

    # Test dropdown menu selection
    dropdown = driver.find_element(By.ID, 'dropdownMenuButton')
    dropdown.click()
    option = dropdown.select_by_visible_text('Statistics')
    option.click()
    assert driver.current_url == 'http://localhost:5000/stats'
    option = dropdown.select_by_visible_text('Friends')
    option.click()
    assert driver.current_url == 'http://localhost:5000/friends'
    
    option = dropdown.select_by_visible_text('Sign Out')
    option.click()
    assert 'Log in with Spotify' in driver.page_source