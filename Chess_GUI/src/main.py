import pygame
import sys
from constant import *
from game import Game
from board import *
from square import Square
from ml_model import model
import time


class Main:

    board = chess.Board()
    options = [(210,210,210), (190,175,160), (150,160,180), (100,100,100)]
    index = 0
    border_width = 10
    checker = False
    checker2 = False
    checkmate_or_stalemate = ""
    promotion_piece = None
    pop_up_opponent = ""
    pop_up_current_player = ""
    
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.sidebar = pygame.draw.rect(self.screen, self.options[self.index], (800, 0, MOVE_HISTORY_SIDEBAR, HEIGHT))
        pygame.draw.rect(self.screen, (0,0,0), self.sidebar, self.border_width)
        pygame.display.set_caption("Chess Game")
        self.game = Game()
        self.move_history_ls = []
        self.reset_delay = 5000
        self.checkmate_reset_time = 0
        self.game_state = False
        

    def mainloop(self):

        screen = self.screen
        game = self.game
        dragger = self.game.dragger
        board = self.game.board

        while True:

            game.show_bg(screen)
            self.sidebar
            pygame.draw.rect(self.screen, (0,0,0), self.sidebar, self.border_width)

            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if dragger.dragging:
                dragger.update_blit(screen)


            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    
                    clicked_row = dragger.mouseY // SQUARE_SIZE
                    clicked_col = dragger.mouseX // SQUARE_SIZE

                    if 0 <= clicked_row < 8 and 0 <= clicked_col < 8:
                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece

                            if piece.color == game.next_player:

                                board.calc_moves(piece,clicked_row,clicked_col, bool = True)
                                dragger.save_initial(event.pos)           
                                dragger.drag_piece(piece)

                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)


                elif event.type == pygame.MOUSEMOTION:

                    motion_row = event.pos[1] // SQUARE_SIZE
                    motion_col = event.pos[0] // SQUARE_SIZE

                    if  0 <= motion_col < 7:
                        game.set_hover(motion_row,motion_col)
                        if dragger.dragging:
                            game.hovered_square = None
                            dragger.update_mouse(event.pos)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen) 
                            game.show_hover(screen)
                            dragger.update_blit(screen)
                
               
                elif event.type == pygame.KEYDOWN:

                    if event.key ==pygame.K_t:
                        game.change_theme()
                        self.index = game.side_bar_color(self.index, self.options,screen)
                
                    if event.key ==pygame.K_r:
                        game.reset()
                        game = self.game
                        dragger = self.game.dragger
                        board = self.game.board
                        self.sidebar = pygame.draw.rect(self.screen, self.options[self.index], (800, 0, MOVE_HISTORY_SIDEBAR, HEIGHT))
                        self.move_history_ls.clear()
                        self.board.reset()

                        
                    if event.key == pygame.K_c:
                        game.reset()
                        game = self.game
                        dragger = self.game.dragger
                        board = self.game.board
                        self.sidebar = pygame.draw.rect(self.screen, self.options[self.index], (800, 0, MOVE_HISTORY_SIDEBAR, HEIGHT))
                        self.move_history_ls.clear()
                        self.checker = True

                elif event.type == pygame.MOUSEBUTTONUP:

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQUARE_SIZE
                        released_col = dragger.mouseX // SQUARE_SIZE

                        #create possible move
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial=initial, final=final)

                        if board.valid_move(dragger.piece, move):

                            captured = board.squares[released_row][released_col].has_piece()
                            board.set_true_en_passant(dragger.piece)
                            board.move(dragger.piece, move)

                            result, promo_data = board.move(dragger.piece, move)

                            if result == "promotion":
                                row, col, color = promo_data
                                option_rects = game.draw_promotion(screen,color, row, col)
                                promoted_piece = None

                                while promoted_piece == None:
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            pygame.quit()
                                            sys.exit()
                                        elif event.type == pygame.MOUSEBUTTONDOWN:
                                           pos = pygame.mouse.get_pos()
                                           for rect, piece_type in option_rects:
                                               if rect.collidepoint(pos):
                                                   promoted_piece = piece_type
                                                   self.promotion_piece = promoted_piece

                                board.pawn_promotion(row,col,promoted_piece,color)
                            
                           
                            
                            opponent = "black" if game.next_player == "white" else "white"
                            current_player = game.next_player

                            self.pop_up_opponent = opponent
                            self.pop_up_current_player = current_player
                           
                            if board.in_checkmate(opponent) and not self.game_state:
                                game.checkmate_history(released_row,released_col,dragger.piece, self.move_history_ls)
                                print(f"{current_player.capitalize()} Wins!")
                                self.checkmate_reset_time = pygame.time.get_ticks()
                                self.game_state = True
                            elif board.in_stalemate(opponent):
                                game.stalemate_history(self.move_history_ls)
                            elif board.check_history(opponent) and result == "promotion":
                                game.promotion_check(row,col,promoted_piece, self.move_history_ls)
                            elif board.check_history(opponent):
                                game.is_in_check(released_row, released_col, dragger.piece, self.move_history_ls)
                            elif result == "promotion":
                                game.promotion_history(row,col,promoted_piece, self.move_history_ls)
                            elif result == "queenside castling" or result == "kingside castling":
                                game.castling_history(result, self.move_history_ls)
                            elif captured:
                                game.capture_history(dragger.initial_row,dragger.initial_col, released_row,released_col, dragger.piece, self.move_history_ls)
                            else:
                                game.move_history(dragger.initial_row,dragger.initial_col, released_row,released_col, dragger.piece, self.move_history_ls)
                            

                            game.format_move_history(screen, self.move_history_ls)
                            game.sound_effect(captured)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            game.next_turn()

                
                            #Engine Moves

                            if self.checker:

                                #AI functionality
                                board.chess_board_update(initial.row, initial.col, final.row,final.col, self.board, result, self.promotion_piece) #updating white's move to the chess board 
                                    #fen_list.append(fen)

                                if not self.board.is_checkmate():
                                    if game.next_player == "black":    #Machine's turn to make a move 
                                            #create possible move
                                        best_move = board.machine_black_move(self.board, model.fen_to_position, model.transform_fen_features, model.model)
                                        #print((best_move))
                                        init_col, init_row, fin_col, fin_row = board.move_to_board(best_move)
                                        black_piece = board.squares[init_row][init_col].piece
                                            #print(type(black_piece))
                                        init = Square(init_row, init_col)
                                        fin = Square(fin_row, fin_col)
                                        move = Move(initial=init, final=fin)
                                        board.move(black_piece, move)
                                        board.chess_board_update(init.row, init.col, fin.row,fin.col, self.board, result, self.promotion_piece)

                                        captured = board.squares[fin_row][fin_col].has_piece()

                                        opponent = "black" if game.next_player == "white" else "white"
                                        current_player = game.next_player
                                        

                                    
                                        if board.in_checkmate("white"):
                                            game.checkmate_history(fin_row,fin_col,black_piece, self.move_history_ls)
                                            print("Black Wins")
                                        elif board.in_stalemate("white"):
                                            game.stalemate_history(self.move_history_ls)
                                        elif board.check_history("white"):
                                            game.is_in_check(fin_row, fin_col, black_piece, self.move_history_ls)
                                        elif board.machine_promotion(fin_col,fin_row,black_piece,"black"):
                                            game.promotion_history(fin_row,fin_col,black_piece, self.move_history_ls)
                                        #elif result == "queenside castling" or result == "kingside castling":
                                            #game.castling_history(result, self.move_history_ls)
                                        elif captured:
                                            game.capture_history(init_row,init_col, fin_row,fin_col, black_piece, self.move_history_ls)
                                        else:
                                            game.move_history(init_row,init_col, fin_row,fin_col, black_piece, self.move_history_ls)

                                        game.format_move_history(screen, self.move_history_ls)
                                        game.next_turn()
                                        game.show_bg(screen)
                                        game.show_last_move(screen)
                                        game.show_pieces(screen)
                                    

                                elif self.board.is_stalemate():
                                    if game.next_player == "black":    #Machine's turn to make a move 
                                            #create possible move
                                        best_move = board.machine_black_move(self.board, model.fen_to_position, model.transform_fen_features, model.model)
                                        #print((best_move))
                                        init_col, init_row, fin_col, fin_row = board.move_to_board(best_move)
                                        black_piece = board.squares[init_row][init_col].piece
                                        init = Square(init_row, init_col)
                                        fin = Square(fin_row, fin_col)
                                        move = Move(initial=init, final=fin)
                                        board.move(black_piece, move)
                                        board.chess_board_update(init.row, init.col, fin.row,fin.col, self.board)

                                        captured = board.squares[fin_row][fin_col].has_piece()

                                        opponent = "black" if game.next_player == "white" else "white"
                                        current_player = game.next_player

                                    
                                        if board.in_checkmate("white"):
                                            game.checkmate_history(fin_row,fin_col,black_piece, self.move_history_ls)
                                            print("Black Wins")
                                        elif board.in_stalemate("white"):
                                            game.stalemate_history(self.move_history_ls)
                                        elif board.check_history("white"):
                                            game.is_in_check(fin_row, fin_col, black_piece, self.move_history_ls)
                                        elif board.machine_promotion(fin_col,fin_row,black_piece,"black"):
                                            game.promotion_history(fin_row,fin_col,black_piece, self.move_history_ls)
                                        #elif result == "queenside castling" or result == "kingside castling":
                                            #game.castling_history(result, self.move_history_ls)
                                        elif captured:
                                            game.capture_history(init_row,init_col, fin_row,fin_col, black_piece, self.move_history_ls)
                                        else:
                                            game.move_history(init_row,init_col, fin_row,fin_col, black_piece, self.move_history_ls)

                                        game.format_move_history(screen, self.move_history_ls)
                                        game.next_turn()
                                        game.show_bg(screen)
                                        game.show_last_move(screen)
                                        game.show_pieces(screen)
                                else:
                                    self.checkmate_reset_time = pygame.time.get_ticks()
                                    self.game_state = True

                    
                    dragger.undrag_piece()


                elif event.type == pygame.QUIT:
                    pygame.quit()   # can try changing to break
                    sys.exit()





            if self.checkmate_reset_time != 0 and self.game_state:
                check_mate_interval = pygame.time.get_ticks() - self.checkmate_reset_time
                if check_mate_interval < self.reset_delay:

                    # pop up screen

                    pop_up_screen = pygame.Surface((WIDTH,HEIGHT))
                    pop_up_screen.fill((105,105,105))
                    pop_up_screen.set_alpha(150)
                    screen.blit(pop_up_screen,(0,0))

                    font = pygame.font.SysFont("Times New Roman", 48)
                    countdown = max(0, (self.reset_delay - check_mate_interval) // 1000)
                    if board.in_checkmate(self.pop_up_opponent):
                        text = font.render(f"{self.pop_up_current_player.capitalize()} wins! Restarting in {countdown} seconds...", True, (255, 255, 255))
                        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                        screen.blit(text, text_rect)


                else:
                    game.reset()
                    game = self.game
                    dragger = self.game.dragger
                    board = self.game.board
                    self.sidebar = pygame.draw.rect(self.screen, self.options[self.index], (800, 0, MOVE_HISTORY_SIDEBAR, HEIGHT))
                    self.move_history_ls.clear()
                    self.board.reset()
                    self.checkmate_reset_time = 0
                    self.game_state = False


        
            pygame.display.update()


main = Main()
main.mainloop()
