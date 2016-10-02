
var board,
  game = new Chess(current_fen),
  statusEl = $('#status'),
  fenEl = $('#fen');

if (current_player === '') {
  current_player = game.turn();  
}

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
  $("#submit_move").hide();
  document.getElementById('submit_move').style.display = 'inline';
  document.getElementById('undo_move').style.display = 'inline';
};

// update the board position after the piece snap 
// for castling, en passant, pawn promotion
var onSnapEnd = function() {
  board.position(game.fen());
  $('#undo_move').bind('click', function() {
    undo_move();
  });
  $('#submit_move').bind('click', function() {
    submit_move();
  });  
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

var submit_move = (function() {
      $.getJSON($SCRIPT_ROOT + '/_get_fen', {
        fen_move: game.fen(),
        game_id: window.location.pathname,
        current_player: current_player,
      }, function(data) {
        window.location.assign(root_path+data.game_url);
    });
    $("#undo_move").unbind();    
})

var undo_move = (function () {
    game.undo();
    board = new_game();
    set_orientation();
    document.getElementById('submit_move').style.display = 'none';
    document.getElementById('undo_move').style.display = 'none';    
    updateStatus();
})

var freeze_game = (function() {
      board = ChessBoard('board', game.fen());
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



