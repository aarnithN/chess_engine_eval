from constant import *
import pygame
from board import *
from dragger import Dragger
from config import Config




class Game:

    def __init__(self):
        self.board = Board()
        self.dragger = Dragger()
        self.next_player = "white"
        self.hovered_square = None
        self.config = Config()

    def show_bg(self, surface):


        for col in range(COLUMNS):
            for row in range(ROWS):
                if (col + row) % 2 == 0:
                    color = self.config.theme.bg.light #light green
                else:
                    color = self.config.theme.bg.dark # dark green

                
                rect = (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

                pygame.draw.rect(surface,color, rect)

                if col == 0:
                    color = self.config.theme.bg.dark if row % 2 == 0 else self.config.theme.bg.light

                    label = self.config.font.render(str(ROWS - row), True, color)
                    label_position = (5, 5 + row * SQUARE_SIZE)
                    surface.blit(label,label_position)
                
                if row == 7:
                    color = self.config.theme.bg.dark if (row + col) % 2 == 0 else self.config.theme.bg.light
                    alphabets = {0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h"}
                    label = self.config.font.render(alphabets[col], True, color)
                    label_position = (col * SQUARE_SIZE + SQUARE_SIZE - 20, HEIGHT - 20)
                    surface.blit(label, label_position)
    
    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLUMNS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    if piece is not self.dragger.piece:
                        piece.set_texture(size = 80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE // 2
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img,piece.texture_rect)

    def show_moves(self, surface):


        if self.dragger.dragging:
            piece = self.dragger.piece

            for move in piece.moves:
                if (move.final.row + move.final.col) % 2 == 0:
                    color = self.config.theme.moves.light
                else:
                    color = self.config.theme.moves.dark

                rect = (move.final.col * SQUARE_SIZE, move.final.row * SQUARE_SIZE, SQUARE_SIZE,SQUARE_SIZE)

                pygame.draw.rect(surface,color,rect)

    def show_last_move(self, surface):

        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial,final]:
                if (pos.row + pos.col) % 2 == 0:
                    color = self.config.theme.trace.light
                else:
                    color = self.config.theme.trace.dark

                rect = (pos.col * SQUARE_SIZE, pos.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

                pygame.draw.rect(surface,color,rect)
    
    def show_hover(self, surface):
        if self.hovered_square:
            color = (180,180,180)
            rect = (self.hovered_square.col * SQUARE_SIZE, self.hovered_square.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface,color,rect, width=3)
    

    def draw_promotion(self, surface, color,row, col):
        options = ["bishop","knight","rook","queen"]
        images = {}
        for p in options:
            images[p] = pygame.image.load(f"assets/images/imgs-80px/{color}_{p}.png")
        
        
        box_width = SQUARE_SIZE 
        box_height = SQUARE_SIZE * 4
        box_x = col * SQUARE_SIZE

        box_y = row * SQUARE_SIZE if color == "white" else row * SQUARE_SIZE - box_height + SQUARE_SIZE
        

        rects = []
        for i, p in enumerate(options):
            rect = pygame.Rect(box_x, box_y + i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface, (255,255,255), rect)
            pygame.draw.rect(surface, (0,0,0), rect, width=2)
            image_rect = images[p].get_rect(center = rect.center)
            surface.blit(images[p], image_rect)
            rects.append((rect, p))
        
        pygame.display.update()
        return rects
    
    def format_move_history(self, surface, move_history_ls):
        x = 860
        y = 40
        for i in range(0, len(move_history_ls), 2):
            move_num = i // 2 + 1
            white = move_history_ls[i]
            black = move_history_ls[i+1] if i+1 < len(move_history_ls) else ""
            move_hist = f"{move_num}. {white} {black}"
            font = pygame.font.SysFont("consolas", 20)
            move_hist_blit = font.render(move_hist, True, (20,20,20))
            surface.blit(move_hist_blit, (x, y))
            y += 30


    def is_in_check(self, final_row, final_col, piece, move_history_ls):

        col_encoding = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6:"g", 7:"h" }
        row_encoding = {0: "8", 1: "7", 2: "6", 3:"5", 4: "4", 5: "3", 6: "2", 7: "1"}

        fin_row = row_encoding[final_row]
        fin_col = col_encoding[final_col]

        if isinstance(piece, Knight):
            move_history_ls.append(f"N{fin_col+fin_row}+")
        
        elif isinstance(piece, Bishop):
            move_history_ls.append(f"B{fin_col+fin_row}+")
        
        elif isinstance(piece, Rook):
            move_history_ls.append(f"R{fin_col+fin_row}+")
        
        elif isinstance(piece, Queen):
            move_history_ls.append(f"Q{fin_col+fin_row}+")
        
        elif isinstance(piece, King):
            move_history_ls.append(f"K{fin_col+fin_row}+")
        
        else:
            move_history_ls.append(f"{fin_col+fin_row}+")
    

    def checkmate_history(self,final_row, final_col, piece, move_history_ls):
        col_encoding = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6:"g", 7:"h" }
        row_encoding = {0: "8", 1: "7", 2: "6", 3:"5", 4: "4", 5: "3", 6: "2", 7: "1"}

        fin_row = row_encoding[final_row]
        fin_col = col_encoding[final_col]


        if isinstance(piece, Knight):
            move_history_ls.append(f"N{fin_col+fin_row}#")
        
        elif isinstance(piece, Bishop):
            move_history_ls.append(f"B{fin_col+fin_row}#")
        
        elif isinstance(piece, Rook):
            move_history_ls.append(f"R{fin_col+fin_row}#")
    
        elif isinstance(piece, Queen):
            move_history_ls.append(f"Q{fin_col+fin_row}#")
        
        elif isinstance(piece, King):
            move_history_ls.append(f"K{fin_col+fin_row}#")
        
        else:
            move_history_ls.append(f"{fin_col+fin_row}#")
    
    def stalemate_history(self, move_history_ls):
        move_history_ls.append("--")

        
    def move_history(self, initial_row, initial_col, final_row, final_col, piece, move_history_ls):

        col_encoding = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6:"g", 7:"h" }
        row_encoding = {0: "8", 1: "7", 2: "6", 3:"5", 4: "4", 5: "3", 6: "2", 7: "1"}

        init_row = row_encoding[initial_row]
        init_col = col_encoding[initial_col]

        fin_row = row_encoding[final_row]
        fin_col = col_encoding[final_col]

        if isinstance(piece, Knight):
            move_history_ls.append(f"N{init_col + init_row}N{fin_col+fin_row}")
        
        elif isinstance(piece, Bishop):
            move_history_ls.append(f"B{init_col + init_row}B{fin_col+fin_row}")
        
        elif isinstance(piece, Rook):
            move_history_ls.append(f"R{init_col + init_row}R{fin_col+fin_row}")
        
        elif isinstance(piece, Queen):
            move_history_ls.append(f"Q{init_col + init_row}Q{fin_col+fin_row}")
        
        elif isinstance(piece, King):
            move_history_ls.append(f"K{init_col + init_row}K{fin_col+fin_row}")
        
        else:
            move_history_ls.append(f"{init_col + init_row}{fin_col+fin_row}")
    
    
    def capture_history(self, initial_row, initial_col, final_row, final_col, piece, move_history_ls):

        col_encoding = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6:"g", 7:"h" }
        row_encoding = {0: "8", 1: "7", 2: "6", 3:"5", 4: "4", 5: "3", 6: "2", 7: "1"}

        init_row = row_encoding[initial_row]
        init_col = col_encoding[initial_col]

        fin_row = row_encoding[final_row]
        fin_col = col_encoding[final_col]

        if isinstance(piece, Knight):
            move_history_ls.append(f"Nx{fin_col+fin_row}")
        
        elif isinstance(piece, Bishop):
            move_history_ls.append(f"Bx{fin_col+fin_row}")
        
        elif isinstance(piece, Rook):
            move_history_ls.append(f"Rx{fin_col+fin_row}")
        
        elif isinstance(piece, Queen):
            move_history_ls.append(f"Qx{fin_col+fin_row}")
        
        elif isinstance(piece, King):
            move_history_ls.append(f"Kx{fin_col+fin_row}")
        
        else:
            move_history_ls.append(f"{init_col}x{fin_col+fin_row}")
        
    def promotion_history(self, final_row, final_col, piece, move_history_ls):

        col_encoding = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6:"g", 7:"h" }
        row_encoding = {0: "8", 1: "7", 2: "6", 3:"5", 4: "4", 5: "3", 6: "2", 7: "1"}

        fin_row = row_encoding[final_row]
        fin_col = col_encoding[final_col]

        promoted_piece = str(piece)[0].upper()

        move_history_ls.append(f"{fin_col + fin_row}={promoted_piece}")
    
    def promotion_check(self, final_row, final_col, piece, move_history_ls):
        col_encoding = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6:"g", 7:"h" }
        row_encoding = {0: "8", 1: "7", 2: "6", 3:"5", 4: "4", 5: "3", 6: "2", 7: "1"}

        fin_row = row_encoding[final_row]
        fin_col = col_encoding[final_col]

        promoted_piece = str(piece)[0].upper()

        move_history_ls.append(f"{promoted_piece}{fin_col + fin_row}+")

    def check_history():
        pass
    def castling_history(self, result, move_history_ls):
        if result == "queenside castling":
            move_history_ls.append("O-O-O")
        elif result == "kingside castling":
            move_history_ls.append("O-O")

    

    def set_hover(self,row,col):
        if 0 <= row < 8 and 0 <= col < 8:
            if self.board.squares[row][col]:
                self.hovered_square = self.board.squares[row][col]

        else:
            self.hovered_square = None
        


    def next_turn(self):
        if self.next_player == "white":
            self.next_player = 'black'
        else:
            self.next_player = "white"

    def change_theme(self):
        self.config.change_theme()

    def side_bar_color(self, index, options, surface):
        
        index += 1
        index %= len(options)
        rect = (800, 0, MOVE_HISTORY_SIDEBAR, HEIGHT)
        pygame.draw.rect(surface,options[index],rect)
        return index
        
    def sound_effect(self, captured = False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()


    




                    



