# import time
# import unittest
# from selenium import webdriver

# class TestURLs(unittest.TestCase):
#     def setUp(self):
#         self.driver = webdriver.Chrome()

#     def tearDown(self):
#         self.driver.close()

#     def test_add_new_post(self):
#         """ Tests if the signin page works properly

#             1. Log the user in

#         """
#         # login
#         self.driver.get("http://sunsun.mn:5000/signin")

#         username_field = self.driver.find_element_by_name("email")
#         username_field.send_keys("manager123@sunsun.com")

#         password_field = self.driver.find_element_by_name("password")
#         password_field.send_keys("password")

#         login_button = self.driver.find_element_by_id("submit")
#         login_button.click()

#     def test_root_redirect(self):
#            """ Tests if the root URL gives a 302 """
#            result = self.client.get('/')
#            assert result.status_code == 302
#            assert "/blog/" in result.headers['Location']

# if __name__ == "__main__":
#     unittest.main()