# 🤖🔒 tedee Custom Component

Integrate your [tedee smart lock](https://tedee.com/product-info/lock/) into [Home Assistant](https://www.home-assistant.io/).

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)  
[![issues_badge](https://img.shields.io/github/issues-raw/patrickhilker/tedee_hass_integration?style=for-the-badge)](https://github.com/patrickhilker/tedee_hass_integration/issues)  


This component gives Home Assistant control of your tedee smart lock. It supports to lock and unlock your tedee lock and pull the spring (if available). Also, it gets some additional data as attributes (battery level, charging, connected, infos about pullspring), a battery sensor and buttons triggering unlocking & unlatching. Both tedee PRO and GO are supported.

> **Note**
> To use the integration you need the [tedee bridge](https://tedee.com/product-info/bridge/) connected to your lock.

## Installation

This custom component can be installed using [HACS](https://hacs.xyz/).

> **Warning**
>  If you are a former user of [joerg65/tedee_lock](https://github.com/joerg65/tedee_lock), please uninstall it by deleting `/config/custom_components/tedee_lock` and remove the configuration from your `configuration.yaml`. You can reuse the personal access key, so you might keep it.

## Setup

### Create personal access key

See the tedee api docs to learn how to [create a personal access key](https://tedee-tedee-api-doc.readthedocs-hosted.com/en/latest/howtos/authenticate.html#personal-access-key).

You will need these scopes:

   - Devices - Read
   - Operate - Lock

### Installation

Go to the integrations page (Configuration - Devices & Services). Click the "+ Add Integration" button in the lower left corner and look for the "tedee" integration. Insert your personal access key and click submit.

After this you should see the tedee integration on your Devices & Services page. This component creates a device for every lock with a lock entity (`lock.name_of_your_lock`).

## Configuration

You can change the following settings after setting up the integration, by going to the integration's settings and pressing the "CONFIGURE" button:

- **Personal Access Key**: You can update your personal access key should it expire soon
- **Unlock pulls latch**: If checked, a "normal" unlock of your lock will also pull the latch. This is like in the tedee App when you have the "auto-pull" enabled. (**Default:** Disabled)

## Roadmap

This project is open for your pull requests - just implement any feature you might need! 🚀

## Known issues

- The state of the lock gets updated every 15 seconds, so there is no realtime update (but it seems to be on tedees roadmap)
- If you add a lock after setup reload the integration to see the new device
- If the tedee server is not available during Home Assistant startup the locks will not come available.
