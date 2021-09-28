document.querySelector('#create-new-game').onclick = function (e) {
    fetch(
        'board/create/7',
        {
            method: "POST",
            mode: 'same-origin',
            headers: {
                'X-CSRFToken': csrftoken
            }
        }
    ).then(res => res.json())
        .then(data => {
            console.log(data)
            window.location.pathname = "playdot/board/" + data["gid"]
        })
};
