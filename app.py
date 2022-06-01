import os
import uuid

from flask import Flask, abort, jsonify, send_from_directory
from flask_sock import Sock

from connection_handler import GameConnectionHandler
from db_handler import DBHandler

app = Flask(__name__, static_folder='build')
sock = Sock(app)

game_connection_handler = GameConnectionHandler(app.logger)
db_handler = DBHandler()


@app.route('/api/new-game', methods=['POST'])
def new_game():
    game_instance = game_connection_handler.new_game()
    db_handler.manage_game(game_instance)

    game_id = game_instance.id
    return jsonify({'game_id': game_id})


@sock.route('/api/game/<game_id>')
def game_endpoint(ws, game_id):
    if game_id is None or not game_connection_handler.has_game(game_id):
        return jsonify(abort(404, 'Game not found'))

    player_id = str(uuid.uuid4()).split('-')[-1]
    try:
        game_connection_handler.add_connection(game_id, ws, player_id)
    except ValueError:
        return jsonify(abort(404, 'Game not found'))

    while True:
        try:
            data = ws.receive()
            game_connection_handler.handle_client_message(game_id, player_id, data)
        except ConnectionError:
            app.logger.warning('[gId: %s][pId: %s] A player disconnected')
            game_connection_handler.close_connection(game_id, player_id)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
