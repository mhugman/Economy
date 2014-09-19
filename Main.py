#-------------------------------------------------------------------------------
# Name:        Multi-agent, multi-good economy based on Cobb-Douglas functions
# Purpose:     Simulate an economy which only has two goods, tea and coffee, and four classes
#              of economic actors: workers, firms, banks, and capitalists.
#
# Author:      Michael R. Hugman
#
# Created:     17/09/2014
# Copyright:   (c) Michael R. Hugman 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


""" 
Workers and capitalists have Cobb-Douglas utility functions, which determines their happiness given the bundle
of goods they purchase. But they don't have perfect knowledge of what they should purchase to maximize happiness. 
Instead, they "guess" by dynamically adjusting their consumption of different goods up and down. The guessing
isn't completely random, we can assume that their utility function tells them whether to adjust up or down, but
not exactly how much. 

>>> correction: agents are assumed to be pretty dumb. They will adjust one of their decisions and then determine
whether to keep doing it based on whether they see a profit/utility increase. Once they can't increase profit anymore
they change another factor. They "learn" from other similar agents/firms and will copy their behavior. 

Firms and banks seek to maximize profit. Firms have Cobb-Douglas technological production functions. But like
the workers, they don't have perfect knowledge. They make informed guesses about how much input to buy. Their
adjustment of prices and wages, however, is different. They take the average price or wage in the market as a 
starting point, and adjust up or down depending on how much they need that type of labor, or how much they need
to sell their stock of goods. 

Participants in a market form a randomized queue to determine in which order they will buy and sell goods. Those
at the end of the queue may not get what they want, if there is excess supply or demand in the market.  


Agents
    
    - Deposits his money in his bank of choice, where it becomes "virtual" money
    - Has a Cobb-Douglas utility function, with fractional parameters for each of m consumer goods (all adding up to 1), 
    loanable funds from his bank, stocks from each of F firms, leisure, and saving
    - has a "type" of labor which he performs, and sells in the labor market for that type of labor. 
    - has a demand for a certain amount of cash on hand (savings) for a rainy day
    

    
Firms

    - Each has a single product that it produces (one of the consumer goods or capital goods), and there may be any number
    of firms producing a given product. 
    
    - Has a technological production function, which requires certain inputs. Has a demand for labor
    and other inputs
    
    - Borrows money from banks - has demand for loanable funds (credit). 
    
Banks

    - Has loyal customers who only deposit their money at that bank. 
    
    - Takes this money and loans it out at interest to workers and firms. 
    
"M" real money supply

- Each firm sets their own prices and wages, so there is not just "one" price for a good

Main Markets: 

    Consumer goods (x1...xM), (p1...pM)
        
        M consumer goods x, each with a price of pm
        
    1st order capital goods (y1...yN), (q1...qN)
    
        N 1st order capital goods y, each with a price of qn        
    
    2nd order capital goods (z1...zP), (r1...rP)
    
        P 2nd order capital goods z, each with a price of rp
        
    Raw resources (a1...aT), (s1...sT)
    
        T raw resources a, each with a price of s
         
    Labor (l1...lQ), (w1...wQ)
    
        Q types of labor l, each with a wage of wq
    
    Loanable Funds (b1...bR), (i1...iR)
    
        R banks b, with an interest rate of i for each bank
    
    Stock Market (f1...fS), (h1...hS)
    
        S stocks for each of F firms f, each with a stock price of h
        
A: number of agents
F: number of firms
R: number of banks 

L: amount of labor a worker supplies (as a percentage of the day)
1 - L: amount of leisure a worker has (as a proportion of the day)
        
The economy starts out with a certain amount of money (more may created later through the actions of banks with the fractional reserve system). We can specify the initial distribution of 
wealth. 

Assume raw resources are infinite, it only requires paying people to extract the resources from the earth

"""


from random import *

# global variables

# number of different things, see main comment section
M = 3
N = 3
P = 3
Q = 3
R = 3
S = 3

A = 100
F = 30

totalMoney = 1000 * (A + F + R )# $1000 for each agent, firm, and bank

agents = []
firms = []
banks = []

# agent is the superclass that all agents belong to

