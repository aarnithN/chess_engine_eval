# Chess Engine using Stockfish Score Evaluations

A pygame GUI chess game where users have the option to play against one another or against an engine. Trained with Stockfish engine evaluations on over 1k games from Lichess Database and built using a CNN regression architecture(predicting eval scores). Engine searches for the best move based on the highest eval score generated from the CNN evaluated on the current position and pushes it to the board. 

## Chess Game GIF

## Inspiration

Tools: python, pygame, numpy, pandas, scikit-learn, tensorflow, chess library

I've had a spotty relationship with chess ever since I was in middle school. From joining the Fallon Chess team to winning Berkley School of CHess competitions and to eventually shutting it out for the majority of high school. Although I hadn't played actively, chess is always something that I have come back to, and even now I am trying to partiicpate in more tournaments while keeping up with some of my favorite players such as R. Pragnananda and Alireza Firouja. As such, for my first project I wanted something that stayed close to my passion for chess while also relating to currently learning deep learning. The result; a chess engine incorporating AI. My goal was to first create a functional CNN architecture that would predict evaluation scores based on current chess positions. To do this, I parsed through a pgn file from the lichess database and extracted FEN's( a notiation for capturing chess positions put simply) and used open source Stockfish engine to predict eval scores for these games. After the data extraction and putting the features (FENSs) and target (Scores) into a csv file I exported, I  cleaned and transformed that data for input to the CNN model. I split up the fen into multiple features including the position, castling rights, player turn, Full Move, Half Move, etc. and normalized it to allow the CNN model to read it. I then converted the position into a tensor matrix of (8,8,12), 8 by 8 for the size of the board and 12 channels for each of the piece types. Using these inputs I was able to train the model to output a regression score based on a current position. I had completed my first goal but I thought I could make it cooler if I could actually play against an engine using this model. I had expereince in python but by using a youtube tutorial by "Coding Spot" I was able to create a functioning chess gui for player vs player, where I then implemented the ml model to play against. 


## Usage

press 't' on keyboard to change the theme 
press 'r' on keyboard to restart
press 'c' on keyboard to play against AI


## Set up instructions

Clone repo first 

1.  Set up Virtual Environment

Mac/Linux 

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

2. install required packages

```bash
pip install -r requirements.txt
```

3. run main file

```bash
cd Chess_GUI/src/
python main.py
```


# Project optimizations
- adjusted epochs, filter size, and increased layers
- adjusted amount of training data to find balance between overfitting and underfitting



### Limitations/future optimizations
- Improve the precision of eval scores:
    - Add an extra channel for better interpretability 
    - Increase the amount of layers or adjust filter size to capture more patterns
    - Use higher quality games such as grandmaster/elite level games for better score accuracy and move output
- Enable functionality for the engine to play as white
- Fix piece move bugs and any existing bugs
- Use minimax algorithm to provide the engine with higher search depth

### Lessons/Learning Oppurtunies
The model did not work as accurate as I hoped but I don't plan to give up. I'm going to first try optimizing various aspects of my CNN model such as adding an extra dimension for the model to better understand pawn structures, tactic patterns, and piece value. I will also try using higher level chess data to get more accurate evaluation scores. However I learned a lot about the data science workflow and how to extract real world data and build a CNN model with a lot of tweaking and optimization. Additionally learned a lot about model pipelines and creating a CNN model from scratch which was really cool. Huge credits to

## Suggestions
Please feel free to send any issues that you find I am more than happy to review/fix them. Hopefully I want to try to get my model to at least 1,000 elo for my next milestone goal.

#Credits

- This project builds upon the GUI framework provided by AlejoG10 on their youtube channel: "Coding Spot" at https://www.youtube.com/watch?v=OpL0Gcfn4B4 
- The assets folder is taken from author's github repo as allowed in the tutorial video: Github Repo: https://github.com/AlejoG10/python-chess-ai-yt 
- PGN chess data from Lichess Open Database: https://database.lichess.org under Creative Commons CCO license: https://creativecommons.org/publicdomain/zero/1.0/
- Stockfish engine for evaluating FEN's: https://stockfishchess.org under GPL lisence v3 https://www.gnu.org/licenses/gpl-3.0.html



Note: CNN Architecture, Lichess data preprocessing, AI implementation in GUI interface, bug fixes including stalemate function, checkmate function, pop-up window, etc. were created and implemented seperately and independently. 






