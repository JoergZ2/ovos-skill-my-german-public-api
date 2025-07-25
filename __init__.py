import requests, json
from time import sleep
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill
from ovos_bus_client.session import SessionManager
from ovos_date_parser import extract_datetime, nice_date

# -*- coding: utf-8 -*-
DEFAULT_SETTINGS = {
    "__mycroft_skill_firstrun": "False",
    "states": {
        "schleswig-holstein": {
            "name": "Schleswig-Holstein",
            "code": "SH",
            "key": "1"
        },
        "hamburg": {
            "name": "Hamburg",
            "code": "HH",
            "key": "2"
        },
        "niedersachsen": {
            "name": "Niedersachsen",
            "code": "NI",
            "key": "3"
        },
        "bremen": {
            "name": "Bremen",
            "code": "HB",
            "key": "4"
        },
        "nordrhein-westfalen": {
            "name": "Nordrhein-Westfalen",
            "code": "NW",
            "key": "5"
        },
        "hessen": {
            "name": "Hessen",
            "code": "HE",
            "key": "6"
        },
        "rheinland-pfalz": {
            "name": "Rheinland-Pfalz",
            "code": "RP",
            "key": "7"
        },
        "baden-württemberg": {
            "name": "Baden-Württemberg",
            "code": "BW",
            "key": "8"
        },
        "bayern": {
            "name": "Bayern",
            "code": "BY",
            "key": "9"
        },
        "saarland": {
            "name": "Saarland",
            "code": "SL",
            "key": "10"
        },
        "berlin": {
            "name": "Berlin",
            "code": "BE",
            "key": "11"
        },
        "brandenburg": {
            "name": "Brandenburg",
            "code": "BB",
            "key": "12"
        },
        "mecklenburg-vorpommern": {
            "name": "Mecklenburg-Vorpommern",
            "code": "MV",
            "key": "13"
        },
        "sachsen": {
            "name": "Sachsen",
            "code": "SN",
            "key": "14"
        },
        "sachsen-anhalt": {
            "name": "Sachsen-Anhalt",
            "code": "ST",
            "key": "15"
        },
        "thueringen": {
            "name": "Thüringen",
            "code": "TH",
            "key": "16"
        }
    }
}

