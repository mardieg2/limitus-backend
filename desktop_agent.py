# desktop_agent.py

import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MetaMaskReader:
    """
    A helper class to launch Microsoft Edge with the MetaMask extension,
    unlock the wallet, and fetch the balance shown in the MetaMask UI.
    """

    def __init__(self, extension_path: str, metamask_password: str, extension_id: str):
        """
        :param extension_path: The file path to the unpacked MetaMask extension folder.
        :param metamask_password: The password to unlock the MetaMask wallet.
        :param extension_id: The MetaMask extension ID (e.g. 'nkbihfbeogaeaoehlefnkodbefgpgknn')
        """
        self.extension_path = extension_path
        self.metamask_password = metamask_password
        self.extension_id = extension_id
        self.driver = None

    def setup_edge_with_metamask(self):
        """Initializes Edge with the MetaMask extension loaded."""
        edge_options = Options()
        # Load the unpacked MetaMask extension
        edge_options.add_argument(f"--load-extension={self.extension_path}")
        # If you prefer to see the browser instead of headless, omit the next line:
        # edge_options.add_argument("--headless")
        
        service = Service(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service, options=edge_options)
        return self.driver

    def unlock_metamask(self):
        """
        Navigates to the MetaMask extension page, enters the password,
        and waits for the main MetaMask UI to load.
        """
        if not self.driver:
            raise Exception("Driver not initialized. Call setup_edge_with_metamask() first.")
        
        # Construct the extension URL using the ID you pass in
        metamask_url = f"chrome-extension://{self.extension_id}/home.html"
        self.driver.get(metamask_url)

        # Wait for the password input to appear
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        # Enter the MetaMask password
        pw_field = self.driver.find_element(By.ID, "password")
        pw_field.send_keys(self.metamask_password)

        # Click the 'Unlock' button
        unlock_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Unlock')]")
        unlock_button.click()

        # Wait until the balance area is loaded
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".currency-display-component__text"))
        )

    def get_metamask_balance(self) -> str:
        """
        Reads the textual ETH balance from the MetaMask UI.
        """
        if not self.driver:
            raise Exception("Driver not initialized. Call setup_edge_with_metamask() first.")
        
        balance_el = self.driver.find_element(By.CSS_SELECTOR, ".currency-display-component__text")
        return balance_el.text

    def read_balance(self) -> str:
        """
        Main wrapper method:
          1) Setup driver
          2) Unlock metamask
          3) Grab the displayed balance
          4) Close the browser
        Returns the balance as a string.
        """
        try:
            self.setup_edge_with_metamask()
            self.unlock_metamask()
            balance = self.get_metamask_balance()
            return balance
        except Exception as exc:
            return f"Error reading MetaMask balance: {exc}"
        finally:
            if self.driver:
                self.driver.quit()
