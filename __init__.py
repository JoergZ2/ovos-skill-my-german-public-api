import urllib3, json
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill
from ovos_bus_client.session import SessionManager
from ovos_date_parser import extract_datetime, nice_date

http = urllib3.PoolManager()
# -*- coding: utf-8 -*-
DEFAULT_SETTINGS = {
    "__mycroft_skill_firstrun": "False"
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
        self.settings_change_callback = self.on_settings_changed
    
    def on_settings_changed(self, settings):
        LOG.info("Settings changed: {}".format(settings))
        # Handle settings changes if necessary

    #Functions
    ##postalcode functions
    def make_query_plz(self, state, town, street):
        state = state[:2].lower()  # Ensure state is in lowercase and only first two letters
        base_url = "https://openplzapi.org/" + state + "/Streets?name=" \
                + street + "&locality=" + town + "&page=1&pageSize=10"
        response = http.request('GET',base_url, headers={"accept": "application/json"})
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
