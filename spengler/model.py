from datetime import datetime, timedelta
from threading import Thread
import sqlalchemy
import time

def create_engine(sqlalchemy_url, display_name=None):
    engine = sqlalchemy.create_engine(sqlalchemy_url)
    setattr(engine, 'display_url', '%s@%s:%d/%s' % (engine.url.username, 
                                                    engine.url.host, 
                                                    engine.url.port, 
                                                    engine.url.database))
    if display_name:
        setattr(engine, 'display_name', display_name)
    else:
        setattr(engine, 'display_name', engine.display_url)
    
    return engine

class DatabasePair():
    def __init__(self, name, left=None, right=None, selector=None, validator=None, callbacks=None):
        self.name = name

        # Database engines
        self.left = left
        self.right = right

        # Queries
        self.selector = selector
        self.validator = validator

        if callbacks == None:
            self.callbacks = []
        else:
            self.callbacks = callbacks

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def test_replication(self):
        results = self.__test_replication(self.left, self.right)
        for callback in self.callbacks:
            callback(**results)
        results = self.__test_replication(self.right, self.left)
        for callback in self.callbacks:
            callback(**results)

    def __test_replication(self, a, b):
        con_a = a.connect()
        con_b = b.connect()

        selection_time = time.time()
        a_row_id = con_a.execute(self.selector).fetchone()[0]
        selection_time = time.time() - selection_time

        validation_time = time.time()
        b_count = con_b.execute(self.validator % a_row_id).fetchone()[0]
        validation_time = time.time() - validation_time

        synced = True if b_count else False

        return dict(synced=synced, row_id=a_row_id, found=b_count,
                    timestamp=datetime.now().isoformat(),
                    selection_time=selection_time,
                    validation_time=validation_time,
                    source=a.display_name,
                    destination=b.display_name,
                    pair_name=self.name)

class ReplicationStatusDaemon():
    def __init__(self, database_pairs={}, check_interval=600, left_alias="Left", right_alias="Right", callbacks=[]):
        self.database_pairs = database_pairs
        self.current_results = {}
        self.left_alias = left_alias
        self.right_alias = right_alias
        self.check_interval = check_interval
        self.callbacks = callbacks
        
        self.callbacks.append(self.results_callback)

        self.active = False
        self.check_threads = []

    def start(self):
        print "Starting interval timer thread"
        self.active = True
        self.interval_thread = Thread(target=self.interval_timer)
        self.interval_thread.setDaemon(True)
        self.interval_thread.start()        

    def add_database(self, database_pair):
       self.database_pairs[database_pair.name] = database_pair
       for callback in self.callbacks:
           database_pair.add_callback(callback)

    def check_replication(self):
        for name, db in self.database_pairs.items():
            db.test_replication()

    def interval_timer(self):
        while self.active:
            print "Starting replication thread at %s" % (time.asctime())
            check_thread = Thread(target=self.check_replication)
            check_thread.setDaemon(True)
            check_thread.start()
            self.check_threads.append(check_thread)

            dead_threads = []
            for t in self.check_threads:
                if not t.isAlive():
                    dead_threads.append(t)

            for dt in dead_threads:
                self.check_threads.remove(dt)

            print "%d threads checking replications status" % len(self.check_threads)
            time.sleep(self.check_interval)


    def remove_database(self, name):
        try:
            del self.database_pairs[name]
        except KeyError:
            pass

    def results_callback(self, **results):
        pair_name = results['pair_name']
        if not self.current_results.has_key(pair_name):
            self.current_results[pair_name] = {}
        self.current_results[pair_name][results['destination']] = results


def configure_replication_daemon(configuration):
    callbacks = []
    for callback_desc in configuration['callbacks']:
        mod_name, func_name = callback_desc.split(':')
        fromlist = None
        try:
            parent = mod_name[0:mod_name.rindex('.')]
            fromlist = [parent]
        except:
            pass
        mod = __import__(mod_name, fromlist=fromlist)
        callback = getattr(mod, func_name)
        callbacks.append(callback)

    rep_daemon = ReplicationStatusDaemon(callbacks=callbacks)

    rep_daemon.left_alias = configuration['aliases']['left']
    rep_daemon.right_alias = configuration['aliases']['right']

    for db in configuration['databases']:
        left = create_engine(db['left'], "%s-%s" % (db['name'], 
                                                    rep_daemon.left_alias))
        right = create_engine(db['right'], "%s-%s" % (db['name'],
                                                      rep_daemon.right_alias))
        selector = configuration['query_classes'][db['query_class']]['selector']
        validator = configuration['query_classes'][db['query_class']]['validator']

        pair = DatabasePair(db['name'],
                            left, right, selector, validator)

        rep_daemon.add_database(pair)
    
    return rep_daemon
