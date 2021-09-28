const ROOM_DATA = JSON.parse(document.getElementById('room-data').textContent);
const SPACE_SIZE = 35;
const PIECE_SIZE = SPACE_SIZE * 0.45

const BOARD_COLOR = "#ddb34e"
const GRID_COLOR = "#333333"
const P1_COLOR = "#FFFFFF"
const P2_COLOR = "#000000"

const cell_transform = (cell) => {
    return (cell) * (SPACE_SIZE + 1)
}

const uncell_transform = (pos) => {
    return Math.round(pos / (SPACE_SIZE + 1)) - 1
}

const drawGrid = (canvas, board_size) => {
    let ctx = canvas.getContext('2d');
    ctx.beginPath()
    ctx.strokeStyle = GRID_COLOR

    //Vertical lines
    for (let i = 1; i <= board_size; i++) {
        ctx.moveTo(cell_transform(i) + 1, cell_transform(1))
        ctx.lineTo(cell_transform(i) + 1, cell_transform(board_size) + 1)
    }
    // Horizontal lines
    for (let j = 1; j <= board_size; j++) {
        ctx.moveTo(cell_transform(1), cell_transform(j) + 1)
        ctx.lineTo(cell_transform(board_size) + 1, cell_transform(j) + 1)
    }

    ctx.stroke();
}

const drawPiece = (canvas, x, y, color) => {
    let ctx = canvas.getContext('2d');
    const x_pos = cell_transform(x + 1) + 1;
    const y_pos = cell_transform(y + 1) + 1;

    const x_shad = x_pos + PIECE_SIZE * 0.2;
    const y_shad = y_pos + PIECE_SIZE * 0.2;

    var shadow_gradient = ctx.createRadialGradient(x_shad, y_shad, 0, x_shad, y_shad, 1.1 * PIECE_SIZE);
    shadow_gradient.addColorStop(0, "#0033");
    shadow_gradient.addColorStop(0.7, "#0036");
    shadow_gradient.addColorStop(1, "#0030");

    ctx.globalCompositeOperation = "darken";
    ctx.beginPath();
    ctx.arc(x_shad, y_shad, PIECE_SIZE * 1.05, 0, 2 * Math.PI, false);
    ctx.fillStyle = shadow_gradient;
    ctx.fill();
    ctx.globalCompositeOperation = "source-over";

    var stone_gradient = ctx.createRadialGradient(x_pos - PIECE_SIZE * 0.3, y_pos - PIECE_SIZE * 0.3, PIECE_SIZE * 0.1, x_pos, y_pos, 2 * PIECE_SIZE);
    if (color == '1') {
        stone_gradient.addColorStop(0, "#333");
        stone_gradient.addColorStop(1, "#000");
    } else {
        stone_gradient.addColorStop(0, "#fff");
        stone_gradient.addColorStop(1, "#ccc");
    }
    ctx.beginPath();
    ctx.fillStyle = stone_gradient;
    ctx.arc(x_pos, y_pos, PIECE_SIZE, 0, 2 * Math.PI, false);
    ctx.fill();
}

const drawBoard = (game_data, canvas) => {
    console.log(game_data)
    let ctx = canvas.getContext('2d');
    ctx.fillStyle = BOARD_COLOR;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawGrid(canvas, game_data.board_width);
    game_data.board.map(
        (piece) => {
            drawPiece(canvas, piece.x, piece.y, piece.value)
        }
    )
}


class PlaydotApp {
    constructor(canvas) {
        this.player = null;
        this.socket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/playdot/'
            + ROOM_DATA.gid
            + '/'
        );

        this.canvas = canvas
        this.update();
        this.attachListeners();
    }

    attachListeners() {
        this.canvas.addEventListener("mousedown", (event) => {
            const error_span = document.getElementById("error")
            if (error_span !== null) {
                error_span.remove()
            }
            if (this.player != this.game_data.next_player) {
                return
            }
            if (this.player == "observer") {
                return
            }
            const x = uncell_transform(event.offsetX)
            const y = uncell_transform(event.offsetY)
            let side;
            if (x > Math.round(this.game_data.board_width / 2)) {
                side = "R"
            } else {
                side = "L"
            }
            this.socket.send(JSON.stringify({
                'method': 'move',
                'data': {
                    'side': side,
                    'y': y,
                    'piece': this.player,
                }
            }))
        })

        this.socket.onmessage = (e) => {
            console.log("got message")
            const msg = JSON.parse(e.data);
            if (msg["method"] == "assign_player") {
                console.log("getting_assigned" + msg["data"])
                this.player = msg["data"]
            }
            if (msg["method"] == "state_change") {
                this.update()
            }
            if (msg["method"] == "invalid_move") {
                let error_span = document.createElement('span')
                error_span.id = "error"
                error_span.innerHTML = msg["data"]
                const appElement = document.getElementById("app")
                appElement.append(error_span)
            }
        };
        this.socket.onclose = (e) => {
            console.error('playdot socket closed unexpectedly');
        };
        this.socket.onopen = (e) => {
            console.log("socket channel open")
        }

    }
    update() {
        fetch(
            'state',
            {
                method: "GET",
                mode: 'same-origin',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            })
            .then(res => res.json())
            .then(data => {
                this.game_data = data
                this.canvas.height = cell_transform(
                    data.board_width + 1);
                this.canvas.width = cell_transform(
                    data.board_width + 1);
                this.draw(data)
                if (data.winner !== null) {
                    const winner_txt = document.createElement('span')
                    winner_txt.innerHTML = "Game Over! Player " + data.winner + " won!"
                    const app = document.getElementById("app")
                    app.append(winner_txt)
                }
            })

    }
    draw(game_data) {
        drawBoard(game_data, this.canvas)
    }
}


const appElement = document.getElementById("app")
if (appElement !== null) {
    const canvas = document.createElement('canvas')
    appElement.append(canvas)
    playdot = new PlaydotApp(canvas)
}