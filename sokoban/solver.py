import sys
import collections
import numpy as np
import heapq
import time
import numpy as np
global posWalls, posGoals

class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""
    def  __init__(self):
        self.Heap = []
        self.Count = 0
        self.len = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0

"""Load puzzles and define the rules of sokoban"""

def transferToGameState(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace('\n','') for x in layout]
    layout = [','.join(layout[i]) for i in range(len(layout))]
    layout = [x.split(',') for x in layout]
    maxColsNum = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == ' ': layout[irow][icol] = 0  
            elif layout[irow][icol] == '#': layout[irow][icol] = 1 
            elif layout[irow][icol] == '&': layout[irow][icol] = 2 
            elif layout[irow][icol] == 'B': layout[irow][icol] = 3 
            elif layout[irow][icol] == '.': layout[irow][icol] = 4 
            elif layout[irow][icol] == 'X': layout[irow][icol] = 5 
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)]) 

    return np.array(layout)

def transferToGameState2(layout, player_pos):
    """Transfer the layout of initial puzzle"""
    maxColsNum = max([len(x) for x in layout])
    temp = np.ones((len(layout), maxColsNum))
    for i, row in enumerate(layout):
        for j, val in enumerate(row):
            temp[i][j] = layout[i][j]

    temp[player_pos[1]][player_pos[0]] = 2
    return temp

def PosOfPlayer(gameState):
    """Return the position of agent"""
    return tuple(np.argwhere(gameState == 2)[0]) 

def PosOfBoxes(gameState):
    """Return the positions of boxes"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5)))

def PosOfWalls(gameState):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1))

def PosOfGoals(gameState):
    """Return the positions of goals"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5)))

def isEndState(posBox):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(posBox) == sorted(posGoals)

def isLegalAction(action, posPlayer, posBox):
    """Check if the given action is legal"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper(): 
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    return (x1, y1) not in posBox + posWalls

def legalActions(posPlayer, posBox):
    """Return all legal actions for the agent in the current game state"""
    allActions = [[-1,0,'u','U'],[1,0,'d','D'],[0,-1,'l','L'],[0,1,'r','R']]
    xPlayer, yPlayer = posPlayer
    legalActions = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox: 
            action.pop(2) 
        else:
            action.pop(3)
        if isLegalAction(action, posPlayer, posBox):
            legalActions.append(action)
        else: 
            continue     

    return tuple(tuple(x) for x in legalActions)

def updateState(posPlayer, posBox, action):
    """Return updated game state after an action is taken"""
    xPlayer, yPlayer = posPlayer
    newPosPlayer = [xPlayer + action[0], yPlayer + action[1]]
    posBox = [list(x) for x in posBox]
    if action[-1].isupper(): # if pushing, update the position of box
        posBox.remove(newPosPlayer)
        posBox.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1]])
    posBox = tuple(tuple(x) for x in posBox)
    newPosPlayer = tuple(newPosPlayer)
    return newPosPlayer, posBox

def isFailed(posBox):
    """This function used to observe if the state is potentially failed, then prune the search"""
    rotatePattern = [[0,1,2,3,4,5,6,7,8],
                    [2,5,8,1,4,7,0,3,6],
                    [0,1,2,3,4,5,6,7,8][::-1],
                    [2,5,8,1,4,7,0,3,6][::-1]]
    flipPattern = [[2,1,0,5,4,3,8,7,6],
                    [0,3,6,1,4,7,2,5,8],
                    [2,1,0,5,4,3,8,7,6][::-1],
                    [0,3,6,1,4,7,2,5,8][::-1]]
    allPattern = rotatePattern + flipPattern

    for box in posBox:
        if box not in posGoals:
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1), 
                    (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1), 
                    (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox: return True
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls: return True
    return False

"""Implement all approaches"""

def depthFirstSearch(gameState):
    """Implement depthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    startState = (beginPlayer, beginBox) # trạng thái ban đầu gồm vị trí player và boxes
    frontier = collections.deque([[startState]]) # stack chứa các đường đi (dùng deque, pop từ cuối → DFS)
    exploredSet = set() # tập các trạng thái đã duyệt để tránh lặp
    actions = [[0]] # danh sách action tương ứng với mỗi đường đi trong frontier
    temp = [] # kết quả cuối cùng (chuỗi action)

    while frontier:
        node = frontier.pop()           # lấy đường đi cuối cùng trong stack (DFS)
        node_action = actions.pop()     # lấy action tương ứng

        if isEndState(node[-1][-1]):    # nếu trạng thái cuối của đường đi là goal
            temp += node_action[1:]     # lưu lại chuỗi action (bỏ sentinel 0 đầu tiên)
            break

        if node[-1] not in exploredSet:          # nếu trạng thái chưa được duyệt
            exploredSet.add(node[-1])            # đánh dấu đã duyệt
            for action in legalActions(node[-1][0], node[-1][1]):  # duyệt các action hợp lệ
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):          # bỏ qua nếu trạng thái là deadlock
                    continue
                frontier.append(node + [(newPosPlayer, newPosBox)])  # thêm trạng thái mới vào stack
                actions.append(node_action + [action[-1]])           # thêm action tương ứng
    return temp

