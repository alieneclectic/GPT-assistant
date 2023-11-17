from flask import Flask, render_template, request, jsonify
import requests
import json
import time
from replit import db
import os

app = Flask(__name__)

# Set the OpenAI token and assistant ID
openAI_token = os.environ['OPENAI_KEY']
assistant_id = os.environ['OPENAI_ASSISTANT_ID']

headers = {
  'OpenAI-Beta': 'assistants=v1',
  'Authorization': f'Bearer {openAI_token}',
  'Content-Type': 'application/json'
}


@app.route('/')
def home():
  return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
  user_message = request.form['message']
  thread_id = db.get('thread_id')

  if not thread_id:
    # Create a new thread if one does not exist and store it in the db
    thread_creation_response = requests.post(
      'https://api.openai.com/v1/threads', headers=headers)
    thread_id = thread_creation_response.json()['id']
    db['thread_id'] = thread_id

  # Add a message to the thread
  message_data = {'role': 'user', 'content': user_message}
  requests.post(f'https://api.openai.com/v1/threads/{thread_id}/messages',
                headers=headers,
                data=json.dumps(message_data))

  # Create a run to get the assistant's response
  run_data = {'assistant_id': assistant_id}
  creation_response = requests.post(
    f'https://api.openai.com/v1/threads/{thread_id}/runs',
    headers=headers,
    data=json.dumps(run_data))
  run_id = creation_response.json()['id']

  # Wait for the run to complete
  def wait_till_run_complete():
    while True:
      status_response = requests.get(
        f'https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}',
        headers=headers)
      if status_response.status_code != 200:
        raise Exception(f"Error fetching run status: {status_response.text}")
      status = status_response.json()['status']
      if status not in ['queued', 'in_progress']:
        break
      time.sleep(1)

  wait_till_run_complete()

  # Get the assistant's response
  response = requests.get(
    f'https://api.openai.com/v1/threads/{thread_id}/messages', headers=headers)
  messages = response.json()['data']
  assistant_message = next(
    (msg for msg in messages if msg['role'] == 'assistant'),
    {}).get('content', [{
      'text': {
        'value': 'No response'
      }
    }])[0]['text']['value']

  return jsonify({'response': assistant_message})


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
