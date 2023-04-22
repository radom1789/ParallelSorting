#################################################
# Parallel Sorting
# Tracy Yang, tracyy
# 
# Project description: The objective of the Parallel Sorting is to sort the 
# liquids in the flask/ bottle according to their color. There will be a set of 
# bottles, both empty and filled with layers of different colored liquid, at the
# start of the game. You can only pour liquids of the same color from bottle to 
# bottle (unless the bottle is empty). Once a bottle is filled, you cannot pour 
# any more liquid into the bottle even if they are the same color. You win the 
# game if all colors are sorted. The game ends (at that particular puzzle) if 
# there are no more moves to go.
#################################################


from cmu_graphics import *
from PIL import Image
import random


class Cup:
    # assuming there is only 4 cups that have liquids in them
    colors = ["red", "blue", "yellow", "pink"]
    def __init__(self, maxLevel, levels):
        self.level = maxLevel
        self.colorsInCup = levels
    
    def __repr__(self):
        return f'{self.level} {self.colorsInCup}'
    

class Puzzle:
    # self.cups variable idea was taken from WaterPouringPuzzle
    def __init__(self, app, numCups):
        self.cups = []
        self.coordLst = []
        allColorLst = []

        # makes a list of all the colors that will be in the cups to make sure 
        # there will be a set number of times each color appears
        for _ in range(numCups):
            for i in range(len(Cup.colors)):
                allColorLst += [i]
        
         # shuffles the list twice to make sure the puzzle will be randomized 
         # and decreases the chances of a fully sorted cup from appearing
        for _ in range(2):
            random.shuffle(allColorLst)

        # gets the list of cups plus the 2 empty cups
        for i in range(numCups + 2):
            indexLst = []
            # fills numCups number of cups
            if i != numCups + 1 and i != numCups:
                for j in range(len(Cup.colors)):
                    indexLst += [allColorLst[0]]
                    allColorLst.pop(0)

                cup = Cup(4, indexLst)

                self.cups.append(cup)
            # leaves last 2 cups empty
            else:
                self.cups.append(Cup(4, indexLst))

        # gets the coordinates list for self.coordLst
        # manually inputed app.cupHeight and app.cupWidth
        spaceH = app.height - (len(self.cups)//2-1)*300 - 50
        spaceW = app.width - len(self.cups)//2*150 - 60*(len(self.cups)//2-1)
        for i in range(len(self.cups)):
            if i < 3:
                self.coordLst += [[spaceW // 2 + i*(150+50), spaceH // 2]]
            else:
                self.coordLst += [[spaceW // 2 + (i-3)*(150+50), spaceH // 2 + (300+60)]]
        
    # isWin function has some inspiration from WaterPouringPuzzle (loops
    # through list of cups to check for something, but that something was my own
    # idea)
    def isWin(self, app):
        # loops through the cups to make sure all is sorted
        for i in range(len(app.puzzle.cups)):
            if app.puzzle.cups[i].colorsInCup != []:
                # sets the color of the first level
                color = app.puzzle.cups[i].colorsInCup[0]
                # checks that a fully sorted cup is len of the number of levels
                if len(app.puzzle.cups[i].colorsInCup) == len(Cup.colors):
                    # checks that the color is the same within the cups
                    for level in app.puzzle.cups[i].colorsInCup:
                        if level != color:
                            return False
                else: return False  
        return True

    # the pourCup function has some inspiration from WaterPouringPuzzle (that
    # there should be a puzzle that allows the user to pour from cup to cup)            
    def pourCup(self, app, fromCupIndex, toCupIndex):
        if canPour(app, fromCupIndex, toCupIndex):
            # grabs the last level (or on screen, the top level)
            fromCupLength = len(self.cups[fromCupIndex].colorsInCup)
            fromCupTopLevel = self.cups[fromCupIndex].colorsInCup[fromCupLength-1]

            index = consecutiveColorIndex(self.cups[fromCupIndex])

            for i in range(index):
                self.cups[toCupIndex].colorsInCup.append(fromCupTopLevel)
                self.cups[fromCupIndex].colorsInCup.pop(len(self.cups[fromCupIndex].colorsInCup)-1)

# Button class is taken from in class demo of button class with some changes
class Button:
    def __init__(self, x, y, r, fun):
        self.x = x
        self.y = y
        self.r = r
        self.fun = fun

    def checkForPress(self, app, mouseX, mouseY):
        # Might want to change this if you want a non-circular button
        if ((mouseX - self.x)**2 + (mouseY-self.y)**2)**0.5 <= self.r:
            self.fun(app)
    
# returns the index where the last consecutive color occurs
def consecutiveColorIndex(cup):
    count = 0
    for i in range(len(cup.colorsInCup)-1, -1, -1):
        if cup.colorsInCup[i] == cup.colorsInCup[i-1]:
            count +=1
        else:
            return count + 1
    return count

# the canPour function is an extension of pourCup function
def canPour(app, fromCupIndex, toCupIndex):
    # checks that the fromCup is not empty
    if app.puzzle.cups[fromCupIndex].colorsInCup == []:
        return False
    # checks that there is room in the toCup
    if (len(app.puzzle.cups[toCupIndex].colorsInCup) >= 
            app.puzzle.cups[toCupIndex].level):
        return False
    # checks that the toCup is not empty
    if app.puzzle.cups[toCupIndex].colorsInCup != []:
        lengthToCup = len(app.puzzle.cups[toCupIndex].colorsInCup)
        lengthFromCup = len(app.puzzle.cups[fromCupIndex].colorsInCup)
        # makes sure that the colors at the top of cup match
        if (app.puzzle.cups[toCupIndex].colorsInCup[lengthToCup-1] != 
           app.puzzle.cups[fromCupIndex].colorsInCup[lengthFromCup-1]):
           return False
    return True

def isSolvablePuzzle(app):
    visited = []
    if app.puzzle.isWin(app):
        return True
    else:
        for i in range(len(app.puzzle.cups)):
            for j in range(i+1, len(app.puzzle.cups)):
                if isLegal(app, visited):
                    app.puzzle.pourCup(app, i, j)
                    result = isSolvablePuzzle(app)
                    visited += [(i, j)]
                    if result != False:
                        return True
                    app.puzzle.pourCup(app, j, i)
        return False

# determines if a move can still be made
def hasNextMove(app):
    for i in range(len(app.puzzle.cups)):
        for j in range(i+1, len(app.puzzle.cups)):
            if canPour(app, i, j):
                return True
    return False

# determines if every move has been visited or if there is a possible move to go
def isLegal(app, visitedMoves):
    if not hasNextMove(app): return False
    else:
        # makes a list of all possible moves
        allStates = []
        for i in range(len(app.puzzle.cups)):
            for j in range(i+1, len(app.puzzle.cups)):
                allStates += [(i, j)]
        
        # checks to see if the current visited moves list is the same as the 
        # list of all possible moves. If the lists are equal, should return 
        # False or else the backtracking function would be an infinite loop
        for state in visitedMoves:
            if state not in allStates:
                return True
        return False

def onAppStart(app):
    Images(app)
    app.puzzle = Puzzle(app, 4)
    # while not isSolvablePuzzle(app):
    #     app.puzzle = Puzzle(app, 4)
    app.selectedCup = None
    app.cupHeight = 300
    app.cupWidth = 150

def Images(app):
    app.cupImage = Image.open("Cup.png")
    app.capImage = Image.open("Cap.png")

    app.cupImage = CMUImage(app.cupImage)
    app.capImage = CMUImage(app.capImage)

# while the idea may be similiar from the WaterPouringPuzzle of getJarIndexFromPoint
# I didn't actually look at the function because I wrote this function after
# I wrote onMousePress function and thought of the idea. I only looked at it 
# after I finishd the function
def getCupIndexFromPoint(app, mouseX, mouseY):
    coordLst = app.puzzle.coordLst
    # adds the bottom right coordinate
    for lst in coordLst:
        lst += [lst[0] + app.cupWidth, lst[1] + app.cupHeight]
    
    index = 0
    for coords in coordLst:
        if coords[0] <= mouseX <= coords[2] and coords[1] <= mouseY <= coords[3]:
            return index
        index += 1
    return -1

# there was some inspiration from onMousePress function in the WaterPouringPuzzle
# (the idea of what to do in different clicked scenarios)
def onMousePress(app, mouseX, mouseY):
    index = getCupIndexFromPoint(app, mouseX, mouseY)
    if index != -1:
        # if no cup is selected, set it as the selected cup and shift it up
        if app.selectedCup == None:
            app.selectedCup = index
            app.puzzle.coordLst[index][1] -= 50
        # if the selected cup and the newly selected cup is the same, deselect 
        # and place it back in its original position
        elif app.selectedCup != None and app.selectedCup == index:
            app.selectedCup = None
            app.puzzle.coordLst[index][1] += 50
        # if the selected cup and the newly selected cup is not the same
        elif app.selectedCup != None and app.selectedCup != index:
            # if can pour from the selected cup into the newly selected cup,
            # pour liquid from cup to the other
            if canPour(app, app.selectedCup, index):
                app.puzzle.pourCup(app, app.selectedCup, index)
                app.puzzle.coordLst[app.selectedCup][1] += 50
            # if cannot pour from the selected cup into the newly selected cup,
            # place the selected cup back in its original position
            else:
                app.puzzle.coordLst[app.selectedCup][1] += 50
            app.selectedCup = None

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = "turquoise" )
    liquidH = (app.cupHeight-20)/len(Cup.colors)
    cupLst = app.puzzle.cups
    # fills 4 cups and leaves 2 empty and draws 6 cups
    for i in range(len(app.puzzle.cups)):
        if i < 3:
            # fill top cups
            for j in range(len(cupLst[i].colorsInCup)):
                drawRect(app.puzzle.coordLst[i][0], app.puzzle.coordLst[i][1] + 
                        (app.cupHeight - liquidH) - (j*(liquidH)), 150, liquidH, 
                        fill = cupLst[i].colors[cupLst[i].colorsInCup[j]])
            # draws top cups
            drawRect(app.puzzle.coordLst[i][0], app.puzzle.coordLst[i][1], 150, 
                    300, fill = None, border = "black")
        
        else:
            # fill bottom cups
            for j in range(len(cupLst[i].colorsInCup)):
                drawRect(app.puzzle.coordLst[i][0], app.puzzle.coordLst[i][1] + 
                        (app.cupHeight - liquidH) - (j*(liquidH)), 150, liquidH, 
                        fill = cupLst[i].colors[cupLst[i].colorsInCup[j]])
            # draws bottom cups
            drawRect(app.puzzle.coordLst[i][0], app.puzzle.coordLst[i][1], 150, 
                     300, fill = None, border = "black")

    if app.puzzle.isWin(app):
        drawRect(app.width//3, app.height//3, 300, 200, fill = "navy" )
        drawLabel("You Win!", app.width//3 + 150, app.height//3 + 100, fill = "white", size = 30)



# class Bubbles:
#     color = ["red", "blue", "yellow", "pink"] #insert some colors
#     def __init__(self):
#         self.color = Bubbles.color[random.randint(0,6)]

#         self.stepCounter = 0

#         #Set initial position, velocity, acceleration
#         self.x, self.y = 100, 100
#         self.dy = 0
#         self.ddy = .1

#     def draw(self, app):
#         drawCircle(self.x, self.y, self.r, fill = self.color)

runApp(width=1200, height=800)