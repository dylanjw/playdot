# playdot - Sideways connect four

## How to Set Up Developer Environment

```python
python -m venv venv
. venv/bin/activate
pip install poetry
poetry install
```


### Running Tests

```python
pytest
```

### Running the Dev Server

```
./manage.py runserver
```

### Local Play

Navigate to the game lobby:
`http://localhost:8000/playdot` and click **New Game**.

Copy the address into a separate browser tab.

## More to do

- [X] Send moves/board state over channels
- [ ] Update lobby game list with games
- [X] Have players assigned, after 2 aditional players are "observers"
- [X] Make board less ugly
- [X] Simplify board state, board logic and game logic



Issues:

- [X] Player assignment is wrong. 
As players join the game, the newest player gets assigned 
instead of being made an observer

- [ ] Mid-line is wrong.