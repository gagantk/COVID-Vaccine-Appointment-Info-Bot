import requests
from datetime import datetime, timedelta
from helpers import constants


class Helper:

    def __init__(self, pincode: str) -> None:
        self.data = dict()
        self.pincode = pincode
        self.process_results()

    def process_results(self, pincode: str = None) -> None:
        if not pincode:
            pincode = self.pincode
        res = requests.get(
            constants.BASE_URL,
            params={
                'pincode': pincode,
                'date': (datetime.now() + timedelta(days=1)).strftime(constants.DATE_FORMAT)
            },
            headers=constants.HEADERS
        )
        self.status = res.status_code
        if res.status_code == 401:
            self.status = False
        else:
            self.status = True
            self.data[pincode] = res.json()['centers']

    def check_results(self):
        return self.status

    def check_age_category(self, age_category: str, pincode: str) -> bool:
        self.age_category = age_category
        age_categories = set([session['min_age_limit']
                              for center in self.data[pincode] for session in center['sessions']])
        if int(age_category) in age_categories:
            return True
        return False

    def get_centers(self, pincode: str = None) -> list:
        if pincode != self.pincode:
            self.process_results(pincode)
        details = []
        for center in self.data[pincode]:
            age_categories = set([str(session['min_age_limit'])
                                  for session in center['sessions']])
            if self.age_category in age_categories:
                details.append((center['name'], str(center['center_id'])))
        return details

    def get_center_details(self, center_id: str) -> str:
        text = ''
        for center in self.data[self.pincode]:
            if str(center['center_id']) == center_id:
                text += f"{center['name']}, {center['state_name']}, {center['pincode']}"
                for session in center['sessions']:
                    text += f"\n\n{session['date']}:\n"
                    text += f"Slots Available: {session['available_capacity']}"
                    if session['slots']:
                        text += f"\nSlots Timings: {', '.join(session['slots'])}"
                    else:
                        text += f"\nSlots Timings: Data Not Available"
                    if session['vaccine']:
                        text += f"\nVaccine: {session['vaccine']}"
        return text
