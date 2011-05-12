# Upload this script to tropo.com and bind it to your application there
message(msg, { "to": numberToDial,  "network":"SMS", "callerID": callerID})
log("Sent to %s: %s" % (numberToDial, msg))
