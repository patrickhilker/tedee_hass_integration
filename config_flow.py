import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import CONF_ACCESS_TOKEN

DOMAIN = "tedee"

class TedeeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=Tedee, data=user_input)
        
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN): cv.string})
        )
