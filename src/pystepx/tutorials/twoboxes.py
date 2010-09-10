#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Two boxes problem presented in Koza II.
Do not use the ADF.

We must find a function computing the difference of
volume between two boxes.

L0, W0 and H0 contains the information about box 0.
In order to evaluate the trees only one time, these variables
do not hold single values, but an array (one line per example).
Same thing for L1, W1, H1.


XXX End debuggin to activate the changing of fitness after each generation
"""


import numpy as np
from random import random
import logging

import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness
import pystepx.tree.numpyfunctions
from pystepx.tree.numpyfunctions import _add, _sub, _mul, _protected_division
MIN = 1
MAX = 200
NB_EXAMPLES = 10

try:
    import psyco
    psyco.profile()
except ImportError:
    pass

def _root_branch(inputs):
    """Return the input."""
    return inputs

#Function definition
functions = {
    '+': _add,
    '-': _sub,
    '*': _mul,
    '%': _protected_division,
    'root': _root_branch, 
}

#Terminal definition
terminals = {
  'L0': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'W0': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'H0': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'L1': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'W1': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'H1': np.random.random_integers(MIN, MAX, NB_EXAMPLES)
}



#Compute the result
attended = terminals['L0']*terminals['W0']*terminals['H0'] - terminals['L1']*terminals['W1']*terminals['H1'] 


def change_fitness_case():
    """Re-compute again the fitness case."""

    #XXX pb when reevaluating new trees
    return

    print 'Change fitness cases'

    global terminals
    global attended

    terminals['L0'] = np.random.random_integers(MIN, MAX, NB_EXAMPLES)
    terminals['W0'] = np.random.random_integers(MIN, MAX, NB_EXAMPLES)
    terminals['H0'] = np.random.random_integers(MIN, MAX, NB_EXAMPLES)
    terminals['L1'] = np.random.random_integers(MIN, MAX, NB_EXAMPLES)
    terminals['W1'] = np.random.random_integers(MIN, MAX, NB_EXAMPLES)
    terminals['H1'] = np.random.random_integers(MIN, MAX, NB_EXAMPLES)


    attended = terminals['L0']*terminals['W0']*terminals['H0'] - terminals['L1']*terminals['W1']*terminals['H1'] 

#Fitness function (sum of the absolute difference between result and attended)
def fitness_function(tree):
    """Compute the fitness value of the tree.
    For each fitness case, the absolute difference between the tree value and the real value is computed.
    Theses fitness are added together.
    The closer this sum of errors is to 0, the better the program.
    """

    global fte
    
    compiled_tree = fte.compile_tree(tree, one_input_set=False)
    values = eval(compiled_tree, None, {'self': fte}) #the tree is evaluated only one time (inputs are arrays)

    
    res = np.sum(np.abs(values - attended))

    del values
    del compiled_tree

    return res

#Build the tree rules
default_function_set = [
        (1,2,'+'),
        (1,2,'-'),
        (1,2,'*'),
        (1,2,'%'),
        ]
default_terminal_set = [
        (3,0,'H0'),
        (3,0,'W0'),
        (3,0,'H0'),
        (3,0,'W1'),
        (3,0,'L1'),
        (3,0,'H1'),
        ]
tree_rules = {
    'root': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '+': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '-': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '*': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '%': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
        }

#Parameters
evolve = evolver.Evolver( \
        popsize=10, #16000,
        min_depth=6, #6
        max_depth=17, #17
        max_nb_runs=50,
        crossover_prob=0.9,
        mutation_prob=0.0,
        size=5,
        prob_selection=0.8,
        fitness_criterion=0.01)

gp_engine = pySTEPX.PySTEPX(start_from_scratch=False)
gp_engine.set_evolver(evolve)
gp_engine.set_tree_rules(tree_rules)
gp_engine.set_functions(functions)
gp_engine.set_terminals(terminals)
gp_engine.set_low_memory_footprint(True)
gp_engine.set_endofgeneration(change_fitness_case)

fte = evalfitness.FitnessTreeEvaluation()
fte.set_terminals(terminals)
fte.set_functions(functions)
fte.check_configuration() #global object used in the function

gp_engine.set_fitness_function(fitness_function)


def main():
    logging.basicConfig(level=logging.INFO)
    
    gen = gp_engine.sequentially_evolve()
    gen.next()

    #gp_engine.evolve()


if __name__ == "__main__":
    main()

