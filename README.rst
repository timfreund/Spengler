===================================
 Spengler Database Streams Monitor
===================================

You're playing with the big kids now.  Your databases are replicated
using any one of many viable technologies in near real time across the
country to a disaster recovery site.  Maybe you've gone one step
further, and you're running transactions in an active-active
configuration.

Are you **really** sure that your data is replicating in a reasonable
amount of time across the country?  Spengler provides a mechanism for
cross checking data between your replicated database pairs to ensure
that updates are flowing in both directions.

My team uses a database that allows for streaming replication, and we
found the built in monitoring was less than adequate.  Every once in a
while it would lose track of the streams process and report a good
status when data was long out of sync, thus Spengler was born.

But what about the name?  Why Spengler?  I think this says it all::

    Dr. Egon Spengler: There's something very important I forgot to tell you. 
    Dr. Peter Venkman: What? 
    Dr. Egon Spengler: Don't cross the streams. 
    Dr. Peter Venkman: Why? 
    Dr. Egon Spengler: It would be bad. 
    Dr. Peter Venkman: I'm fuzzy on the whole good/bad thing. What do you mean, "bad"? 
    Dr. Egon Spengler: Try to imagine all life as you know it stopping instantaneously and every molecule in your body exploding at the speed of light. 
    Dr Ray Stantz: Total protonic reversal. 
    Dr. Peter Venkman: Right. That's bad. Okay. All right. Important safety tip. Thanks, Egon. 

Components
==========

Database Pair
-------------

A DatabasePair object contains two SQLAlchemy database engines,
affectionately named ``left`` and ``right``.  It also has two queries:

1. The ``selector`` query should select the latest unique ID from a
frequently used table.  Our replication scheme takes up to two minutes to 
move data, so our query looks something like this::

    select transaction_id 
    from our_business_object_table 
    where transaction_time > (select max(transaction_time) -2/1440
                              from our_business_object_table) order by timestamp asc.

2. The ``validator`` query will run against the other half of the database
pair to ensure that the data appears in both halves::

    select count(*) from our_business_object_Table where transaction_id=%d

We cross check in both directions:  does ``right`` have the latest data from 
``left`` and does ``left`` have the latest data from ``right``.  We've seen 
replication fail in only one direction, so this is an important detail.

Callbacks
---------

Validating the synchronization status of databases is an asynchronous process done
on a regular interval by the ``ReplicationStatusDaemon``.  You can inspect the 
synchronization results in ``ReplicationStatusDaemon.current_results`` at any time,
or you can receive real time status updates by providing callback functions to the
``ReplicationStatusDaemon`` or individual ``DatabasePair`` objects.  Sample callbacks
are provided at ``spengler.cli.results_printer`` and ``spengler.cli.verbose_printer``.

Web Server
----------

Spengler includes a small web server.  The web server script runs a
``ReplicationStatusDaemon`` and publishes the results on the host and
port specified by you.  Requests of type ``application/json`` will be
met with a JSON formatted response for easy consumption by other
applications.

Sample invocation::
  spengler-webserver -c my_configuration_file.json --port 8442

Sample client request::
  curl -H "Content-Type: application/json" http://localhost:8442/

Spengler's Building Blocks
==========================

Spengler was built quickly with help from the following two libraries:

* `SQLAlchemy`_ - doing anything with a relational database without the
  help of SQLAlchemy is just terrible.  
* `Flask`_ - a nice, tiny, web framework.  Great for small stuff like
  this, and plays nice with larger WSGI deployments if that's your
  thing.

.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Flask: http://flask.pocoo.org/

