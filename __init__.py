import requests, json
from datetime import datetime
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
    "flood_warning_states": {
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
    },
    "pollen_federal_states": {
        "Schleswig-Holstein": 10,
        "Hamburg": 10,
        "Mecklenburg-Vorpommern": 20,
        "Niedersachsen": 30,
        "Bremen": 30,
        "Nordrhein-Westfalen": 40,
        "Brandenburg": 50,
        "Berlin": 50,
        "Sachsen-Anhalt": 60,
        "Thüringen":70 ,
        "Sachsen": 80,
        "Hessen": 90,
        "Rheinland-Pfalz": 100,
        "Saarland": 100,
        "Baden-Württemberg": 110,
        "Bayern": 120,
    },
        "pollen_regions": {
        "\u00d6stl. Niedersachsen": "östliches Niedersachsen",
        "Rhein.-Westf\u00e4l. Tiefland": "Rheinisch-Westfälisches Tiefland",
        "Tiefland Th\u00fcringen": "Thüringer Tiefland",
        "Th\u00fcringen": "Thüringen",
        "Mittelgebirge Th\u00fcringen": "Thüringer Mittelgebirge",
        "Baden-W\u00fcrttemberg": "Baden-Württemberg",
        "Mittelgebirge Baden-W\u00fcrttemberg": "Baden-Württemberg Mittelgebirge",
        "Allg\u00e4u/Oberbayern/Bay. Wald": "Allgäu, Oberbayern und Bayerischer Wald",
        "Bayern n\u00f6rdl. der Donau, o. Bayr. Wald, o. Mainfranken": "Bayern nördlich der Donau, ohne Bayerischen Wald und ohne Mainfranken",
        "Pollenflug-Gefahrenindex f\u00fcr Deutschland ausgegeben vom Deutschen Wetterdienst": "Pollenflug-Gefahrenindex für Deutschland, ausgegeben vom Deutschen Wetterdienst",
        "Donauniederungen": "Donauniederungen",
        "Inseln und Marschen": "Inseln und Marschen",
        "Geest,Schleswig-Holstein und Hamburg": "Geest, Schleswig-Holstein und Hamburg",
        "Westl. Niedersachsen/Bremen": "Westliches Niedersachsen und Bremen",
        "Ostwestfalen": "Ostwestfalen",
        "Mittelgebirge NRW": "Mittelgebirge Nordrhein-Westfalen",
        "Tiefland Sachsen-Anhalt": "Sachsen-Anhalt Tiefland",
        "Harz": "Harz",
        "Tiefland Sachsen": "Sachsen Tiefland",
        "Mittelgebirge Sachsen": "Sachsen Mittelgebirge",
        "Nordhessen und hess. Mittelgebirge": "Nordhessen und hessisches Mittelgebirge",
        "Rhein-Main": "Rhein-Main",
        "Rhein, Pfalz, Nahe und Mosel": "Rhein, Pfalz, Nahe und Mosel",
        "Mittelgebirgsbereich Rheinland-Pfalz": "Mittelgebirgsbereich Rheinland-Pfalz",
        "Saarland": "Saarland",
        "Oberrhein und unteres Neckartal": "Oberrhein und unteres Neckartal",
        "Hohenlohe/mittlerer Neckar/Oberschwaben": "Hohenlohe, mittlerer Neckar und Oberschwaben",
        "Mainfranken": "Mainfranken",
        "Mecklenburg-Vorpommern": "Mecklenburg-Vorpommern"
    },
    "pollen_days": {
        "heute": "today",
        "morgen": "tomorrow",
        "übermorgen": "dayafter_to"
    },
    "pollen_stress_factors": {
    "0": "keine Belastung",
    "0-1": "keine bis geringe Belastung",
    "1": "geringe Belastung",
    "1-2": "geringe bis mittlere Belastung",
    "2": "mittlere Belastung",
    "2-3": "mittlere bis hohe Belastung",
    "3": "hohe Belastung"
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
        self.flood_warning_states = self.settings.get('flood_warning_states', {})
        self.pollen_federal_states = self.settings.get('pollen_federal_states', {})
        self.pollen_regions = self.settings.get('pollen_regions', {})
        self.pollen_days = self.settings.get('pollen_days', {})
        self.pollen_stress_factors = self.settings.get('pollen_stress_factors', {})
        self.settings_change_callback = self.on_settings_changed
    
    def on_settings_changed(self, settings):
        LOG.info("Settings changed: {}".format(settings))
        # Handle settings changes if necessary

    #Functions
    ##Helpers
    def make_date_non_dayname(self, date):
        """
        Normally nice_date delivers speakable date always with name of the day e. g. 'Monday, 2th....'.
        """
        join_chr = ", "
        date = nice_date(date, lang = self.lang)
        date = date.split(",") #makes a list from utterance
        date_del = date.pop(0) #deletes first entry of list - the name of the day e.g. 'Monday. '
        date = join_chr.join(date) # makes a string of the list
        return date
    ##General functios
    ###State values
    def state_values(self, state):
        if state.lower() in self.flood_warning_states:
            state_name = self.flood_warning_states[state]['name']
            state_code = self.floo[state]['code']
            state_key = self.flood_warning_states[state]['key']
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
                results.append(answer[i]['name'] + " in " + answer[i]['locality'] + ", Postleitzahl " + answer[i]['postalCode'])
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
                    warn_area = data['data'][i]['areaDesc'].replace("Lkr.","Landkreis")
                    self.speak("Region: " + warn_area + ", Meldung: " + warn_type)
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

    ##travel warnings functions
    def fetch_travel_warnings(self, country=None):
        url = "https://www.auswaertiges-amt.de/opendata/travelwarning"
        headers = {
            'Accept': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            LOG.debug("Request result: " + str(data))
            if data['response']['contentList']:
                warnings = []
                partial_warnings = []
                situations_warnings = []
                situation_part_warnings = []
                no_warnings = []
                for i in data['response']['contentList']:
                    if data['response'][i]['warning']:
                        timestamp = data['response'][i]['lastModified']
                        date = datetime.fromtimestamp(timestamp)
                        warnings.append({"date": date, "message": data['response'][i]['title'],"country": data['response'][i]['countryName']})
                    if data['response'][i]['partialWarning']:
                        timestamp = data['response'][i]['lastModified']
                        date = datetime.fromtimestamp(timestamp)
                        partial_warnings.append({"date": date, "message": data['response'][i]['title'],"country": data['response'][i]['countryName']})
                    if data['response'][i]['situationWarning']:
                        timestamp = data['response'][i]['lastModified']
                        date = datetime.fromtimestamp(timestamp)
                        situations_warnings.append({"date": date, "message": data['response'][i]['title'],"country": data['response'][i]['countryName']})
                    if data['response'][i]['situationPartWarning']:
                        timestamp = data['response'][i]['lastModified']
                        date = datetime.fromtimestamp(timestamp)
                        situation_part_warnings.append({"date": date, "message": data['response'][i]['title'],"country": data['response'][i]['countryName']})
                    else:
                        no_warnings.append(data['response'][i]['countryName'])
                LOG.debug(str(warnings) + "\n\n" + str(partial_warnings) + "\n\n" + str(situations_warnings) + "\n\n" + str(situation_part_warnings))
                warning_counter = len(warnings)
                partial_warning_counter = len(partial_warnings)
                situation_warning_counter = len(situations_warnings)
                situation_part_warning_counter = len(situation_part_warnings)
                if warning_counter == 0 and partial_warning_counter == 0 and situation_warning_counter == 0 and situation_part_warning_counter == 0:
                    self.speak("Aktuell liegen keine Reisewarnungen und Sicherheitsinformationen vor.")
                if warning_counter != 0:
                    warning_string = "Es gibt " + str(warning_counter) + " Reisewarnungen  für folgende Länder: "
                    countries = []
                    for country in warnings:
                        countries.append(country['country'])
                    countries_string = ", ".join(countries)
                    countries_string = countries_string.replace(", ", ",  -  ")
                    self.speak(warning_string + countries_string)
                    sleep(len(countries)) #necessary to avoid TTS overlapping
                if warning_counter != 0 and partial_warning_counter != 0:
                    warning_string = " und " + str(partial_warning_counter) + " Sicherheitshinweise."
                    self.speak(warning_string)
                    answer = self.ask_yesno("ask_for_part_warnings")
                    if answer == "yes":
                        self.speak("Sicherheitshinweise gibt es für folgende Länder: ")
                        countries = []
                        for country in partial_warnings:
                            countries.append(country['country'])
                        countries_string = ", ".join(countries)
                        self.speak(countries_string)
                        sleep(len(countries)) #necessary to avoid TTS overlapping
                    else:
                        pass
                if warning_counter == 0 and partial_warning_counter != 0:
                    warning_string += "Es gibt Sicherheitshinweise für " + str(partial_warning_counter) + "Länder."
                    self.speak(warning_string)
                    answer = self.ask_yesno("ask_for part_warnings")
                    if answer == "yes":
                        self.speak("Es gibt " + str(partial_warning_counter) + " Sicherheitshinweise für folgende Länder: ")
                        countries = []
                        for country in partial_warnings:
                            countries.append(country['country'])
                        countries_string = ", ".join(countries)
                        self.speak(countries_string)
                    else:
                        pass
                if situation_warning_counter != 0 or situation_part_warning_counter != 0:
                    warning_string = "Es gibt allgemeine Hinweise für " + str(situation_warning_counter + situation_part_warning_counter) + "Länder"
                    self.speak(warning_string)
                    answer = self.ask_yesno("ask_for part_warnings")
                    if answer == "yes":
                        countries = []
                        for country in situations_warnings:
                            countries.append(country['country'])
                        for country in situation_part_warnings:
                            countries.append(country['country'])
                        countries_string = ", ".join(countries)
                        self.speak(countries_string)
                    else:
                        pass
                #i = 0
                #if warnings:
                    #while i < len(warnings):
                        #LOG.debug("Warnings are: " + str(warnings[i]))
                        #date = self.make_date_non_dayname(warnings[i]['date'])
                        #message = warnings[i]['message']
                        #if country != None and country.lower() == warnings[i]['countyName'].lower():
                            #self.speak("Ja, es gibt eine Reisewarnung für " + country + " seit dem " + date)
                            #break
                        #self.speak("Reisewarnung für " + message + " seit dem " + date)
                        #sleep(5)
                        #i += 1
            else:
                self.speak("Aktuell liegen keine Reisewarnungen vor.")
        except requests.exceptions.RequestException as e:
            self.speak("Ein Fehler bei der API-Anfrage ist aufgetreten: " + str(e))
            LOG.debug("Exception: " + str(e))
        except json.JSONDecodeError:
            self.speak("Fehler beim Parsen der JSON-Antwort.")

    ##Pollen warnings
    def speak_pollen_warning(self, federal_state, day):
        url = 'https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json'
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        try:
            fed_st_nr = self.pollen_federal_states[federal_state]
        except KeyError as e:
            self.speak("Das Bundesland " + str(e) + " gibt es nicht.")
            LOG.info("Federal state " + str(e) + " does not exist.")
            return
        try:
            day = self.pollen_days[day]
        except KeyError:
            self.speak("Nur die Zeitangaben heute, morgen oder übermorgen sind zulässig.")
            LOG.info("Time specification invalid.")
            return
        i = 0
        regions = {}
        new_region = {}
        while i < len(data['content']):
            pollen = []
            if data['content'][i]['region_id'] == fed_st_nr:
                for key in data['content'][i]['Pollen'].keys():
                    if data['content'][i]['Pollen'][key][day] != '0':
                        stress_factor = self.pollen_stress_factors[data['content'][i]['Pollen'][key][day]]
                        pollen.append(key + ", " + stress_factor)
                if data['content'][i]['partregion_name'] == "":
                    new_region = {str(data['content'][i]['region_name']): pollen}
                else:
                    new_region = {str(data['content'][i]['partregion_name']): pollen}
            regions.update(new_region)
            i += 1
        self.speak("Folgende Belastungen sind für " + federal_state + " gemeldet: ")
        for key in regions:
            self.speak("Region " + self.pollen_regions[key] + ": " + ". ".join(regions[key]))


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

    @intent_handler('travel_warnings.intent')
    def handle_travel_warnings(self, message):
        country = message.data.get('country', None)
        self.fetch_travel_warnings(country)
    
    @intent_handler('pollen_warning.intent')
    def handle_pollen_warning(self, message):
        federal_state = self.get_response('ask_for_federal_state')
        day = self.get_response('ask_for_day').lower()
        self.speak_pollen_warning(federal_state, day)

    @intent_handler('pollen_warning2.intent')
    def handle_pollen_warning2(self, message):
        federal_state = message.data.get('federalstate')
        federal_state = federal_state[0].upper() + federal_state[1:]
        day = message.data.get('day')
        self.speak_pollen_warning(federal_state, day)
