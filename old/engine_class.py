import random, os, chess, platform, chess.engine

import move_translator

class engine_class():

    # returns a list of moves with (search time in milliseconds)
    def get_moves_list(self, board, movetime, move_depth, time_scramble):
        # get unordered list
        moves = []
        analysis = self.stockfish.analyse(board, chess.engine.Limit(time = movetime, depth = move_depth), multipv=5)
        for info in analysis:
            try:
                if(str(info["score"])[0] == '#'):
                    if(time_scramble):
                        moves.append([str(info["pv"][0]), (1000 / int(str(info.get("score"))[1:]))])
                    else:
                        moves.append([str(info["pv"][0]), (5000 / int(str(info.get("score"))[1:]))])
                else:
                    moves.append([str(info["pv"][0]), int(str(info.get("score")))])
            except: pass
        # selection sort
        n = len(moves)
        for i in range(len(moves)):
            min_index = i
            j = i+1
            while j < n:
                if moves[i][0] < moves[min_index][0]:
                    min_index = j
                j += 1
            temp = moves[min_index]
            moves[min_index] = moves[i]
            moves[i] = temp
        return moves

    def import_engine(self, contempt):
        # import stockfish engine
        if platform.system() == "Linux":
            self.stockfish = chess.engine.SimpleEngine.popen_uci(r"stockfish-bin/Linux/stockfish_10_x64")
        elif platform.system() == "Windows":
            self.stockfish = chess.engine.SimpleEngine.popen_uci(r"stockfish-bin/Windows/stockfish_10_x64.exe")
        else: # unsupported platform
            print("ERROR:", platform.system(), "unsupported")
            quit()
        #configures the contempt of the engine
        self.stockfish.configure({"Contempt": contempt})

    #engine time limit calcuation
    #basically calculates the amount of time the engine thinks for
    def ect(self, time_control, own_time):
        #the time the engine thinks for decreases as your own time decreases
        #the decrease is exponential, it decreases slowly but picks up speed when you get low on time
        num = (((own_time/time_control) + ((1.0 - (own_time/time_control)) / 1.5)) * (time_control/1000.0) * (self.strength / 10))
        return num

    #engine depth limit calculation
    #calculates the depth in which the engine thinks to
    def ecd(self, time_control, own_time, opponent_time):
        base_depth = 5 + ((self.strength + 5) * ((own_time/time_control) + ((1.0 - (own_time/time_control))/1.2)))
        #make sure the base_depth doesn't go under 5 (bad things happen if it does)
        if(base_depth < 5):
            base_depth = 5
        return base_depth

    def move_selector(self, moves_list, player_time, opponent_time):
        pass

    def __init__(self, strength, speed, contempt):
        self.strength = strength
        self.speed = speed
        self.import_engine(contempt)