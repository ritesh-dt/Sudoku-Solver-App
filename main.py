from random import randrange
from functools import partial
import kivy
kivy.require('1.11.0')
from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.clock import Clock
from kivy.graphics import Line, Color, Rectangle
from kivy.core.window import Window

cellArray = []
board = []
BOARD_SIZE, BLOCK_SIZE = 9, -1
blockCount, blockSize = -1, -1
sectionX, sectionY = -1, -1

def generateBoardFromFile(type="Play"):
	global board, BOARD_SIZE, BLOCK_SIZE, blockCount, blockSize, sectionX, sectionY
	boardArray = []
#	print(f"boards_{BOARD_SIZE}.txt")
	boardFile = open(f"boards_{BOARD_SIZE}.txt", "r").read().split('\n')
	BOARD_SIZE = int(boardFile[0])
	BLOCK_SIZE = int(BOARD_SIZE ** 0.5)
	boardFile.pop(0)
	boardFile.remove('')
	boardCount = len(boardFile)//(BOARD_SIZE)
	for boards in range(boardCount):
		board = []
		for row in range(BOARD_SIZE):
			rowList = boardFile[boards*(BOARD_SIZE)+row].strip('[]').split(',')
			board.append([int(num) for num in rowList])
		boardArray.append(board[:])
	board = []
#	print(boardCount)
	if type == "Solve":
		for elem in boardArray[randrange(0, 1)]:
			board.append(elem[:])
	else:
		for elem in boardArray[randrange(1, boardCount)]:
			board.append(elem[:])

	blockCount = int(BOARD_SIZE**0.5)
	blockSize = 9*Window.size[0]/(10*BOARD_SIZE)
	sectionX = Window.size[0]*0.05
	sectionY = Window.size[1]*0.85 - blockSize
		

def check_board_validity(board, BOARD_SIZE: int):
	num_list = []
	
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

def list_delete(num_array, elem):
	try:
		num_array.remove(elem)
	except ValueError:
		pass

