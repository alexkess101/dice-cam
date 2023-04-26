import os

from requests_oauthlib import OAuth1Session


def lambda_handler(event, context):
	params = event["queryStringParameters"]
	status = params["status"]
	client_key = params["clientKey"]
	client_secret = params["clientSecret"]
	token = params["token"]
	token_secret = params["tokenSecret"]

	if os.environ["ALEX_KEY"] == params["alexKey"]:
		return {
			'statusCode': 200,
			'body': tweet(status, client_key, client_secret, token, token_secret)
		}


def tweet(status, client_key=os.environ["CONSUMER_KEY"], client_secret=os.environ["CONSUMER_SECRET"], token=os.environ["ACCESS_TOKEN"], token_secret=os.environ["ACCESS_TOKEN_SECRET"]):
	twitter = OAuth1Session(client_key, client_secret=client_secret, resource_owner_key=token, resource_owner_secret=token_secret)
	data = {
		"status": status
	}
	response = twitter.post("https://api.twitter.com/1.1/statuses/update.json", data=data)
	return response