class Agent() :
    
    # Utility function: U = sum as t -> infinity ([x1^a1 * x2^a2 * x3^a3 ... xM^aM * (1 - laborProvided)^b * (money)^c (1 - delta)^t ]_t)
    # where delta is time discounting/preference
    
    # id is the number identifying the worker
    def __init__(self, identity) :
        
                 
        self.money = totalMoney / (A + F + R)  # initial amount of money is a random number between 0 and 1000. This is actual cash on hand.
        self.virtualMoney = 0.0  # this is the amount of money in the worker's checking account at the bank. Its assumed that this can be withdrawn as necessary.
        self.chosenBank = randrange(0, R, 1)  # the identity of the bank the agent choses to deposit money at
        self.employer = -1 # the identity of the firm which employs the worker (-1 if unemployed)
        self.id = identity
        self.type = randrange(0, Q, 1) # type of labor the worker performs (if any)
        
        self.laborSupply = 0.0
        self.laborProvided = 0.0
        self.leisureParameter = 0.0 # parameter for leisure in the utility function
        
        self.goodDemand = [] # amount demanded for each good
        self.goodAcquired = [] # amount of each good acquired
        self.goodParameters = [] # parameters for each good in the utility function
        
        self.stocks = []
        self.debts = [] # money owed to each of the banks the agent loaned from
        
        self.moneyDemand = 0.0
        self.moneyParameter = 0.0 # parameter for money (savings) in the utility function
           
class Firm():
    
    # chooses prices and amount of inputs to maximize profit (p if producing consumer good, q if 1st order, r if 2nd order)
    
    # maximize over time as above for agent
    
    # Production function: xM = T * y1^a1 * y2^a2 * ... * yN^aN * z1^b1 * z2^b2 * ... * zP^bP * a1^s1 * a2^s2 * ... * aP^sP * l1^c1 * l2^c2 * ... * lQ^cQ
    
    # (if manufacturing consumer goods: only y and l terms, if 1st order, only z and l, if 2nd order, only a and l, if raw resources, only l
    # T is a technology factor
    
    # Profit function: profit = price * xM - ( y1*q1 + y2*q2 + ... + yN*qN + z1*r1 + z2*r2 + ... + zP*rP +  l1*w1 + l2*w2 + ... + lQ*wQ + a1*s1 + a2*s2 + ... + aP*sP )
    
    # price is the price of the good manufactured (p, q, r, or s)

    # product is what the firm produces, determining its type
    def __init__(self, identity) :
               

        self.money = totalMoney / (A + F + R)  # initial amount of money is a random number between 0 and 1000. This is actual cash on hand.
        self.virtualMoney = 0.0  # this is the amount of money in the worker's checking account at the bank. Its assumed that this can be withdrawn as necessary.
        self.chosenBank = 0  # the identity of the bank the agent choses to deposit money at
        self.id = identity
        self.type = type # type: whether the firm produces consumer goods, 1st order capital goods, 2nd order capital goods, or raw resources
                
        self.employees = [] # identities of the employees on the firm's payroll
        self.wage = []  # wage rate paid to each of q types of employees
        self.price = randrange(0, 100, 1) # price charged for good
        
        self.laborDemand = [] # the firms demands for the q types of labor
        self.laborParameters = []
        self.laborAcquired = []  # amount of labor actually acquired.
        
        self.inputDemand = [] # demands for inputs (if it is a consumer good firm, it will demand 1st order capital goods. 
            # if it is a 2nd order capital good firm, it will only demand labor and won't have input demands
        self.inputParameters = []
        self.inputAcquired = []
        
        
        self.supply = 0.0  # amount of product the firm produces
        self.sold = 0.0  # amount of product the firm actually sells
        self.profitHistory = [] # figure out whether to increase or decrease factor based on profit history


class Bank() :
    
    # Chooses i and money supplied to maximize profit = revenue - cost = sum t-> infinity ( [(1 + i)*(money lent out at t - 1) - (money lent out at t) ](1 - delta))
    # where delta is time discounting/preference

    def __init__(self, identity):

        
        self.virtualMoney = totalMoney / (A + F + R) # this is the amount of money in the worker's checking account at the bank. Its assumed that this can be withdrawn as necessary.
        
        self.id = identity
        self.money = randrange(0, 10000, 1)
        self.interest = randrange(0, 30, 1)  #percent interest charged on loans. Random % from 0 to 30
        
        
        self.profit = 0.0





# get the initial number of agents in the economy

#create the agents in the economy
def createAgents() :

    global agents
    global firms
    global banks

    # pass the ID, i, to each agent. Add them to lists of their class
    for i in range(A) :

        agent = Agent(i)
        agents.append(agent)

    for i in range(F) :

        agent = Firm(i)
        firms.append(agent)

   
    for i in range(R) :

        agent = Bank(i)
        banks.append(agent)




def setup() :

    #getInitialValues()

    createAgents()

  
def main():

    setup()

    print("done setting up")

   


if __name__ == '__main__':
    main()
