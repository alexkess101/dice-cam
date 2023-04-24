import os
from requests_oauthlib import OAuth1Session

def handler(event, context):
	response = tweet("something else")
	print(response.text)


def tweet(tweet):
	client_key = os.environ["CONSUMER_KEY"]
	client_secret = os.environ["CONSUMER_SECRET"]
	token = os.environ["ACCESS_TOKEN"]
	token_secret = os.environ["ACCESS_TOKEN_SECRET"]

	twitter = OAuth1Session(client_key, client_secret=client_secret, resource_owner_key=token, resource_owner_secret=token_secret)
	request = f'https://api.twitter.com/1.1/statuses/update.json?status={tweet}'
	print(request)
	data = {
		"status": tweet
	}
	response = twitter.post("https://api.twitter.com/1.1/statuses/update.json", data=data)
	return response