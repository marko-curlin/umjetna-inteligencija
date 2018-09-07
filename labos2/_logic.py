import util 
import functools 

class Labels:
    """
    Labels describing the WumpusWorld
    """
    WUMPUS = 'w'
    TELEPORTER = 't'
    POISON = 'p'
    SAFE = 'o'

    """
    Some sets for simpler checks
    >>> if literal.label in Labels.DEADLY: 
    >>>     # Don't go there!!!
    """ 
    DEADLY = set([WUMPUS, POISON])
    WTP = set([WUMPUS, POISON, TELEPORTER])

    UNIQUE = set([WUMPUS, POISON, TELEPORTER, SAFE])

    POISON_FUMES = 'b'
    TELEPORTER_GLOW = 'g'
    WUMPUS_STENCH = 's'

    INDICATORS = set([POISON_FUMES, TELEPORTER_GLOW, WUMPUS_STENCH])


def stateWeight(state):
    """
    To ensure consistency in exploring states, they will be sorted 
    according to a simple linear combination. 
    The maps will never be 
    larger than 20x20, and therefore this weighting will be consistent.
    """
    x, y = state 
    return 20*x + y 


@functools.total_ordering
class Literal:
    """
    A literal is an atom or its negation
    In this case, a literal represents if a certain state (x,y) is or is not 
    the location of GhostWumpus, or the poisoned pills.
    """

    def __init__(self, label, state, negative=False):
        """
        Set all values. Notice that the state is remembered twice - you
        can use whichever representation suits you better.
        """
        x,y = state 
        
        self.x = x 
        self.y = y 
        self.state = state 

        self.negative = negative
        self.label = label 

    def __key(self):
        """
        Return a unique key representing the literal at a given point
        """
        return (self.x, self.y, self.negative, self.label)

    def __hash__(self):
        """
        Return the hash value - this operator overloads the hash(object) function.
        """
        return hash(self.__key())

    def __eq__(first, second):
        """
        Check for equality - this operator overloads '=='
        """
        return first.__key() == second.__key()

    def __lt__(self, other):
        """ 
        Less than check
        by using @functools decorator, this is enough to infer ordering
        """
        return stateWeight(self.state) < stateWeight(other.state)

    def __str__(self):
        """
        Overloading the str() operator - convert the object to a string
        """
        if self.negative: return '~' + self.label
        return self.label

    def __repr__(self):
        """
        Object representation, in this case a string
        """
        return self.__str__()

    def copy(self):
        """
        Return a copy of the current literal
        """
        return Literal(self.label, self.state, self.negative)

    def negate(self):
        """
        Return a new Literal containing the negation of the current one
        """
        return Literal(self.label, self.state, not self.negative)

    def isDeadly(self):
        """
        Check if a literal represents a deadly state
        """
        return self.label in Labels.DEADLY

    def isWTP(self):
        """
        Check if a literal represents GhostWumpus, the Teleporter or 
        a poisoned pill
        """
        return self.label in Labels.WTP

    def isSafe(self):
        """
        Check if a literal represents a safe spot
        """
        return self.label == Labels.SAFE

    def isTeleporter(self):
        """
        Check if a literal represents the teleporter
        """
        return self.label == Labels.TELEPORTER


class Clause: 
    """ 
    A disjunction of finitely many unique literals. 
    The Clauses have to be in the CNF so that resolution can be applied to them. The code 
    was written assuming that the clauses are in CNF, and will not work otherwise. 

    A sample of instantiating a clause (~B v C): 

    >>> premise = Clause(set([Literal('b', (0, 0), True), Literal('c', (0, 0), False)]))

    or; written more clearly
    >>> LiteralNotB = Literal('b', (0, 0), True)
    >>> LiteralC = Literal('c', (0, 0), False)

    >>> premise = Clause(set([[LiteralNotB, LiteralC]]))
    """ 

    def __init__(self, literals):
        """
        The constructor for a clause. The clause assumes that the data passed 
        is an iterable (e.g., list, set), or a single literal in case of a unit clause. 
        In case of unit clauses, the Literal is wrapped in a list to be safely passed to 
        the set.
        """
        if not type(literals) == set and not type(literals) == list:
            self.literals = set([literals])
        else:
            self.literals = set(literals)

    def isResolveableWith(self, otherClause):
        """
        Check if a literal from the clause is resolveable by another clause - 
        if the other clause contains a negation of one of the literals.
        e.g., (~A) and (A v ~B) are examples of two clauses containing opposite literals 
        """
        for literal in self.literals: 
            if literal.negate() in otherClause.literals:
                return True 
        return False 

    def isRedundant(self, otherClauses):
        """
        Check if a clause is a subset of another clause.
        """
        for clause in otherClauses:
            if self == clause: continue
            if clause.literals.issubset(self.literals):
                return True
        return False

    def isIrrelevant(self):
        """
        Check if a cluase contains a complementary pair of literals
        """
        for literal1 in self.literals:
            for literal2 in self.literals:
                if literal1.state == literal2.state and literal1.negative != literal2.negative:
                    return True
        return False

    def negateAll(self):
        """
        Negate all the literals in the clause to be used 
        as the supporting set for resolution.
        """
        negations = set()
        for literal in self.literals:
            clause = Clause(literal.negate())
            negations.add(clause)
        return negations

    def __str__(self):
        """
        Overloading the str() operator - convert the object to a string
        """
        return ' V '.join([str(literal) for literal in self.literals])

    def __repr__(self):
        """
        The representation of the object
        """
        return self.__str__()

    def __key(self):
        """
        Return a unique key representing the literal at a given point
        """
        return tuple(sorted(list(self.literals)))

    def __hash__(self):
        """
        Return the hash value - this operator overloads the hash(object) function.
        """
        return hash(self.__key())

    def __eq__(first, second):
        """
        Check for equality - this operator overloads '=='
        """
        return first.__key() == second.__key()


