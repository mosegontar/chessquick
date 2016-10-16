function share()  {
    prompt("Share your game with this link!", root_path + game_url);
};

function updatePlayerStatus(white, black) {
    document.getElementById('whiteplayer').textContent = white;
    document.getElementById('blackplayer').textContent = black;
}

updatePlayerStatus(white, black);  

var action_dict = {
        'save': showUnsave,
        'unsave': showSave
    }

function update(action) {
    toggled = action_dict[action];
    $.getJSON($SCRIPT_ROOT +'/_save', {
        action: action,
        match_url: game_url,
        current_player: current_player,
    }, function(data) {
        toggled();
        updatePlayerStatus(data.white_player_name, data.black_player_name);
 })};

function showSave() {
    document.getElementById('save_link').textContent = 'Save!';
    document.getElementById("save_link").onclick = function (){ 
        update('save');
    };
};

function showUnsave() {
    document.getElementById('save_link').textContent = 'Un-save!';
    document.getElementById("save_link").onclick = function () {
        update('unsave');
    };
};

