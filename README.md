# Four In a Row
## The game
Four in a row game - user vs. computer.  
Each turn the user and the computer select a column and drop a token, the first one (user or computer) that gets 4 token in a row, colum or diagonal wins.  
Has 2 levels - 
1. Easy - the computer puts tokens randomly.
2. Hard - the computer tries to block the user from winning.
## Server.py
Server is the computer - the game from the computer prespective - 
1. Handles the game - 
   - Handels connection to the game
   - Choose a column for the computer to drop a token in
   - Check user's input
   - Place the tokens in the board (for both - user and computer)
   - Checks who wins 
   - Calculate statisticts for each round and game
2. Plays as computer - chooses a columns to drop token to.
## Client
The game from the user prespective - 
1. Chooses the level of the game.
2. Lets the user choose column to drop to.
