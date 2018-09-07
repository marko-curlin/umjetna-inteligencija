
"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
from logic import *

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def miniWumpusSearch(problem): 
    """
    A sample pass through the miniWumpus layout. Your solution will not contain 
    just three steps! Optimality is not the concern here.
    """
    from game import Directions
    e = Directions.EAST 
    n = Directions.NORTH
    return [e, n, n]


def fillKnowledgeBank(clauseSet, problem):
    currentState = problem.getStartState()
    visitedStates = []
    nextStates = set()
    while True:
        visitedStates.append(currentState)
        print currentState
        for i in problem.getSuccessors(currentState):
            nextStates.add(i[0])

        literal = Literal(Labels.POISON_FUMES, currentState, True)
        fillSetForPositive(clauseSet, Labels.POISON, problem.getSuccessors(currentState), literal)

        positivePoisonFumes = Literal(Labels.POISON_FUMES, currentState)
        fillSetForNegative(clauseSet, Labels.POISON, problem.getSuccessors(currentState), positivePoisonFumes)

        literal = Literal(Labels.WUMPUS_STENCH, currentState, True)
        fillSetForPositive(clauseSet, Labels.WUMPUS, problem.getSuccessors(currentState), literal)

        positiveWumpusStench = Literal(Labels.WUMPUS_STENCH, currentState)
        fillSetForNegative(clauseSet, Labels.WUMPUS, problem.getSuccessors(currentState), positiveWumpusStench)

        literal = Literal(Labels.TELEPORTER_GLOW, currentState, True)
        fillSetForPositive(clauseSet, Labels.TELEPORTER, problem.getSuccessors(currentState), literal)

        positiveTeleporterGlow = Literal(Labels.TELEPORTER_GLOW, currentState)
        fillSetForNegative(clauseSet, Labels.TELEPORTER, problem.getSuccessors(currentState),
                           positiveTeleporterGlow)

        clauseSet.add(Clause([Literal(Labels.WUMPUS, currentState), Literal(Labels.POISON, currentState), Literal(Labels.SAFE, currentState)]))



        if len(nextStates) == 0:
            return
        currentState = nextStates.pop()
        while currentState in visitedStates:
            if len(nextStates) == 0:
                return
            currentState = nextStates.pop()

