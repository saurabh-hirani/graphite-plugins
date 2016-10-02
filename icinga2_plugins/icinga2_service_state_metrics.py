#!/usr/bin/env python

"""
Usage:
  icinga2_service_state_metrics.py [--help] [--host <host>] [--port <port>] --user <user> --password <password> [--state <state>] [--verbose] [--graphite-scheme <graphite_scheme>] [--time-slots <slots_file>]

Options:
  --host <host>                             icinga2 host [default: localhost]
  --port <port>                             icinga2 port [default: 5665]
  --user <user>                             icinga2 user
  --password <password>                     icinga2 password
  -s, --state <state>                       icinga2 service state to query [default: ok]
  -v, --verbose                             verbose mode
  --time-slots <time_slots_file>            json file containig metric duration slots [default: icinga2-time-slots.json]
  -g, --graphite-scheme <graphite_scheme>   graphite scheme. [default: None]
"""

import sys
import json
import time
import datetime

import slotter
from icinga2_api import api
from prettytable import PrettyTable
from docopt import docopt

def _get_service_state_by_name(name):
  if name == 'ok':
    return 0
  if name == 'warning':
    return 1
  if name == 'critical':
    return 2
  return 3

def _is_icinga2_output_valid(output):
  """ Validate icinga2 api call output """
  valid = True
  if output['status'] != 'success':
    sys.stderr.write('ERROR: icinga2 api returned status: %s' % output['status'])
    valid = False
  elif output['response']['status_code'] != 200:
    sys.stderr.write('ERROR: icinga2 api returned status_code: %s' % output['response']['status_code'])
    valid = False

  if not valid:
    sys.stderr.write(json.dumps(output, indent=2))
    return False

  return True

def _humanize_duration(duration):
  return str(datetime.timedelta(seconds=duration))

def print_slots_graphite(slotter_obj, graphite_scheme):
  """ Print graphite consumable output of the slot items """
  # print metrics count 'in' a slot e.g num warnings in the range of 1-2 hours
  for slot in slotter_obj.get_slots():
    items = slotter_obj.get_items(slot)
    slot_name = str(slot)
    time_range, time_type = slot_name.split(' ')
    graphite_str = '%s.%s.in.%s' % (graphite_scheme, time_type, time_range)
    print '%s %s %d' % (graphite_str, len(items), time.time())

  # print metric count 'beyond' a slot i.e. num warnings beyond 1-2 hours
  beyond_count = 0
  for slot in reversed(slotter_obj.get_slots()):
    items = slotter_obj.get_items(slot)
    slot_name = str(slot)
    time_range, time_type = slot_name.split(' ')
    graphite_str = '%s.%s.beyond.%s' % (graphite_scheme, time_type, time_range)
    print '%s %s %d' % (graphite_str, beyond_count, time.time())
    beyond_count += len(items)

def print_slots_table(slotter_obj):
  """ Print a table of the slot items """
  table = PrettyTable(['Host', 'Service', 'Duration'])
  table.align = 'l'
  for slot in slotter_obj.get_slots():
    for item in slotter_obj.get_items(slot):
      host, service = item[0][0].split('!')
      duration = item[0][1]
      table.add_row([host, service, duration])
  print table

def slot_icinga2_results(slotter_obj, icinga2_results):
  """ Slot icinga2 API results in slotter object slots """
  curr = int(time.time())
  for service_name, timestamp in icinga2_results.iteritems():
    time_passed = curr - timestamp
    slotter_obj.add_item((service_name, _humanize_duration(time_passed)), time_passed)

def get_icinga2_results(args):
  """ Get service - timestamp mapping from icinga2 api """
  # create api object
  obj = api.Api(
    host = args['--host'],
    port = args['--port'],
    user = args['--user'],
    password = args['--password']
  )
  uri = '/v1/objects/services'
  state_number = _get_service_state_by_name(args['--state'])

  filter_expr = ''
  # consider only services in desired state
  filter_expr += 'service.state==%d ' % state_number
  # and only those in the hard desired state
  filter_expr += '&& service.state_type==1 '
  # and only those whose hosts are reachable
  filter_expr += '&& service.last_reachable '
  # and only those whose hosts are not in downtime
  filter_expr += '&& !service.last_in_downtime '
  # and only those which have active checks enabled
  filter_expr += '&& service.enable_active_checks '
  # and only those which have notifications enabled
  filter_expr += '&& service.enable_notifications '
  # and only those which are not acknowledged
  filter_expr += '&& service.acknowledgement==0 '

  # ready the payload
  data = {
    'attrs': [
      # when was the last time this service was healthy
      'last_state_ok',
      # when was the last hard state change - use if last_state_ok == 0
      'last_hard_state_change'
    ],
    'filter': filter_expr
  }

  # fire
  output = obj.read(uri, data)

  # 404 - query returned nothing
  if output['response']['status_code'] == 404:
    return []

  # validate output
  if not _is_icinga2_output_valid(output):
    if args['--graphite-scheme']:
      print '%s.%s %d %d' % (args['--graphite-scheme'], 'error', 1, time.time())
    return []

  if len(output['response']['data']['results']) == 0:
    return []

  service_timestamp_map = {}
  for record in output['response']['data']['results']:
    if record['attrs']['last_state_ok'] == 0:
      last_state_ok = record['attrs']['last_hard_state_change']
    else:
      last_state_ok = record['attrs']['last_state_ok']
    service_timestamp_map[record['name']] = last_state_ok

  return service_timestamp_map

def load_time_slots(target_file):
  """ Load the metric durations """
  ds = json.loads(open(target_file).read())
  slotter_obj = slotter.create()
  for slot_type in ds:
    multiplier = ds[slot_type]['multiplier']
    for slot in ds[slot_type]['slots']:
      start, end = slot
      key = '%s-%s %s' % (str(start), str(end), slot_type)
      slotter_obj.add_slot(slot[0] * multiplier, slot[1] * multiplier, desc=key)
  return slotter_obj

def parse_cmdline():
  """ Parse cmdline """
  return docopt(__doc__)

def main():
  """ Main function wrapper """
  args = parse_cmdline()
  slotter_obj = load_time_slots(args['--time-slots'])
  if args['--verbose']:
    print "----------------"
    print "SLOTS:"
    print json.dumps(slotter_obj.dump(), indent=2)
    print "----------------"

  icinga2_results = get_icinga2_results(args)

  if args['--verbose']:
    print "----------------"
    print "ICINGA2 API RESULT:"
    print json.dumps(icinga2_results, indent=2)
    print "----------------"

  if len(icinga2_results) == 0:
    return []
  slot_icinga2_results(slotter_obj, icinga2_results)

  if args['--verbose']:
    print "----------------"
    print "TABULAR REPRESENTATION:"
    print_slots_table(slotter_obj)
    print "----------------"

  if args['--graphite-scheme'] != 'None':
    print_slots_graphite(slotter_obj, args['--graphite-scheme'] + '.' + args['--state'])

if __name__ == "__main__":
  main()
