# HomeSeer Custom Integration for Home Assistant Forked from https://github.com/marthoc/homeseer

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) 

[Home Assistant](https://home-assistant.io/) custom integration supporting [HomeSeer](www.homeseer.com) Smart Home Software (HS3 and HS4).

This integration will create Home Assistant entities for the following types of devices in HomeSeer by default:

- "Switchable" devices (i.e. devices with On/Off controls) as a Home Assistant switch entity
- "Dimmable" devices (i.e. devices with On/Off and Dim controls) as a Home Assistant light entity
- "Lockable" devices (i.e. devices with Lock/Unlock controls) as a Home Assistant lock entity
- "Status" devices (i.e. devices with no controls) as a Home Assistant sensor entity

The type of entity created can also depend on whether a "quirk" has been added for the device (see below) and options chosen by the user during configuration. This custom integration currently supports creating entities for the following Home Assistant platforms: binary sensor, cover, light, lock, scene, sensor, switch. Fan and Media Player entities will be added in a future update!

## Pre-Installation
This integration communicates with HomeSeer via both JSON and ASCII. You must enable control using JSON and ASCII commands in Tools/Setup/Network in the HomeSeer web interface. 

## Installation
This custom integration must be installed for it to be loaded by Home Assistant.

_The recommended installation method is via [HACS](https://hacs.xyz)._

### HACS

1. Add https://github.com/Airey001/homeseer as a custom repository in HACS.
2. Search for "HomeSeer" under "Integrations" in HACS.
3. Click "Install".
4. Proceed with Configuration (see below).

### Manual

1. Create a `custom_components` director in your Home Assistant configuration directory.
2. Download the latest release from the GitHub "Releases" page.
3. Copy the custom_components/homeseer directory from the archive into the custom_components directory in your Home Assistant configuration directory.
4. Restart Home Assistant and proceed with Configuration (see below).

## Configuration

To enable the integration, add it from the Configuration - Integrations menu in Home Assistant: click `+`, then click "HomeSeer".

The following options must be configured at the first stage of the configuration:

|Parameter|Description|Default|
|---------|-----------|-------|
|Host|The IP address of the HomeSeer instance.|N/A|
|Username|The username used to log into HomeSeer.|"default"|
|Password|The password used to log into HomeSeer.|"default"|
|HTTP Port|The HTTP port of the HomeSeer instance.|80|
|ASCII Port|The ASCII port of the HomeSeer instance.|11000|

After clicking submit, the following additional options will be presented to the user:

|Parameter|Description|Default|
|---------|-----------|-------|
|Namespace|A unique string identifying this HomeSeer instance. You may input any string. (This will be used in a future release to allow connections to multiple HomeSeer instances.)|"homeseer"|
|Entity Name Template|A template (Jinja2 format) describing how Home Assistant entities will be named. Default format is "location2 location name".|"{{ device.location2 }} {{ device.location }} {{ device.name }}"|
|Create Scenes from HomeSeer Events?|If this box is ticked, a Home Assistant Scene will be created for each Event in HomeSeer. Events can be filtered by group during a later stage of the configuration.|True|

After clicking submit, the user will be presented with successive dialogs to select: 
- Technology interfaces present in HomeSeer to allow in Home Assistant. The type "HomeSeer" represents devices native to HomeSeer such as virtual devices. (Note: Z-Wave is best-supported, but most devices from other interfaces should 'just work'.) Deselecting an interface name here means that devices from that interface will NOT create Entities in Home Assistant.
- If the user has ticked "Create scenes from HomeSeer Events?", the user will be able to select Event Groups in HomeSeer to allow in Home Assistant. Selecting any groups here will allow ONLY those groups; selecting no groups here will allow ALL event groups. The selected groups (or all groups) will create a Home Assistant Scene for each Event in that group.
- Switches and Dimmers from HomeSeer to be represented as Covers (i.e. blinds or garage doors) in Home Assistant. Device refs selected here will not create a Switch or Light entity in Home Assistant but instead a garage door or blind.

## Quirks

Certain devices in HomeSeer should be represented as an entity other than their HomeSeer features would suggest. Quirks exist in this integration to allow "forcing" a certain type of device to be a certain Home Assistant entity. Currently, there are quirks for the following types of devices:
- Z-Wave Barrier Operator as "cover" (i.e. a garage door)
- Z-Wave Central Scene as Home Assistant events (see below)
- Z-Wave Sensor Binary as "binary sensor"

Further quirks can be requested by opening an issue in this repository with information about the device (and ideally, debug logs from libhomeseer or the integration itself which will contain the information necessary to create the quirk).

## Home Assistant events

Certain HomeSeer devices should be represented as a Home Assistant event - no entity will be created for these devices. Instead, when one of these devices are updated in HomeSeer, this integration will fire an event on the Home Assistant event bus which can be used to trigger a Home Assistant Automation.

The event will contain the following parameters:

`event_type`: homeseer_event  
`event_data`:
- `id`: Device Ref of the Central Scene device in HomeSeer.
- `event`: Numeric value of the device in HomeSeer for a given event.

Currently, the following types of HomeSeer devices will fire events in Home Assistant:
- Z-Wave Central Scene

Support for other "stateless" devices (i.e. remotes) such as these can be added in future updates. Please request support by opening an issue in this repository.

## Services

The integration exposes the following services:
- homeseer.control_device_by_value

### homeseer.control_device_by_value

Allows the user to set any value on a HomeSeer device.  

|Parameter|Description|Format|Required?|
|---------|-----------|------|---------|
|ref|Ref corresponding to the HomeSeer device |Integer|True|
|value|Value to set the device to (integer) |Integer|True|

## Support

Please open an issue on this repository for any feature requests or bug reports. Some issues may be moved to the upstream repo marthoc/libhomeseer if the request or bug relates to the underlying python library.

Debug logs are essential when requesting new features or for tracking down bugs. You can enable debug logging for the integration by adding the following to your configuration.yaml:

```yaml
logger:
  default: critical
  logs:
    custom_components.homeseer: debug
    libhomeseer: debug
```
The above entry will essentially silence the logs except for debug output from this integration and the underlying library.

The only sensitive or personally identifying information contained in the debug logs will be your HomeSeer username, if you have supplied a value other than "default" (no passwords or external IPs are included in the debug logs).

## Caveats

The HomeSeer JSON API exposes only limited information about the devices present in HomeSeer. Requests for certain features may be declined due to the required data not being present in the API response.
