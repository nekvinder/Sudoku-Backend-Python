import cv2 as cv
import numpy as np
import math


class SudokuValidate:
    def __init__(self, board):
        self.board = board

    def updateBoard(self, board):
        self.board = board

    def __Repeat(self, x):
        _size = len(x)
        repeated = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(_size):
            k = i + 1
            for j in range(k, _size):
                if x[i] == x[j] and x[i] not in repeated:
                    repeated[i], repeated[j] = 1, 1
        return repeated

    def __getRowValidator(self, r):
        return self.__Repeat(self.board[r-1])

    def __getColValidator(self, c):
        return self.__Repeat(self.board[:, c-1])

    def __getBlockValidator(self, blockRow, blockCol):
        return np.reshape(self.__Repeat(np.reshape(self.board[blockRow*3:blockRow *
                                                              3+3, blockCol*3:blockCol*3+3], 9)), (3, 3))

    def getValidator(self):
        tmp = np.zeros((9, 9), int)
        for x in range(3):
            for y in range(3):
                tmp[x*3:x * 3+3, y*3:y*3 +
                    3] = self.__getBlockValidator(x, y)

        for x in range(9):
            tmp[x] = np.add(tmp[x], self.__getRowValidator(x+1))
            tmp[:, x] = np.add(tmp[:, x], self.__getColValidator(x+1))

        return(tmp)


class SudokuDesign:

    def __init__(self, board, validator):
        # self.name = name
        self.board = board
        self.validator = validator
        self.create_background()

    def updateBoard(self, board):
        self.board = board

    def getBoardImage(self, frame):
        frame = self.__create_sudoku(frame, self.board)
        return frame

    def create_background(self):
        frame = np.ones(shape=[500, 500, 3], dtype=np.uint8)
        frame = cv.rectangle(frame, (0, 0), (500, 500), (255, 255, 255), -1)
        return frame

    def __create_one_box(self, frame, r, c, value, valid):
        r, c = c-1, r-1
        frame = cv.rectangle(frame, ((0+r)*50, (0+c)*50),
                             (50+((0+r)*50), 50+((0+c)*50)), (200, 200, 200), 2)
        frame = cv.putText(frame, value, (((0+r)*50)+12, (50+((0+c)*50)) - 12), cv.FONT_HERSHEY_SIMPLEX,
                           1, (255 if valid else 0, 0, 0 if valid else 255), 2, cv.LINE_AA)
        return frame

    def __addUnitPossibles(self, frame, r, c, possibles: set):
        frame = cv.putText(frame, "".join(map(str, possibles)), (((0+c)*50)+2, (50+((0+r)*50)) - 37), cv.FONT_HERSHEY_SIMPLEX,
                           0.4, (100, 50, 100), 1, cv.LINE_AA)
        return frame

    def addPossibles(self, frame, sdkSolver):
        for x in range(9):
            for y in range(9):
                if int(self.board[x, y]) < 1:
                    self.__addUnitPossibles(frame,
                                            x, y, sdkSolver.possibleValues(x+1, y+1))
        return frame

    def __create_one_block(self, frame, r, c, values):
        for x in range(3*(r-1), r*3):
            for y in range(3*(c-1), c*3):
                frame = self.__create_one_box(frame,
                                              x+1, y+1, str(values[x, y]), True if self.validator[x, y] == 0 else False)
        frame = cv.rectangle(frame, (50*3*(c-1), 50*3*(r-1)),
                             (50*3*(c), 50*3*(r)), (0, 0, 0), 4)
        return frame

    def __create_sudoku(self, frame, values):
        for x in range(1, 4):
            for y in range(1, 4):
                frame = self.__create_one_block(frame, x, y, values)
        return frame


class SudokuSolver:
    def __init__(self, board):
        self.board = board

    def updateBoard(self, board):
        self.board = board

    def __getRow(self, r) -> set:
        return set(self.board[r-1])-{0}

    def __getCol(self, c) -> set:
        return set(self.board[:, c-1])-{0}

    def __getBlock(self, x, y) -> set:
        x, y = math.ceil(x/3)-1, math.ceil(y/3)-1
        return set(np.reshape(self.board[x*3:(x*3)+3, y*3:(y*3)+3], (9)))-{0}

    def possibleValues(self, r, c):
        return set(c for c in range(1, 10)) - (self.__getRow(r) | self.__getCol(c) | self.__getBlock(r, c))

    def getSolvedBoard(self):
        for x in range(9):
            for y in range(9):
                if int(self.board[x, y]) < 1:
                    vals = self.possibleValues(x+1, y+1)
                    if len(vals) == 1:
                        self.board[x, y] = vals.pop()
        return self.board


def solveX():
    f = open("sudokus.txt", "r")
    arr = f.readlines()
    f.close()
    boards = []
    for i in range(0, 480, 10):
        lst = ""
        for x in arr[i:i+9]:
            lst += x[:9]
        boards.append(np.reshape(np.array(list(lst), int), (9, 9)))

    # print(boards)

    maxtries = 20
    totalFails = 0
    cnt = -1
    for board in boards[31:32]:
        print(board)
        cnt = cnt+1
        tries = 0
        sdkValidator = SudokuValidate(board)
        validator = sdkValidator.getValidator()
        sdkDesigner = SudokuDesign(board, validator)
        sdkSolver = SudokuSolver(board)
        speed = 100
        while 0 in set(np.reshape(board, (81))):
            frame = sdkDesigner.create_background()
            sdkDesigner.addPossibles(frame, sdkSolver)
            frame = sdkDesigner.getBoardImage(frame)
            # cv.imwrite('solutions/image{}_{}.jpg'.format(cnt, tries), frame)
            cv.imshow('image', frame)
            cv.waitKey(speed)

            f2 = sdkDesigner.create_background()
            sdkDesigner.updateBoard(sdkSolver.getSolvedBoard())
            f2 = sdkDesigner.getBoardImage(f2)
            # cv.imwrite('solutions/image{}_{}_sol.jpg'.format(cnt, tries), f2)
            cv.imshow('image', f2)
            cv.waitKey(speed)
            tries += 1
            if tries > maxtries:
                totalFails += 1
                break

        # break
    print("Total Fails:{}".format(totalFails))
    cv.waitKey(1000)
    cv.destroyAllWindows()


solveX()
