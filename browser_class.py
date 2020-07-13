import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

class browser_class:

    def get_tile_offsets(self, tile, white):
        # extract dimension variables from the transform object
        width, height = self.board_transform[2: ]
        # make sure that the tile parameter is lowercase
        tile = tile.lower()
        # convert the letter at the start of the tile coordinate to a number
        tile = str(ord(tile[0])-96) + tile[1]
        # split the tile parameter into horizontal and vertical components
        h, v = list(tile)
        # convert the horizontal and vertical components into integers and subtract one from each to convert to a zero based coordinate system
        h = int(h)-1
        v = int(v)-1
        # invert the vertical coordinate if the bot is playing white
        if white:
            v = (v-7)*-1
        # invert the horizontal coordinate if the bot is playing black
        if not white:
            h = (h-7)*-1
        # return the calculated x and y position components of the specified tile
        return (width/16+width/8*h, height/16+height/8*v)

    # make a given raw engine move with a given browser and transform object as well as a boolean indicating whether the bot is playing white or black
    def raw_move_selenium(self, move, white, delay=0.0):
        # ensure that the move notation is in lower case
        move = move.lower()
        # convert move into source and destination variables
        tile_1 = move[0:2]
        tile_2 = move[2: ]
        # get pixel offsets
        tile_1_offsets = self.get_tile_offsets(tile_1, white)
        tile_2_offsets = self.get_tile_offsets(tile_2, white)
        # perform the move given the pixel offset calculations

        action_1 = webdriver.common.action_chains.ActionChains(self.browser)
        action_1.move_to_element_with_offset(self.board_element, tile_1_offsets[0], tile_1_offsets[1])
        action_2 = webdriver.common.action_chains.ActionChains(self.browser)
        action_2.click()
        action_3 = webdriver.common.action_chains.ActionChains(self.browser)
        action_3.move_to_element_with_offset(self.board_element, tile_2_offsets[0], tile_2_offsets[1])
        action_4 = webdriver.common.action_chains.ActionChains(self.browser)
        action_4.click()
        action_1.perform()
        action_2.perform()
        time.sleep(delay)
        action_3.perform()
        action_4.perform()

    def get_own_clock(self):
        try:
            bottom_clock = self.browser.find_element_by_id("main-clock-bottom")
            return float(bottom_clock.text.split(":")[0])*60+float(bottom_clock.text.split(":")[1])
        except:
            return -1.0

    # get the current top clock time
    def get_opponent_clock(self):
        try:
            opponent_clock = self.browser.find_element_by_id("main-clock-top")
            return float(opponent_clock.text.split(":")[0])*60+float(opponent_clock.text.split(":")[1])
        except:
            return -1.0

    # get the last two moves from the current chess game with a given selenium browser object
    def get_moves(self, number_of_moves):
        #start_time = time.time()
        last_move = self.browser.find_elements_by_css_selector("span.move-text-component")
        moves = []
        for x in range(number_of_moves, len(last_move)):
            moves.append(last_move[x].text)
        #print("--- %s seconds ---" % (time.time() - start_time))
        return moves

    def search_start(self):
        try:
            return ("Starting Position" in self.browser.find_element_by_class_name("board-opening-name").text)
        except:
            return False

    def check_gameover(self):
        try:
            self.browser.find_element_by_class_name("draw-button-component")
            return False
        except:
            return True

    def check_color(self):
        if ("flipped" not in self.browser.find_element_by_id("game-board").get_attribute("class")):
            self.controller.log("Playing as White")
            return True
        else:
            self.controller.log("Playing as Black")
            return False

    # returns a transform object (the position and dimensions of the chess board) from given a browser
    def board_transformation(self):
        # find the chess board element
        board_element = self.browser.find_element_by_id("game-board")
        # extract location and dimensions of the board
        location = board_element.location
        dimensions = board_element.size
        # return the location and dimensions of the board element
        return [location["x"], location["y"], dimensions["width"], dimensions["height"]]

    def get_board_properties(self):
        self.board_element = self.browser.find_element_by_id("game-board")
        self.board_transform = self.board_transformation()

    def login(self, username, password):
        username_form = self.browser.find_element_by_id("username")
        username_form.send_keys(username)
        password_form = self.browser.find_element_by_id("password")
        password_form.send_keys(password)
        password_form.submit()
        self.browser.get("https://www.chess.com/live")
        self.controller.log("Successfully Logged In")
        time.sleep(1)

    def __init__(self, controller):
        self.controller = controller
        opts = Options()
        opts.add_argument("--disable-notifications")
        self.browser = Chrome(executable_path=r'C:\chromedriver.exe', options=opts)
        self.browser.get("https://www.chess.com/live")
