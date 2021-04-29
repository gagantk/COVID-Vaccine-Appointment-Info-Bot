import os

BASE_URL = 'https://api.cowin.gov.in/api/v2/appointment/sessions/calendarByPin'
DATE_FORMAT = r'%d-%m-%Y'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}
TOKEN = os.getenv('TOKEN')
MY_PROFILE = int(os.getenv('MY_PROFILE'))
