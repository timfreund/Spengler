from flask import Flask
from optparse import OptionParser
from spengler import cli, model
import flask

app = Flask(__name__)

@app.before_request
def before_request():
    if app.config.rep_check_daemon != None:
        if not app.config.rep_check_daemon.active:
            app.config.rep_check_daemon.start()

@app.route('/')
def index():
    if flask.request.content_type == 'application/json':
        return flask.jsonify(app.config.rep_check_daemon.current_results)
    else:
        return flask.render_template('index.html',
                                     current_status=app.config.rep_check_daemon.current_results)

def run_server():
    parser = OptionParser(usage="usage: %%prog\n%s" % __doc__)
    parser.add_option("-c", "--config-file", dest="configuration_file")
    parser.add_option("-a", "--address", dest="host", default="0.0.0.0")
    parser.add_option("-p", "--port", dest="port", default=8442)
    parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true")

    (options, args) = parser.parse_args()

    if options.configuration_file == None:
        print "A configuration file is required"
        sys.exit(1)

    rep_check_daemon = cli.configure_replication_check_daemon(options.configuration_file)
    app.config.rep_check_daemon = rep_check_daemon
    app.run(host=options.host,
            port=options.port,
            debug=options.debug)
