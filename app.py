from io import BytesIO
import os
import random
import chess
import chess.svg
import cairosvg
from dotenv import load_dotenv
from flask import Flask, request, url_for
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

app = Flask(__name__)
client = Client()
twilio_number = os.environ.get('TWILIO_NUMBER')
players = [
    os.environ['MY_NUMBER'],
    os.environ['FRIEND_NUMBER'],
]
board = None

def respond(message):
    response = MessagingResponse()
    response.message(message)
    return str(response)

@app.route('/webhook', methods=['POST'])
def webhook():
    player = request.form.get('From')
    if player not in players:
        return respond('You are not a player. Bye!')
    opponent = players[0] if players[1] == player else players[1]
    message = request.form.get('Body').lower()

    if message == 'play':
        return new_game()

    if message == 'resign':
        return resign_game(opponent)

    if board is None:
        return respond('You are not currently playing a game. '
                       'Type "play" to start one.')

    if (board.turn == chess.WHITE and player != players[0]) or \
            (board.turn == chess.BLACK and player != players[1]):
        return respond('Not your turn to move!')

    try:
        move = chess.Move.from_uci(message)
        if move not in board.legal_moves:
            raise ValueError()
    except ValueError:
        return respond('Invalid move, please try again.')

    board.push(move)
    return send_move(opponent, move)


def new_game():
    global board, players
    if board is not None:
        return respond('A game is currently in progress. '
                       'Type "resign" to end it.')
    board = chess.Board()
    random.shuffle(players)
    send_move(players[0])
    return str(MessagingResponse())

def resign_game(winner):
    global board, players
    if board is None:
        return respond('You are not currently playing a game. '
                       'Type "play" to start one.')
    board = None

    client.messages.create(from_=twilio_number,
                           to=winner,
                           body='Your opponent resigned. You win!')
    return respond('Okay.')

def send_move(player, last_move=None):
    is_black = player == players[1]
    client.messages.create(from_=twilio_number, to=player,
                           body='It\'s your turn to play!',
                           media_url=url_for(
                               'render_board', fen=board.fen(),
                               last_move=last_move,
                               flip='1' if is_black else None,
                               _external=True))
    return respond('Got it! Now waiting for your opponent to move.')

@app.route('/board')
def render_board():
    board = chess.Board(request.args.get('fen'))
    flip = request.args.get('flip', False)
    last_move = None
    if 'last_move' in request.args:
        last_move = chess.Move.from_uci(request.args.get('last_move'))
    png = BytesIO()
    cairosvg.svg2png(bytestring=chess.svg.board(
        board, lastmove=last_move, flipped=flip), write_to=png)
    return png.getvalue(), 200, {'Content-Type': 'image/png'}
