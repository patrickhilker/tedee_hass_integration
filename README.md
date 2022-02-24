# 🤖🔒 tedee Custom Component

Integrate your [tedee smart lock](https://tedee.com/product-info/lock/) into [Home Assistant](https://www.home-assistant.io/).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This component gives basic access to your tedee smart lock. Right now it supports to lock and unlock your tedee and pull the spring. Also it gets some additional data as attributes (battery level, charging, connected, infos about pullspring).

To use the integration you need the [tedee bridge](https://tedee.com/product-info/bridge/) connected to your lock.

## Installation

This custom component can be installed using [HACS](https://hacs.xyz/).

- Make sure you have [HACS installed](https://hacs.xyz/docs/setup/prerequisites)
- Add a new custom repository to HACS (HACS - Integrations - three dots top right - Custom repositories)
- Insert the link to this repository as `Repository`
- Choose `Integration` in the `Category` field
- Click the add button
- The custom component should now display as a new discovered component in HACS
- Install it like every other HACS custom component
- Restart Home Assistant

### Setup

#### Create personal access key

See the tedee api docs to learn how to [create a personal access key](https://tedee-tedee-api-doc.readthedocs-hosted.com/en/latest/howtos/authenticate.html#personal-access-key).

You will need these scopes:

   - Devices - Read
   - Operate - Lock

#### Configuration

Go to the integrations page (Configuration - Devices & Services). Click the "+ Add Integration" button in the lower left corner and look for the "tedee" integration. Insert your personal access key and click submit.

After this you should see the tedee integration on your Devices & Services page. This component creates a device for every lock with a lock entity (`lock.name_of_your_lock`).

## Roadmap

- validate personal access key during setup
- make personal access key configurable after setup
- split out the battery level as a sensor

This project is open for your pull requests - just implement any feature you might need! 🚀

## Known issues

- the state of the lock gets updated every 10 seconds, so there is no realtime update (but it seems to be on tedees roadmap)
- if you add a lock after setup you have to restart Home Assistant to see the new device
- no real error reporting/handling