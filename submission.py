from time import time
import numpy as np

ans = [7,7]

posvalue = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
			[1,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
			[1,2,3,3,3,3,3,3,3,3,3,3,3,2,1],
			[1,2,3,4,4,4,4,4,4,4,4,4,3,2,1],
			[1,2,3,4,5,5,5,5,5,5,5,4,3,2,1],
			[1,2,3,4,5,6,6,6,6,6,5,4,3,2,1],
			[1,2,3,4,5,6,7,7,7,6,5,4,3,2,1],
			[1,2,3,4,5,6,7,8,7,6,5,4,3,2,1],
			[1,2,3,4,5,6,7,7,7,6,5,4,3,2,1],
			[1,2,3,4,5,6,6,6,6,6,5,4,3,2,1],
			[1,2,3,4,5,5,5,5,5,5,5,4,3,2,1],
			[1,2,3,4,4,4,4,4,4,4,4,4,3,2,1],
			[1,2,3,3,3,3,3,3,3,3,3,3,3,2,1],
			[1,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
			[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

def get_score(board, pos, idx):
	dire = ((-1,-1),(-1,0),(-1,1),(0,1))
	x,y = pos[0],pos[1]
	score = 0
	Chong_4 = 0
	Huo_3 = 0
	for dir in dire:
		s = '1'
		xx,yy = x,y
		for j in range(4):
			xx += dir[0]
			yy += dir[1]
			if (in_bound((xx,yy))):
				if (board[xx][yy]==idx):
					s = ''.join((s, '1'))
				elif (board[xx][yy]==0):
					s = ''.join((s, '0'))
				else:
					s = ''.join((s, '2'))
			else:
				break
		xx,yy = x,y
		for j in range(4):
			xx -= dir[0]
			yy -= dir[1]
			if (in_bound((xx,yy))):
				if (board[xx][yy]==idx):
					s = ''.join(('1', s))
				elif (board[xx][yy]==0):
					s = ''.join(('0', s))
				else:
					s = ''.join(('2', s))
			else:
				break
		
		if (s.find('11111')!=-1):
			score += 500000000
			continue
		if (s.find('011110')!=-1):
			score += 1000000
			continue
		for tp in ('011112', '211110', '10111', '11101','11011'):
			if (s.find(tp)!=-1):
				Chong_4 += 1
				break
		if (s.find('01110')!=-1):
			Huo_3 += 1
		for tp in ['1011', '1101']:
			if (s.find(tp)!=-1):
				score += 7000
				break
		for tp in ('001112', '211100', '010112', '211010', '011012',
					'210110', '10011', '11001', '10101', '2011102'):
			if (s.find(tp)!=-1):
				score += 500
				break
		for tp in ('001100', '01010', '1001'):
			if (s.find(tp)!=-1):
				score += 50
				break


	if (Chong_4+Huo_3>=2):
		score += 100000
	elif (Chong_4>=1 or Huo_3>=1):
		score += 10000
	
	return score*posvalue[x][y]


def evaluate(board, idx):
	my_score, oppo_score = 0, 0
	for i in range(15):
		for j in range(15):
			if (board[i][j]==idx):
				my_score += get_score(board, (i,j), idx)
			elif (board[i][j]==3-idx):
				oppo_score += get_score(board, (i,j), 3-idx)
	return 0.1*my_score - oppo_score

def in_bound(pos):
	return ((pos[0]>=0) and (pos[0]<15) and (pos[1]>=0) and (pos[1]<15))

def has_neighbor(pos, board):
	dire = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
	for dir in dire:
		x,y = pos[0]+dir[0], pos[1]+dir[1]
		if (in_bound((x,y))):
			if (board[x][y]>0):
				return True
	return False

def PointScore(board, pos, idx):
	board[pos[0]][pos[1]] = idx
	my_score = get_score(board, pos, idx)
	board[pos[0]][pos[1]] = 3-idx
	oppo_score = get_score(board, pos, 3-idx)
	board[pos[0]][pos[1]] = 0
	return my_score, oppo_score

def get_steps(board, idx):
	five, my_4, oppo_4, my_s4, oppo_s4 = [],[],[],[],[]
	steps = []
	for i in range(15):
		for j in range(15):
			if (board[i][j]==0 and has_neighbor((i,j), board)):
				my_score, oppo_score = PointScore(board, (i,j), idx)
				if (my_score>=1000000 or oppo_score>=1000000):
					five.append((i,j))
				elif (my_score>=100000):
					my_4.append((i,j))
				elif (oppo_score>=100000):
					oppo_4.append((i,j))
				elif (my_score>=10000):
					my_s4.append((i,j))
				elif (oppo_score>=10000):
					oppo_s4.append((i,j))
				steps.append((max(my_score,oppo_score),(i,j)))
	if (len(five)>0):
		return five
	if (len(my_4)>0):
		return my_4
	if (len(oppo_4)>0):
		if (len(my_s4)==0):
			return oppo_4+my_s4

	steps.sort(reverse=True)
	tmpsteps = []
	for i in range(min(6,len(steps))):
		tmpsteps.append(steps[i][1])
	return tmpsteps

	# 此处参考https://blog.csdn.net/marble_xu/article/details/90726034

def minmax_search(board, idx, depth, alpha, beta):
	if (depth==2):
		return evaluate(board, idx)
	steps = get_steps(board, idx)
	for (i,j) in steps:
		board[i][j] = idx
		score = minmax_search(board, 3-idx, depth+1, alpha, beta)
		board[i][j] = 0
		if (depth%2==0):
			if (score>alpha):
				alpha=score
				global ans
				ans = (i,j)
			if (alpha>=beta):
				return alpha
		else:
			if (score<beta):
				beta = score
			if (alpha>=beta):
				return beta
	if (depth%2==0):
		return alpha
	else:
		return beta


def my_controller(observation, action_space, is_act_continuous=False):
	time1 = time()
	board = np.array(observation['state_map'])
	board = board[:,:,0]
	my_idx = observation['chess_player_idx']
	minmax_search(board, my_idx, 0, -1e9, 1e9)
	global ans
	output = [[0 for i in range(15)] for j in range(2)]
	output[0][ans[0]] = 1
	output[1][ans[1]] = 1
	time2 = time()
	print(time2-time1)
	return output