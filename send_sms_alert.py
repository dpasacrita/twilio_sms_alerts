#!/usr/bin/python3.4
from twilio.rest import Client
import time
import os
import sys

# Globals
alert_file = "last_alert.txt"
alert_file_path = "xxxxxxxxxxxxxx/last_alert.txt"
sms_log_file = "sms.log"
alert_threshold = 1800
contact_list = ["xxxxxxxxx", "xxxxxxxxxxxxx", "xxxxxxxxxx", "xxxxxxxxxx"]
host = ""
service = ""
state = ""
justhost = False


def send_sms(to, body):
    """
    This function will send the actual SMS message.
    :param to: The "To" number for the SMS
    :param body: The body of the SMS
    :return:
    """

    # Twilio Code
    # These are our account credentials
    account_sid = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    auth_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    # Set up the message and send
    client = Client(account_sid, auth_token)
    client.messages.create(
        to="+"+to,
        from_="+xxxxxxxxxxxx",
        body=body)


def logit(data):
    """
    Allows you to send simple log messages to a log file.
    :param data: The text of the log
    :return:
    """
    global sms_log_file
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        log_file = open(sms_log_file, "a")
    except:
        return
        # Fire email warning about cannot log to disk
    try:
        log_file.write(cur_time + " -- " + data + "\n")
    except:
        return
        # Email warning about can't write to logfile
    log_file.close()


def compare_times(runtime, alert_file):
    """
    This function will take the runtime and compare it with the last time the script ran.
    If an hour has not elapsed, no alert text will send.
    :param runtime: The current time.
    :param alert_file: The file that contains the last_time.
    :return: True or False
    """
    # Try to open the file
    try:
        time_file = open(alert_file, "r+")
    except:
        logit("ERROR: Can't open the %s file!" % alert_file)
        return False
    # Check if the file is empty or not
    if os.stat(alert_file_path).st_size == 0:
        logit("INFO: File is Empty. Alert will send.")
        time_file.write(str(runtime))
        time_file.close()
        return True

    # Now we're going to try reading the time from the file
    try:
        last_time = float(time_file.readline())
    except:
        # Since we got junk, truncate it and return True.
        logit("ERROR: Invalid Value in %s!" % alert_file)
        time_file.close()
        time_file = open(alert_file, "w")
        time_file.close()
        return True
    # Check if the time in the file is an hour earlier than now
    # If it is, we're going to return True and send the alert
    # If it's not, we'll return false and send nothing
    if (runtime-last_time) >= alert_threshold:
        logit("INFO: Alert threshold exceeded. Sending alert.")
        # Log the new last time to file
        time_file.close()
        time_file = open(alert_file, "w")
        time_file.write(str(runtime))
        time_file.close()
        return True
    else:
        logit("INFO: Alert threshold not yet exceeded. NOT sending alert.")
        # Close file and do nothing
        time_file.close()
        return False


def parse_arguments():
    """
    This function will check that there are the correct number of arguments,
    then exit the script if it's a SOFT alert.
    Then it will update the globals with the host and service names.
    :return:
    """

    global host
    global service
    global state
    global host
    global justhost

    # Check if the host is down. If it is, send an alert with that as the subject.
    if sys.argv[5] == 'DOWN':
        logit("INFO: This host is reporting DOWN. A alert will be sent immediately if this is also a HARD alert")
        if sys.argv[6] == 'HARD':
            logit("INFO: HARD alert confirmed. Sending host down alert.")
            justhost = True
            host = sys.argv[1]
            return
        elif sys.argv[6] == 'SOFT':
            logit("INFO: Still just a SOFT alert, do nothing.")
            sys.exit()
        else:
            logit("ERROR: HOSTALERTTYPE contains bad data: %s" % sys.argv[6])
            sys.exit()
    # Likewise, if the host is coming back up, don't alert.
    if sys.argv[4] == '$SERVICESTATE$':
        logit("INFO: Host is just coming back up. No worries. Not sending alert.")
        sys.exit()

    # Exit if state is OK
    if sys.argv[4] == "OK":
        logit("INFO: State is %s" % sys.argv[4])
        logit("INFO: Exiting.")
        sys.exit()

    logit("INFO: State is %s" % sys.argv[4])
    # Exit the script right away if it's a SOFT state
    if sys.argv[3] == "SOFT":
        logit("INFO: Type is %s" % sys.argv[3])
        logit("INFO: Nagios detected a SOFT warning/critical state.")
        logit("INFO: Exiting for now until a HARD state is detected.")
        sys.exit()
    else:
        logit("INFO: Type is %s" % sys.argv[3])
        logit("INFO: Nagios detected a HARD warning/critical state.")
        logit("INFO: Proceeding with text alerts.")

    # Grab the hostname and service
    # These are globals so the function can end after that
    host = sys.argv[1]
    service = sys.argv[2]
    state = sys.argv[4]


if __name__ == "__main__":

    # Debug statement, remove later
    logit("INFO: %s" % sys.argv)

    # Collect information on the issue
    parse_arguments()

    # If justhost == true, this is only a host and we need to run a different alert.
    if justhost:

        # Get the time of this run
        runtime = time.time()

        if compare_times(runtime, alert_file):
            logit("INFO: Beginning alerts now.")
            for number in contact_list:
                logit("INFO: Sending alert to %s" % number)
                send_sms(number, "HOST " + host + " is reporting DOWN, investigate immediately.")
            sys.exit()
        else:
            logit("INFO: Closing without sending anything.")
            sys.exit()

    # Get the time of this run
    runtime = time.time()

    if compare_times(runtime, alert_file):
        logit("INFO: Beginning alerts now.")
        for number in contact_list:
            logit("INFO: Sending alert to %s" % number)
            send_sms(number, "Nagios reported a status change change with an Email Host. Investigate this immediately!")
    else:
        logit("INFO: Closing without sending anything.")
        sys.exit()
