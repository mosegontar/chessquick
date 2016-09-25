var current_player = "b";
var current_fen = 'rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1'
var board,
  game = new Chess(current_fen),
  statusEl = $('#status'),
  fenEl = $('#fen');

///////////////////////////////////////////////////////////////////////////////
/* Code integrating ChessBoardJS with ChessJS from ChessBoardJS example:
http://chessboardjs.com/examples#5000 */

// do not pick up pieces if the game is over
// only pick up pieces for the side to move
var onDragStart = function(source, piece, position, orientation) {
  if (game.game_over() === true ||
      (game.turn() === 'w' && piece.search(/^b/) !== -1) ||
      (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
    return false;
  }
};

var onDrop = function(source, target) {
  // see if the move is legal
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  });

  // illegal move
  if (move === null) return 'snapback';
  updateStatus();
};

// update the board position after the piece snap 
// for castling, en passant, pawn promotion
var onSnapEnd = function() {
  board.position(game.fen());
  freeze_game();
};

var updateStatus = function() {
  var status = '';

  var moveColor = 'White';
  if (game.turn() === 'b') {
    moveColor = 'Black';
  }

  // checkmate?
  if (game.in_checkmate() === true) {
    status = 'Game over, ' + moveColor + ' is in checkmate.';
  }

  // draw?
  else if (game.in_draw() === true) {
    status = 'Game over, drawn position';
  }

  // game still on
  else {
    status = moveColor + ' to move';

    // check?
    if (game.in_check() === true) {
      status += ', ' + moveColor + ' is in check';
    }
  }

  statusEl.html(status);
  fenEl.html(game.fen());
  
};

var new_game = function () {
  var cfg = {
    draggable: true,
    position: game.fen(),
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd
  };
  board = ChessBoard('board', cfg);
  return board;
}

updateStatus();
/////////////////////////////////////////////////////////

var freeze_game = (function() {
      board = ChessBoard('board', game.fen());
      $.getJSON('/_get_fen', {
        a: game.fen(),
      }, function(data) {
        return;
      });
      set_orientation();
});

var set_orientation = function() {
    if (current_player === 'w') {
        board.orientation('white');
    } else {
        board.orientation('black');
    }
};

if (game.turn() !== current_player) {
  board = ChessBoard('board', game.fen());
}
else {
  board = new_game();
};
set_orientation();