remainingTime = -1
def timerStart(dt, label):
	global remainingTime
	remainingTime -= 1
	time_in_minutes = "%2d:%02d" %(remainingTime//60, remainingTime%60)
	label.text= ("Time remaining: " + time_in_minutes)
	if remainingTime > 60:
		label.color = (0, 0.85, 0, 1)
	else:
		label.color = (1, 0, 0, 1)
	print("Time remaining: " + time_in_minutes)
	if screen_manager.current == "Board":
		if remainingTime > 0:
			label.parent.children[4].disabled = True
			Clock.schedule_once(partial(timerStart, label=label), 1)
#			print(label.parent.children[4].text)
		else:
			label.parent.children[4].disabled = False
			print(label.parent.children)
			label.parent.children[1].disabled = True

def isSolved():
	global screen_manager, inputBoard
	board_screen = screen_manager.screens[2]
#	for label in board_screen.children[-1].children[-4:]:
#		print(label.text)
#	print(board_screen.children[-1].children)
#	Clock.schedule_once(partial(timerStart, label=board_screen.children[-1].children[6]), 1)
	print(board_screen.ids, board_screen.children)
	solvedLabel = board_screen.ids.solvedLabel
	solvedLabel.text = "Not Solved"
	solvedLabel.color = (1, 0, 0, 1)
	inputBoard = []
	for row in range(BOARD_SIZE):
		inputBoard.append(list())
		for col in range(BOARD_SIZE):
			text = cellArray[row*BOARD_SIZE+col].text
			inputBoard[row].append(int(text) if text else 0)
	
	tilesLabel = board_screen.children[-1].children[8]
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

def cell_options (board, row, col):
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
	
def cell_valid(index):
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

def solve (parent):
	parent.children[4].disabled = True
	Clock.schedule_once(partial(solveDelay, parent), 1)

def solveDelay(parent, dt):
	global index, cells_filled, board
#	print("Solving board...")
	index = 0
	cells_filled = []
	while index < BOARD_SIZE**2:
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
					print("Board not solvable")
					break
				board[index//BOARD_SIZE][index%BOARD_SIZE] = 0
				cellArray[index].text = str(board[index//BOARD_SIZE][index%BOARD_SIZE])
		else:
			index += 1
	print("Board solved")
	isSolved()
	parent.children[4].disabled = False

def addCells(layout):
	global cellArray
	
	def validate(instance):
		global inputBoard
		
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
			isSolved()

	def lostFocus(instance, value):
		if not value:
			isSolved()
			validate(instance)
		else:
			instance.foreground_color = 0,0,0,1
	
	layout.clear_widgets()
	cellArray = []
	for row in range(BOARD_SIZE):
		for col in range(BOARD_SIZE):
			if board[row][col]:
				numButton = Label(text=str(board[row][col]) if board[row][col] else "")
			else:
				numButton = NumInput(text=str(board[row][col]) if board[row][col] else "")
				numButton.bind(on_text_validate=validate, focus=lostFocus)
				numButton.padding_y = (blockSize-(400/BOARD_SIZE))/2
			layout.add_widget(numButton)
			cellArray.append(numButton)
			with numButton.canvas.after:
				Color(193/255, 163/255, 123/255, 1)
				Line(width=2, rectangle=(sectionX + blockSize*(col), sectionY - blockSize*(row), blockSize, blockSize))
				if (row+1)%blockCount==0 and (col)%blockCount==0:
					Color(193/255, 163/255, 123/255, 1)
					Line(width=5, rectangle=(sectionX + blockSize*(col), sectionY - blockSize*(row), blockSize*blockCount, blockSize*blockCount))
				with layout.canvas:
					Color(193/255, 163/255, 123/255, 1)
					Line(width=5, rectangle=(sectionX + blockSize*(0), sectionY - blockSize*(BOARD_SIZE-1), blockSize*BOARD_SIZE, blockSize*BOARD_SIZE))


class NumInput(TextInput):
	def __init__(self, **kwargs):
		super(NumInput, self).__init__(**kwargs)
	
	def insert_text(self, substring, from_undo=False):
		if len(self.text) > 0:
			substring = ""
		TextInput.insert_text(self, substring, from_undo)
		

class Board(GridLayout):
	def __init__(self, **kwargs):
		global cellArray
		super(Board, self).__init__(**kwargs)
		self.cols= BOARD_SIZE
		self.rows= BOARD_SIZE
		
		addCells(self)


class BoardScreen(FloatLayout):
	def __init__(self, **kwargs):
		super(BoardScreen, self).__init__(**kwargs)
		#self.clear_widgets()
#		print(self.parent, "Init")
		self.board = Board()
		self.board.size_hint = (9/10, 9*Window.size[0]/(Window.size[1]*10))
		#self.add_widget(self.board)
		self.borderGrid = GridLayout()
		self.borderGrid.size_hint = (9/10, 9*Window.size[0]/(Window.size[1]*10))
		self.add_widget(self.borderGrid)
		
	def updateCell(self, row, col):
		cellArray[row*BOARD_SIZE+col].text = board[row][col]
	
	def solveBoard(self):
		global cellArray, board
		inputBoard = []
		for row in range(BOARD_SIZE):
			inputBoard.append([int(elem.text) if elem.text else 0 for elem in cellArray[row*BOARD_SIZE:(row+1)*BOARD_SIZE]])
		if check_board_validity(inputBoard, BOARD_SIZE) == "Valid":
			#self.children[5].disabled = True
			board = inputBoard.copy()
			solve(self)
			for row in range(BOARD_SIZE):
				for col in range(BOARD_SIZE):
					cellArray[row*BOARD_SIZE+col].text = str(board[row][col]) if board[row][col] else ""
			#self.children[3].disabled = False
#			print("Enabled")
		else:
			print("Invalid Board")		
#			print(check_board_validity(inputBoard, BOARD_SIZE))
	
	def generateBoard(self):
		Clock.schedule_once(loadBoardScreen, 0.7)
		screen_manager.transition.direction = "left"
		screen_manager.current = "Loading"
		
	def select_board_size(self, board_size: int, instance):
		global BOARD_SIZE
		main_app.board_size = board_size
		BOARD_SIZE = board_size
		print(BOARD_SIZE)
		print(instance.parent.children)
		for btn in instance.parent.children:
			btn.disabled = False
		instance.disabled = True
	
	def loadMainScreen(self):
		global screen_manager
		screen_manager.transition.direction = "right"
		screen_manager.current = "Main"
		
screen_manager = ScreenManager()

def loadBoardScreen(dt, type="Play"):
	global screen_manager, remainingTime
	board_screen = screen_manager.screens[2]
	generateBoardFromFile(type)
#	print(board, "For ", type)
	for widget in board_screen.children[:-1]:
		board_screen.remove_widget(widget)
#	print(board_screen.children, "DT")
	board_screen.board = Board()
	board_screen.board.size_hint = (9/10, 9*Window.size[0]/(Window.size[1]*10))
	board_screen.add_widget(board_screen.board)
	board_screen.borderGrid = GridLayout()
	board_screen.borderGrid.size_hint = (9/10, 9*Window.size[0]/(Window.size[1]*10))
	board_screen.add_widget(board_screen.borderGrid)
	screen_manager.transition.direction = "left"
	screen_manager.current = "Board"
	remainingTime = 22
	isSolved()
#	print(board_screen.children[-1].children)
	Clock.schedule_once(partial(timerStart, label=board_screen.children[-1].children[7]), 1)
#	print(board)

class MainScreen(Screen):
	def select_board_size(self, board_size: int, instance):
		global BOARD_SIZE
		main_app.board_size = board_size
		BOARD_SIZE = board_size
		print(BOARD_SIZE)
		for btn in instance.parent.children:
			btn.disabled = False
		instance.disabled = True

	def loadGame(self, type="Play"):
		Clock.schedule_once(partial(loadBoardScreen, type=type), 0.7)
		screen_manager.transition.direction = "left"
		screen_manager.current = "Loading"

class LoadingScreen(FloatLayout):
	def __init__ (self, **kwargs):
		super(LoadingScreen, self).__init__(**kwargs)
		self.loading_label = Label(text="Loading...")
		self.loading_label.font_size = 64
		self.loading_label.pos_hint = {"center_x": 0.5, "center_y": 0.5}
		self.add_widget(self.loading_label)
	

class SudokuApp(App):
	global BOARD_SIZE
	board_size = int(open("boards_9.txt", "r").readlines()[0])
	BOARD_SIZE = board_size
	def build(self):
		global screen_manager
		screen = Screen(name="Main")
		screen.add_widget(MainScreen())
		screen_manager.add_widget(screen)
		
		screen = Screen(name="Loading")
		screen.add_widget(LoadingScreen())
		screen_manager.add_widget(screen)
		
		generateBoardFromFile()
		screen = Screen(name="Board")
		screen.add_widget(BoardScreen())
		screen_manager.add_widget(screen)
		
		print(board)
		screen_manager.current = "Main"
		return screen_manager
	
if __name__ == "__main__":
	main_app = SudokuApp()
	main_app.run()