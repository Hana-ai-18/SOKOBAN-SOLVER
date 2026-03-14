#solver.py 
import sys
import collections
import numpy as np
import heapq
import time
global posWalls, posGoals

nodes_expanded = 0



class PriorityQueue:

    def __init__(self):
        self.Heap  = []   
        self.Count = 0     

    def push(self, item, priority):
        
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)  
        self.Count += 1                 

    def pop(self):
    
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        
        return len(self.Heap) == 0




def transferToGameState(layout):
    
    layout = [x.replace('\n', '') for x in layout]      
    layout = [','.join(layout[i]) for i in range(len(layout))] 
    layout = [x.split(',') for x in layout]              
    maxColsNum = max([len(x) for x in layout])            
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            
            if   layout[irow][icol] == ' ': layout[irow][icol] = 0   
            elif layout[irow][icol] == '#': layout[irow][icol] = 1   
            elif layout[irow][icol] == '&': layout[irow][icol] = 2  
            elif layout[irow][icol] == 'B': layout[irow][icol] = 3   
            elif layout[irow][icol] == '.': layout[irow][icol] = 4   
            elif layout[irow][icol] == 'X': layout[irow][icol] = 5  
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum - colsNum)])
    return np.array(layout)   


def transferToGameState2(layout, player_pos):
    
    maxColsNum = max([len(x) for x in layout])            
    temp = np.ones((len(layout), maxColsNum))              
    for i, row in enumerate(layout):
        for j, val in enumerate(row):
            temp[i][j] = layout[i][j]                     
    temp[player_pos[1]][player_pos[0]] = 2                 
    return temp



def PosOfPlayer(gameState):
    """Tra ve vi tri (row, col) cua player (o co gia tri = 2)"""
    return tuple(np.argwhere(gameState == 2)[0])

def PosOfBoxes(gameState):
    """Tra ve tuple cac vi tri hop: ca hop chua vao dich (3) lan da vao dich (5)"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5)))

def PosOfWalls(gameState):
    """Tra ve tuple cac vi tri tuong (gia tri = 1)"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1))

