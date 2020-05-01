import kivy
kivy.require('1.11.0')
from functools import partial
 
from kivy.app import App

from kivy.animation import Animation

from kivy.clock import Clock

from kivy.core.audio import SoundLoader
from kivy.core.window import Window

from kivy.graphics import Line, Color, Rectangle

from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty

from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput

from random import randrange

'''Board constants'''
BOARD_SIZE = 9
BLOCK_SIZE = int(BOARD_SIZE**0.5)
boardArray = []
board = [
			[1,0,0,4,5,6,7,8,9],
			[1,0,3,4,5,6,7,8,9],
			[1,0,0,4,5,0,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9]
		]
best_time = -100
board_id = -1

'''Points earned when solving a board of specific dimension'''
pointsDict = {
	4: 20,
	9: 80,
	16: 200
}

'''Definitions for various UI elements used in the application'''
class Board(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

class BoardLabel(Label):
	pass
class ButtonUI(Button):
	border_color = ListProperty()
	icon_path = StringProperty()
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.button_click = SoundLoader.load("res/click.wav")

	def play_sound(self):
		if settingsDict["Sound"] == 1:
			self.button_click.play()


class NumInput(TextInput):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	# Used to validate whether input is numeric and in between 1 to n (dimension)
	def insert_text(self, substring, from_undo=False):
		if (self.text + substring).isdigit():
			if not int(self.text + substring) in range(1, BOARD_SIZE+1):
				substring = ""
		else:
			substring = ""
		TextInput.insert_text(self, substring, from_undo)

class SolvedDialog(FloatLayout):
	y_hint = NumericProperty()
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


def cell_valid(index):
	'''Check whether a specific cell has valid entry or not'''
	BLOCK_SIZE = int(BOARD_SIZE**0.5)
	row, col = index//BOARD_SIZE, index%BOARD_SIZE
	cellNum = inputBoard[row][col]
	if inputBoard[row].count(cellNum) > 1 and cellNum > 0:
		return "Invalid1"
	for y in range(BOARD_SIZE):
		if inputBoard[y][col] == cellNum and cellNum > 0 and y != row:
			return "Invalid2"
	blockX, blockY = row//BLOCK_SIZE, col//BLOCK_SIZE

	for x in range(BLOCK_SIZE):
		for y in range(BLOCK_SIZE):
			currentBlock = inputBoard[blockX*BLOCK_SIZE+x][blockY*BLOCK_SIZE+y]
			if currentBlock == cellNum and cellNum > 0 and (blockX*BLOCK_SIZE+x, blockY*BLOCK_SIZE+y) != (row, col):
				return "Invalid3"
	return "Valid"

def cell_options (board, row, col):
	'''Find available entries for a specific cell'''
	BLOCK_SIZE = int(BOARD_SIZE**0.5)
	num_list = [num for num in range(1,BOARD_SIZE+1)]
	if (row, col) in cells_filled:
		for elem in cells_filled[cells_filled.index((row, col))+1]:
			list_delete(num_list, elem)
	
	for i in range(BOARD_SIZE):
		list_delete(num_list, board[row][i])
		list_delete(num_list, board[i][col])

	blockX, blockY = row//BLOCK_SIZE, col//BLOCK_SIZE
	for x in range(BLOCK_SIZE):
		for y in range(BLOCK_SIZE):
			currentBlock = board[blockX*BLOCK_SIZE+x][blockY*BLOCK_SIZE+y]
			list_delete(num_list, currentBlock)
	return num_list

def check_board_validity(board, BOARD_SIZE):
	'''Check whether each and every cell has a valid entry and return either "Valid" or "Not Valid"'''
	num_list = []
	BLOCK_SIZE = int(BOARD_SIZE**0.5)
	for row in board:
		for digit in row:
			if str(digit) not in "".join([str(number) for number in range(0,BOARD_SIZE+1)]):
				return "Not ValidR1"
			elif row.count(digit) > 1 and digit != 0:
				return "Not ValidR2"

	for index in range(BOARD_SIZE):	# Check the columns of the board
		num_list = []
		for row in board:
			num_list.append(row[index])
		for digit in num_list:
			if str(digit) not in "".join([str(number) for number in range(0,BOARD_SIZE+1)]):
				return "Not ValidC1"
			elif num_list.count(digit) > 1 and digit != 0:
				return "Not ValidC2"
	
	for row_index in range(0, BOARD_SIZE, BLOCK_SIZE):	# Check the individual block of the board
		for col_index in range(0, BOARD_SIZE, BLOCK_SIZE):
			num_list = []
			for row in range(BLOCK_SIZE):
				for col in range(BLOCK_SIZE):
					num_list.append(board[row_index+row][col_index+col])
			for digit in num_list:
				if str(digit) not in "".join([str(number) for number in range(0,BOARD_SIZE+1)]):
					return "Not ValidB1", 
				elif num_list.count(digit) > 1 and digit != 0:
					return "Not ValidB2"
	return "Valid"

def generate_board(game_type="Play"):
	'''Find a board from the stored text files and return it as a 2-dimensional list'''
	global board, best_time, board_id, boardArray
	boardArray = []
	boardFile = open(f"res/boards/boards_{BOARD_SIZE}.txt", "r").read().split("\n")
	boardFile.pop(0)
#	boardFile.remove('')
	boardCount = len(boardFile)//(BOARD_SIZE+1)
#	print("boardCount", boardCount)
	for boards in range(boardCount):
		board = []
		for row in range(BOARD_SIZE+1):
			rowList = boardFile[boards*(BOARD_SIZE+1)+row].strip('[]').split(',')
			board.append([int(num) for num in rowList])
		boardArray.append(board[:])
	board = []
	if game_type == "Solve":
		board = [[0 for cell in range(BOARD_SIZE)] for row in range(BOARD_SIZE)]
		best_time = -100
	elif game_type == "Play":
		board_id = randrange(1, boardCount)
		best_time = boardArray[board_id][-1][0]
		for elem in boardArray[board_id][:-1]:
			board.append(elem[:])

def isSolved():
	'''Check whether the board has been solved by the user and so update the UI'''
	global screen_manager, inputBoard
	board_screen = sudoku_app.root.ids.board_screen
	#print(board_screen.ids, board_screen.children)
	solvedLabel = sudoku_app.root.ids.solvedLabel
	solvedLabel.text = "Not Solved"
	solvedLabel.color = (1, 0, 0, 1)
	inputBoard = []
	for row in range(BOARD_SIZE):
		inputBoard.append(list())
		for col in range(BOARD_SIZE):
			text = cellArray[row*BOARD_SIZE+col].text
			inputBoard[row].append(int(text) if text else 0)
	
	tilesLabel = sudoku_app.root.ids.tilesLabel
	emptyCells = 0
	for row in inputBoard:
		emptyCells += row.count(0)
	tilesLabel.text = "Empty Cells: %d/%d" %(emptyCells, BOARD_SIZE**2)

	for row in inputBoard:
		if 0 in row:
			return False
	if check_board_validity(inputBoard, BOARD_SIZE) == "Valid":
		solvedLabel.text = "Solved"
		solvedLabel.color = (0, 0.85, 0, 1)
		return True
	else:
		return False

def list_delete(num_array, elem):
	'''Delete an element from list "num_array" without causing ValueError'''
	try:
		num_array.remove(elem)
	except ValueError:
		pass

def save_settings():
	'''Save user settings like music, sound effects and user score in settings.txt'''
	with open("res/settings.txt", "w") as settingsTxt:
		settingsTxt.write("\n".join([f"{key}={value}" for key, value in settingsDict.items()]))

cells_filled = []
def solve(parent, dt=None):
	'''Solve a given board using the backtrackking algorithm'''
	global index, cells_filled, board
#	print("Solving board...")
	index = 0
	cells_filled = []
	while index < BOARD_SIZE**2:
#		print(index)
		if board[index//BOARD_SIZE][index%BOARD_SIZE] == 0:
			currentOptions = cell_options(board, index//BOARD_SIZE, index%BOARD_SIZE)
			if currentOptions != []:
				board[index//BOARD_SIZE][index%BOARD_SIZE] = currentOptions[0]
				cellArray[index].text = str(board[index//BOARD_SIZE][index%BOARD_SIZE])
				if (index//BOARD_SIZE, index%BOARD_SIZE) not in cells_filled:
					cells_filled.append((index//BOARD_SIZE, index%BOARD_SIZE))
					cells_filled.append([currentOptions[0]])
				else:
					cellIndex = cells_filled.index((index//BOARD_SIZE, index%BOARD_SIZE))
					cells_filled[cellIndex+1].append(currentOptions[0]) 
				index += 1
			else:
				if (index//BOARD_SIZE, index%BOARD_SIZE) in cells_filled:
					cells_filled.pop(-1)
					cells_filled.pop(-1)
				if not cells_filled == []:
					index = cells_filled[-2][0]*BOARD_SIZE + cells_filled[-2][1]
				else:
					solve_modal_view = ModalView(size_hint=(0.1, 0.1))
					solve_modal_view.add_widget(Label(text="Board not solvable"))
					solve_modal_view.open()
					return "Board not solvable"
				board[index//BOARD_SIZE][index%BOARD_SIZE] = 0
				cellArray[index].text = str(board[index//BOARD_SIZE][index%BOARD_SIZE])
		else:
			index += 1
#	print("Board solved")
	if isSolved():
		if game_type == "Play":
			solve_anim = Animation(y_hint=0.5, duration= 0.65, t="in_out_sine")
			sudoku_app.root.ids.solved_dialog.ids.new_points_label.text = f"+0"
			sudoku_app.root.ids.solved_dialog.ids.time_bonus_label.text = f"+0"
			solve_anim.start(sudoku_app.root.ids.solved_dialog)


def validate(instance):
	'''Update UI elements according to the current board entries''' 
	global inputBoard, settingsDict
	
	instance.foreground_color = 0,0,0,1
	if instance.text == "":
		return
	if instance.text not in "".join([str(number) for number in range(1,BOARD_SIZE+1)]):
		#instance.text = ""
		instance.foreground_color = 1,0,0,1
	else:
		index = cellArray.index(instance)
		row, col = index//BOARD_SIZE, index%BOARD_SIZE
		inputBoard = []
		for row in range(BOARD_SIZE):
			inputBoard.append(list())
			for col in range(BOARD_SIZE):
				text = cellArray[row*BOARD_SIZE+col].text
				inputBoard[row].append(int(text) if text else 0)
#			print(board, inputBoard)
		if cell_valid(index) != "Valid":
			instance.foreground_color = 1,0,0,1
		if isSolved():
			sudoku_app.root.ids.solved_dialog.ids.complete_label.text = "BOARD COMPLETE!!"
			solve_anim = Animation(y_hint=0.5, duration= 0.65, t="in_out_sine")
			solve_anim.start(sudoku_app.root.ids.solved_dialog)
			sudoku_app.root.ids.solved_dialog.ids.new_points_label.text = f"+{pointsDict[BOARD_SIZE]}"
			if remaining_time < best_time:
				time_bonus = (best_time - remaining_time)//20*BOARD_SIZE
			else:
				time_bonus = 0
			sudoku_app.root.ids.solved_dialog.ids.time_bonus_label.text = f"+{time_bonus}"

			settingsDict["Points"] += pointsDict[BOARD_SIZE] + time_bonus
			sudoku_app.points = settingsDict["Points"]
			save_settings()

def lostFocus(instance, value):
	global current_text_input
	if not value:
		validate(instance)
	else:
		instance.foreground_color = 0,0,0,1


screen_manager = None
cellArray = []
inputBoard = []
remaining_time = -1
game_type = None
settingsDict = {
	"Points": -1,
	"Music": 0,
	"Sound": 0
}
current_text_input = None

class SudokuApp(App):
	'''Main Kivy application class'''
	board_size = BOARD_SIZE
	points = NumericProperty()
	play_or_solve = StringProperty()

	def update_board(self, dt=None):
		global cellArray
		#print(board)
		#print("--------------", self.root.ids, sudoku_app.root)
		for child in self.root.ids.board_screen.children:
			if isinstance(child, Board):
				self.root.ids.board_screen.remove_widget(child)
		boardLayout = Board()
		boardLayout.cols = BOARD_SIZE
		cellArray = []
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				if board[row][col]:
					numButton = BoardLabel(text=str(board[row][col]) if board[row][col] else "")
				else:
					numButton = NumInput(text=str(board[row][col]) if board[row][col] else "")
					numButton.bind(on_text_validate = validate, focus = lostFocus)
					#numButton.padding_y =  #(blockSize-(400/BOARD_SIZE))/2
				boardLayout.add_widget(numButton)
				cellArray.append(numButton)
		self.root.ids.board_screen.add_widget(boardLayout, index= 1)


	def build(self):
		'''Defines the root of the application i.e. ScreenManager'''
		global screen_manager
		screen_manager = ScreenManager()
		return screen_manager

	def load_game(self, play_or_solve="Play"):
		'''Display the Sudoku board on-screen'''
		global board, game_type, remaining_time
		self.play_or_solve = play_or_solve
		game_type = play_or_solve
		generate_board(play_or_solve)
#		print("____________", board)
		self.update_board()
		isSolved()
		remaining_time = 0
		if play_or_solve == "Play":
			if best_time != -100:
				self.root.ids.best_time_label.text = "%2d:%02d" %(best_time//60, best_time%60)
			else:
				self.root.ids.best_time_label.text = "--:--"
			self.root.ids.timer_label.text= "%2d:%02d" %(remaining_time//60, remaining_time%60)
			Clock.schedule_once(self.timerStart, 3)
		else:
			self.root.ids.best_time_label.text = "--:--"
			self.root.ids.timer_label.text = "--:--"
		self.root.ids.solved_dialog.y_hint = 1.7

		Clock.schedule_once(partial(self.transition, "Board", "left"), 2)
		#print("Loading Game")
		

	def on_start(self):
		'''Runs before the application starts'''
		global settingsDict
		settings = open("res/settings.txt", "r").read().split("\n")
		for line in settings:
			settingsDict[line.split("=")[0]] =  int(line.split("=")[1])
		self.points = settingsDict["Points"]
		self.root.ids.music_button.icon_path = f"res/icons/music-icon-{settingsDict['Music']}.png"
		self.root.ids.sound_button.icon_path = f"res/icons/sound-icon-{settingsDict['Sound']}.png"
		#self.root.ids.points_label.text = str(self.points)
			
		self.background_music = SoundLoader.load("res/background_music.wav")
		self.background_music.loop = True
		self.background_music.volume = 0.2
		if settingsDict["Music"] == 1:
			print("Playing BGM")
			self.background_music.play()

	def select_board_size(self, size, color):
		'''Update sudoku board depending on the given dimension (size)'''
		global BOARD_SIZE
		BOARD_SIZE = size
		self.board_size = BOARD_SIZE
		for child in self.root.ids.size_layout.children:
			if str(size) in child.text:
				child.disabled = True
			else:
				child.disabled = False

	def solve_board(self):
		'''Provides sudoku board data for the solve() function'''
		global cellArray, board
		inputBoard = []
		for row in range(BOARD_SIZE):
			inputBoard.append([int(elem.text) if elem.text else 0 for elem in cellArray[row*BOARD_SIZE:(row+1)*BOARD_SIZE]])
		if check_board_validity(inputBoard, BOARD_SIZE) == "Valid":
			board = inputBoard.copy()
			solve(self)
			for row in range(BOARD_SIZE):
				for col in range(BOARD_SIZE):
					cellArray[row*BOARD_SIZE+col].text = str(board[row][col]) if board[row][col] else ""
		else:
			solve_modal_view = ModalView()
			solve_modal_view.add_widget(Label(text="Invalid Board"))
			solve_modal_view.open()
#			print("Invalid Board")		
	

	def timerStart(self, dt=None):
		'''Controls the application timer'''
		global remaining_time
		remaining_time += 1
		time_in_minutes = "%2d:%02d" %(remaining_time//60, remaining_time%60)
		timer_label = self.root.ids.timer_label
		timer_label.text= ("" + time_in_minutes)
		#print("Time remaining: " + time_in_minutes)
		if self.root.current == "Board":
			if remaining_time > 0:
				Clock.schedule_once(self.timerStart, 1)

	def toggle_settings(self, setting_type, button):
		'''Control application settings like music and sound effects''' 
		global settingsDict
		settingsDict[setting_type] = 0 if settingsDict[setting_type] else 1
		button.icon_path = f"res/icons/{setting_type.lower()}-icon-{settingsDict[setting_type]}.png"
		if setting_type == "Music":
			if settingsDict["Music"] == 1:
				self.background_music.play()
			else:
				self.background_music.stop()
		save_settings()

	def transition(self, screen_name, direction, dt=None):
		'''Transition from one screen to another in a specified direction'''
		screen_manager.transition.direction = direction
		self.root.current = screen_name
		#print(f"Switching to {screen_name}")

if __name__ == "__main__":
	sudoku_app = SudokuApp()
	sudoku_app.run()
