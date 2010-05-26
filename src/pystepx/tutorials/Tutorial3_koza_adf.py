#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
:mod:`pystepx.tutorial.Tutorial3` -- Tutorial 3 module
=====================================================

Contains the class managing the tutorial 3
"""

# AUTHOR Romain Giot <romain.giot@ensicaen.fr>


import random
import logging
import sys
sys.path.append("./..")

import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness_meta, evalfitness

import pystepx.tutorials.basetut as basetut




from pystepx.tree.treeconstants import ROOT_BRANCH, \
                                    FUNCTION_BRANCH, \
                                    ADF_DEFINING_BRANCH, \
                                    VARIABLE_LEAF, \
                                    CONSTANT_LEAF, \
                        				    ADF_LEAF, \
   KOZA_ADF_DEFINING_BRANCH, \
   KOZA_ADF_FUNCTION_BRANCH, \
   KOZA_ADF_PARAMETER

import psyco
psyco.profile()

class Tutorial3(basetut.BaseTutorial):
    """
    Contains all parameters for the evolutionary run, grammar rules, constraints,
    and specifics about the terminal and function set of the trees in tutorial3.

    This example file gather all the settings for a 'multiple' polynomial regression.
    We want to evolve a system of ordered polynomial equations by using the
    mathematical operators: '+','*' and the an ADF.
    
    The main program must used the adf function and returns the score of two equation systems,
    which we will not child1 and child2 (referring to ADF1 and ADF2 in Tutorial3).

    We try to find the following model being shaped as a system of polynomials:

    |child1=x+y
    |child2=child^3

    from 30 sets of testing data (30 different values for x and y).
    This means the each tree has to be evaluated for every different example,
    so 30 times. There is an alternative solution which we will see in the next tutorial,
    where instead of evaluating a tree 30 times, we will input an array of 30 data in the
    variable leafs of the tree.

    In the original tutorial, the generated ADF have no arguments and return one value (this is not 
    the same kind of ADFs than in Koza books).
    In this tutorial, the ADF is a real function with arguments and which can be called 
    several times with various parameters.

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
            logging.info('add')
            try:
                result = []
                for i in xrange(len(listElem[0])):
                    result.append(listElem[0][i] + listElem[1][i])
                return result
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def multiply(listElem):
            logging.info('mul')
            try:
                result = []
                for i in xrange(len(listElem[0])):
                    result.append(listElem[0][i] * listElem[1][i])
                return result
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"


        def rootBranch(x):
            logging.info('root')
            try:
                #merge results
                a = x[0]
                b = x[1]
                c = [ [i,j] for i,j in zip(a,b)]
                logging.debug(c)
                return c
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

 

        logging.info('Associate each function to its label')
        functions = {
            '+':add,
            '*':multiply,
            '_root':rootBranch,

             '_ADF0': None, #Automatically computed
             'ADF0': None, #Just to choose (maybe as root ?)
             'ADF0_+': add,
             'ADF0_*': multiply,

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
                'x': all_x,
                'y': all_y,
                
                '_ADF0_PARAM0': None, #Automatically set, must respect this syntax
                '_ADF0_PARAM1': None, #Automatically set

                }


        # default function set applicable by for main program
        default_function_set = [
            (1,2,'+'), 
            (1,2,'*'),
            (KOZA_ADF_FUNCTION_BRANCH, 2, '_ADF0'),
            ]
        # default function set for the adf
        adf0_call_function_set = [
            (1,2,'+'), 
            (1,2,'*'),
        ]

        # default terminal set for main program or adf call
        default_terminal_set = [(3,0,'x'), (3,0,'y')]


        #ADF0 part
        adf0_function_set = [
                (FUNCTION_BRANCH, 2, 'ADF0_+'),
                (FUNCTION_BRANCH, 2, 'ADF0_*'),
        ]
        adf0_terminal_set = [
                (KOZA_ADF_PARAMETER, 0, 'ADF0_PARAM0'),
                (KOZA_ADF_PARAMETER, 0, 'ADF0_PARAM1'),
            ]

        #The first member of the root, is the ADF0, the second is the program
        tree_rules = {
            'root': [ ( [(KOZA_ADF_DEFINING_BRANCH, 1, 'ADF0')], [] ), #ADF
                      ( [(0,2,'_root')], [])],          #because their is only one main program
            '_root': [
                      (default_function_set, default_terminal_set), #equation 1
                      (default_function_set, default_terminal_set), #equation 2
                      ],

            '+': [  (default_function_set, default_terminal_set), 
                    (default_function_set, default_terminal_set)],
            '*': [  (default_function_set, default_terminal_set),
                    (default_function_set, default_terminal_set)],
            '_ADF0': [ (adf0_call_function_set, default_terminal_set), 
                       (adf0_call_function_set, default_terminal_set)],
         
            'ADF0': [ (adf0_function_set, adf0_terminal_set)],
            'ADF0_+': [ (adf0_function_set, adf0_terminal_set), (adf0_function_set, adf0_terminal_set)],
            'ADF0_*': [ (adf0_function_set, adf0_terminal_set), (adf0_function_set, adf0_terminal_set)],

                }


        return functions, \
                terminals, \
                tree_rules, \
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
        fte = evalfitness_meta.FitnessTreeEvaluation_meta()
        fte.set_terminals(terminals)
        fte.set_functions(functions)
        fte.check_configuration()
        ffe = evalfitness.FinalFitness(ideal_results, nb_eval)
        def FitnessFunction(my_tree):
            res = fte.eval_with_adf(my_tree)
            logging.debug(res)
            return ffe.FinalFitness(res)
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