def resolution(clauses, goal):#resolution(set([premise1, premise2, premise3]), goal)
    # type: (set, Clause) -> Bool
    """
    clauses - set klauzula (koje se sastoje od seta Literala)

    Implement refutation resolution.

    The pseudocode for the algorithm of refutation resolution can be found 
    in the slides. The implementation here assumes you will use set of support 
    and simplification strategies. We urge you to go through the slides and 
    carefully design the code before implementing.
    """
    resolvedPairs = set()   #ubacujemo parove koje smo vratili iz selectClauses
    setOfSupport = goal.negateAll()

    "*** YOUR CODE HERE ***"
    localClauses = clauses.copy()
    for i in setOfSupport:
        localClauses.add(i)
    new = set()
    while True:
        removeRedundant(localClauses, setOfSupport)
        for (c1, c2) in selectClauses(localClauses, setOfSupport, resolvedPairs):
            resolvents = resolvePair(c1, c2)
            for i in resolvents.copy():
                if i.isIrrelevant():
                    resolvents.remove(i)
                    continue
                setOfSupport.add(i)
            if Clause(set()) in resolvents:
                return True
            for i in resolvents:
                new.add(i)
        removeRedundant(new, setOfSupport)
        if new.issubset(localClauses):
            return False
        for i in new:
            localClauses.add(i)
    "*** YOUR CODE HERE ***"


def removeRedundant(clauses, setOfSupport):
    """
    Remove redundant clauses (clauses that are subsets of other clauses)
    from the aforementioned sets.
    Be careful not to do the operation in-place as you will modify the
    original sets. (why?)
    """
    "*** YOUR CODE HERE ***"
    for clause1 in clauses.copy():
        if clause1.isRedundant(clauses):
            if clauses.__contains__(clause1):
                clauses.remove(clause1)
    for clause1 in setOfSupport.copy():
        if clause1.isRedundant(clauses):
            if clauses.__contains__(clause1):
                clauses.remove(clause1)
    return
    "*** YOUR CODE HERE ***"


def resolvePair(firstClause, secondClause):
    """
    clause - set literala
    Clause(set([Literal('a', (0, 0), True), Literal('b', (0, 0), False)]))

    vraca set (rezolviranih) klauzula

    Resolve a pair of clauses.
    """
    "*** YOUR CODE HERE ***"
    returnSet = set()
    if not firstClause.isResolveableWith(secondClause):
        return returnSet
    for literal1 in firstClause.literals:
        for literal2 in secondClause.literals:
            if literal1.label == literal2.label and literal1.state == literal2.state and literal1.negative != literal2.negative:
                returnClause1 = firstClause.literals - {literal1}
                returnClause2 = secondClause.literals - {literal2}
                returnSet.add(Clause(returnClause1.union(returnClause2)))
                break
    return returnSet
    "*** YOUR CODE HERE ***"

def selectClauses(clauses, setOfSupport, resolvedPairs):
    """
    cluses - set svih kluzula, setOfSupport - set SoS-a,
    resolvedPairs - set vec rezolviranih tuplova(parova) klauzula

    vrati set tuplova(parova) kroz koji ce iterirati

    Select pairs of clauses to resolve.
    """
    "*** YOUR CODE HERE ***"
    returnSet = set()
    for supportClause in setOfSupport:
        for clause in clauses:
            if not clause == supportClause:
                if (supportClause, clause) not in resolvedPairs:
                    returnSet.add((supportClause, clause))
                    resolvedPairs.add((supportClause, clause))
        for clause in setOfSupport:
            if not clause == supportClause:
                if (supportClause, clause) not in resolvedPairs:
                    returnSet.add((supportClause, clause))
                    resolvedPairs.add((supportClause, clause))
    return returnSet
    "*** YOUR CODE HERE ***"


