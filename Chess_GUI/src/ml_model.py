from board import Board
import chess
import pandas as pd
import numpy as np
import sklearn
import tensorflow as tf

class model:

    
    model = tf.keras.models.load_model("/Users/aarnithnetrawali/Desktop/Chess_AI_Engine/Chess_GUI/model/chess_eval_model.h5", compile = False)  #have to change this to retrain data 



    def fen_to_position(position):
        board_matrix = np.zeros((12,8,8))
        piece_to_rep = {'p': 0, 'n': 1, 'b': 2, 'r': 3, 'q': 4, 'k': 5,
                'P': 6, 'N': 7, 'B': 8, 'R': 9, 'Q': 10, 'K': 11}
        rows = position.split("/")
        
        for row_index, row in enumerate(rows):
            column_index = 0
            for char in row:
                if char.isdigit():
                    column_index += int(char)
                else:
                    piece_index = piece_to_rep[char]
                    board_matrix[piece_index, row_index, column_index] = 1
                    column_index += 1
        return board_matrix

#transform features from fen besides position
    def transform_fen_features(split):
        player_turn = split[1]
        player_turn = 1 if player_turn == "w" else 0

        castling_rights = split[2]
        K = 0
        Q = 0
        k = 0
        q = 0
        if "K" in castling_rights:
            K = 1
        if "Q" in castling_rights:
            Q = 1
        if "k" in castling_rights:
            k = 1
        if "q" in castling_rights:
            q = 1
            
        en_passant = split[3]
        if en_passant == "-":
            en_passant = 1
        elif en_passant != "-":
            en_passant = 0

        fifty_move_rule_mean = 1.70958084
        fifty_move_rule_sd = 2.44142722
        fifty_move_rule = int(split[4])
        fifty_move_rule = (fifty_move_rule - fifty_move_rule_mean)/fifty_move_rule_sd

        full_move_mean = 21.35329341
        full_move_sd = 13.45766386
        full_move = int(split[5])
        full_move = (full_move - full_move_mean)/full_move_sd

        result = []
        result.append(player_turn)
        result.append(K)
        result.append(Q)
        result.append(k)
        result.append(q)
        result.append(en_passant)
        result.append(fifty_move_rule)
        result.append(full_move)

        features_arr = np.array(result, dtype = "float32")
        features_arr = features_arr.reshape(1,-1)

        return features_arr
    
    



    





        



    
    
