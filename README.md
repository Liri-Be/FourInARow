# FourInARow
## The game
Four in a row game - user vs. computer.  
Each turn the users selects a column and drop a token, the first one (user or computer) that gets 4 token in a row, colum or diagonal wins.  
Has 2 levels - 
1. Easy - the computer puts tokens randomly.
2. Hard - the computer tries to block the user from winning.
## Server
1. Handles the game - handels connection to the game, place the tokens in the board and checks who wins.
2. Plays as computer - chooses a columns to drop token to.
## Client
User - 
1. Chooses the level of the game.
2. Lets the user choose column to drop to.
