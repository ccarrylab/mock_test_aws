import sys
sys.path.append("..")
import boto3
from package.moto import mock_sns, mock_cloudwatch
# from moto import mock_sns, mock_cloudwatch
from src.my_handler import *
import time
from os import getenv
from datetime import datetime, timedelta, tzinfo, timezone
from aws_lambda_context import LambdaContext

SUBSCRIPTORS_TO_REPORT = getenv('SUBSCRIPTORS_TO_REPORT', 'testlambda1@mailinator.com')

@mock_sns
def test_get_subs_endpoint():
    client = boto3.client("sns", region_name="us-east-1")
    client.create_topic(Name="my-topic")
    resp = client.create_topic(Name="my-topic")
    arn = resp["TopicArn"]
    # print(arn)
    resp = client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda1@mailinator.com")
    resp = client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda2@mailinator.com")
    assert get_subs_endpoint(arn) == ['testlambda1@mailinator.com','testlambda2@mailinator.com']
    print("=========================================")
    print("test_get_subs_endpoint ran successful")
    print("=========================================")


@mock_cloudwatch
@mock_sns
def test_get_alarms():
    client = boto3.client("cloudwatch", region_name="us-east-1")
    client = boto3.client("sns", region_name="us-east-1")
    client.create_topic(Name="my-topic")
    resp = client.create_topic(Name="my-topic")
    arn = resp["TopicArn"]
    client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda1@mailinator.com")
    client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda2@mailinator.com")
    start_date = '2020-06-24T18:59:06.442Z'
    resp = get_alarms(start_date, end_date = None, offset = None)
    assert resp['myalarm']['end_points'] == ['testlambda1@mailinator.com', 'testlambda2@mailinator.com']
    assert resp['myalarm']['count'] == 3

    offset = 2
    resp = get_alarms(start_date, end_date = None, offset = offset)
    assert resp['myalarm']['end_points'] == ['testlambda1@mailinator.com', 'testlambda2@mailinator.com']
    assert resp['myalarm']['count'] == 3

    print("=========================================")
    print("test_get_alarms ran successful")
    print("=========================================")


@mock_cloudwatch
@mock_sns
def test_get_alarm_to_report():
    client = boto3.client("cloudwatch", region_name="us-east-1")
    client = boto3.client("sns", region_name="us-east-1")
    client.create_topic(Name="my-topic")
    resp = client.create_topic(Name="my-topic")
    arn = resp["TopicArn"]
    client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda1@mailinator.com")
    client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda2@mailinator.com")
    start_date = '2020-06-24T18:59:06.442Z'

    event = {'date': '2020-06-24T18:59:06.442Z',
             'date_start': '2020-06-25 18:00:00',
             'date_end': '2020-06-25 19:00:00.123'}

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


    resp = get_alarm_to_report(set(SUBSCRIPTORS_TO_REPORT.replace(" ", "").lower().split(",")), date)
    assert resp[0]['Alarm'] == 'myalarm'
    assert resp[0]['# Events'] == 3
    assert resp[0]['Description'] == 'Test Description'
    assert resp[0]['Status / JIRA Ticket'] == 'Test Jira Ticket 123'

    resp = get_alarm_to_report(set(SUBSCRIPTORS_TO_REPORT.replace(" ", "").lower().split(",")), date_start, date_end)
    assert resp[0]['Alarm'] == 'myalarm'
    assert resp[0]['# Events'] == 1
    assert resp[0]['Description'] == 'Test Description'
    assert resp[0]['Status / JIRA Ticket'] == 'Test Jira Ticket 123'


    offset = 2
    event = {'date': '2020-06-24T20:59:06.442Z',
             'date_start': '2020-06-25 20:00:00',
             'date_end': '2020-06-25 21:00:00.123'}

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
    resp = get_alarm_to_report(set(SUBSCRIPTORS_TO_REPORT.replace(" ", "").lower().split(",")), date_start, date_end, offset)

    assert resp[0]['Alarm'] == 'myalarm'
    assert resp[0]['# Events'] == 1
    assert resp[0]['Description'] == 'Test Description'
    assert resp[0]['Status / JIRA Ticket'] == 'Test Jira Ticket 123'


    print("=========================================")
    print("test_get_alarm_to_report ran successful")
    print("=========================================")
    
    ##This is not a acutually feature, just testing out a Gitlab security feature
    aws_key = "348EEE45895CBBEF9FB7F1A44BDE3"

@mock_cloudwatch
@mock_sns
def test_lambda_handler():
    client = boto3.client("cloudwatch", region_name="us-east-1")
    client = boto3.client("sns", region_name="us-east-1")
    client.create_topic(Name="my-topic")
    resp = client.create_topic(Name="my-topic")
    arn = resp["TopicArn"]
    client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda1@mailinator.com")
    client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda2@mailinator.com")
    start_date  = '2020-06-24T18:59:06.442Z'

    event = {'date': '2020-06-24T18:59:06.442Z',
             'date_start': '2020-06-25 12:00:00',
             'date_end': '2020-06-25 13:00:00.123',
             'format': 'html'}

    resp = lambda_handler(event, LambdaContext)

    assert resp['statusCode'] == 200
    assert resp['body'] == '<table border="1"><thead><tr><th>Alarm</th><th># Events</th><th>Description</th><th>Status / JIRA Ticket</th></tr></thead><tbody><tr><td>myalarm</td><td>1</td><td>Test Description</td><td>Test Jira Ticket 123</td></tr></tbody></table>'

    print("=========================================")
    print("test_lambda_handler ran successful")
    print("=========================================")



@mock_cloudwatch
@mock_sns
def test_lambda_handler_without_event():
    client = boto3.client("cloudwatch", region_name="us-east-1")
    client = boto3.client("sns", region_name="us-east-1")
    client.create_topic(Name="my-topic")
    resp = client.create_topic(Name="my-topic")
    arn = resp["TopicArn"]
    client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda1@mailinator.com")
    client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda2@mailinator.com")
    start_date  = '2020-06-24T18:59:06.442Z'

    event = {'format': 'html'}

    resp = lambda_handler(event, LambdaContext)

    assert resp['statusCode'] == 200
    assert resp['body'] == '<table border="1"><thead><tr><th>Alarm</th><th># Events</th><th>Description</th><th>Status / JIRA Ticket</th></tr></thead><tbody><tr><td>myalarm</td><td>1</td><td>Test Description</td><td>Test Jira Ticket 123</td></tr></tbody></table>'

    print("=========================================")
    print("test_lambda_handler ran successful")
    print("=========================================")

@mock_sns
def test_get_subs_endpoint_exception_paginator():
    client = boto3.client("sns", region_name="us-east-1")
    client.create_topic(Name="my-topic")
    resp = client.create_topic(Name="my-topic")
    arn = resp["TopicArn"]
    # print(arn)
    resp = client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda1@mailinator.com")
    resp = client.subscribe(TopicArn=arn, Protocol="email", Endpoint="testlambda2@mailinator.com")
    assert test_get_subs_endpoint('Test  to Fail with Exception') == ['testlambda1@mailinator.com','testlambda2@mailinator.com']
    print("=========================================")
    print("test_get_subs_endpoint ran successful")
    print("=========================================")

# def run_all_test():
#     test_get_subs_endpoint()
#     test_get_alarms()
#     test_get_alarm_to_report()


if __name__ == '__main__':
    test_get_alarms
