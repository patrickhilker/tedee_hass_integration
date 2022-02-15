# tedee Custom Component

Integrate your tedee smart lock into Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This component gives access to your tedee smart lock. To use the integration you need the tedee bridge connected to your lock.

## Installation

This custom component can be installed using hacs. You need to add this repository as a custom repository (HACS -> three dots top right -> custom repositories). Add the link to this repository and choose `integration` in the select field. The custom component should display as a new discovered component in hacs and can now be installed. After installation restart Home Assistant.

### Setup

Put these lines into your `configuration.yaml`:

```yaml
lock:
  - platform: tedee
    access_token: your-tedee-pak
```

See the tedee api docs to learn how to [create a personal access key](https://tedee-tedee-api-doc.readthedocs-hosted.com/en/latest/howtos/authenticate.html#personal-access-key).

You will need these scopes:

   - Devices - Read
   - Operate - Lock


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
