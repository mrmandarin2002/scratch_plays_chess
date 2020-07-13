import json, os, time, chess, keyboard
from datetime import datetime

#own files
import move_translator, engine_class, browser_class

class bot:

    number_of_bots = 0

    def log(self, message):
        log_message = f"BOT {self.bot_number}: {str(datetime.now()).split()[1].split('.')[0]} {message}"
        print(log_message)
        self.bot_log.write(log_message)

    def __init__(self, username, password, strength, speed, contempt):

        bot.number_of_bots += 1
        self.bot_number = bot.number_of_bots
        self.number_of_games_played = 0

        #opens file to be logged
        self.bot_log = open("bot" + str(self.bot_number) + "_log.txt", "w+")

        self.browser = browser_class.browser_class(self)
        self.browser.login(username, password)
        self.engine = engine_class.engine_class(strength, speed, contempt)

        #gameloop
        while(True):
            if(not self.browser.check_gameover()):
                self.log("Found Game!")
                is_white = self.browser.check_color()

                board = chess.Board()
                move_idx = 0
                in_game = True
                moves = []
                time_control = False
                time_scramble = False
                white_turn = True
                self.browser.get_board_properties()

                while(in_game and not self.browser.check_gameover() and not board.is_game_over()):
                    
                    if(keyboard.is_pressed('b')):
                        break

                    #gets the time control                    
                    if(not time_control):
                        time_control = max(self.browser.get_own_clock(), self.browser.get_opponent_clock())

                    #mine all that fucking info
                    player_time = self.browser.get_own_clock()
                    opponent_time = self.browser.get_opponent_clock()

                    #if it's ur turn
                    if(white_turn == is_white):
                        engine_calc_time = self.engine.ect(time_control, player_time, strength, speed)
                        engine_calc_depth = self.engine.ecd(time_control, player_time, opponent_time, strength)
                        engine_potential_moves = self.engine.get_moves_list(board, engine_calc_time, engine_calc_depth, time_scramble)
                        print(engine_potential_moves)
                        self.log(f"Engine Calculation Time: {engine_calc_time}")
                        self.log(f"Engine Calculation Depth: {engine_calc_depth}")
                        if(len(engine_potential_moves) != 0):
                            self.browser.raw_move_selenium(engine_potential_moves[0][0], is_white, delay = 0)
                        white_turn = not white_turn
                    else:
                        #premoves?
                        pass

                    #get the list of moves
                    moves.extend(self.browser.get_moves(len(moves)))

                    #this basically adds moves to the board and is based on the moves given by chess.com
                    for x in range(move_idx, len(moves)):
                        self.log(f"Move #{len(moves)}")
                        try:
                            move_translator_output = move_translator.get_from_move(moves[x], board)
                        except:
                            in_game = False
                            self.log(f"Game #{self.number_of_games_played} has ended!")
                            self.number_of_games_played += 1
                            break
                        self.log(f"Move Translator Output: {move_translator_output}")
                        move_formatted = chess.Move.from_uci(move_translator_output)
                        board.push(move_formatted)
                        self.log("Board:")
                        self.log("\n" + str(board))
                        move_idx += 1
                        white_turn = (len(moves) + 1) % 2

bot_list = []
bot_strength = 5
bot_speed = 5
bot_contempt = 24

#start of program
with open("user_info.json") as user_file:
    user_info = json.load(user_file)
    login_info = user_info["user_info"]
    for x in range(0, int(len(login_info) / 2)):
        print(f"Starting account with Username: {login_info[x * 2]} and Password: {login_info[x * 2 + 1]}.")
        bot_list.append(bot(login_info[x * 2], login_info[x * 2 + 1], bot_strength, bot_speed, bot_contempt))

