===================================
 Spengler Database Streams Monitor
===================================

You're playing with the big kids now.  Your databases are replicated 
using any one of many viable technologies in near real time across
the country to your disaster recovery site.  Maybe you've gone one step
further, and you're running transactions in an active-active configuration.  

Are you **really** sure that your data is replicating in a reasonable
amount of time across the country?  Spengler provides a mechanism for
cross checking data between your replicated database pairs to ensure that
updates are flowing in both directions.  

My team uses a database that allows for streaming replication, and we found the
built in monitoring was less than adequate for us.  Every once in a while it'd
lose track of the streams process and report a good status when data was long
out of sync, thus Spengler was born.

But what about the name?  Why Spengler?  

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

Callbacks
---------

Web Server
----------



