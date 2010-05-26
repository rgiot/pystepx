#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Solve the same problem than in Tutorial 3, expect
that in this case, we use the real Koza ADFs.
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






class Tutorial3(basetut.BaseTutorial):
    """
    Contains all parameters for the evolutionary run, grammar rules, constraints,
    and specifics about the terminal and function set of the trees in tutorial3.

    This example file gather all the settings for a 'multiple' polynomial regression.
    We want to evolve a system of ordered polynomial equations by using the
    mathematical operators: '+','*' and the ADF: ADF1 and ADF2, in the said order.

    an ADF2 branch could then call for an ADF1 terminal, but not the opposite.
    We try to find the following model being shaped as a system of polynomials:

    |ADF1=x+y

    |ADF2=ADF1^3

    from 30 sets of testing data (30 different values for x and y).
    This means the each tree has to be evaluated for every different example,
    so 30 times. There is an alternative solution which we will see in the next tutorial,
    where instead of evaluating a tree 30 times, we will input an array of 30 data in the
    variable leafs of the tree.

    Considering the constraints for building the trees, the root node will have 2 children ADF1 and ADF2 (in order),
    and ADF2 must be able to reuse ADF1 as a terminal...
    """

    def __init__(self):
        super(Tutorial3, self).__init__()


    def define_grammar(self):
        """
        Define the necessary grammar and returns:
        - the whole function set
        - the whole terminal set
        - the treeRules
        - mapping

        """

        logging.info('Generation of the functions')
        # first, we create result processing methods for each function:
        def add(listElem):
            try:
                return listElem[0]+listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def multiply(listElem):
            try:
                return listElem[0]*listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def adfBranch(x):
            try:
                return x
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def rootBranch(x):
            try:
                return x
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"



        logging.info('Associate each function to its label')
        functions = {
            '+':add,
            '*':multiply,
            'adf2_+':add,
            'adf2_*':multiply,
            'adf1':adfBranch,
            'adf2':adfBranch,
            'root':rootBranch
            }

        logging.info('Set the crossover mapping')
        # when swapping subtrees during crossover, we can transform the following branches:
        # + can be transformed into ADF2_+, and so on...
        crossover_mapping = [('+','adf2_+'),('adf2_+','+'),('*','adf2_*'),('adf2_*','*')]

        logging.info('Get the terminal nodes')
        nb_eval = 30
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


        # default function set applicable by for branches:
        defaultFunctionSet = [(1,2,'+'), (1,2,'*')]
        # default terminal set applicable by for branches:
        defaultTerminalSet = [(3,0,'x'), (3,0,'y')]
        Adf2DefaultFunctionSet = [(1,2,'adf2_+'), (1,2,'adf2_*')]
        Adf2DefaultTerminalSet = [(3,0,'x'), (3,0,'y'), (5,0,'adf1')]
        treeRules = {'root':[ ([(2,1,'adf1')],[]) , ([(2,1,'adf2')],[]) ],
                            'adf1':[(defaultFunctionSet,defaultTerminalSet)],
                            'adf2':[(Adf2DefaultFunctionSet,Adf2DefaultTerminalSet)],
                            '+':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '*':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            'adf2_+':[(Adf2DefaultFunctionSet,Adf2DefaultTerminalSet),(Adf2DefaultFunctionSet,Adf2DefaultTerminalSet)],
                            'adf2_*':[(Adf2DefaultFunctionSet,Adf2DefaultTerminalSet),(Adf2DefaultFunctionSet,Adf2DefaultTerminalSet)],
                            }

        return functions, \
                terminals, \
                treeRules, \
                crossover_mapping

    def build_engine(self, functions, terminals, rules):
        """Build the engine

        @param functions: dictionnary of the function set
        @param terminals: dictionnary of the terminals

        @return the generated gp_engine
        """
        nb_eval = 30
        all_x = terminals['x']
        all_y = terminals['y']

        logging.info('Compute the ideal results')
        # Create the attended results
        # ideal polynomial to find
        ideal_results = []
        for nb in xrange(nb_eval):
            ideal_results.append([all_x[nb] + all_y[nb], (all_x[nb] + all_y[nb]) ** 3])
        logging.info('Create evolver')
        evolve = evolver.Evolver( popsize=2000, root_node=(0, 2, 'root'))

        logging.info('Create and configure pySTEPX object')
        gp_engine = pySTEPX.PySTEPX()
        gp_engine.set_evolver(evolve)
        gp_engine.set_tree_rules(rules)
        gp_engine.set_functions(functions)
        gp_engine.set_terminals(terminals)
        gp_engine.set_strongly_typed_crossover_degree(True)
        gp_engine.set_adf_ordered(True)



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

    logging.info('Launch tutorial 3')
    t = Tutorial3()
    t.run()


if __name__ == "__main__":
    main()