def PosOfGoals(gameState):
    """Tra ve tuple cac vi tri dich: ca o dich trong (4) lan da co hop (5)"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5)))



def isEndState(posBox):
    return sorted(posBox) == sorted(posGoals)

def isLegalAction(action, posPlayer, posBox):
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper():
      
        x1, y1 = xPlayer + 2*action[0], yPlayer + 2*action[1]
    else:
       
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    
    return (x1, y1) not in posBox + posWalls

def legalActions(posPlayer, posBox):
    
    allActions = [[-1, 0, 'u', 'U'],   
                  [ 1, 0, 'd', 'D'],  
                  [ 0,-1, 'l', 'L'],   
                  [ 0, 1, 'r', 'R']]   
    xPlayer, yPlayer = posPlayer
    result = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]   
        if (x1, y1) in posBox:
            action.pop(2)   
        else:
            action.pop(3)   
        if isLegalAction(action, posPlayer, posBox):
            result.append(action)   
    return tuple(tuple(x) for x in result)   

def updateState(posPlayer, posBox, action):
 
    xPlayer, yPlayer = posPlayer
    newPosPlayer = [xPlayer + action[0], yPlayer + action[1]]
    posBox = [list(x) for x in posBox]  
    if action[-1].isupper():
        
        posBox.remove(newPosPlayer)                                       
        posBox.append([xPlayer + 2*action[0], yPlayer + 2*action[1]])    
    posBox = tuple(tuple(x) for x in posBox)   
    return tuple(newPosPlayer), posBox

def isFailed(posBox):
    
    rotatePattern = [[0,1,2,3,4,5,6,7,8],        
                     [2,5,8,1,4,7,0,3,6],        
                     [0,1,2,3,4,5,6,7,8][::-1],  
                     [2,5,8,1,4,7,0,3,6][::-1]]  
    flipPattern   = [[2,1,0,5,4,3,8,7,6],        
                     [0,3,6,1,4,7,2,5,8],        
                     [2,1,0,5,4,3,8,7,6][::-1], 
                     [0,3,6,1,4,7,2,5,8][::-1]]  
    allPattern = rotatePattern + flipPattern     

    for box in posBox:
        if box not in posGoals:   
            board = [
                (box[0]-1, box[1]-1), (box[0]-1, box[1]), (box[0]-1, box[1]+1), 
                (box[0],   box[1]-1), (box[0],   box[1]), (box[0],   box[1]+1),  
                (box[0]+1, box[1]-1), (box[0]+1, box[1]), (box[0]+1, box[1]+1), 
            ]
            for pattern in allPattern:
                nb = [board[i] for i in pattern]   
                if nb[1] in posWalls and nb[5] in posWalls:
                    return True  
                elif nb[1] in posBox and nb[2] in posWalls and nb[5] in posWalls:
                    return True   
                elif nb[1] in posBox and nb[2] in posWalls and nb[5] in posBox:
                    return True 
                elif nb[1] in posBox and nb[2] in posBox and nb[5] in posBox:
                    return True  
                elif (nb[1] in posBox and nb[6] in posBox and
                      nb[2] in posWalls and nb[3] in posWalls and nb[8] in posWalls):
                    return True   
    return False   


# ============================================================
#  HEURISTIC CHO A*
# ============================================================

def heuristic(posPlayer, posBox):
    """
    Ham uoc luong chi phi con lai h(n) cho A*.

    Gom 2 phan:
      Phan 1: Tong khoang cach Manhattan tu moi hop den vi tri dich gan nhat.
      Phan 2: Khoang cach Manhattan tu player den hop chua vao dich gan nhat.

    Ham nay la ADMISSIBLE (khong bao gio uoc luong cao hon chi phi thuc su)
    vi khoang cach Manhattan la can duoi cua so buoc can thiet.
    Do do A* su dung ham nay se dam bao tra ve loi giai toi uu.
    """
    h = 0   # gia tri heuristic, khoi tao = 0

    # --- Phan 1: tong min-Manhattan(hop -> dich) ---
    for box in posBox:
        if box not in posGoals:   # chi tinh cho hop chua vao dich
            # Khoang cach Manhattan den dich gan nhat cua hop nay
            # Manhattan = |delta_row| + |delta_col|
            h += min(abs(box[0] - g[0]) + abs(box[1] - g[1]) for g in posGoals)

    # --- Phan 2: khoang cach player -> hop chua vao dich gan nhat ---
    free_boxes = [b for b in posBox if b not in posGoals]   # loc cac hop chua vao dich
    if free_boxes:
        # Khoang cach Manhattan ngan nhat tu player den mot trong cac hop chua vao dich
        h += min(abs(posPlayer[0] - b[0]) + abs(posPlayer[1] - b[1])
                 for b in free_boxes)

    return h   # tra ve gia tri heuristic tong hop


# ============================================================
#  HAM CHI PHI CHO UCS VA A*
# ============================================================

def cost(actions):
    """
    Ham chi phi g(n): dem so buoc WALK trong chuoi hanh dong.
    - Walk = ky tu chu thuong (u/d/l/r): player di chuyen, khong day hop.
    - Push = ky tu chu hoa (U/D/L/R): player day hop.
    Chi phi chi tinh buoc walk, khong tinh buoc push.
    """
    return len([x for x in actions if x.islower()])


# ============================================================
#  THUAT TOAN 1: DEPTH-FIRST SEARCH (DFS)
# ============================================================

def depthFirstSearch(gameState):
    """
    Tim kiem theo chieu sau (DFS).
    Su dung ngan xep LIFO (deque.pop tu cuoi).
    Khong dam bao tim duoc loi giai toi uu.
    """
    global nodes_expanded
    nodes_expanded = 0   # reset bien dem nut

    # Xac dinh trang thai khoi dau: vi tri player va cac hop
    startState  = (PosOfPlayer(gameState), PosOfBoxes(gameState))

    # frontier: ngan xep luu cac duong di (moi phan tu la list cac trang thai)
    # Khoi tao voi mot duong di chi gom trang thai ban dau
    frontier    = collections.deque([[startState]])

    # actions: ngan xep luu chuoi hanh dong tuong ung voi tung duong di trong frontier
    # [0] la sentinel (gia tri gia de bo qua khi tra ket qua)
    actions     = [[0]]

    exploredSet = set()   # tap cac trang thai da duoc tham (tranh lap)
    temp        = []      # luu ket qua cuoi cung (chuoi hanh dong)

    while frontier:   # lap cho den khi frontier rong hoac tim duoc loi giai
        node        = frontier.pop()       # lay duong di tu DINH ngan xep (LIFO = DFS)
        node_action = actions.pop()        # lay chuoi hanh dong tuong ung

        if isEndState(node[-1][-1]):       # kiem tra trang thai cuoi cua duong di co la dich khong
            temp += node_action[1:]        # luu chuoi hanh dong (bo phan tu sentinel [0] dau tien)
            break                          # tim duoc loi giai, thoat vong lap

        if node[-1] not in exploredSet:              # neu trang thai hien tai chua duoc tham
            exploredSet.add(node[-1])                # danh dau la da tham
            nodes_expanded += 1                      # tang so nut duoc mo rong

            for action in legalActions(node[-1][0], node[-1][1]):   # duyet tung hanh dong hop le
                p2, b2 = updateState(node[-1][0], node[-1][1], action)   # tinh trang thai ke tiep
                if isFailed(b2):                     # neu trang thai ke tiep la deadlock -> bo qua
                    continue
                frontier.append(node + [(p2, b2)])             # them duong di moi vao ngan xep
                actions.append(node_action + [action[-1]])     # them hanh dong tuong ung

    return temp   # tra ve chuoi hanh dong (rong neu khong tim duoc loi giai)


# ============================================================
#  THUAT TOAN 2: BREADTH-FIRST SEARCH (BFS)
# ============================================================

def breadthFirstSearch(gameState):
    """
    Tim kiem theo chieu rong (BFS).
    Su dung hang doi FIFO (deque.popleft tu dau).
    Dam bao tim duoc loi giai co so buoc di chuyen it nhat (toi uu theo so buoc).
    """
    global nodes_expanded
    nodes_expanded = 0   # reset bien dem nut

    # Xac dinh trang thai khoi dau
    startState  = (PosOfPlayer(gameState), PosOfBoxes(gameState))

    # frontier: hang doi FIFO luu cac duong di
    # Phan tu moi duoc them vao CUOI, lay ra tu DAU -> BFS
    frontier    = collections.deque([[startState]])

    # actions: hang doi FIFO luu chuoi hanh dong tuong ung
    actions     = collections.deque([[0]])   # [0] la sentinel

    exploredSet = set()   # tap trang thai da duoc tham
    temp        = []      # luu ket qua

    while frontier:   # lap cho den khi tim duoc loi giai hoac frontier rong
        node        = frontier.popleft()       # lay duong di tu DAU hang doi (FIFO = BFS)
        node_action = actions.popleft()        # lay chuoi hanh dong tuong ung

        if isEndState(node[-1][-1]):           # kiem tra co phai trang thai dich khong
            temp += node_action[1:]            # luu ket qua, bo sentinel
            break                              # thoat ngay khi tim duoc loi giai toi uu

        if node[-1] not in exploredSet:        # neu trang thai chua tham
            exploredSet.add(node[-1])          # danh dau da tham
            nodes_expanded += 1               # tang so nut mo rong

            for action in legalActions(node[-1][0], node[-1][1]):   # duyet hanh dong hop le
                p2, b2 = updateState(node[-1][0], node[-1][1], action)   # tinh trang thai moi
                if isFailed(b2):              # bo qua neu la deadlock
                    continue
                frontier.append(node + [(p2, b2)])             # them vao CUOI hang doi
                actions.append(node_action + [action[-1]])     # them hanh dong tuong ung

    return temp   # chuoi hanh dong toi uu theo so buoc


# ============================================================
#  THUAT TOAN 3: UNIFORM COST SEARCH (UCS)
# ============================================================

def uniformCostSearch(gameState):
    """
    Tim kiem chi phi dong nhat (UCS).
    Su dung hang doi uu tien min-heap, mo rong nut co chi phi g(n) thap nhat.
    Ham chi phi g(n) = cost() = so buoc WALK (khong tinh buoc push).
    Dam bao tim duoc loi giai toi uu theo ham chi phi nay.
    """
    global nodes_expanded
    nodes_expanded = 0   # reset bien dem nut

    # Xac dinh trang thai khoi dau
    startState  = (PosOfPlayer(gameState), PosOfBoxes(gameState))

    # frontier: hang doi uu tien, priority = g(n) = chi phi tich luy
    frontier    = PriorityQueue()
    frontier.push([startState], 0)   # trang thai khoi dau co chi phi = 0

    # actions: hang doi uu tien luu chuoi hanh dong tuong ung
    actions     = PriorityQueue()
    actions.push([0], 0)   # [0] la sentinel, priority = 0

    exploredSet = set()   # tap trang thai da duoc tham
    temp        = []      # luu ket qua

    while not frontier.isEmpty():   # lap cho den khi frontier rong
        node        = frontier.pop()    # lay nut co chi phi g(n) THAP NHAT
        node_action = actions.pop()     # lay chuoi hanh dong tuong ung

        if isEndState(node[-1][-1]):    # kiem tra dich
            temp += node_action[1:]    # luu ket qua, bo sentinel
            break                      # loi giai toi uu da tim duoc

        if node[-1] not in exploredSet:             # neu trang thai chua tham
            exploredSet.add(node[-1])               # danh dau da tham
            nodes_expanded += 1                     # tang so nut mo rong

            for action in legalActions(node[-1][0], node[-1][1]):   # duyet hanh dong hop le
                p2, b2     = updateState(node[-1][0], node[-1][1], action)   # tinh trang thai moi
                if isFailed(b2):                    # bo qua deadlock
                    continue
                new_action = node_action + [action[-1]]    # chuoi hanh dong moi
                new_cost   = cost(new_action[1:])          # g(n) moi = so buoc walk tich luy
                frontier.push(node + [(p2, b2)], new_cost) # them vao frontier voi priority = g(n)
                actions.push(new_action, new_cost)         # them hanh dong tuong ung

    return temp   # chuoi hanh dong toi uu theo chi phi walk


# ============================================================
#  THUAT TOAN 4: A* SEARCH
# ============================================================

def aStarSearch(gameState):
    """
    Tim kiem A* (A Star).

    Danh gia moi nut bang: f(n) = g(n) + h(n)
      - g(n): chi phi THUC SU da di = cost() = so buoc walk
      - h(n): uoc luong chi phi CON LAI = heuristic()

    A* mo rong nut co f(n) THAP NHAT truoc.
    Nho co h(n) huong dan, A* thuong mo rong it nut hon UCS
    ma van dam bao loi giai toi uu (vi heuristic admissible).
    """
    global nodes_expanded
    nodes_expanded = 0   # reset bien dem nut

    # Xac dinh trang thai khoi dau
    beginPlayer = PosOfPlayer(gameState)
    beginBox    = PosOfBoxes(gameState)
    startState  = (beginPlayer, beginBox)

    # Tinh gia tri heuristic cho trang thai khoi dau: h(s0)
    h0 = heuristic(beginPlayer, beginBox)

    # frontier: hang doi uu tien, priority = f(n) = g(n) + h(n)
    frontier = PriorityQueue()
    frontier.push([startState], h0)   # f(s0) = g=0 + h0; priority = h0

    # actions: hang doi uu tien luu chuoi hanh dong tuong ung voi frontier
    actions  = PriorityQueue()
    actions.push([0], h0)   # [0] la sentinel, cung priority = h0

    exploredSet = set()   # tap trang thai da duoc tham (closed set)
    temp        = []      # luu ket qua cuoi cung

    while not frontier.isEmpty():   # lap cho den khi tim duoc loi giai hoac frontier rong
        node        = frontier.pop()    # lay nut co f(n) = g + h THAP NHAT
        node_action = actions.pop()     # lay chuoi hanh dong tuong ung

        if isEndState(node[-1][-1]):    # kiem tra xem co phai trang thai dich khong
            temp += node_action[1:]    # luu chuoi hanh dong, bo sentinel [0]
            break                      # thoat: loi giai toi uu da tim duoc

        if node[-1] not in exploredSet:              # neu trang thai chua duoc tham
            exploredSet.add(node[-1])                # danh dau da tham (them vao closed set)
            nodes_expanded += 1                      # tang so nut duoc mo rong

            curPlayer, curBox = node[-1]             # lay vi tri player va cac hop hien tai

            for action in legalActions(curPlayer, curBox):       # duyet tung hanh dong hop le
                p2, b2 = updateState(curPlayer, curBox, action)  # tinh trang thai ke tiep
                if isFailed(b2):                     # bo qua neu la deadlock
                    continue

                new_action = node_action + [action[-1]]   # them hanh dong moi vao chuoi
                g = cost(new_action[1:])                  # g(n): chi phi thuc su = so buoc walk
                h = heuristic(p2, b2)                     # h(n): uoc luong chi phi con lai
                f = g + h                                 # f(n): gia tri danh gia tong the

                frontier.push(node + [(p2, b2)], f)       # them trang thai moi vao frontier voi priority = f
                actions.push(new_action, f)               # them chuoi hanh dong tuong ung

    return temp   # tra ve chuoi hanh dong toi uu



def get_move(layout, player_pos, method):
    """
    Ham duoc goi tu game.py de giai mot level.
    Nhan vao layout ban do va vi tri player, tra ve:
      (result, elapsed_solve, nodes_expanded)
      - result        : chuoi hanh dong de giai level (list cac ky tu)
      - elapsed_solve : thoi gian chay thuat toan (don vi: giay)
      - nodes_expanded: so nut da duoc mo rong trong qua trinh tim kiem
    method: 'dfs' | 'bfs' | 'ucs' | 'astar'
    """
    global posWalls, posGoals, nodes_expanded
    nodes_expanded = 0   
    t0 = time.time()   
 
 
    gameState = transferToGameState2(layout, player_pos)
    posWalls  = PosOfWalls(gameState)    
    posGoals  = PosOfGoals(gameState)    

    if   method == 'dfs':   result = depthFirstSearch(gameState)
    elif method == 'bfs':   result = breadthFirstSearch(gameState)
    elif method == 'ucs':   result = uniformCostSearch(gameState)
    elif method == 'astar': result = aStarSearch(gameState)
    else: raise ValueError(f'Invalid method: {method}')
 
    t1 = time.time()              
    elapsed_solve = t1 - t0       
    n = len(result) if result else 0
 
    
    print(f'[{method.upper():5s}] {n:4d} steps | {elapsed_solve:7.2f}s | {nodes_expanded} nodes expanded')
 
   
    return result, elapsed_solve, nodes_expanded