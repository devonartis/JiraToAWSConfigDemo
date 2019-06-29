#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import boto3
import json
from botocore.vendored import requests

def add_priority(issue, priority):
	fields = issue["fields"]
	fields["priority"] = {"name": priority}

def add_assignee(issue, assignee):
	fields = issue["fields"]
	fields["assignee"] = {"name": assignee}

def add_due_date(issue, due_date):
	fields = issue["fields"]
	fields["duedate"] = due_date

def handler(event, context):

	client = boto3.client("ssm")

	ssm_parameter_name = event["SSMParameterName"].strip()

	secret = client.get_parameter(Name=ssm_parameter_name, WithDecryption=True)['Parameter']['Value']

	username = event["JiraUsername"].strip()
	url = event["JiraURL"].strip()

	issue = {
		"fields": {
			"summary": event["IssueSummary"].strip(),
			"project": {
				"key": event["ProjectKey"].strip()
			},
			"description": event["IssueDescription"].strip(),
			"issuetype": {
				"name": event["IssueTypeName"].strip()
			}
		}
	}

	priority = event["PriorityName"].strip()
	if priority:
		add_priority(issue, priority)

	assignee = event["AssigneeName"].strip()
	if assignee:
		add_assignee(issue, assignee)

	due_date = event["DueDate"].strip()
	if due_date:
		add_due_date(issue, due_date)

	data = json.dumps(issue)

	headers = {'Content-Type':'application/json'}

	response = requests.post('{0}/rest/api/2/issue/'.format(url),
							 headers=headers,
							 data=data,
							 auth=(username, secret))

	if not response.ok:
		raise Exception("Received error with status code " + str(response.status_code) + " from Jira")
	else:
		issue_key = (response.json()["key"])
		return {"IssueKey": issue_key}







