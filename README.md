# Steps to run this:

go to terminal and go to inside this folder

### Setup Python Virtual Environment
> pip install virtualenv

> virtualenv myvirtualevn

For Mac OS / Linux
> source myvirtualevn/bin/activate

For Windows
> myvirtualevn\Scripts\activate


### then below commands in sequence:
pip install -r requirements.txt

pytest test/test_my_handler.py

### check coverage:
pytest --cov=src tests/

Note: There are couple of things to note when you run/test this code.

- As 'describe_alarm_history' method was not implemented in actual moto library
we implemented this in the code with the sample alarms provide.
The sample alarms are given below:
```python
alarms = [{
        "Timestamp": "2020-06-25T18:59:06.442Z",
        "HistoryItemType": "StateUpdate",
        "AlarmName": "myalarm",
        "HistoryData": "{\"version\":\"1.0\",\"oldState\":{\"stateValue\":\"ALARM\",\"stateReason\":\"testing purposes\"},\"newState\":{\"stateValue\":\"OK\",\"stateReason\":\"Threshold Crossed: 2 datapoints were not greater than the threshold (70.0). The most recent datapoints: [38.958, 40.292].\",\"stateReasonData\":{\"version\":\"1.0\",\"queryDate\":\"2014-04-09T18:59:06.419+0000\",\"startDate\":\"2014-04-09T18:44:00.000+0000\",\"statistic\":\"Average\",\"period\":300,\"recentDatapoints\":[38.958,40.292],\"threshold\":70.0}}}",
        "HistorySummary": "Alarm updated from ALARM to OK arn:aws:sns:us-east-1:123456789012:my-topic"
    },
    {
        "Timestamp": "2020-06-25T19:59:06.442Z",
        "HistoryItemType": "StateUpdate",
        "AlarmName": "myalarm",
        "HistoryData": "{\"version\":\"1.0\",\"oldState\":{\"stateValue\":\"OK\",\"stateReason\":\"Threshold Crossed: 2 datapoints were not greater than the threshold (70.0). The most recent datapoints: [38.839999999999996, 39.714].\",\"stateReasonData\":{\"version\":\"1.0\",\"queryDate\":\"2014-03-11T22:45:41.569+0000\",\"startDate\":\"2014-03-11T22:30:00.000+0000\",\"statistic\":\"Average\",\"period\":300,\"recentDatapoints\":[38.839999999999996,39.714],\"threshold\":70.0}},\"newState\":{\"stateValue\":\"ALARM\",\"stateReason\":\"testing purposes\"}}",
        "HistorySummary": "Alarm updated from OK to ALARM arn:aws:sns:us-east-1:123456789012:my-topic"
    },
    {
        "Timestamp": "2020-06-25T20:59:06.442Z",
        "HistoryItemType": "StateUpdate",
        "AlarmName": "myalarm",
        "HistoryData": "{\"version\":\"1.0\",\"oldState\":{\"stateValue\":\"OK\",\"stateReason\":\"Threshold Crossed: 2 datapoints were not greater than the threshold (70.0). The most recent datapoints: [38.839999999999996, 39.714].\",\"stateReasonData\":{\"version\":\"1.0\",\"queryDate\":\"2014-03-11T22:45:41.569+0000\",\"startDate\":\"2014-03-11T22:30:00.000+0000\",\"statistic\":\"Average\",\"period\":300,\"recentDatapoints\":[38.839999999999996,39.714],\"threshold\":70.0}},\"newState\":{\"stateValue\":\"ALARM\",\"stateReason\":\"testing purposes\"}}",
        "HistorySummary": "Alarm updated from OK to ALARM arn:aws:sns:us-east-1:123456789012:my-topic"
    }]
```

This is just for testing purpose, so if you want to modify it you can go below
and modify it according to your alarms and need to modify the test cases accordingly:
> package -> moto -> cloudwatch -> responses.py -> line 142

- In the testing we use environment variable SUBSCRIPTORS_TO_REPORT.
If there is no data get found in that variable then by default it will take 'testlambda1@mailinator.com' as a value.


### Deactivate the virtual environment
To decativate the virtual environment and use your original Python environment, simply type ‘deactivate’.
> deactivate
