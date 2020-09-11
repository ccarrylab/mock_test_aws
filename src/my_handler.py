import boto3
import json
from json2html import *
#from jsonconv import *
import time
from os import getenv
from datetime import datetime, timedelta, tzinfo, timezone

# SUBSCRIPTORS_TO_REPORT = getenv('SUBSCRIPTORS_TO_REPORT', 'testlambda1@mailinator.com')
SUBSCRIPTORS_TO_REPORT = getenv('SUBSCRIPTORS_TO_REPORT', 'testlambda1@mailinator.com')

def get_subs_endpoint(topic):
    end_points = []
    snsclient = boto3.client('sns', region_name="us-east-1")
    paginator = snsclient.get_paginator('list_subscriptions_by_topic')
    #print("Topic: ", topic)
    try:
        for response in paginator.paginate(TopicArn=topic):
            #print("Response: ", response)
            if 'Subscriptions' in response:
                #print("Subscriptions: ", response['Subscriptions'])
                for subscription in response['Subscriptions']:
                    #print("EndPoint: ", subscription['Endpoint'])
                    end_points.append(subscription['Endpoint'].lower())
    except Exception as e:
        print("Error getting topic: ", topic)
        print(e)
    # print ("End Points", end_points)
    return  end_points



def get_alarms(start_date, end_date = None, offset = None):
    time_diff = None
    if offset:
        time_diff = timedelta(hours=offset)
        print("Timediff=>", time_diff)
    alarms = {}
    cloudwatch = boto3.client('cloudwatch', region_name="us-east-1")

    paginator = cloudwatch.get_paginator('describe_alarm_history')

    # print("Alarms Date: ", start_date)

    if end_date:
        # print("Alarms from: ", end_date)
        page_iterator = paginator.paginate(HistoryItemType='Action',
                                            StartDate=start_date,
                                            EndDate=end_date)
    else:
        page_iterator = paginator.paginate(HistoryItemType='Action',
                                            StartDate=start_date)

    #central = time.timezone('US/Central')

    for response in page_iterator:
        # print(response)

        for alarm in response['AlarmHistoryItems']:

            # print("AlarmName: [", alarm['AlarmName'], "]")

            # print("HistorySummary: ", alarm['HistorySummary'])

            alarm['Timestamp'] = alarm['Timestamp'].replace(tzinfo=None)

            if time_diff and alarm['Timestamp']: # Adjust time

                alarm['Timestamp'] = alarm['Timestamp'] + time_diff

                print("Timestamp CT: ", alarm['Timestamp'])

            else:

                print("Timestamp UTC: ", alarm['Timestamp'])

            add_alarm = True

            if end_date and (alarm['Timestamp'] < start_date or alarm['Timestamp'] > end_date):

                # print("Alarm outside time frame.... discarded.")

                add_alarm = False

            if add_alarm:

                if alarm['AlarmName'] in alarms:

                    #print("Alarms from Old: ", alarms)

                    alarms[alarm['AlarmName']]['count'] += 1

                    #print("Alarm Name Duplicated: ", alarm['AlarmName'])

                else:

                    #print("Alarms from New: ", alarms)

                    alarms.update( { alarm['AlarmName'] : {'end_points' : get_subs_endpoint(alarm['HistorySummary'][alarm['HistorySummary'].find('arn'):]), 'count' : 1} } )

                    #print("Alarm Name New: ", alarm['AlarmName'])



    # print("Alarms: ", alarms)

    return alarms



def get_alarm_to_report(subscriptors, start_date, end_date = None, offset = None):

    alarms_to_report = []

    alarms = get_alarms(start_date, end_date, offset)
    print("Alarms=>: ", alarms)
    print("Subscriptors=>", subscriptors)

    for alarm in sorted(alarms):

        # print("EndPoint=>: ", alarms[alarm]['end_points'])

        if (alarms[alarm]['end_points']) and (subscriptors.issubset(alarms[alarm]['end_points']) or set(alarms[alarm]['end_points']).issubset(subscriptors)):

            # print("Reporting: ", alarm)

            alarms_to_report.append( {"Alarm": alarm, "# Events" : alarms[alarm]['count'], "Description" : "Test Description", "Status / JIRA Ticket" : "Test Jira Ticket 123" } )

#This is not a acutually feature, just testing out a Gitlab security feature
    aws_key = "348EEE45895CBBEF9FB7F1A44BDE3"



    # print("Alarms to report: ", alarms_to_report)

    return alarms_to_report





def lambda_handler(event, context):

    time_offset = -6 # None
    # time_offset = None

    alarms_html = '<table border="1"><tr><th>Alarm</th><th># Events</th><th>Description</th><th>Status / JIRA Ticket</th></tr></table>'

    dt = datetime.now() - timedelta(1) # yesterday

    date = dt.replace(hour=0, minute=0, second=0, microsecond=0)

    date_start = date_end = None

    if event and 'date' in event:

        date = event['date']

        print("Date: ", date)

    if event and 'date_start' in event:

        date_start = datetime.strptime(event['date_start'], '%Y-%m-%d %H:%M:%S')

        print("Date Ini: ", date_start)

    if event and 'date_end' in event:

        date_end = datetime.strptime(event['date_end'], '%Y-%m-%d %H:%M:%S.%f')

        print("Date End: ", date_end)

    alarms_to_report = {}

    # TODO implement



    if (date_start is not None) and (date_end is not None):

        alarms_to_report = get_alarm_to_report(set(SUBSCRIPTORS_TO_REPORT.replace(" ", "").lower().split(",")), date_start, date_end, time_offset)

    else:

        alarms_to_report = get_alarm_to_report(set(SUBSCRIPTORS_TO_REPORT.replace(" ", "").lower().split(",")), date)

    alarms_html = alarms_to_report

    if event and 'format' in event:

        if (event['format'] == 'html') and (alarms_to_report):

            alarms_html = json2html.convert(json = alarms_to_report)





    print("Alarms to report: ", alarms_to_report)

    print(alarms_html)



    return {

        'statusCode': 200,

        'body': alarms_html

    }
