import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries

from homeassistant.const import CONF_ACCESS_TOKEN

DOMAIN = "tedee"

class TedeeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    
    def __init__(self):
        """Initialize."""
        self._errors = {}
    
    async def async_step_user(self, user_input=None):
        self._errors = {}
        
        if user_input is not None:
            return self.async_create_entry(title=Tedee, data=user_input)
        
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN): cv.string})
        )