def logicBasedSearch(problem):
    """
    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:
    """
    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())

    print "Does the Wumpus's stench reach my spot?", problem.isWumpusClose(problem.getStartState())

    print "Can I sense the chemicals from the pills?", problem.isPoisonCapsuleClose(problem.getStartState())

    print "Can I see the glow from the teleporter?", problem.isTeleporterClose(problem.getStartState())
    
    """
    Feel free to create and use as many helper functions as you want.

    A couple of hints: 
        * Use the getSuccessors method, not only when you are looking for states 
        you can transition into. In case you want to resolve if a poisoned pill is 
        at a certain state, it might be easy to check if you can sense the chemicals 
        on all cells surrounding the state. 
        * Memorize information, often and thoroughly. Dictionaries are your friends and 
        states (tuples) can be used as keys.
        * Keep track of the states you visit in order. You do NOT need to remember the
        tranisitions - simply pass the visited states to the 'reconstructPath' method 
        in the search problem. Check logicAgents.py and search.py for implementation.
    """
    # array in order to keep the ordering
    visitedStates = []
    startState = problem.getStartState()
    visitedStates.append(startState)

    "*** YOUR CODE HERE ***"
    knowledgeBank = {}
    # 'safeState' is a set of states = ((x,y), transition, cost)
    safeStates = set()
    currentState = startState
    clauseSet = set()
    fillKnowledgeBank(clauseSet, problem)
    while True:
        visitedStates.append(currentState)
        print "Visiting:", currentState
        #clauseSet.add(Clause([Literal(Labels.WUMPUS, currentState), Literal(Labels.POISON, currentState), Literal(Labels.SAFE, currentState)]))
        if problem.isGoalState(currentState):
            print "Game over: Teleported home!"
            problem.reconstructPath(visitedStates)


        if problem.isPoisonCapsuleClose(currentState):
            print "Sensed: b", currentState
            # literal = Literal(Labels.POISON_FUMES, currentState, True)
            # fillSetForPositive(clauseSet, Labels.POISON, problem.getSuccessors(currentState), literal)
            clauseSet.add(Clause(Literal(Labels.POISON_FUMES, currentState)))
        else:
            print "Sensed: ~b", currentState
            # positivePoisonFumes = Literal(Labels.POISON_FUMES, currentState)
            # fillSetForNegative(clauseSet, Labels.POISON, problem.getSuccessors(currentState), positivePoisonFumes)
            clauseSet.add(Clause(Literal(Labels.POISON_FUMES, currentState, True)))

        if problem.isWumpusClose(currentState):
            print "Sensed: s", currentState
            #clauseSet.add(Clause(Literal(Labels.WUMPUS_STENCH, currentState, True)))
            # literal = Literal(Labels.WUMPUS_STENCH, currentState, True)
            # fillSetForPositive(clauseSet, Labels.WUMPUS, problem.getSuccessors(currentState), literal)
            clauseSet.add(Clause(Literal(Labels.WUMPUS_STENCH, currentState)))
        else:
            print "Sensed: ~s", currentState
            # positiveWumpusStench = Literal(Labels.WUMPUS_STENCH, currentState)
            # fillSetForNegative(clauseSet, Labels.WUMPUS, problem.getSuccessors(currentState), positiveWumpusStench)
            clauseSet.add(Clause(Literal(Labels.WUMPUS_STENCH, currentState, True)))

        if problem.isTeleporterClose(currentState):
            print "Sensed: g", currentState
            #clauseSet.add(Clause(Literal(Labels.TELEPORTER_GLOW, currentState, True)))
            # literal = Literal(Labels.TELEPORTER_GLOW, currentState, True)
            # fillSetForPositive(clauseSet, Labels.TELEPORTER, problem.getSuccessors(currentState), literal)
            clauseSet.add(Clause(Literal(Labels.TELEPORTER_GLOW, currentState)))
        else:
            print "Sensed: ~g", currentState
            # positiveTeleporterGlow = Literal(Labels.TELEPORTER_GLOW, currentState)
            # fillSetForNegative(clauseSet, Labels.TELEPORTER, problem.getSuccessors(currentState), positiveTeleporterGlow)
            clauseSet.add(Clause(Literal(Labels.TELEPORTER_GLOW, currentState, True)))

        for state in problem.getSuccessors(currentState):
            #print clauseSet

            # clauseSet.add(Clause([Literal(Labels.WUMPUS, state[0]), Literal(Labels.POISON, state[0]),
            #                        Literal(Labels.SAFE, state[0])]))
            if resolution(clauseSet, Clause(Literal(Labels.WUMPUS, state[0]))):
                print "Concluded: w", state[0]
                clauseSet.add(Clause(Literal(Labels.WUMPUS, state[0])))
                w = True
            if resolution(clauseSet, Clause(Literal(Labels.WUMPUS, state[0], True))):
                print "Concluded: ~w", state[0]
                clauseSet.add(Clause(Literal(Labels.WUMPUS, state[0], True)))
                w = False

            if resolution(clauseSet, Clause(Literal(Labels.TELEPORTER, state[0]))):
                print "Concluded: t", state[0]
                clauseSet.add(Clause(Literal(Labels.TELEPORTER, state[0])))
                currentState = state
                continue
            if resolution(clauseSet, Clause(Literal(Labels.TELEPORTER, state[0], True))):
                print "Concluded: ~t", state[0]
                clauseSet.add(Clause(Literal(Labels.TELEPORTER, state[0], True)))

            if resolution(clauseSet, Clause(Literal(Labels.POISON, state[0]))):
                print "Concluded: p", state[0]
                clauseSet.add(Clause(Literal(Labels.POISON, state[0])))
                p = True
            if resolution(clauseSet, Clause(Literal(Labels.POISON, state[0], True))):
                print "Concluded: ~p", state[0]
                clauseSet.add(Clause(Literal(Labels.POISON, state[0], True)))
                p = False

            #if not (p or w):
            if resolution(clauseSet, Clause(Literal(Labels.SAFE, state[0]))):
                print "Concluded: o", state[0]
                clauseSet.add(Clause(Literal(Labels.SAFE, state[0])))
                safeStates.add(state)
            #else:
            if resolution(clauseSet, Clause(Literal(Labels.SAFE, state[0], True))):
                print "Concluded: ~o", state[0]
                clauseSet.add(Clause(Literal(Labels.SAFE, state[0], True)))

            minimumStateWeight = 999999
            minimumState = 0
            for i in safeStates:
                currentStateWeight = stateWeight(i[0])#izvlacimo koordinate sa i[0]
                if minimumStateWeight > currentStateWeight:
                    if i[0] not in visitedStates:
                        minimumState = i
                        minimumStateWeight = currentStateWeight

            if minimumState != 0:
                currentState = minimumState[0]
                continue

        util.pause()
    "*** YOUR CODE HERE ***"


"*** YOUR CODE HERE ***"
def fillSetForPositive(clauseSet, label, succesors, literal):
    # type: (set, Labels, set) -> None
    """
    :param set: Set Clause-ova
    :param label: Label koji nanjusimo
    :param succesors: Sucesori=((x,y), direction, cost) trenutnog stanja
    :return: None
    """
    literalSet = set()
    literalSet.add(literal)
    for state in succesors:
        x, y = state[0]
        literalSet.add(Literal(label, (x, y)))
    clauseSet.add(Clause(literalSet))


def fillSetForNegative(clauseSet, label, succesors, literal):
    # type: (set, Labels, set, Literal) -> None
    """
    :param set: Set Clause-ova
    :param label: Label koji nanjusimo
    :param succesors: Sucesori=((x,y), direction, cost) trenutnog stanja
    :param literal: Literal(label, state, negative) koji ubacujemo u sve klauzule
    :return: None
    """
    literalSet = set()

    for state in succesors:
        literalSet.add(literal)
        x,y = state[0]
        literalSet.add(Literal(label, (x, y), True))
        clauseSet.add(Clause(literalSet))
        literalSet.clear() # nebi triba brisat iz literala poslanih u konstruktoru
"*** YOUR CODE HERE ***"


# Abbreviations
lbs = logicBasedSearch
