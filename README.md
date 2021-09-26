# playdot - Sideways connect four

## Gameplay

## How to Set Up Developer Environment

### Running Tests

### Running the Dev Server

### Local Play

Navigate to the game lobby:
`http://localhost:8000/playdot` and click **New Game**.

In a separate browser tab open the lobby page and the new game should be listed. Click on it to join the game.

## More to do

- [ ] Send moves/board state over channels
- [ ] Update lobby game list with games
- [ ] Have players assigned, after 2 aditional players are "observers"
- [X] Make board less ugly
- [X] Simplify board state, board logic and game logic


Data model API:

- get all active game bid
- get a specific board state
- change board state --> make a move

Game object - Holds a specific game, as well as logic for running/scoring a game. Extra game state data.
Dumb grid based board persistence. Retrieves and updates the grid.
Active games...vs inactive for listing. we need a "Games" model.