let room_data = JSON.parse(document.getElementById('room-data').textContent);
fetch(
    '../../board/' + room_data["gid"] + "/",
    {
        method: "GET",
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(res => res.json())
    .then(data => {
        console.log(data)
        room_data = data
    })

const board = document.querySelector("#txt-board")

const playdotSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/playdot/'
    + room_data.bid
    + '/'
);

playdotSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data)
    document.querySelector('#txt-board').value = (data.as_string + '\n');
};

playdotSocket.onclose = function (e) {
    console.error('playdot socket closed unexpectedly');
};

document.querySelector('#player-input').focus();
document.querySelector('#player-input').onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#player-input-submit').click();
    }
};

document.querySelector('#player-input-submit').onclick = function (e) {
    const playerInputDom = document.querySelector('#player-input');
    const playerSelectDom = document.querySelector('#select_player');
    const move = playerInputDom.value;
    const player = playerSelectDom.value;

    playdotSocket.send(JSON.stringify({
        'move': move,
        'player': player,
        'bid': room_data.bid,
    }));
    playerInputDom.value = '';
};