from gurobipy import *

def modeling(m, x, v):
    # for i in range(len(x)):
    #     m.addVar(vtype=GRB.BINARY, name=f"x{i}")
    # m.update()
    
    expr = LinExpr(v[:-2], x)
    expr.addConstant(v[-2])
    if v[-1] == ">=":
        m.addConstr(expr >= 0)
    else:
        m.addConstr(expr == 0)

def addConstrPerm(m, x, y, p):
    for j in range(64):
        m.addConstr(x[p[j]] == y[j])

def addConstrSbox(m, x, y, listIneq):
    for ineq in listIneq:
        modeling(m, x+y, ineq)

def genModelPresent(nbRounds):
    m = Model()
    m.Params.OutputFlag = 0 #Disable gurobi solver output
    ineqSbox = [[1, 1, 1, 1, -1, -1, -1, -1, 0, '>='],
                [-4, -2, -2, -2, -3, 1, 4, 1, 7, '>='],
                [-2, 0, 0, 0, 2, -1, -1, -1, 3, '>='],
                [0, -1, -1, -2, 2, 3, 3, 3, 0, '>='],
                [1, 1, 1, 1, -2, 1, -2, -2, 1, '>='],
                [1, 0, 0, 0, -1, -2, -1, 1, 2, '>='],
                [-2, -1, -1, 0, -1, 1, 0, 1, 3, '>='],
                [0, 0, 0, 0, 1, -1, 1, -1, 1, '>='],
                [0, -2, -2, 0, 2, 1, -1, 1, 3, '>='],
                [-1, 0, -1, 0, 1, 2, 2, 2, 0, '>=']]
    p = [0, 16, 32, 48, 1, 17, 33, 49, 2, 18, 34, 50, 3, 19, 35, 51,
        4, 20, 36, 52, 5, 21, 37, 53, 6, 22, 38, 54, 7, 23, 39, 55,
        8, 24, 40, 56, 9, 25, 41, 57, 10, 26, 42, 58, 11, 27, 43, 59,
        12, 28, 44, 60, 13, 29, 45, 61, 14, 30, 46, 62, 15, 31, 47, 63]
    x = [[m.addVar(vtype=GRB.BINARY, name=f"x{i}_{j}") for j in range(64)] for i in range(nbRounds+1)] #some gurobi variables (r+1) x, each wth 64 variables
    y = [[m.addVar(vtype=GRB.BINARY, name = f"y{i}_{j}") for j in range(64)] for i in range(nbRounds)] #some gurobi variables r y, each with 64 variables
    m.update()
    for r in range(nbRounds):
        #Add Constraints corresponding to x[r] --Sbox--> y[r]
        for i in range(16):
            #create tmpx = 4 input vars of the i-th sbox
            tmpx = [x[r][4*i+j] for j in range(4)]
            #create tmpy = 4 output vars of the i-th sbox
            tmpy = [y[r][4*i+j] for j in range(4)]
            addConstrSbox(m,tmpx,tmpy,ineqSbox)

        #Add Constraints corresponding to y[r] --P--> x[r+1]
        addConstrPerm(m, x[r+1], y[r], p)
        
    return m, x, y 

def getOutputProperty():
	#Get the model
    #Fix the input to input
    #compute stringoutput as below
    #return stringoutput

    nbRounds = 5
    for i in range(1, 65):
        inp = (1 << i) - 1
        inp = [int(n) for n in bin(inp)[2:].zfill(64)] #convert to integers
        inp.reverse()
        existTrail = [None for _ in range(64)]
        for j in range(64):
                output = 1 << j
                output = [int(n) for n in bin(output)[2:].zfill(64)] #convert to integers
                output.reverse()
                m, x, y = genModelPresent(nbRounds)
                for k in range(64):
                    m.addConstr(x[0][k] == inp[k]) #x[0][k] == inp[k]
                    m.addConstr(x[nbRounds][k] == output[k])
                m.optimize()
                if m.Status == GRB.OPTIMAL:
                    existTrail[j] = True
                else:
                    existTrail[j] = False
        inp = "".join(str(n) for n in inp)
        print(f"For input {inp} ({i})")
        stringOutput = [None for _ in range(64)]
        for k in range(64):
            if existTrail[k] == True:
                stringOutput[k] = "?"
            else:
                stringOutput[k] = "0"
        stringOutput = "".join(n for n in stringOutput)
        print(f"Output  : {stringOutput}")
        print()

getOutputProperty()
            
"""
nbRounds = 5
for i in range(64):
	#Get the input i = 0...01...1  
							^ index i
	#as an integer, this is (1 << i) - 1
	input = 0...01...1   (as a list of 0 and 1)
				 ^ index i
	
	existTrail = [None for _ in range(64)]
	#For each unit vector for the output
	for j in range(64):
		output = 0...010...0 (as a list of 0 and 1)
					  ^ index j
		m,x,y = genModelPresent(nbRounds)
		#Add constraints to fix x[0] to the input and x[nbRounds] to the output
		....
		m.optimize()
		if m has a feasible solution:
			existTrail[j] = True
		else:
			existTrail[j] = False
	print(f"For input {input} : {existTrail}")
	   0000000000000000000000000000000000000000000000000000000000001111
	-> 000000000000000000000000000000000000000000000000000000000??00000 <- stringoutput
	if existrTrail[j] == True:
		stringoutput[j] = ?
	else:
		stringoutput[j] = 0
"""

"""
- Compute the stringoutput for each input 
- Find the "best" one : we  want not many zeroes in the input, lot of zeroes in the output
- Implement the corresponding attack on 6 rounds
- search for a distinguisher on 6 rounds (for the 7 rounds attack)
"""

"""
Distinguisher on 5 rounds :
For input 1111111111111000000000000000000000000000000000000000000000000000 (13)
Output  : 0000000000000000000000000000000000000000000000000000000000000000
Implement the attack. 
Search for the distinguisher over 6 rounds.
Give the estimate data and key-recovery complexity for each distinguisher
- How many plaintexts in each structure (data complexity)
- How many key bits do we recover
- How many key bits do we need to brute force 
"""

"""
Most likely distinguisher for 6 rounds:
For input 1111111111111111000000000000000000000000000000000000000000000000 (16)
Output  : 000000000000000000000???00000???00000???00000???00000???00000???
  = 0000 0000 0000 0000 0000 0??? 0000 0??? 0000 0??? 0000 0??? 0000 0??? 0000 0???
- we can recover most bits with a fairly sized input (2^16)
- we still need to brute force the unrecovered 18 bits
Second (unlikely) candidate for a 6 round distinguisher:
For input 1111111111111111111111111111111100000000000000000000000000000000 (32)
Output  : 0000000000000000000000000000000000000000000000000000000000000000
- we can recover all 64 bits, so (in theory) no brute force needed
- but the required input is 2^16 times bigger than the previous candidate (more impractical to use)
"""