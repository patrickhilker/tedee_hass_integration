# tedee Custom Component

Integrate your [tedee smart lock](https://tedee.com/product-info/lock/) into [Home Assistant](https://www.home-assistant.io/).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This component gives very basic access to your tedee smart lock. Right now it supports to lock and unlock your tedee.

To use the integration you need the [tedee bridge](https://tedee.com/product-info/bridge/) connected to your lock.

## Installation

This custom component can be installed using [HACS](https://hacs.xyz/).

- Make sure you have [HACS installed](https://hacs.xyz/docs/setup/prerequisites)
- Add a new custom repository to HACS (Home Assistant - left menu - HACS - three dots top right - custom repositories)
- Insert the link to this repository in the textfield
- Choose `integration` in the select field
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

Copy these lines into your `configuration.yaml` and replace `your-tedee-pak` with your personal access key:

```yaml
lock:
  - platform: tedee
    access_token: your-tedee-pak
```


Restart Home Assistant again. After this you should see your lock as a new entity (`lock.name_of_your_lock`) in Home Assistant.

## Usage examples

![Image of Tede Lock Entity](images/Lock_Entity.png)

Here is how I made a horizontal-stack with two custom button-cards:

```yaml
type: horizontal-stack
title: Haustür
cards:
  - entity: lock.lock_326b
    type: 'custom:button-card'
    state:
      - value: locked
        color: gray
        icon: 'mdi:lock'
        name: verriegelt
      - value: unlocked
        color: orange
        icon: 'mdi:lock'
        name: verriegeln
    tap_action:
      action: call-service
      service: lock.lock
      service_data:
        entity_id: lock.lock_326b
  - entity: lock.lock_326b
    type: 'custom:button-card'
    state:
      - value: unlocked
        color: gray
        icon: 'mdi:lock-open'
        name: entriegelt
      - value: locked
        color: green
        icon: 'mdi:lock-open'
        name: entriegeln
    tap_action:
      action: call-service
      service: lock.unlock
      service_data:
        entity_id: lock.lock_326b
```
![Image of Tede Lock with button-cards](images/Lock_two_button_cards.png)
