# HomeSeer HS3 Custom Component for Home Assistant

## Supported Devices

Z-Wave devices of the following types should create entities in Home Assistant:
- Z-Wave Barrier Operator (as Home Assistant cover)
- Z-Wave Battery (as Home Assistant sensor)
- Z-Wave Door Lock (as Home Assistant lock)
- Z-Wave Sensor Binary (as Home Assistant binary sensor)
- Z-Wave Switch (as Home Assistant switch)
- Z-Wave Switch Binary (as Home Assistant switch)
- Z-Wave Switch Multilevel (as Home Assistant light)
- Z-Wave Central Scene (as Home Assistant event - see below)

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
3. Add the below config to your configuration.yaml and restart Home Assistant.
4. Problems with certain devices (i.e. not supported yet) will be reported in the debug logs for the component/pyHS3.

## Upgrade

0. Stop Home Assistant
1. `cd` into the `custom_components/homeseer` directory and do `git pull`.
2. Start Home Assistant

## configuration.yaml example

```yaml
homeseer:
  host:  192.168.1.10
  namespace: homeseer
  http_port: 80
  ascii_port: 11000
  username: default
  password: default
  allow_events: True
```
|Parameter|Description|Required/Optional|
|---------|-----------|-----------------|
|host|IP address of the HomeSeer HS3 HomeTroller|Required|
|namespace|Unique string identifying the HomeSeer instance|Required|
|port|HTTP port of the HomeTroller|Optional, default 80|
|ascii_port|ASCII port of the HomeTroller|Optional, default 11000|
|username|Username of the user to connect to the HomeTroller|Optional, default "default"|
|password|Password of the user to connect to the HomeTroller|Optional, default "default"|
|allow_events|Create Home Assistant scenes for HomeSeer events|Optional, default True|

### Namespace

In order to generate unique ids for entities to enable support for the entity registry (most importantly, allowing users to rename entities and change entity ids from the UI), a unique string is required. Namespace can be any string you like. If this string changes, all entities will generate new entries in the entity registry, so only change this string if you absolutely know what you are doing.