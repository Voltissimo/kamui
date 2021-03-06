from collections import defaultdict
from engine import game, UCI
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)


@app.route('/position', methods=["GET"])
def get_position():
    fen = request.args.get('fen')
    moves = request.args.get('m', default=None)
    if moves is not None:
        new_fen, move_made_pgn = UCI.position(fen, moves, return_move=True)
    else:
        new_fen, move_made_pgn = fen if fen != "startpos" else game.Board.create_standard_board().to_FEN(), ''
    success = True
    if new_fen == fen and moves:
        return jsonify({'success': False, 'error': f'Move {moves} cannot be made.'})
    else:
        possible_moves = defaultdict(list)
        board = game.Board.from_FEN(new_fen)
        for move in board.current_player.calculate_legal_moves():
            possible_moves[move.original_coordinate].append(move.destination_coordinate)
        return jsonify({
            'success': success,
            'fen': new_fen,
            'move': move_made_pgn,
            'moves': possible_moves,
            'checkmate': board.current_player.is_in_checkmate(),
            'stalemate': board.current_player.is_in_stalemate()
        })


@app.route('/go', methods=["GET"])
def get_best_move():
    fen = request.args.get('fen')
    depth = request.args.get('d', type=int, default=4)
    return jsonify({'move': UCI.go(fen, depth)})


@app.route('/favicon.ico', methods=["GET"])
def get_favicon():
    return send_file('favicon.ico')

if __name__ == '__main__':
    app.run()
