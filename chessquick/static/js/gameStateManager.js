function share()  {
    prompt("Share your game with this link!", root_path + game_url);
};

function updatePlayerStatus(white, black, notify) {
    document.getElementById('whiteplayer').textContent = white;
    document.getElementById('blackplayer').textContent = black;
}

var action_dict = {
        'save': showUnsave,
        'unsave': showSave,
        'notify': notifyOn,
        'unnotify': notifyOff
    }


function update(action, game_url, current_player, game) {
    if (game === undefined) {
        game = true;
    }
    toggled = action_dict[action];
    $.getJSON($SCRIPT_ROOT +'/_save', {
        action: action,
        match_url: game_url,
        current_player: current_player,
    }, function(data) {

        if (data.resp == 'need confirmation') {
            window.location.assign(root_path+game_url);
        } else {
            toggled();
            if (game == true) {updatePlayerStatus(data.white_player_name, data.black_player_name);}
        }
        
 })};

function showSave() {
    document.getElementById('save_link').textContent = 'Save!';
    $('#save_span').show();    
    document.getElementById("save_link").onclick = function (){ 
        update('save', game_url, current_player);
    };
    update('unnotify', game_url, current_player);
    $('#notify_link').hide();
    $('#notify_span').hide();
};

function showUnsave() {
    document.getElementById('save_link').textContent = 'Un-save!';
    $('#save_span').show();    
    document.getElementById("save_link").onclick = function () {
        update('unsave', game_url, current_player);
    };
    $('#notify_link').show();  
    $('#notify_span').show();
};

function notifyOn(notify) {
    document.getElementById('notify_link').textContent = 'Notify: On';
    document.getElementById('notify_link').onclick = function () {
        update('unnotify', game_url, current_player);
    };
};

function notifyOff() {
    document.getElementById('notify_link').textContent = 'Notify: Off';
    document.getElementById('notify_link').onclick = function () {
        update('notify', game_url, current_player);
    };
};