def breadthFirstSearch(gameState):
    """Implement breadthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)       # lấy vị trí ban đầu của các box
    beginPlayer = PosOfPlayer(gameState)   # lấy vị trí ban đầu của player

    startState = (beginPlayer, beginBox)          # trạng thái ban đầu
    frontier = collections.deque([[startState]])  # queue chứa các đường đi (dùng deque, popleft → BFS)
    exploredSet = set()                           # tập trạng thái đã duyệt
    actions = collections.deque([[0]])            # queue action tương ứng với frontier
    temp = []                                     # kết quả chuỗi action

    while frontier:
        node = frontier.popleft()           # lấy đường đi đầu tiên trong queue (BFS - FIFO)
        node_action = actions.popleft()     # lấy action tương ứng

        if isEndState(node[-1][-1]):        # kiểm tra trạng thái cuối có phải goal không
            temp += node_action[1:]         # lưu chuỗi action (bỏ sentinel 0)
            break

        if node[-1] not in exploredSet:              # nếu trạng thái chưa duyệt
            exploredSet.add(node[-1])                # đánh dấu đã duyệt
            for action in legalActions(node[-1][0], node[-1][1]):  # duyệt action hợp lệ
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):              # bỏ qua deadlock
                    continue
                frontier.append(node + [(newPosPlayer, newPosBox)])  # thêm vào cuối queue
                actions.append(node_action + [action[-1]])           # thêm action tương ứng
    return temp

def cost(actions):
    """A cost function - đếm số bước đi KHÔNG đẩy box (chữ thường = walk, không push)"""
    return len([x for x in actions if x.islower()])

def uniformCostSearch(gameState):
    """Implement uniformCostSearch approach"""
    beginBox = PosOfBoxes(gameState)       # lấy vị trí ban đầu của các box
    beginPlayer = PosOfPlayer(gameState)   # lấy vị trí ban đầu của player

    startState = (beginPlayer, beginBox)   # trạng thái ban đầu
    frontier = PriorityQueue()             # priority queue chứa các đường đi, ưu tiên chi phí thấp
    frontier.push([startState], 0)         # đẩy trạng thái ban đầu với chi phí 0
    exploredSet = set()                    # tập trạng thái đã duyệt
    actions = PriorityQueue()              # priority queue action tương ứng với frontier
    actions.push([0], 0)                   # push sentinel với chi phí 0
    temp = []                              # kết quả chuỗi action

    while not frontier.isEmpty():
        node = frontier.pop()              # lấy đường đi có chi phí thấp nhất
        node_action = actions.pop()        # lấy action tương ứng

        if isEndState(node[-1][-1]):       # kiểm tra trạng thái cuối có phải goal không
            temp += node_action[1:]        # lưu chuỗi action (bỏ sentinel 0)
            break

        if node[-1] not in exploredSet:              # nếu trạng thái chưa duyệt
            exploredSet.add(node[-1])                # đánh dấu đã duyệt
            for action in legalActions(node[-1][0], node[-1][1]):  # duyệt action hợp lệ
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):              # bỏ qua deadlock
                    continue
                new_node_action = node_action + [action[-1]]       # thêm action mới
                new_cost = cost(new_node_action[1:])               # tính chi phí: số bước walk
                frontier.push(node + [(newPosPlayer, newPosBox)], new_cost)  # thêm vào frontier với chi phí mới
                actions.push(new_node_action, new_cost)                      # thêm action tương ứng
    return temp

"""Read command"""
def readCommand(argv):
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokobanLevels',
                      help='level of game to play', default='level1.txt')
    parser.add_option('-m', '--method', dest='agentMethod',
                      help='research method', default='bfs')
    args = dict()
    options, _ = parser.parse_args(argv)
    with open('assets/levels/' + options.sokobanLevels,"r") as f: 
        layout = f.readlines()
    args['layout'] = layout
    args['method'] = options.agentMethod
    return args

def get_move(layout, player_pos, method):
    time_start = time.time()
    global posWalls, posGoals
    gameState = transferToGameState2(layout, player_pos)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)
    
    if method == 'dfs':
        result = depthFirstSearch(gameState)
    elif method == 'bfs':        
        result = breadthFirstSearch(gameState)
    elif method == 'ucs':
        result = uniformCostSearch(gameState)
    else:
        raise ValueError('Invalid method.')
    time_end = time.time()
    print('Runtime of %s: %.2f second.' %(method, time_end-time_start))
    print(result)
    return result