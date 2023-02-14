from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)

@app.route('/webhook',methods=['POST'])
def webhook():
  player = request.form.get('From')
  message = request.form.get('Body').lower()
  return respond(f'You are: {player}.\nYou said: {message}')

def respond(message):
  response = MessagingResponse()
  response.message(message)
  return str(response)
