import os
import time
import random

import requests
import pytz
from requests_oauthlib import OAuth1Session
# from dotenv import load_dotenv
from datetime import datetime

MAX_RETRIES = 7
RETRY_DELAY = 2
ALL_CAMERAS = 64422


def handler(event, context):
	response = tweet(webcam_stringify())
	print(response)

	# print(webcam_stringify())


def tweet(status):
	client_key = os.environ["CONSUMER_KEY"]
	client_secret = os.environ["CONSUMER_SECRET"]
	token = os.environ["ACCESS_TOKEN"]
	token_secret = os.environ["ACCESS_TOKEN_SECRET"]

	twitter = OAuth1Session(client_key, client_secret=client_secret, resource_owner_key=token,
							resource_owner_secret=token_secret)
	data = {
		"status": status
	}
	response = twitter.post("https://api.twitter.com/1.1/statuses/update.json", data=data)
	return response


def webcam_stringify():
	data = get_embedded_webcam()
	tweet_string = f'ID: {data["id"]}\n'\
				   f'Link type: {data["type"]}\n'\
				   f'Location: {data["location"]["city"]}, {data["location"]["country"]}\n'\
				   f'Lat/Long: {data["location"]["latitude"]}, {data["location"]["longitude"]}\n'\
				   f'Local time: {get_local_time(data["location"]["timezone"])}\n'\
				   f'Cam link: {data["link"]}\n'\
				   f'Map link: {map_link(data["location"]["latitude"], data["location"]["longitude"])}\n'
	return tweet_string


def get_embedded_webcam():
	webcam_id = get_new_webcam_id()
	player_response = windy_request("GET", f'https://api.windy.com/api/webcams/v2/list/webcam={webcam_id}?show=webcams:player')
	location_response = windy_request("GET", f'https://api.windy.com/api/webcams/v2/list/webcam={webcam_id}?show=webcams:location')
	player_data = player_response.json()
	location_data = location_response.json()

	players = player_data["result"]["webcams"][0]["player"]
	live = players["live"]
	day = players["day"]

	location = location_data["result"]["webcams"][0]["location"]

	response = {
		"id": webcam_id,
		"location": location,
		"type": "",
		"link": "",
	}

	if live["available"]:
		response["type"] = "live stream"
		response["link"] = live["embed"]
	elif day["available"]:
		response["type"] = "24hr time-lapse"
		response["link"] = day["embed"]
	return response


def map_link(lat, long):
	return f'https://www.google.com/maps/search/?api=1&query={lat},{long}'


def get_local_time(timezone):
	timezone_obj = pytz.timezone(timezone)
	local_time = datetime.now(timezone_obj)

	return local_time


def get_new_webcam_id():
	response = windy_request("GET", f'https://api.windy.com/api/webcams/v2/list/limit=1,{generate_offset()}')
	data = response.json()

	return data["result"]["webcams"][0]["id"]


def generate_offset():
	return random.randint(0, ALL_CAMERAS)


def windy_request(method, url):
	headers = {
		"x-windy-key": os.environ["WINDY_API_SECRET_KEY"],
		"Authorization": "Bearer " + os.environ["WINDY_BEARER_TOKEN"]
	}

	for i in range(MAX_RETRIES):
		try:
			response = requests.request(method, url, headers=headers, timeout=5)
			return response
		except requests.exceptions.Timeout as e:
			print("Timeout Error: ", e)
		except requests.exceptions.RequestException as e:
			print("Error: ", e)

		if i == MAX_RETRIES - 1:
			break
		time.sleep(RETRY_DELAY)

# load_dotenv()
# handler("", "")