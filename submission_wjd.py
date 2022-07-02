import numpy as np

max_layer = 3

def get_available_attempt(state_map, board_width, board_height):
    state_map_ex = np.zeros((board_width+4, board_height+4))
    state_map_ex[2:board_width+2, 2:board_height+2] = state_map.copy()

    chess_around = (state_map_ex[0:-4, 0:-4]                            + state_map_ex[0:-4, 2:-2]                            + state_map_ex[0:-4, 4:]+
                    state_map_ex[1:-3, 0:-4] + state_map_ex[1:-3, 1:-3] + state_map_ex[1:-3, 2:-2] + state_map_ex[1:-3, 3:-1] + state_map_ex[1:-3, 4:]+
                    state_map_ex[2:-2, 0:-4] + state_map_ex[2:-2, 1:-3]                            + state_map_ex[2:-2, 3:-1] + state_map_ex[2:-2, 4:]+
                    state_map_ex[3:-1, 0:-4] + state_map_ex[3:-1, 1:-3] + state_map_ex[3:-1, 2:-2] + state_map_ex[3:-1, 3:-1] + state_map_ex[3:-1, 4:]+
                    state_map_ex[4:, 0:-4]                              + state_map_ex[4:, 2:-2]                              + state_map_ex[4:, 4:])

    available_state_map = (chess_around>0) & (state_map==0)
    available_attempt = np.where(available_state_map==True)

    if len(available_attempt[0])==0:
        return np.array([[board_width//2], [board_height//2]])

    return available_attempt
    # where chess is available to put
    # there is chess(whatever it belongs) within distance of 2


def get_score(state_map, attempt_x, attempt_y, player_idx):

    def get_diag_line(state_map, attempt_x, attempt_y):
        tmp=[]
        stx, sty, enx, eny= 0, 0, 0, 0
        if (attempt_x<5 or attempt_y<5):
            stx, sty = attempt_x-min(attempt_x, attempt_y), attempt_y-min(attempt_x, attempt_y)
        else:
            stx, sty = attempt_x-5, attempt_y-5
        if (attempt_x>9 or attempt_y>9):
            enx, eny = attempt_x+min(15-attempt_x, 15-attempt_y), attempt_y+min(15-attempt_x, 15-attempt_y)
        else:
            enx, eny = attempt_x+6, attempt_y+6
        for i,j in zip(range(stx, enx), range(sty, eny)):
            tmp.append(state_map[i][j])
        return str(tmp)

    line = []
    line.append(str(state_map[attempt_x, max(0, attempt_y-5):min(15, attempt_y+6)]).replace(',','').replace(' ',''))
    line.append(str(state_map[max(0, attempt_x-5):min(15, attempt_x+6), attempt_y]).replace(',','').replace(' ',''))
    line.append(get_diag_line(state_map, attempt_x, attempt_y))
    line.append(get_diag_line(np.fliplr(state_map), attempt_x, 14-attempt_y))
    # line[row, column, diag, diag-rev] of nextby 9 blank

    score = 0
    chess_type = [[], ['11111', '011110', '1111', '11101', '11011', '10111', '01110', '111', '1011', '1101', '0110', '11', '101'],
                    ['22222', '022220', '2222', '22202', '22022', '20222', '02220', '222', '2022', '2202', '0220', '22', '202']]

    for i in range(4):
        if (chess_type[player_idx][0] in line[i]):
            return (score, True)
        elif (chess_type[player_idx][1] in line[i]):
            score += 100000
        elif ((chess_type[player_idx][2] in line[i]) or (chess_type[player_idx][3] in line[i]) or (chess_type[player_idx][4] in line[i]) 
            or (chess_type[player_idx][5] in line[i])):
            score += 10000
        elif (chess_type[player_idx][6] in line[i]):
            score += 8000
        elif ((chess_type[player_idx][7] in line[i]) or (chess_type[player_idx][8] in line[i]) or (chess_type[player_idx][9] in line[i])):
            score += 1000
        elif (chess_type[player_idx][10] in line[i]):
            score += 100
        elif (chess_type[player_idx][11] in line[i]) or (chess_type[player_idx][12] in line[i]):
            score += 20
        else:
            score += 5

    return (score, False)


def max_decision(state_map, board_width, board_height, chess_player_idx, depth):
    # print('max', depth)

    available_attempt = get_available_attempt(state_map, board_width, board_height)
    score = np.zeros(len(available_attempt[0]))
    
    idx = 0
    for i in range(len(available_attempt[0])):
        state_map[available_attempt[0][i]][available_attempt[1][i]] = chess_player_idx
        score[i], winning = get_score(state_map.copy(), available_attempt[0][i], available_attempt[1][i], chess_player_idx)
        score[i] *= (0.8**depth)
        if (winning==True):
            if (depth>0):
                return (score[i], True)
            else:
                return (available_attempt[0][i], available_attempt[1][i])
        if (depth<=max_layer):
            score_next_layer, losing = min_decision(state_map, board_width, board_height, 3-chess_player_idx, depth)
            if (losing==True):
                state_map[available_attempt[0][i]][available_attempt[1][i]] = 0
                continue
            score[i] += score_next_layer
        state_map[available_attempt[0][i]][available_attempt[1][i]] = 0
        if (score[i]>score[idx]):
            idx = i

    if (depth>0):
        return (score[idx], False)
    else:
        return (available_attempt[0][idx], available_attempt[1][idx])
    

def min_decision(state_map, board_width, board_height, chess_player_idx, depth):
    # print('min', depth)

    available_attempt = get_available_attempt(state_map, board_width, board_height)
    score = np.zeros(len(available_attempt[0]))
    
    idx = 0
    for i in range(len(available_attempt[0])):
        state_map[available_attempt[0][i]][available_attempt[1][i]] = chess_player_idx
        score[i], losing = get_score(state_map.copy(), available_attempt[0][i], available_attempt[1][i], chess_player_idx)
        score[i] *= (0.8**depth)*(-0.6)
        if (losing==True):
            return (0, True)
        if (depth<max_layer):
            score_next_layer, winning = max_decision(state_map, board_width, board_height, 3-chess_player_idx, depth+1)
            if (winning==True):
                state_map[available_attempt[0][i]][available_attempt[1][i]] = 0
                continue
            score[i] += score_next_layer
        state_map[available_attempt[0][i]][available_attempt[1][i]] = 0
        if (score[i]>score[idx]):
            idx = i

    return (score[idx], False)


def my_controller(observation, action_space, is_act_continuous=False):
    board_width = observation['board_width']
    board_height = observation['board_height']
    chess_player_idx = observation['chess_player_idx']
    state_map = np.array(observation['state_map'])
    state_map = state_map[:,:,0]

    output = [[0]*15, [0]*15]
    answer_x, answer_y = max_decision(state_map, board_width, board_height, chess_player_idx, depth=0)
    output[0][answer_x] = 1
    output[1][answer_y] = 1
    return output