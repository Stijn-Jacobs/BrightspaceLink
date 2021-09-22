import os
import pathlib
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import datetime
from webdriver_manager.chrome import ChromeDriverManager
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import Settings

SCOPES = ['https://www.googleapis.com/auth/calendar']

service = None

# Start selenium webdriver
chrome_options = Options()
scriptDirectory = pathlib.Path().absolute()
chrome_options.add_argument(f"user-data-dir={scriptDirectory}\\chrome-data-temp")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get("https://brightspace.avans.nl")


def save_event(title, date):
    if service is not None:
        date = date.date()
        event = {
            'summary': str(title),
            'start': {
                'date': str(date)
            },
            'end': {
                'date': str(date)
            },
            'reminders': {
                'useDefault': True,
            },
        }
        service.events().insert(calendarId=Settings.CALENDAR_ID, body=event).execute()
        print("Added: " + title)
    else:
        print("Not authenticated with Google")


def run():
    for index, row in enumerate(driver.find_elements_by_xpath('//*[@id="z_b"]/tbody/tr')):
        title_elements = row.find_elements_by_xpath('//*[@id="z_b"]/tbody/tr[' + str(index + 1) + ']/th/div[1]/div/a')
        try:
            date_element = row.find_element_by_xpath('//*[@id="z_b"]/tbody/tr[' + str(index + 1) + ']/td[4]/label')
        except NoSuchElementException:
            continue
        if len(title_elements) > 0:
            # Found valid title and date
            title = title_elements[0].text
            date = datetime.datetime.strptime(date_element.text, '%d %B %Y %H:%M')
            save_event(title, date)


def login_google():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


service = login_google()

while True:
    inp = input("Enter command")
    if inp == "run":
        run()
    elif inp == "login":
        service = login_google()
