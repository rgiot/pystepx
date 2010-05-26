#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Resolve the XOR problem.
We have to find the xor function:
  xor(x1,x2)= | 1 if x1 != x2
              | 0 otherwise


Numpy is used to evaluate trees on the list of input.
"""


import numpy as np

import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness

#List of functions (and, or, nor, nand, i)

def _and(inputs):
    """Return a logical and."""
    return np.logical_and(inputs[0],  inputs[1])

def _or(inputs):
    """Return a logical and."""
    return np.logical_or(inputs[0],  inputs[1])

def _nand(inputs):
    """Return a logical and."""
    return np.logical_not(np.logical_and(inputs[0],  inputs[1]))

def _nor(inputs):
    """Return a logical and."""
    return np.logical_not(np.logical_or(inputs[0],  inputs[1]))

def _identity(inputs):
    """Identity"""
    return inputs[0]

def _root_branch(inputs):
    """Return the input."""
    return inputs

functions = {'and': _and,
             'or': _or,
             'nand': _nand,
             'nor': _nor,
             'identity': _identity,
             'root': _root_branch,
             }# Build the engine


# terminal nodes

_x1 = np.array([True, True, False, False])
_x2 = np.array([True, False, True, False])
_res = np.logical_xor(_x1, _x2)

terminals = { 'x1': _x1,
              'x2': _x2,
              }


# yping
default_function_set = [
        (1,2,'and'),
        (1,2,'or'),
        (1,2,'nor'),
        (1,2,'nand'),
        (1,1,'identity')
        ]
default_terminal_set = [
        (3,0,'x1'),
        (3,0,'x2'),
        ]

tree_rules = {
    'root': [ (default_function_set, default_terminal_set) ],
    'or': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    'and': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    'nor': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    'nand': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    'identity': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
        }

fte = evalfitness.FitnessTreeEvaluation()
fte.set_terminals(terminals)
fte.set_functions(functions)
fte.check_configuration()

def fitness_function(my_tree):
    """Evaluation of the tree."""

    tmp =  fte.EvalTreeForOneListInputSet(my_tree) == _res
    return 4 - np.sum(tmp)



evolve = evolver.Evolver( \
        popsize=200,
        min_depth=3,
        max_depth=5,
        max_nb_runs=20,
        crossover_prob=0.7,
        mutation_prob=0.25,
        size=7,
        prob_selection=0.8)

gp_engine = pySTEPX.PySTEPX(start_from_scratch=True)
gp_engine.set_evolver(evolve)
gp_engine.set_tree_rules(tree_rules)
gp_engine.set_functions(functions)
gp_engine.set_terminals(terminals)
gp_engine.set_fitness_function(fitness_function)


def main():
    gp_engine.evolve()
if __name__ == "__main__":
    main()
