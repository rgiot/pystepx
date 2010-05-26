#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Resolves the problem of car centering.
"""

from random import random
import logging

import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness


#list of the functions
def _add(inputs):
    """Add two numbers together."""
    return inputs[0] + inputs[1]

def _sub(inputs):
    """Substract two numbers together."""
    return inputs[0] - inputs[1]

def _mul(inputs):
    """Multiply two numbers together."""
    return inputs[0] * inputs[1]

def _div(inputs):
    """Divides two numbers together.
    TODO protect the division.
    """
    if inputs[1] == 0:
        return 1
    else:
        return inputs[0] / inputs[1]

def _abs(inputs):
    """Returns the absolute value of the first input."""
    return abs(inputs[0])

def _gt(inputs):
    """Returns 1 if the value returned by the first child node is greater than the value returned by the second child node, -1 otherwise.
    """
    if inputs[0] > inputs[1]:
        return 1.0
    else:
        return -1.0


def _root_branch(inputs):
    """Return the input."""
    return inputs

functions = {'+': _add,
             '-': _sub,
             '*': _mul,
             '/': _div,
             'abs': _abs,
             '>': _gt,
             'root': _root_branch,
             }


#Definition of terminals
#In this example, values are set at execution.
terminals = { 'velocity': 0,
        'position': 0,
        '-1': -1}

NB_STEP_ERC = 10
begin = -5
end = 5
step = begin
set_ERC = []
for i in xrange(NB_STEP_ERC):
    step = (end-begin)/NB_STEP_ERC + step
    terminals[':'+str(i+1)] = step
    set_ERC.append((4,0,':'+str(i+1)))

#Definition of grammar

default_function_set = [
        (1,2,'+'),
        (1,2,'-'),
        (1,2,'*'),
        (1,2,'/'),
        (1,1,'abs')
        ]
default_terminal_set = [
        (3,0,'velocity'),
        (3,0,'position'),
        (3,0,'-1'),
        ]

default_terminal_set.extend(set_ERC)

tree_rules = {
    'root': [ ([(1, 2, '>')], []) ], #only the condition
    '>': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '+': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '-': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '*': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    '/': [ (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)],
    'abs': [ (default_function_set, default_terminal_set)],
        }
#fitness function
def fitness_function(my_tree): 
    """Apply the formula.
    The tree is evaluated 20 times with various input values.
    The car stops when its velocity approach 0 at position 0.
    """
    #logging.info('Eval tree')
    #logging.info(my_tree)

    global fte
    
    compiled_tree = fte.compile_tree(my_tree, one_input_set=False)

    sum = 0.0
    for  i in xrange(20):
        velocity = 1.5 * random() - 0.75
        position = 1.5 * random() - 0.75
        time = 0

        while time < 10 \
                and (abs(velocity) > 0.01 or abs(position) > 0.01) :

            #set the terminal values of the individual
            terminals['velocity'] = velocity
            terminals['position'] = position

            thrust = eval(compiled_tree, None, {'self': fte})
            velocity += thrust[0] * 0.02
            position += velocity * 0.02

            time += 0.2
      
        sum += time
    
    return sum
  

# Build the engine
evolve = evolver.Evolver( \
        popsize=100,
        min_depth=3,
        max_depth=10,
        max_nb_runs=200,
        crossover_prob=0.5,
        mutation_prob=0.25,
        size=5,
        prob_selection=0.8)

gp_engine = pySTEPX.PySTEPX(start_from_scratch=True)
gp_engine.set_evolver(evolve)
gp_engine.set_tree_rules(tree_rules)
gp_engine.set_functions(functions)
gp_engine.set_terminals(terminals)
gp_engine.set_strongly_typed_crossover_degree(False)


fte = evalfitness.FitnessTreeEvaluation()
fte.set_terminals(terminals)
fte.set_functions(functions)
fte.check_configuration() #global object used in the function

gp_engine.set_fitness_function(fitness_function)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gp_engine.evolve()
