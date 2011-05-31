from optparse import OptionParser
from spengler import model
import json
import sys
import time

def results_printer(synced, source, destination, **kw):
    status = "SYNCED" if synced else "FAILED"
    print "%s: %s -> %s" % (status, source, destination)

def verbose_printer(synced, source, destination, row_id, selection_time, validation_time, **kw):
    print "%s,%s,%s,%s,%s,%s" % (synced, source, destination, row_id, selection_time, validation_time)

def replication_check():
    parser = OptionParser(usage="usage: %%prog\n%s" % __doc__)
    parser.add_option("-c", "--config-file", dest="configuration_file")

    (options, args) = parser.parse_args()

    if options.configuration_file == None:
        print "A configuration file is required"
        sys.exit(1)

    print "Synced, Source DB, Destination DB, Row ID, Selection Query Time, Validation Query Time"
    daemon = configure_replication_check_daemon(options.configuration_file)
    daemon.check_replication()

def configure_replication_check_daemon(configuration_location):
    configuration_file = open(configuration_location, "r")
    configuration_text = configuration_file.read()
    configuration_file.close()

    json_decoder = json.JSONDecoder()
    configuration_json = json_decoder.decode(configuration_text)

    daemon = model.configure_replication_daemon(configuration_json)
    return daemon

def replication_check_daemon():
    parser = OptionParser(usage="usage: %%prog\n%s" % __doc__)
    parser.add_option("-c", "--config-file", dest="configuration_file")

    (options, args) = parser.parse_args()

    if options.configuration_file == None:
        print "A configuration file is required"
        sys.exit(1)

    daemon = configure_replication_check_daemon(options.configuration_file)
    daemon.start()

    while not len(daemon.check_threads):
        time.sleep(5)
    daemon.active = False

    while len(daemon.check_threads):
        time.sleep(5)
