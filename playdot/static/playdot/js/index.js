document.querySelector('#game-id-input').focus();
document.querySelector('#game-id-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#game-id-submit').click();
    }
};

document.querySelector('#game-id-submit').onclick = function(e) {
    var gameID = document.querySelector('#game-id-input').value;
    window.location.pathname = '/playdot/' + gameID + '/';
};
