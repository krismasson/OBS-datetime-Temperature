import obspython as obs
import datetime
from bs4 import BeautifulSoup as bs
import requests

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
# US english
LANGUAGE = "en-US,en;q=0.5"
URL = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=weather+Palm+Bay"
interval    = 10
source_name = "text"
temperature = 55

# ------------------------------------------------------------

def update_temp():
    global temperature
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html = session.get(URL)
    # create a new soup
    soup = bs(html.text, "html.parser")
    # store all results on this dictionary
    temperature = soup.find("span", attrs={"id": "wob_tm"}).text



def update_text():
    global interval
    global source_name
    global temperature

    source = obs.obs_get_source_by_name(source_name)
    


    if source is not None:
        now = datetime.datetime.now()
        zeros = now.strftime("%S")
        if (zeros == "00"):
            update_temp()


        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", now.strftime("%b %d %I:%M:%S %p ") + str(temperature) + "°")
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)

def refresh_pressed(props, prop):
    update_text()

# ------------------------------------------------------------

def script_description():
    return "Updates a text source to the current date and time"

def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "interval", 10)
    obs.obs_data_set_default_string(settings, "source", "")

def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 1, 3600, 1)

    p = obs.obs_properties_add_list(props, "source", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
    return props

def script_update(settings):
    global interval
    global source_name

    interval    = obs.obs_data_get_int(settings, "interval")
    source_name = obs.obs_data_get_string(settings, "source")

    obs.timer_remove(update_text)
    
    if source_name != "":
        obs.timer_add(update_text, interval * 1000)
