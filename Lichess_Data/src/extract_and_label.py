import chess
import chess.engine
import chess.pgn
import pandas as pd

pgn_file = open("data/lichess_db_standard_rated_2019-04.pgn", encoding="utf-8") # opens the lichess database file
stockfish_file = "data/stockfish/stockfish-macos-m1-apple-silicon" # stockfish engine path

fen = []
score = []

fen_max = 1000
counter = 0

stockfish_engine = chess.engine.SimpleEngine.popen_uci(stockfish_file) # initializes the stockfish engine


# A loop that runs through each game in the pgn file

while True:  #runs through each game in a pgn file until an exit condition is achieved

    game = chess.pgn.read_game(pgn_file) # reads each game in pgn_file

    if game == None or counter >= fen_max: #breaks out of the loop when all the games finish
         break
    board = chess.Board() #initializes a chess board
    for move in game.mainline_moves():  # gets the fen for the first game in the pgn file
        try:                               # visualizes a chess board and adds moves from each game in the pgn to the board. Records the FEN of every 3 move order positions
            board.push(move)
            counter += 1
            if counter % 3 == 0:
                fen.append(board.fen())
                if counter >= fen_max:
                    break
        except:                          # ingores any errors
            continue
       


# Stockfish Engine calculates the Score based on each FEN

for i in range(len(fen)):  
    boards = chess.Board(fen[i])
    info = stockfish_engine.analyse(board=boards, limit=chess.engine.Limit(depth=12))
    score.append(info['score'].white().score(mate_score=1000))


#Putting FEN and Scores in a dataframe to export as a csv file.

dataset = pd.DataFrame({"FENs":fen, "Scores":score}) 
dataset.to_csv("data/fen_and_scores.csv", index = False)



stockfish_engine.quit()
pgn_file.close()




