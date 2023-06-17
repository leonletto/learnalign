# agenda = {"course": "Math", "topic": "Quadratic Functions", "subtopic":""}
# user = {"age": 13, "interest": "baseball"}

import openai
import requests

OPENAI_API_KEY = "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"
X_RapidAPI_Key = "619309f7a7msh6e974be053cf6afp15e693jsn158ac76a32d7"
X_RapidAPI_Host = "large-text-to-speech.p.rapidapi.com"

openai.api_key = OPENAI_API_KEY


def get_story(temperature=0):
  input_prompt = (
    "Below is an instruction that describes a task, paired with an input that provides further context."
    "Write a response that appropriately completes the request.\n\n"
    "### Instruction:\n"
    f"Teach a {user['age']} year old a new topic with a story about {user['interest']}\n\n"
    "### Input: \n"
    f"{agenda['course']}-{agenda['topic']}\n\n"
    "### Response: \n"
    "[your_response]")

  messages = [{"role": "user", "content": input_prompt}]
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=temperature,
  )
  return response.choices[0].message["content"]


def request_speach(text):
  url = "https://large-text-to-speech.p.rapidapi.com/tts"

  payload = {"text": text}
  headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": X_RapidAPI_Key,
    "X-RapidAPI-Host": X_RapidAPI_Host
  }

  response = requests.post(url, json=payload, headers=headers).json()
  job_id = response['id']
  job_status = response['status']

  return job_id, job_status


def get_speach(job_id):
  url = "https://large-text-to-speech.p.rapidapi.com/tts"

  querystring = {"id": job_id}

  headers = {
    "X-RapidAPI-Key": X_RapidAPI_Key,
    "X-RapidAPI-Host": X_RapidAPI_Host
  }

  response = requests.get(url, headers=headers, params=querystring).json()
  job_status = response['status']
  if job_status != 'success':
    url = ""
  else:
    url = response['url']
  return url, job_status


# import time
# story = get_story()
# job_id, status = request_speach(story)
# while status != 'success':
#   time.sleep(5)
#   url, status = get_speach(job_id)
