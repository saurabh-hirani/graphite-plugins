### Introduction

This plugin takes [icinga2_api](https://github.com/saurabh-hirani/icinga2_api) connection parameters, target state (ok/warning/critical), a list of time slots (example: icinga2-time-slots.json) and gives metrics on how many services have been in that state for the given time slots.

### Why?

Read [this](TODO)

### Installation

This program is not distributed as a standalone module. Ensure that the following modules are installed before running this program:

```
sudo pip install icinga2_api slotter prettytable
```

### Examples

- Get warning state metrics

```
python icinga2_service_state_metrics.py --host icinga2-host --port 5665 --user root --password password --state warning --graphite-scheme icinga2.services.state -v

icinga2.services.state.warning.minutes.in.0-1 0 1475429031
icinga2.services.state.warning.minutes.in.1-10 0 1475429031
icinga2.services.state.warning.minutes.in.10-30 0 1475429031
icinga2.services.state.warning.minutes.in.30-60 1 1475429031
icinga2.services.state.warning.hours.in.1-2 1 1475429031
icinga2.services.state.warning.hours.in.2-6 0 1475429031
icinga2.services.state.warning.hours.in.6-12 1 1475429031
icinga2.services.state.warning.hours.in.12-24 1 1475429031
icinga2.services.state.warning.days.in.1-2 0 1475429031
icinga2.services.state.warning.days.in.2-5 0 1475429031
icinga2.services.state.warning.days.in.5-10 1 1475429031
icinga2.services.state.warning.days.in.10-9999 0 1475429031
icinga2.services.state.warning.days.beyond.10-9999 0 1475429031
icinga2.services.state.warning.days.beyond.5-10 0 1475429031
icinga2.services.state.warning.days.beyond.2-5 1 1475429031
icinga2.services.state.warning.days.beyond.1-2 1 1475429031
icinga2.services.state.warning.hours.beyond.12-24 1 1475429031
icinga2.services.state.warning.hours.beyond.6-12 2 1475429031
icinga2.services.state.warning.hours.beyond.2-6 3 1475429031
icinga2.services.state.warning.hours.beyond.1-2 3 1475429031
icinga2.services.state.warning.minutes.beyond.30-60 4 1475429031
icinga2.services.state.warning.minutes.beyond.10-30 5 1475429031
icinga2.services.state.warning.minutes.beyond.1-10 5 1475429031
icinga2.services.state.warning.minutes.beyond.0-1 5 1475429031
```

- Get critical state metrics - same as above with 'warning' replaced by 'critical'

- Get ok state metrics - same as above with 'critical' replaced by 'ok'

- Verbose output. Use this mode for debugging purposes only because graphite expects the output in non verbose mode

```
python icinga2_service_state_metrics.py --host icinga2-host --port 5665 --user root --password password --state warning --graphite-scheme icinga2.services.state

SLOTS:
{
  "30-60 minutes": [],
  "2-6 hours": [],
  "0-1 minutes": [],
  "10-9999 days": [],
  "1-2 hours": [],
  "2-5 days": [],
  "10-30 minutes": [],
  "1-2 days": [],
  "1-10 minutes": [],
  "12-24 hours": [],
  "6-12 hours": [],
  "5-10 days": []
}
----------------
----------------
ICINGA2 API RESULT:
{
  "host1!service1": 1474969193.225809,
  "host2!service2": 1475377506.875772,
  "host3!service3": 1475424395.995471,
  "host4!service4": 1475394225.861527,
  "host5!check_all_disks-0": 1475426113.557184
}
----------------
----------------
TABULAR REPRESENTATION:
+-------------------------------+-----------------------------------+------------------------+
| Host                          | Service                           | Duration               |
+-------------------------------+-----------------------------------+------------------------+
| host5                         | service5                          | 0:48:37.442816         |
| host3                         | service3                          | 1:17:15.004529         |
| host4                         | service4                          | 9:40:05.138473         |
| host2                         | service2                          | 14:18:44.124228        |
| host1                         | service1                          | 5 days, 7:43:57.774191 |
+-------------------------------+-----------------------------------+------------------------+

icinga2.services.state.warning.minutes.in.0-1 0 1475429031
icinga2.services.state.warning.minutes.in.1-10 0 1475429031
icinga2.services.state.warning.minutes.in.10-30 0 1475429031
icinga2.services.state.warning.minutes.in.30-60 1 1475429031
icinga2.services.state.warning.hours.in.1-2 1 1475429031
icinga2.services.state.warning.hours.in.2-6 0 1475429031
icinga2.services.state.warning.hours.in.6-12 1 1475429031
icinga2.services.state.warning.hours.in.12-24 1 1475429031
icinga2.services.state.warning.days.in.1-2 0 1475429031
icinga2.services.state.warning.days.in.2-5 0 1475429031
icinga2.services.state.warning.days.in.5-10 1 1475429031
icinga2.services.state.warning.days.in.10-9999 0 1475429031
icinga2.services.state.warning.days.beyond.10-9999 0 1475429031
icinga2.services.state.warning.days.beyond.5-10 0 1475429031
icinga2.services.state.warning.days.beyond.2-5 1 1475429031
icinga2.services.state.warning.days.beyond.1-2 1 1475429031
icinga2.services.state.warning.hours.beyond.12-24 1 1475429031
icinga2.services.state.warning.hours.beyond.6-12 2 1475429031
icinga2.services.state.warning.hours.beyond.2-6 3 1475429031
icinga2.services.state.warning.hours.beyond.1-2 3 1475429031
icinga2.services.state.warning.minutes.beyond.30-60 4 1475429031
icinga2.services.state.warning.minutes.beyond.10-30 5 1475429031
icinga2.services.state.warning.minutes.beyond.1-10 5 1475429031
icinga2.services.state.warning.minutes.beyond.0-1 5 1475429031
```