def testResolution():
    """
    A sample of a resolution problem that should return True. 
    You should come up with your own tests in order to validate your code. 
    """

    premise1 = Clause(set([Literal('a', (0, 0), True), Literal('b', (0, 0), False)]))
    premise2 = Clause(set([Literal('b', (0, 0), True), Literal('c', (0, 0), False)]))
    premise3 = Clause(Literal('a', (0,0)))

    goal = Clause(Literal('c', (0,0)))
    print resolution(set([premise1, premise2, premise3]), goal)

    "*** YOUR CODE HERE ***"
    premise1 = Clause(set([Literal('U', (0, 0), False), Literal('T', (0, 0), True)]))
    premise2 = Clause(set([Literal('T', (0, 0), False), Literal('A', (0, 0), False)]))
    premise3 = Clause(set([Literal('U', (0, 0), True), Literal('A', (0, 0), True)]))

    goal = Clause(set([Literal('T', (0, 0), True), Literal('A', (0, 0), True)]))
    print resolution(set([premise1, premise2, premise3]), goal)
    "*** YOUR CODE HERE ***"


"*** YOUR CODE HERE ***"
def test0():
    print "test0"
    premise1 = Clause(set([Literal('c', (0, 0), True), Literal('b', (0, 0), False)]))
    premise2 = Clause(set([Literal('b', (0, 0), True), Literal('e', (0, 0), False)]))
    premise3 = Clause(set([Literal('e', (0, 0), True), Literal('b', (0, 0), False)]))
    premise4 = Clause(set([Literal('d', (0, 0), True), Literal('d', (0, 0), True)]))
    premise5 = Clause(Literal('c', (0, 0)))
    premise6 = Clause(Literal('d', (0, 0)))
    premise7 = Clause(Literal('a', (0, 0)))

    goal = Clause(set([Literal('d', (0, 0), True), Literal('a', (0, 0), True)]))
    print "Got:", resolution(set([premise1, premise2, premise3, premise4, premise5, premise6, premise7]),
                             goal), "- Expected: True"


def test1():
    print "test1"
    premise1 = Clause(set([Literal('a', (0, 0), False), Literal('f', (0, 0), False)]))
    premise2 = Clause(set([Literal('a', (0, 0), True), Literal('g', (0, 0), False)]))
    goal = Clause(set([Literal('f', (0, 0), False), Literal('g', (0, 0), False)]))

    print "Got: ", resolution(set([premise1, premise2]), goal), "- Expected: True"


def test2():
    print "test2"
    premise1 = Clause(set([Literal('a', (0, 0), True), Literal('b', (0, 0), False)]))
    premise2 = Clause(set([Literal('b', (0, 0), True), Literal('c', (0, 0), False)]))
    premise3 = Clause(Literal('a', (0, 0)))

    goal = Clause(Literal('c', (0, 0), True))
    print "Got:", resolution(set([premise1, premise2, premise3]), goal), "- Expected: False"


def test3():
    print "test3"
    premise1 = Clause(set([Literal('c', (0, 0), True), Literal('b', (0, 0), False)]))
    premise2 = Clause(set([Literal('b', (0, 0), True), Literal('e', (0, 0), False)]))
    premise3 = Clause(set([Literal('e', (0, 0), True), Literal('b', (0, 0), False)]))
    premise4 = Clause(set([Literal('d', (0, 0), True), Literal('d', (0, 0), True)]))
    premise5 = Clause(Literal('c', (0, 0)))
    premise6 = Clause(Literal('d', (0, 0)))
    premise7 = Clause(Literal('a', (0, 0)))

    goal = Clause(set([Literal('c', (0, 0), True)]))
    print "Got:", resolution(set([premise1, premise2, premise3, premise4, premise5, premise6, premise7]),
                             goal), "- Expected: False"


def test4():
    print "test4"
    premise1 = Clause(set([Literal('a', (0, 0), False), Literal('f', (0, 0), False)]))
    premise2 = Clause(set([Literal('a', (0, 0), True), Literal('g', (0, 0), False)]))
    goal = Clause(set([Literal('f', (0, 0), False), Literal('g', (0, 0), True)]))

    print "Got: ", resolution(set([premise1, premise2]), goal), "- Expected: False"
"*** YOUR CODE HERE ***"


if __name__ == '__main__':
    """
    The main function - if you run logic.py from the command line by 
    >>> python logic.py 

    this is the starting point of the code which will run. 
    """
    testResolution()
    "*** YOUR CODE HERE ***"
    test0()
    test1()
    test2()
    test3()
    test4()
    "*** YOUR CODE HERE ***"