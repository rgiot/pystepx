#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Code to launch on all the islands.
"""
import logging
import math
import random

from pystepx.island  import evolver
from pystepx.fitness import evalfitness
from pystepx.pySTEPX import PySTEPX


def add(listElem):
    try:
        return listElem[0]+listElem[1]
    except:
        raise WrongValues, "Wrong values sent to function node.\nCan't get result"

def sub(listElem):
    try:
        return listElem[0]-listElem[1]
    except:
        raise WrongValues, "Wrong values sent to function node.\nCan't get result"

def neg(listElem):
    try:
        return 0-listElem[0]
    except:
        raise WrongValues, "Wrong values sent to function node.\nCan't get result"

def multiply(listElem):
    try:
        return listElem[0]*listElem[1]
    except:
        raise WrongValues, "Wrong values sent to function node.\nCan't get result"

def square(listElem):
    try:
        return listElem[0]*listElem[0]
    except:
        raise WrongValues, "Wrong values sent to function node.\nCan't get result"

def cos(listElem):
    try:
        return math.cos(listElem[0])
    except:
        raise WrongValues, "Wrong values sent to function node.\nCan't get result"

def sin(listElem):
    try:
        return math.sin(listElem[0])
    except:
        raise WrongValues, "Wrong values sent to function node.\nCan't get result"

def rootBranch(x):
    try:
        return x
    except:
        raise WrongValues, "Wrong values sent to function node.\nCan't get result"

functions = {'+':   add,
            '-':    sub,
            'neg':  neg,
            '*':    multiply,
            '^2':   square,
            'cos':  cos,
            'sin':  sin,
            'root': rootBranch
            }

nb_eval = 2
all_x = []
for i in xrange(nb_eval):
    all_x.append(random.random()*10)

# then, we create a mapping of terminals
# the variables will be given a value coming from a set of examples
# the constants will just be given as such or produced by a
# random producer
terminals = {
    'x': all_x
}

# default function set applicable by for branches:
defaultFunctionSet= [(1,2,'+'), (1,2,'*'), (1,1,'^2'), (1,2,'-'), (1,1,'cos'), (1,1,'sin'), (1,1,'neg')]
# default terminal set applicable by for branches:
defaultTerminalSet= [(3,0,'x')]
treeRules = {'root':[(defaultFunctionSet,defaultTerminalSet)],
                    '+':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                    '*':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                    '^2':[(defaultFunctionSet,defaultTerminalSet)],
                    '-':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                    'neg':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'sin')],defaultTerminalSet)],
                    'cos':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'sin'),(1,1,'neg')],defaultTerminalSet)],
                    'sin':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'neg')],defaultTerminalSet)]
                    }

# Create the attended results
# ideal polynomial to find
ideal_results = []
for nb in xrange(nb_eval):
    ideal_results.append([all_x[nb]**3 + all_x[nb]**2 + math.cos(all_x[nb])])

evolve = evolver.DistributedEvolver(popsize=500, crossover_prob=0.25,
        mutation_prob=0.25)

gp_engine = PySTEPX()
gp_engine.set_evolver(evolve)
gp_engine.set_tree_rules(treeRules)
gp_engine.set_functions(functions)
gp_engine.set_terminals(terminals)


fte = evalfitness.FitnessTreeEvaluation()
fte.set_terminals(terminals)
fte.set_functions(functions)
fte.check_configuration()
ffe = evalfitness.FinalFitness(ideal_results, nb_eval)

def FitnessFunction(my_tree):
    return ffe.FinalFitness(
        fte.EvalTreeForAllInputSets(my_tree, xrange(nb_eval)))
gp_engine.set_fitness_function(FitnessFunction)

if __name__ == "__main__":
    gp_engine.evolve()
