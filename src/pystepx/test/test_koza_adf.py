#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The aim of this testsuite is to verify if
koza adf run normally.

AUTHOR Romain Giot <romain.giot@ensicaen.fr>
DATE 09/09/2010
"""

import unittest
import random

import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness_meta, evalfitness

from pystepx.tree.treeconstants import ROOT_BRANCH, \
                                    FUNCTION_BRANCH, \
                                    ADF_DEFINING_BRANCH, \
                                    VARIABLE_LEAF, \
                                    CONSTANT_LEAF, \
                                    ADF_LEAF, \
                                    KOZA_ADF_DEFINING_BRANCH, \
                                    KOZA_ADF_FUNCTION_BRANCH, \
                                    KOZA_ADF_PARAMETER

class TestTreeKozaADF(unittest.TestCase):

    def __define_grammar(self):
        """
        We assert that this function has no bugs

        Define the necessary grammar and returns:
        - the whole function set
        - the whole terminal set
        - the treeRules
        - mapping

        """

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


        def rootBranch(x):
            try:
                print x
                #merge results
                a = x[0]
                b = x[1]
                c = [ [i,j] for i,j in zip(a,b)]
                return c
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"


        def adfRootBranch(x):
            return x

        # Associate each function to its label
        functions = {
            '+': add,
            '*': multiply,
            '_root': rootBranch,

             '_ADF0': None, #Automatically computed
             'ADF0': None, #Just to choose (maybe as root ?)
             'ADF0_+': add,
             'ADF0_*': multiply,

            }

        # when swapping subtrees during crossover, we can transform the following branches:
        # + can be transformed into ADF2_+, and so on...
        crossover_mapping = [('+','adf2_+'),('adf2_+','+'),('*','adf2_*'),('adf2_*','*')]

        nb_eval = 30
        all_x = []
        all_y = []
        for i in xrange(nb_eval):
            all_x.append(random.random()*10)
            all_y.append(random.random()*10)

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

    def __build_engine(self, functions, terminals, rules):
        """Build the engine

        @param functions: dictionnary of the function set
        @param terminals: dictionnary of the terminals

        @return the generated gp_engine
        """
        nb_eval = 30
        all_x = terminals['x']
        all_y = terminals['y']

        # Create the attended results
        # ideal polynomial to find
        ideal_results = []
        for nb in xrange(nb_eval):
            ideal_results.append([all_x[nb] + all_y[nb], (all_x[nb] + all_y[nb]) ** 3])

        evolve = evolver.Evolver( popsize=2000, root_node=(0, 2, 'root'))

        gp_engine = pySTEPX.PySTEPX()
        gp_engine.set_evolver(evolve)
        gp_engine.set_tree_rules(rules)
        gp_engine.set_functions(functions)
        gp_engine.set_terminals(terminals)
        gp_engine.set_strongly_typed_crossover_degree(True)
        gp_engine.set_adf_ordered(True)



        fte = evalfitness_meta.FitnessTreeEvaluation_meta()
        fte.set_terminals(terminals)
        fte.set_functions(functions)
        fte.check_configuration()
        ffe = evalfitness.FinalFitness(ideal_results, nb_eval)

        return fte, ffe

        def FitnessFunction(my_tree):
            res = fte.eval_with_adf(my_tree)
            return ffe.FinalFitness(res)
        gp_engine.set_fitness_function(FitnessFunction)

        return gp_engine

    def test_tree_with_adf_evaluation(self):
        """Test the evaluation of a tree with an adf."""

        #Initialisation
        functions, terminals, rules, mapping = self.__define_grammar()
        fte, ffe = self.__build_engine( functions, terminals, rules)
        terminals = fte.get_terminals()


        # Tree and its evaluation function by and
        tree = [(0, 2, 'root'), [(6, 1, 'ADF0'), [(1, 2, 'ADF0_+'), (8, 0,
            'ADF0_PARAM0'), (8, 0, 'ADF0_PARAM1')]], [(0, 2, '_root'), [(7, 2,
                '_ADF0'), (3, 0, 'x'), (3, 0, 'y')], [(1, 2, '*'), (3, 0, 'x'), (3, 0, 'y')]]]
        def __adf0(param0, param1):
            return param0 + param1
        def __tree(x, y):
            return  [__adf0(x, y), x*y]
        def __real_results(x, y):
            res = []
            for i in range(len(x)):
                res.append(__tree(x[i], y[i]))
            return res

        computed_results = fte.eval_with_adf(tree)
        expected_results = __real_results(terminals['x'], terminals['y'])

        print computed_results[0]
        print expected_results[0]
        self.assertEqual(computed_results, expected_results, "ADF evaluation erroneous")

if __name__ == "__main__":
    unittest.main()
