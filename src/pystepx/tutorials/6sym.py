#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Resolve the 6 symetry problem,
Koza II, p 122

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


def _root_branch(inputs):
    """Return the input."""
    return inputs

functions = {'and': _and,
             'or': _or,
             'nand': _nand,
             'nor': _nor,
             'root': _root_branch,
             }# Build the engine


# terminal nodes

def build_cases():
    tmp = [[],[],[],[],[],[]]

    for i in range(64):
        digits = [(i >> n) & 1 for n in range(6)]
        for j in range(6):
            tmp[j].append(digits[j])

    return (np.array(tab) for tab in tmp)


def compute_res(D0,D1,D2,D3,D4,D5):
    return np.logical_and(
      D0==D5,
      D1==D4,
      D2==D3)

_D0,_D1,_D2,_D3,_D4,_D5 = build_cases()
_res = compute_res(_D0,_D1,_D2,_D3,_D4,_D5)

terminals = { 'D0': _D0,
              'D1': _D1,
              'D2': _D2,
              'D3': _D3,
              'D4': _D4,
              'D5': _D5,
              }


# yping
default_function_set = [
        (1,2,'and'),
        (1,2,'or'),
        (1,2,'nor'),
        (1,2,'nand'),
        ]
default_terminal_set = [
        (3,0,'D0'),
        (3,0,'D1'),
        (3,0,'D2'),
        (3,0,'D3'),
        (3,0,'D4'),
        (3,0,'D5'),
        ]

tree_rules = {
    'root': [ (default_function_set, default_terminal_set) ],
    'or': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    'and': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    'nor': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    'nand': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
        }

fte = evalfitness.FitnessTreeEvaluation()
fte.set_terminals(terminals)
fte.set_functions(functions)
fte.check_configuration()

def fitness_function(my_tree):
    """Evaluation of the tree."""

    res =  fte.EvalTreeForOneListInputSet(my_tree) == _res
    #raw = np.sum(res)
    std = np.sum(res == False)
    return std



evolve = evolver.Evolver( \
        popsize=500,#16000
        min_depth=3,
        max_depth=10,#17
        max_nb_runs=50,
        crossover_prob=0.7,
        mutation_prob=0,
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
