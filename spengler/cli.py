from optparse import OptionParser
from spengler import model
import json
import sys

def create_default_arg_parser():
    parser = OptionParser(usage="usage: %%prog\n%s" % __doc__)
    parser.add_option("-l", "--left-db", dest="left_db_url")
    parser.add_option("-r", "--right-db", dest="right_db_url")
    parser.add_option("-s", "--selector", dest="selector", help="Query to find the latest data from a database")
    parser.add_option("-v", "--vaildator", dest="validator", help="Query to validate the existence in this database of the other database's latest data")
    parser.add_option("-d", "--debug-output", dest="debug", 
                      action="store_true", default=False,
                      help="Provide verbose debug output")
    return parser

def results_printer(synced, source, destination, **kw):
    status = "SYNCED" if synced else "FAILED"
    print "%s: %s -> %s" % (status, source, destination)

def verbose_printer(synced, source, destination, row_id, selection_time, validation_time, **kw):
    print "%s,%s,%s,%s,%s,%s" % (synced, source, destination, row_id, selection_time, validation_time)

def replication_check():
    (options, args) = create_default_arg_parser().parse_args()

    if options.left_db_url==None or options.right_db_url==None:
        print("Left and right database urls are required")
        sys.exit(1)

    if options.selector==None or options.validator==None:
        print("Selector and validator queries are required")
        sys.exit(1)

    left = model.create_engine(options.left_db_url)
    right = model.create_engine(options.right_db_url)
    
    pair = model.DatabasePair("Manual Check", left, right, 
                              options.selector, options.validator)

    if options.debug:
        pair.add_callback(verbose_printer)
    else:
        pair.add_callback(results_printer)
    
    pair.test_replication()

def replication_check_daemon():
    parser = OptionParser(usage="usage: %%prog\n%s" % __doc__)
    parser.add_option("-c", "--config-file", dest="configuration_file")

    (options, args) = parser.parse_args()

    if options.configuration_file == None:
        print "A configuration file is required"
        sys.exit(1)

    configuration_file = open(options.configuration_file, "r")
    configuration_text = configuration_file.read()
    configuration_file.close()

    json_decoder = json.JSONDecoder()
    configuration_json = json_decoder.decode(configuration_text)

    daemon = model.configure_replication_daemon(configuration_json)
    daemon.start()

    import time
    while True:
        time.sleep(3600)
