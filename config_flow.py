import voluptuous as vol
import homeassistant.helpers.config_validation as cv

DOMAIN = "tedee"

class TedeeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""
    
    async def async_step_user(self, info):
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN, default='no access token given'): cv.string})
        )
