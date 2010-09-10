#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
:mod:`pystepx.tutorial.Tutorial4` -- Tutorial 4 module
=====================================================

Contains the class managing the tutorial4 
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




class Tutorial4(basetut.BaseTutorial):
    """
    Contains all parameters for the evolutionary run, grammar rules, constraints,
    and specifics about the terminal and function set of the trees in tutorial4.

    This example file gather all the settings for a 'multiple' polynomial regression.
    We want to evolve a system of ordered polynomial equations by using the
    mathematical operators: '+','*' and the ADF: ADF1 and ADF2, in the said order.
    an ADF2 branch could then call for an ADF1 terminal, but not the opposite.

    We try to find the following model being shaped as a system of polynomials:

    |ADF1=x+y
    |ADF2=ADF1^3

    from 1 set of 1000 testing data (1000 different values for x and y).

    This time, each tree does not have to be evaluated 1000 times. We will input
    a list of 1000 data points in the variable leafs of the tree. There is not much time
    difference to process 1000 data-points than 5 when we use this trick!

    Considering the constraints for building the trees, the root node will have 2
    children ADF1 and ADF2 (in order), and ADF2 must be able to reuse ADF1 as a
    terminal...
    """

    def __init__(self):
        super(Tutorial4, self).__init__()


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
                result = []
                for i in xrange(len(listElem[0])):
                    result.append(listElem[0][i] + listElem[1][i])
                return result
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def multiply(listElem):
            try:
                result = []
                for i in xrange(len(listElem[0])):
                    result.append(listElem[0][i] * listElem[1][i])
                return result
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
        functions = {'+':add,
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
        # we create the list of all possible values a variable can have
        # Here we tell the system it only learn from one example, so it will
        # only evaluate the tree one time. The difference will be that this unique
        # variable will be an array of 200 of format 'double' ! These 200 variables
        # will then be evaluated at once when a tree is evaluated.
        all_x = []
        all_y = []
        nb_ex = 1000
        for i in xrange(nb_ex):
            all_x.append(random.random() * 10)
            all_y.append(random.random() * 10)

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
        nb_eval = 1
        nb_ex = 1000
        all_x = terminals['x']
        all_y = terminals['y']

        logging.info('Compute the ideal results')
        # Create the attended results
        # ideal polynomial to find
        ideal_results = []
        temp1 = []
        temp2 = []
        for nb in xrange(nb_ex):
            temp1.append(all_x[nb] + all_y[nb])
            temp2.append((all_x[nb] + all_y[nb])**3)
        ideal_results.append(temp1)
        ideal_results.append(temp2)


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
            return ffe.FinalFitness2(
                fte.EvalTreeForOneListInputSet(my_tree))
        gp_engine.set_fitness_function(FitnessFunction)

        return gp_engine

def main():
    """
    Launch  the set of tutorials
    """
    logging.basicConfig(level=logging.ERROR)

    logging.info('Launch tutorial 4')
    t = Tutorial4()
    t.run()


if __name__ == "__main__":
    main()