class MyGermanPublicApi(OVOSSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # be aware that below is executed after `initialize`
        self.override = True

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=False,
            network_before_load=False,
            gui_before_load=False,
            requires_internet=True,
            requires_network=False,
            requires_gui=False,
            no_internet_fallback=True,
            no_network_fallback=True,
            no_gui_fallback=True,
        )
    
    def initialize(self):
        #from template
        self.settings.merge(DEFAULT_SETTINGS, new_only=True)
        self.states = self.settings.get('states', {})
        LOG.debug("States loaded: {}".format(self.states))
        self.settings_change_callback = self.on_settings_changed
    
    def on_settings_changed(self, settings):
        LOG.info("Settings changed: {}".format(settings))
        # Handle settings changes if necessary

    #Functions
    ##General functios
    ###State values
    def state_values(self, state):
        if state.lower() in self.states:
            state_name = self.states[state]['name']
            state_code = self.states[state]['code']
            state_key = self.states[state]['key']
            return (state_name, state_code, state_key)

    ##postalcode functions
    def make_query_plz(self, state, town, street):
        state = state[:2].lower()  # Ensure state is in lowercase and only first two letters
        base_url = "https://openplzapi.org/" + state + "/Streets?name=" \
                + street + "&locality=" + town + "&page=1&pageSize=10"
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(base_url, headers=headers)
        return response.json()
    #next functions

    def prepare_answer(self, answer):
        if not answer:
            return None
        elif len(answer) == 1:
            postalcode = answer[0]['postalCode']
            return postalcode
        else:
            results = []
            i = 0
            while i < len(answer):
                results.append(answer[i]['name'] + "in " + answer[i]['locality'] + "postleitzahl " + answer[i]['postalCode'])
                i += 1
            return "Es gibt mehrere Ergebnisse: " + ", ".join(results)

    ##flood warning functions
    def fetch_flood_warnings(self,states=None):
        if states is None:
            states = ''
        else:
            states = states
        url = 'https://api.hochwasserzentralen.de/public/v1/data/alerts?states=' + states
        headers = {
            'Accept': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            LOG.debug("Request result: " + str(data))
            # Check for key 'data' and length of key
            if 'data' in data and len(data['data'])>0:
                i = 0
                while i < len(data['data']):
                    warn_type = data['data'][i]['lhpClassName']
                    warn_area = data['data'][i]['areaDesc']
                    self.speak("Region: " + warn_area + ", Warnungsart: " + warn_type)
                    if len(data['data']) > 1 and len(data['data']) - i > 0:
                        sleep(3)
                    i += 1
            else:
                self.speak("Aktuell liegen keine Hochwasserdaten vor.")

        except requests.exceptions.RequestException as e:
            self.speak("Ein Fehler bei der API-Anfrage ist aufgetreten: " + e)
        except json.JSONDecodeError:
            self.speak("Fehler beim Parsen der JSON-Antwort.")


    ##traffic jam functions
    def fetch_traffic_jam(self, highway):
        highway = highway.replace(" ", "").upper()
        url = "https://verkehr.autobahn.de/o/autobahn/" + highway + "/services/warning"
        headers = {
            'Accept': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            LOG.debug("Request result: " + str(data))
            if 'warning' in data:
                count_warning = len(data['warning'])
                if count_warning == 0:
                    self.speak("Es gibt keine Verkehrsmeldungen für die Autobahn " + highway + ".")
                if count_warning == 1:
                    warn_location = data['warning'][0]['description'][3].replace("->", "Richtung")
                    if data['warning'][0]['description'][5]:
                        warn_reason = data['warning'][0]['description'][5]
                    else:
                        warn_reason = data['warning'][0]['description'][2].rstrip(",")
                        warn_reason = warn_reason.replace("->", "Richtung").replace("AS", "Ausfahrt").replace(".",",")
                    self.speak(warn_location + ", " + warn_reason)
                if count_warning > 1:
                    self.speak("Es gibt " + str(count_warning) + " Verkehrsmeldungen für die Autobahn " + highway + ".")
                    sleep(6)  # Wait for 5.5 seconds before reading the first warning
                    i = 0
                    while i < count_warning:
                        answer = data['warning'][i]['description'][3].replace("->", "Richtung").replace("AS", "Ausfahrt").replace(".",",")
                        i_natural = str(i + 1)
                        len_answer = len(answer)
                        self.speak("Störung " + i_natural + ":  " + answer)
                        LOG.debug("Zeichenzahl der Störungen, Störung " + i_natural + ", Anzahl: " + str(len_answer))
                        if count_warning - i > 0:
                            if len_answer > 100:
                                sleep(12.5)
                            elif len_answer > 90:
                                sleep(10)
                            elif len_answer > 80:
                                sleep(8.5)
                            else:
                                sleep(5)
                        i += 1
                    self.speak("Ende der Verkehrsmeldungen für die " + highway + ".")
            else:
                self.speak("Aktuell liegen keine Verkehrsdaten vor.")
        except requests.exceptions.RequestException as e:
            self.speak("Ein Fehler bei der API-Anfrage ist aufgetreten: " + e)
        except json.JSONDecodeError:
            self.speak("Fehler beim Parsen der JSON-Antwort.")

    #Intents    
    @intent_handler('postalcode_dialog.intent')
    def handle_postalcode_dialog(self, message):
        town = self.get_response('ask_for_town', num_retries=1)
        street = self.get_response('ask_for_street', num_retries=1)
        street = street.replace("straße","str.") #openplz doesn't have 'straße' only 'str.'
        answer = self.make_query_plz(self.lang, town, street)
        answer = self.prepare_answer(answer)
        if answer:
            self.speak(answer)
        else:
            self.speak_dialog('no_result')

    @intent_handler('flood_warnings.intent')
    def handle_flood_warnings_all(self, message):
        state = message.data.get('state', None)
        if state is not None:
            LOG.debug("State is: " + str(state))
            state = self.state_values(state)
            state = state[1]  # Get the state code for selection of federal stae
        else:
            state = ''
        self.fetch_flood_warnings(states=state)

    @intent_handler('traffic_jam.intent')
    def handle_traffic_jam(self, message):
        highway = message.data.get('highway', None)
        if highway is not None:
            self.fetch_traffic_jam(highway)
        else:
            self.speak("Es muss eine Autobahnnumerin der Form A 39 angegeben werden.")
