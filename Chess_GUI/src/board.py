from constant import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import os
import copy
import chess
import numpy as np
import random



class Board:

    def __init__(self):

    
        self.squares = [[0,0,0,0,0,0,0,0] for col in range(COLUMNS)]
        self.last_move = None

        self._create()

        self.add_pieces("white")
        self.add_pieces("black")


    def move(self, piece, move, testing = False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        #console board move update

        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece


        if isinstance(piece, Pawn):

            #capture en_passant
            diff = final.col - initial.col

            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col+diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:

                    sound = Sound(os.path.join("assets/sounds/capture.wav"))
                    sound.play()

            
            # pawn en passant
            
            if final.row == 0 and piece.color == "white" or final.row == 7 and piece.color == "black":
               return "promotion", (final.row, final.col, piece.color)
            
        
            
        if isinstance(piece, King):

            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if diff < 0 else piece.right_rook
                
                if rook and rook.moves:
                    self.move(rook, rook.moves[-1])
                    piece.clear_moves()

                if diff < 0:
                    return "queenside castling", None
                else:
                    return "kingside castling", None
        
        
        #move
        piece.moved = True

        #clear valid moves
        piece.clear_moves()

        #set last move
        self.last_move = move

        return "moved", None


    def valid_move(self,piece,move):
        return move in piece.moves

    def check_promotion(self, piece, final):

        if final.row == 0 and piece.color == "white" or final.row == 7 and piece.color == "black":
           return "promotion", (final.row, final.col, piece.color)   

    def pawn_promotion(self, row, col, piece_type, color):
        if piece_type == "queen":
            self.squares[row][col].piece = Queen(color)
        elif piece_type == "rook":
            self.squares[row][col].piece = Rook(color)
        elif piece_type == "bishop":
            self.squares[row][col].piece = Bishop(color)
        elif piece_type == "knight":
            self.squares[row][col].piece = Knight(color)
    
    
    def chess_board_update(self, initial_row, initial_col, final_row, final_col, board, result, promoted_piece):


        col_encoding = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6:"g", 7:"h" }
        row_encoding = {0: "8", 1: "7", 2: "6", 3:"5", 4: "4", 5: "3", 6: "2", 7: "1"}

        uci = ""
        initial_row_encoding = row_encoding[initial_row]
        initial_col_encoding = col_encoding[initial_col]
        
        final_row_encoding = row_encoding[final_row]
        final_col_encoding = col_encoding[final_col]

        piece_promoted = str(promoted_piece)[0].lower()

        if result == "promotion":
            uci = (uci + initial_col_encoding +  initial_row_encoding + final_col_encoding + final_row_encoding + piece_promoted)
        else:
            uci = (uci + initial_col_encoding +  initial_row_encoding + final_col_encoding + final_row_encoding)

        push_obj = chess.Move.from_uci(uci)
        
       
        board.push(push_obj)
      
    
    def machine_white_move(self, board, fen_to_position, transform_fen_features, model):
        best_move = None
        best_eval = float('-inf')
        
        for move in board.legal_moves:
            board_copy = board.copy()
            board_copy.push(move)
            fen = board_copy.fen()

            split = fen.split(" ")
            feature_arr = transform_fen_features(split)

            position = split[0]

            tensor = fen_to_position(position)
            tensor = np.transpose(tensor, (1, 2, 0)).astype('float32') 
            tensor_input = np.expand_dims(tensor, axis=0) 

            predict_score = model.predict([tensor_input, feature_arr], verbose=0)
            ml_score = predict_score[0][0]

            if ml_score > best_eval:
                best_eval = ml_score
                best_move = move
            
        return str(best_move)



    def machine_black_move(self, board, fen_to_position, transform_fen_features, model):
        
        best_move = None
        best_eval = float('inf')
        
        for move in board.legal_moves:
            board_copy = board.copy()
            board_copy.push(move)
            fen = board_copy.fen()

            split = fen.split(" ")
            feature_arr = transform_fen_features(split)

            position = split[0]

            tensor = fen_to_position(position)
            tensor = np.transpose(tensor, (1, 2, 0)).astype('float32') 
            tensor_input = np.expand_dims(tensor, axis=0) 

            predict_score = model.predict([tensor_input, feature_arr], verbose=0)
            ml_score = predict_score[0][0]

            if ml_score < best_eval:
                best_eval = ml_score
                best_move = move
            
        return str(best_move)
    
    def machine_promotion(self, final_row, final_col, piece, color):
        if isinstance(piece, Pawn):
            if final_row == 7 and color == "black":
                options = [Queen(color), Rook(color),Bishop(color),Knight(color)]
                probabilities = [0.7, 0.1, 0.1, 0.1]
                promoted_piece = random.choices(options, weights = probabilities, k=1)[0]
                self.squares[final_row][final_col].piece = promoted_piece
    
    def move_to_board(self, move):
        col_encoding = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g":6, "h":7 }
        row_encoding = {"8": 0, "7": 1, "6": 2, "5":3, "4": 4, "3": 5, "2": 6, "1": 7}

        initial_col = col_encoding[move[0]]
        initial_row = row_encoding[move[1]]

        final_col = col_encoding[move[2]]
        final_row = row_encoding[move[3]]

        return initial_col, initial_row, final_col, final_row

    
    
    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2
    
    
    def set_true_en_passant(self, piece):
        if not isinstance(piece, Pawn):
            return
        
        for row in range(ROWS):
            for col in range(COLUMNS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
                    

        piece.en_passant = True


    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing=True)


        for row in range(ROWS):
            for col in range(COLUMNS):
                if temp_board.squares[row][col].has_rival_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool = False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
                            
        return False


    def return_in_check(self):
        return "in check"
    
    def check_history(self,color):

        king = None
        king_position = None
        for row in range(ROWS):
            for col in range(COLUMNS):
                piece = self.squares[row][col].piece
                if piece and piece.color == color and isinstance(piece, King):
                    king = piece
                    king_position = Square(row, col)
                    break
            if king:
                break
        
        
        #not in check 
        if self.in_check(king,Move(king_position, king_position)):
            return True
        
        return False
        

    
    def in_stalemate(self, color):
        
        #king position
        king = None
        king_position = None
        for row in range(ROWS):
            for col in range(COLUMNS):
                piece = self.squares[row][col].piece
                if piece and piece.color == color and isinstance(piece, King):
                    king = piece
                    king_position = Square(row, col)
                    break
            if king:
                break
        
        
        #not in check 
        if self.in_check(king,Move(king_position, king_position)):
            return False
        
        # No legal moves for any pieces
        for row in range(ROWS):
            for col in range(COLUMNS):
                piece = self.squares[row][col].piece
                if piece and piece.color == color:
                    self.calc_moves(piece, row, col, bool = True)
                    if piece.moves:
                        return False
                
        return True

    def in_checkmate(self, color):

        #king position
        king = None
        king_position = None
        for row in range(ROWS):
            for col in range(COLUMNS):
                piece = self.squares[row][col].piece
                if piece and piece.color == color and isinstance(piece, King):
                    king = piece
                    king_position = Square(row, col)
                    break
            if king:
                break
        
        
        #not in check
        if not self.in_check(king,Move(king_position, king_position)):
            return False
        
        #No legal moves for any pieces 
        for row in range(ROWS):
            for col in range(COLUMNS):
                piece = self.squares[row][col].piece
                if piece and piece.color == color:
                    self.calc_moves(piece, row, col, bool = True)
                    for move in piece.moves:
                        if not self.in_check(piece, move):
                            return False
         
        return True


    def calc_moves(self,piece, row, col, bool = True):

        def pawn_moves():
            if piece.moved:
                steps = 1
            else:
                steps = 2

            #vertical moves
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for move_row in range(start,end,piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        initial = Square(row, col)
                        final = Square(move_row, col)

                        move = Move(initial=initial, final=final)


                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
                            
                        
                    else:
                        break
                else:
                    break

            #diagonal moves

            move_rows = row + piece.dir
            move_cols = [col -1,col+1]
            for move_col in move_cols:
                if Square.in_range(move_row,move_col):
                    if self.squares[move_rows][move_col].has_rival_piece(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[move_row][move_col].piece
                        final = Square(move_rows, move_col, final_piece)
                        move = Move(initial=initial, final=final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            #en_passant moves

            r = 3 if piece.color == "white" else 4
            fr = 2 if piece.color == "white" else 5

            #left en_passant
            if Square.in_range(col -1) and row == r:
                if self.squares[row][col-1].has_rival_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)
                            move = Move(initial=initial, final=final)
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

            #right en_passant

            if Square.in_range(col + 1) and row == r:
                if self.squares[row][col+1].has_rival_piece(piece.color):
                    p = self.squares[row][col+1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col+1, p)
                            move = Move(initial=initial, final=final)
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)


        def knight_moves():
            possible_moves = [
                (row -2, col + 1),
                (row -2, col -1),
                (row -1, col -2),
                (row -1, col + 2),
                (row +1, col -2),
                (row +1, col + 2),
                (row +2, col -1),
                (row +2, col + 1),
            ]
            
            for move in possible_moves:
                possible_row_move, possible_col_move = move
                if Square.in_range(possible_row_move, possible_col_move):
                    if self.squares[possible_row_move][possible_col_move].isempty_or_rival(piece.color):
                        initial = Square(row,col)
                        final_piece = self.squares[possible_row_move][possible_col_move].piece
                        final = Square(possible_row_move,possible_col_move,final_piece)

                        move = Move(initial=initial, final=final)

                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            #else:
                                #break
                        else:
                            piece.add_move(move)

        def straightline_moves(increments):      #For Bishop, Queen, and Rook
            for inc in increments:
                row_inc, col_inc = inc  
                possible_move_row = row + row_inc
                possible_move_col = col + col_inc

                while True:
                    if Square.in_range(possible_move_row,possible_move_col):

                        #create squares of the new move 
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial = initial, final = final )
                        

                        # square is empty
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            #create a new move
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)


                        # square has enemy piece
                        elif self.squares[possible_move_row][possible_move_col].has_rival_piece(piece.color):
                            #create a new move
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break
                        # square has team piece
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                    else:
                        break

                    possible_move_row += row_inc
                    possible_move_col += col_inc
        
        def king_moves():
            adjs = [
                (row,col + 1),
                (row,col-1),
                (row-1,col),
                (row+1,col),
                (row-1, col+1),
                (row-1, col-1),
                (row+1,col+1),
                (row+1,col-1),
            ]

            #normal moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row,possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        initial = Square(row,col)
                        final = Square(possible_move_row,possible_move_col)

                        move = Move(initial=initial, final=final)

                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else:
                                continue
                        else:
                            piece.add_move(move)
            #castling moves (Queen and King Castling)


        #queen side castling
            if not piece.moved:
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1,4):
                            if self.squares[row][c].has_piece():
                                break
                            
                            if c == 3:
                                piece.left_rook = left_rook

                                #rook move

                                initial = Square(row,0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)
                                

                                #king move

                                initial = Square(row,col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)
                                

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        left_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    left_rook.add_move(moveR)
                                    piece.add_move(moveK)
            
            #king side castling 
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5,7):
                            if self.squares[row][c].has_piece():
                                break
                            
                            if c == 6:
                                piece.right_rook = right_rook

                                #rook move

                                initial = Square(row,7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)



                                #king move

                                initial = Square(row,col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)
            

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        right_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    right_rook.add_move(moveR)
                                    piece.add_move(moveK)


                

        if isinstance(piece, Pawn):
            pawn_moves()
        elif isinstance(piece, Knight):
            knight_moves()
        elif isinstance(piece, Bishop):
            straightline_moves([
                (-1, 1),
                (-1, -1),
                (1,1),
                (1,-1),
            ])
        elif isinstance(piece, Rook):
            straightline_moves([
                (-1, 0),
                (0, -1),
                (1,0),
                (0,1),
            ])
        elif isinstance(piece, Queen):
            straightline_moves([
                (-1, 1),
                (-1, -1),
                (1,1),
                (1,-1),
                (-1, 0),
                (0, -1),
                (1,0),
                (0,1),
            ])
        elif isinstance(piece, King):
            king_moves()


    #iterate throughout the board and assign each square a row and column to the Square Class
    def _create(self):
        for row in range(ROWS):
            for col in range(COLUMNS):
                self.squares[row][col] = Square(row,col)

    def add_pieces(self, color):
        row_pawn, row_other = (6,7) if color == "white" else (1,0)

        #pawns
        for col in range(COLUMNS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        #knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))


        # bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))


        #rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))


        #queen
        self.squares[row_other][3] = Square(row_other,3,Queen(color))



        #king
        self.squares[row_other][4] = Square(row_other,4, King(color))









