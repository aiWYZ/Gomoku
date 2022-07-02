import numpy as np

board_width = 0
board_height = 0
state_map = []
chess_player_idx = 0
opponent_idx = 0
max_layer = 2
ans = [7, 7]
chess_type = [[], ['11111', '011110', '1111', '11101', '11011', '10111', '01110', '111', '1011', '1101', '0110', '11', '101'],
    ['22222', '022220', '2222', '22202', '22022', '20222', '02220', '222', '2022', '2202', '0220', '22', '202']]

def get_available_attempt():
    state_map_expand = np.zeros((board_width+2, board_height+2))
    state_map_expand[1:board_width+1, 1:board_height+1] = state_map.copy()
    chess_around = (state_map_expand[0:-2, 0:-2] + state_map_expand[0:-2, 1:-1] + state_map_expand[0:-2, 2:]+
                    state_map_expand[1:-1, 0:-2]                                + state_map_expand[1:-1, 2:]+
                    state_map_expand[2:  , 0:-2] + state_map_expand[2:  , 1:-1] + state_map_expand[2:,   2:])

    available_state_map = (chess_around>0) & (state_map==0)
    available_attempt = np.where(available_state_map==True)
    if len(available_attempt[0])==0:
        return [[7,7]]

    att = []
    for i in range(len(available_attempt[0])):
        att.append([available_attempt[0][i], available_attempt[1][i]])
    return att
    """
    周围一格内有棋子才去考虑
    返回一个n*2的list，表示可能可以落子的坐标
    """


def get_score(s, player_idx):
    if (chess_type[player_idx][0] in s):
        return 1e7
    elif (chess_type[player_idx][1] in s):
        return 10000
    elif ((chess_type[player_idx][2] in s) or (chess_type[player_idx][3] in s) or (chess_type[player_idx][4] in s) 
        or (chess_type[player_idx][5] in s)):
        return 1000
    elif (chess_type[player_idx][6] in s):
        return 500
    elif ((chess_type[player_idx][7] in s) or (chess_type[player_idx][8] in s) or (chess_type[player_idx][9] in s)):
        return 200
    elif (chess_type[player_idx][10] in s):
        return 100
    elif (chess_type[player_idx][11] in s) or (chess_type[player_idx][12] in s):
        return 20
    else:
        return 1
    """
    简单粗暴，帮我想想其他棋形可能长什么样
    """


def evaluate():
    def evaluate_(idx):
        score = 0
        for i in range(board_width):
            line = str(state_map[i,:]).replace(',','').replace(' ','')
            score += get_score(line, idx)
            line = str(state_map[:, i]).replace(',','').replace(' ','')
            score += get_score(line, idx)

        state_map_fliplr = np.fliplr(state_map)
        for i in range(-14, 15):
            line = str(np.diagonal(state_map, offset=i)).replace(',','').replace(' ','')
            score += get_score(line, idx)
            line = str(np.diagonal(state_map_fliplr, offset=i)).replace(',','').replace(' ','')
            score += get_score(line, idx)
        return score

    score = 0
    score += evaluate_(chess_player_idx)
    score -= evaluate_(opponent_idx)*0.1
    return score
    """
    对整个棋盘打分
    横/竖/主对角线/副对角线
    +自己得分-对手得分
    """


def is_winning():
    def check(win_check):
        for i in range(board_width):
            if ((win_check in str(state_map[i,:]).replace(',','').replace(' ','')) or
                (win_check in str(state_map[:, i]).replace(',','').replace(' ',''))):
                return True

        state_map_fliplr = np.fliplr(state_map)
        for i in range(-10, 11):
            if ((win_check in str(np.diagonal(state_map, offset=i)).replace(',','').replace(' ',''))
                or (win_check in str(np.diagonal(state_map_fliplr, offset=i)).replace(',','').replace(' ',''))):
                return True

    if (check('11111')):
        return True
    if (check('22222')):
        return True
    return False


def maxmin_decision(depth, is_opponent, alpha, beta):
    if (depth==max_layer) or is_winning():
        return evaluate()

    available_attempt = get_available_attempt()
    global ans

    if (is_opponent):
        score = 1e9
        for step in available_attempt:
            state_map[step[0]][step[1]] = opponent_idx
            score = min(score, maxmin_decision(depth+1, False, alpha, beta))
            state_map[step[0]][step[1]] = 0
            if (score<beta):
                beta = score
                if (alpha>=beta):
                    return alpha
        return beta
        # 对手落子 挑尽可能小的 score取min
        # 返回的值是我们在上一层向这一层挑（呃呃
        # 返回的值尽可能大
        # 如果对手在这一支路挑出来的分数已经不大于我们在其他支路的得分 beta<=alpha（这里的支路指从上一层扩散出去的）
        # 就直接结束 因为如果我们挑了这条路 对手一定选当前这个beta让我们得到的分数变小

    else:
        score = -1e9
        target = []
        for step in available_attempt:
            state_map[step[0]][step[1]] = chess_player_idx
            tmpscore = maxmin_decision(depth+1, True, alpha, beta)
            state_map[step[0]][step[1]] = 0
            if (tmpscore>score):
                score = tmpscore
                target = step
            if (score>alpha):
                alpha = score
                if (alpha>=beta):
                    if (depth==0):
                        ans = step
                    return beta
        if (depth==0):
            ans = target
        return alpha
        # 我们落子 挑尽可能大的 score取max
        # 对手挑我们 返回值希望尽可能小
        # 如果我们在当前支路返回的分数已经不小于对手在其他支路的得分 对手一定不会挑当前这条支路

    """
    1.如果到最大迭代次数或者出现有人赢了 直接开始算分数
    2.获取可能可以落子的坐标
    3.对每个坐标枚举
    """
    

def my_controller(observation, action_space, is_act_continuous=False):
    global board_width
    global board_height
    global chess_player_idx
    global opponent_idx
    global state_map
    board_width = observation['board_width']
    board_height = observation['board_height']
    chess_player_idx = observation['chess_player_idx']
    state_map = np.array(observation['state_map'])
    state_map = state_map[:,:,0]
    opponent_idx = 3-chess_player_idx

    final_score = maxmin_decision(depth=0, is_opponent=False, alpha=-1e9, beta=1e9)
    output = [[0]*15, [0]*15]
    output[0][ans[0]] = 1
    output[1][ans[1]] = 1
    return output