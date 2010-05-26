#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
:mod:`pystepx.tutorial.Tutorial2` -- Tutorial 2 module
=====================================================

Contains the class managing the tutorial 2
"""

# AUTHOR Romain Giot <romain.giot@ensicaen.fr>


import random
import logging
import sys
sys.path.append("./..")


import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness

import pystepx.tutorials.basetut as basetut

try:
   import psyco
   psyco.full()
except:
   pass

class Tutorial2(basetut.BaseTutorial):
    """
    Contains all parameters for the evolutionary run, grammar rules, constraints,
    and specifics about the terminal and function set of the trees in tutorial2.

    This example file gather all the settings for a simple polynomial regression
    using this time 2 variables x and y, and adding random integer constants between 1 and 5,
    and the following mathematical operators: '+','-','neg','*','^2'(or square).

    We try to find the following polynomial: x^2+3y+4
    from 5 sets of testing data (5 different values for x and y).

    As Koza said, random constants are the "skeleton in Genetic Programming closet".
    Using them will definitely slow down a search...
    Any suggestions of current alternative strategies solving this problem would be
    highly welcomed :)
    Considering the constraints for building the trees, the root node will only have
    one child, and there will be no need for ADF in the function and terminal set.
    """

    def __init__(self):
        super(Tutorial2, self).__init__()


    def define_grammar(self):
        """

        Define the necessary grammar and returns:
        - the whole function set
        - the whole terminal set
        - the treeRules
        - defaultFunctionSet,
        - defaultTerminalSet
        - mapping

        """

        logging.info('Generation of the functions')
        # first, we create result processing methods for each function:
        def add(listElem):
            try:
                return listElem[0]+listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"
                exit

        def sub(listElem):
            try:
                return listElem[0]-listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"
                exit

        def neg(listElem):
            try:
                return 0-listElem[0]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"
                exit



        def multiply(listElem):
            try:
                return listElem[0]*listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"
                exit

        def square(listElem):
            try:
                return listElem[0]*listElem[0]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"
                exit


        def rootBranch(x):
            try:
                return x
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"
                exit




        logging.info('Associate each function to its label')
        # then, we create a set of functions and associate them with the corresponding
        # processing methods
        functions = {'+':add,
                    '-':sub,
                    'neg':neg,
                    '*':multiply,
                    '^2':square,
                    'root':rootBranch
                    }


        logging.info('Get the terminal nodes')
        nb_eval = 5
        all_x = []
        all_y = []
        for i in xrange(nb_eval):
            all_x.append(random.random()*10)
            all_y.append(random.random()*10)

        logging.info('Get the terminal mapping')
        # then, we create a mapping of terminals
        # the variables will be given a value coming from a set of examples
        # the constants will just be given as such or produced by a
        # random producer
        terminals = {
                'x':all_x,
                'y':all_y
                }

        # add a set of ephemeral random constants terminals depending on
        # the number of random constants to be provided in the primitive set,
        # and their range
        # here we produce 5 random integer constants from ranging from 1 to 5
        set_ERC=[]
        for i in xrange(5):
            terminals[':'+str(i+1)]=i
            set_ERC.append((4,0,':'+str(i+1)))


        # default function set applicable by for branches:
        defaultFunctionSet= [(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'neg'),(1,1,'^2')]
        # default terminal set applicable by for branches:
        defaultTerminalSet= [(3,0,'x'),(3,0,'y')]
        defaultTerminalSet.extend(set_ERC)

        treeRules = {'root':[(defaultFunctionSet,defaultTerminalSet)],
                            '+':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '*':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '^2':[(defaultFunctionSet,defaultTerminalSet)],
                            '-':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            'neg':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'^2')],defaultTerminalSet)]
                            }

        return functions, \
                terminals, \
                treeRules, \
                []

    def build_engine(self, functions, terminals, rules):
        """Build the engine

        @param functions: dictionnary of the function set
        @param terminals: dictionnary of the terminals

        @return the generated gp_engine
        """
        nb_eval = 5
        all_x = terminals['x']
        all_y = terminals['y']

        logging.info('Compute the ideal results')
        # Create the attended results
        # ideal polynomial to find
        ideal_results = []
        for nb in xrange(nb_eval):
            ideal_results.append([all_x[nb] ** 2 + (3 * all_y[nb]) + 4])

        logging.info('Create evolver')
        evolve = evolver.Evolver( popsize=2000)

        logging.info('Create and configure pySTEPX object')
        gp_engine = pySTEPX.PySTEPX()
        gp_engine.set_evolver(evolve)
        gp_engine.set_tree_rules(rules)
        gp_engine.set_functions(functions)
        gp_engine.set_terminals(terminals)
        gp_engine.set_strongly_typed_crossover_degree(False)


        logging.info('Set fitness evaluation')
        fte = evalfitness.FitnessTreeEvaluation()
        fte.set_terminals(terminals)
        fte.set_functions(functions)
        fte.check_configuration()
        ffe = evalfitness.FinalFitness(ideal_results, nb_eval)
        def FitnessFunction(my_tree):
            return ffe.FinalFitness(
                fte.EvalTreeForAllInputSets(my_tree, xrange(nb_eval)))
        gp_engine.set_fitness_function(FitnessFunction)

        return gp_engine

def main():
    """
    Launch  the set of tutorials
    """
    logging.basicConfig(level=logging.ERROR)

    logging.info('Launch tutorial 2')
    t = Tutorial2()
    t.run()


if __name__ == "__main__":
    main()
