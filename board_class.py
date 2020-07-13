import chess

class board_class:

    def get_from_move(self, move):

        #removes checks and captures in notation, there is no need anyways
        move = move.replace('+', '')
        move = move.replace('x', '')
        move = move.replace('#', '')
        #if the player wants to castle
        if(move == "O-O"):
            if(self.board.turn == 1):
                return "e1g1"
            else:
                return "e8g8"
        elif(move == "O-O-O"):
            if(self.board.turn == 1):
                return "e1c1"
            else:
                return "e8c8"
        #the square in which the piece is moving to in string notation "e4"
        if(move[len(move) - 1].isalpha()):
            to_square = move[0:2]
        else:
            to_square = move[-2:]
        #determines the rank and file of the square the piece is intended to move to
        piece_file = chess.square_file(self.board_map[to_square])
        piece_rank = chess.square_rank(self.board_map[to_square])
        #variable used later to store which square the piece was from
        from_square = ""
        #the square in which the piece is moving to in integer notation "60"
        current_square = chess.square(piece_file, piece_rank)
        #this is for if two of the same pieces can legally move to one square
        matching_file = True
        matching_cor = 0
        # pawn varibles:
        pIdx1 = piece_rank
        pIdx2 = -1
        pWay = -1

        #to set the range for finding the correct pawn
        if(self.board.turn == False):
            pIdx2 = 8
            pIdx1 = piece_rank
            pWay = 1

        #regular pawn moves
        if(len(move) == 2 or move[len(move) - 1].isalpha()):
            #print("PAWN MOVE!")
            #basically loops on the file of the pawn to determine which pawn it is (if there are multiple pawns)
            for x in range(pIdx1, pIdx2, pWay):
                current_square = (x * 8) + piece_file
                if(self.board.piece_type_at(current_square) == 1):
                    from_square = chess.SQUARE_NAMES[current_square]
                    break
        else:
            #gets which piece is moving or which pawn for that matter
            piece = move[0]
            piece_num = 0

            #pawn captures ***En passant capture not working atm***
            if(piece.islower()):
                piece_num = 1
            else:
                piece_num = self.piece_map[piece]

            #this is for if multiple of the same pieces can legally move / take a square
            if(len(move) >= 4):
                #if it's for files
                if(move[1].isalpha()):
                    matching_cor = (ord(move[1]) - 97)
                #if it's for ranks
                else:
                    matching_file = False
                    matching_cor = ord(move[1]) - 49
            if(move[0].islower()):
                matching_cor = (ord(move[0]) - 97)
                piece_num = 1
            #lists the squares in which the lcurrent square can be attacked from
            attacks_on_square = list(self.board.attackers(self.board.turn, current_square))
            print(attacks_on_square)
            #if the piece moving is the Bishop
            if(piece_num != 6):
                if(len(move) == 3 and move[0].islower() == False):
                    print("HALF IN!")
                    for x in attacks_on_square:
                        if(self.board.piece_type_at(x) == piece_num):
                            from_square = chess.SQUARE_NAMES[x]
                            break
                elif(len(move) == 4 or move[0].islower()):
                    print("WE IN!")
                    for x in attacks_on_square:
                        if(matching_file == True and (chess.square_file(x) == matching_cor) and self.board.piece_type_at(x) == piece_num):
                            from_square = chess.SQUARE_NAMES[x]
                            break
                        elif(matching_file == False and (chess.square_rank(x) == matching_cor) and self.board.piece_type_at(x) == piece_num):
                            from_square = chess.SQUARE_NAMES[x]
                            break
                elif(len(move) == 5):
                    from_square = move[1:3]
            else:
                from_square = (chess.SQUARE_NAMES[self.board.king(self.board.turn)])
        #print(from_square, " ", to_square)
        if(move[len(move) - 1].isalpha()):
            return from_square + to_square + move[len(move)-1].lower()
        else:
            return from_square + to_square

    def 

    def __init__(self):
        self.board = chess.Board()
        self.board_map = {}
        self.piece_map = {}
        cnt = 0
        for x in chess.SQUARE_NAMES:
            self.board_map[x] = cnt
            cnt += 1
        self.piece_map['N'] = 2
        self.piece_map['B'] = 3
        self.piece_map['R'] = 4
        self.piece_map['Q'] = 5
        self.piece_map['K'] = 6
