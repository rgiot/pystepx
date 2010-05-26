#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Two boxes problem presented in Koza II.
This implementation uses the ADF representation.

We must find a function computing the difference of
volume between two boxes.

L0, W0 and H0 contains the information about box 0.
In order to evaluate the trees only one time, these variables
do not hold single values, but an array (one line per example).
Same thing for L1, W1, H1.


The aim is to find an adf which compute the volume and call two times this adf with
the parameters of the two boxes.
By convention:
  ADF0 is the definition
  _ADF0 is the calling

XXX End debuggin to activate the changing of fitness after each generation
"""


import numpy as np
from random import random
import logging

import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness_meta 
import pystepx.tree.numpyfunctions
from pystepx.tree.numpyfunctions import _add, _sub, _mul, _protected_division

from pystepx.tree.treeconstants import ROOT_BRANCH, \
                                    FUNCTION_BRANCH, \
                                    ADF_DEFINING_BRANCH, \
                                    VARIABLE_LEAF, \
                                    CONSTANT_LEAF, \
                        				    ADF_LEAF, \
   KOZA_ADF_DEFINING_BRANCH, \
   KOZA_ADF_FUNCTION_BRANCH, \
   KOZA_ADF_PARAMETER

MIN = 1
MAX = 200
NB_EXAMPLES = 10

def _root_branch(inputs):
    """Return the input."""
    return inputs

#Function definition
functions = {
    '+': _add,
    '-': _sub,
    '*': _mul,
    '%': _protected_division,
    '_root': _root_branch, 

    '_ADF0': None, #Automatically computed
    'ADF0': None, #Just to choose (maybe as root ?)
    'ADF0_+': _add,
    'ADF0_-': _sub,
    'ADF0_*': _mul,
    'ADF0_%': _protected_division,

}

#Terminal definition
#We first set the real terminals, then the ADF0 ones
terminals = {
  'L0': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'W0': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'H0': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'L1': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'W1': np.random.random_integers(MIN, MAX, NB_EXAMPLES),
  'H1': np.random.random_integers(MIN, MAX, NB_EXAMPLES),

  '_ADF0_PARAM0': None, #Automatically set, must respect this syntax
  '_ADF0_PARAM1': None, #Automatically set
  '_ADF0_PARAM2': None, #Automatically set
}



#Compute the result
attended = terminals['L0']*terminals['W0']*terminals['H0'] - terminals['L1']*terminals['W1']*terminals['H1'] 


#Fitness function (sum of the absolute difference between result and attended)
def fitness_function(tree):
    """Compute the fitness value of the tree.
    For each fitness case, the absolute difference between the tree value and the real value is computed.
    Theses fitness are added together.
    The closer this sum of errors is to 0, the better the program.
    """

    global fte
    values = fte.eval_with_adf(tree)
    
    return np.sum(np.abs(values - attended))

#Build the tree rules

#Program part
default_function_set = [
        (FUNCTION_BRANCH, 2, '+'),
        (FUNCTION_BRANCH, 2, '-'),
        (FUNCTION_BRANCH, 2, '*'),
        (FUNCTION_BRANCH, 2, '%'),
        (KOZA_ADF_FUNCTION_BRANCH, 3, '_ADF0'),
        ]
adf0_call_function_set =  [
        (FUNCTION_BRANCH, 2, '+'),
        (FUNCTION_BRANCH, 2, '-'),
        (FUNCTION_BRANCH, 2, '*'),
        (FUNCTION_BRANCH, 2, '%'),
]

default_terminal_set = [
        (VARIABLE_LEAF, 0, 'H0'),
        (VARIABLE_LEAF, 0, 'W0'),
        (VARIABLE_LEAF, 0, 'H0'),
        (VARIABLE_LEAF, 0, 'W1'),
        (VARIABLE_LEAF, 0, 'L1'),
        (VARIABLE_LEAF, 0, 'H1'),
        ]

#ADF0 part
adf0_function_set = [
        (FUNCTION_BRANCH, 2, 'ADF0_+'),
        (FUNCTION_BRANCH, 2, 'ADF0_-'),
        (FUNCTION_BRANCH, 2, 'ADF0_*'),
        (FUNCTION_BRANCH, 2, 'ADF0_%'),
]
adf0_terminal_set = [
        (KOZA_ADF_PARAMETER, 0, 'ADF0_PARAM0'),
        (KOZA_ADF_PARAMETER, 0, 'ADF0_PARAM1'),
        (KOZA_ADF_PARAMETER, 0, 'ADF0_PARAM2'),
    ]

#The first member of the root, is the ADF0, the second is the program
tree_rules = {
    'root': [ ( [(KOZA_ADF_DEFINING_BRANCH, 1, 'ADF0')], []), ([(ROOT_BRANCH, 1, '_root')], [] )], 
      
    '_root': [(default_function_set, default_terminal_set)],

    '+': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '-': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '*': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '%': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '_ADF0': [ (adf0_call_function_set, default_terminal_set), 
               (adf0_call_function_set, default_terminal_set),
               (adf0_call_function_set, default_terminal_set),
               ],
 
    'ADF0': [ (adf0_function_set, adf0_terminal_set), (adf0_function_set, adf0_terminal_set)],
    'ADF0_+': [ (adf0_function_set, adf0_terminal_set), (adf0_function_set, adf0_terminal_set)],
    'ADF0_-': [ (adf0_function_set, adf0_terminal_set), (adf0_function_set, adf0_terminal_set)],
    'ADF0_*': [ (adf0_function_set, adf0_terminal_set), (adf0_function_set, adf0_terminal_set)],
    'ADF0_%': [ (adf0_function_set, adf0_terminal_set), (adf0_function_set, adf0_terminal_set)],


        }

#Parameters
evolve = evolver.Evolver( \
        popsize=400, #4000
        min_depth=6, #6
        max_depth=10, #17
        max_nb_runs=50,
        crossover_prob=0.9,
        mutation_prob=0.0,
        size=5,
        prob_selection=0.8,
        fitness_criterion=0.01,
        root_node = (ROOT_BRANCH, 2, 'root'), #! For adf
        )

gp_engine = pySTEPX.PySTEPX(start_from_scratch=True)
gp_engine.set_evolver(evolve)
gp_engine.set_tree_rules(tree_rules)
gp_engine.set_functions(functions)
gp_engine.set_terminals(terminals)

fte = evalfitness_meta.FitnessTreeEvaluation_meta()
fte.set_terminals(terminals)
fte.set_functions(functions)
fte.check_configuration() #global object used in the function

gp_engine.set_fitness_function(fitness_function)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gp_engine.evolve()
