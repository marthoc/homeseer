# HomeSeer HS3 Custom Component for Home Assistant

## Supported Devices

Z-Wave devices of the following types should create entities in Home Assistant:
- Z-Wave Barrier Operator (as Home Assistant cover)
- Z-Wave Battery (as Home Assistant sensor)
- Z-Wave Door Lock (as Home Assistant lock)
- Z-Wave Sensor Binary (as Home Assistant binary sensor)
- Z-Wave Sensor Multilevel (as Home Assistant sensor) 
- Z-Wave Switch (as Home Assistant switch)
- Z-Wave Switch Binary (as Home Assistant switch)
- Z-Wave Switch Multilevel (as Home Assistant light or cover)
- Z-Wave Central Scene (as Home Assistant event - see below)
- Z-Wave Temperature (as Home Assistant sensor)
- Z-Wave Relative Humidity (as Home Assistant sensor)
- Z-Wave Luminance (as Home Assistant sensor)
- Z-Wave Fan State for HVAC (as Home Assistant sensor)
- Z-Wave Operating State for HVAC (as Home Assistant sensor)

HomeSeer Events will be created as Home Assistant scenes (triggering the scene in Home Assistant will run the HomeSeer event).

### Central Scene devices

HomeSeer devices of the type "Z-Wave Central Scene" will not create an entity in Home Assistant; instead, when a Central Scene device is updated in HomeSeer, this component will fire an event on the Home Assistant event bus which can be used in Automations.

`event_type`: homeseer_event  
`event_data`:
- `id`: Device Ref of the Central Scene device in HomeSeer.
- `event`: Numeric value of the Central Scene device in HomeSeer for a given event.

## Install

0. Enable the ASCII connection in HomeSeer (required to receive device updates in Home Assistant).
1. Create the directory `custom_components` inside your Home Assistant config directory.
2. `cd` into the `custom_components` directory and do `git clone https://github.com/marthoc/homeseer`.
3. Start Home Assistant and configure the integration via the Configuration/Integrations menu.
4. Problems with certain devices (i.e. not supported yet) will be reported in the debug logs for the component/libhomeseer.

## Upgrade

0. Stop Home Assistant
1. `cd` into the `custom_components/homeseer` directory and do `git pull`.
2. Start Home Assistant

### Namespace

In order to generate unique ids for entities to enable support for the entity registry (most importantly, allowing users to rename entities and change entity ids from the UI), a unique string is required. Namespace can be any string you like. If this string changes, all entities will generate new entries in the entity registry, so only change this string if you absolutely know what you are doing.

### Name Template

The HomeSeer integration will generate default entity names and ids in HomeAssistant when devices are added for the first time.
By default, the generated name is of the form "location2 location name". You can customize the name generation by 
specifying your own Jinja2 template in "name_template". This template will only have an effect on newly added devices and
won't change the names of existing entities.

Example:
- HomeSeer location2 "Main Floor"
- HomeSeer location "Living Room"
- HomeSeer device name "Lamp"

Result:
- name_template = "{{ device.name }}": Home Assistant entity will be called "Lamp"
- name_template = "{{ device.location }} - {{ device.name }}": Home Assistant entity will be called "Living Room - Lamp"
- name_template = "HomeSeer - {{ device.name }}": Home Assistant entity will be called "HomeSeer - Lamp"

## Services

The integration exposes the following services:
- homeseer.control_device_by_value

### homeseer.control_device_by_value

Allows the user to set any value on a HomeSeer device.  

|Parameter|Description|Format|Required?|
|---------|-----------|------|---------|
|ref|Ref corresponding to the HomeSeer device |Integer|True|
|value|Value to set the device to (integer) |Integer|True|


