#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module test if there is no problems with the tree evaluation in a compiled
way.

AUTHOR Romain Giot <romain.giot@ensicaen.fr>
"""

import unittest
import random
import math
import time

from pystepx.tree.treeutil import WrongValues
from pystepx.tree import buildtree
from pystepx.fitness import evalfitness


class TestTreeCompilation(unittest.TestCase):
    """
    Tree compilation tester.
    """

    def setUp(self):
        """
        Build some randomly chosen trees.
        """

    #GP configuration
        def add(listElem):
            try:
                return listElem[0]+listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"+str(listElem)

        def sub(listElem):
            try:
                return listElem[0]-listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"+str(listElem)


        def neg(listElem):
            try:
                return 0-listElem[0]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"+str(listElem)


        def multiply(listElem):
            try:
                return listElem[0]*listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"+str(listElem)


        def square(listElem):
            try:
                return listElem[0]*listElem[0]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"+str(listElem)


        def cos(listElem):
            try:
                return math.cos(listElem[0])
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"+str(listElem)


        def sin(listElem):
            try:
                return math.sin(listElem[0])
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"+str(listElem)


        def rootBranch(x):
            try:
                return x
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"+str(listElem)


        # then, we create a set of functions and associate them with the corresponding
        # processing methods
        functions = {'+':   add,
                    '-':    sub,
                    'neg':  neg,
                    '*':    multiply,
                    '^2':   square,
                    'cos':  cos,
                    'sin':  sin,
                    'root': rootBranch
                    }

        # Definition of the terminal nodes
        # In this case, there is only x which is an array of two elements
        nb_eval = 20
        all_x = []
        for i in xrange(nb_eval):
            all_x.append(random.random()*10)

        # then, we create a mapping of terminals
        # the variables will be given a value coming from a set of examples
        # the constants will just be given as such or produced by a
        # random producer
        terminals = {
                'x': all_x
        }

        # default function set applicable by for branches:
        defaultFunctionSet= [(1,2,'+'), (1,2,'*'), (1,1,'^2'), (1,2,'-'), (1,1,'cos'), (1,1,'sin'), (1,1,'neg')]
        # default terminal set applicable by for branches:
        defaultTerminalSet= [(3,0,'x')]
        treeRules = {'root':[(defaultFunctionSet,defaultTerminalSet)],
                            '+':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '*':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '^2':[(defaultFunctionSet,defaultTerminalSet)],
                            '-':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            'neg':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'sin')],defaultTerminalSet)],
                            'cos':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'sin'),(1,1,'neg')],defaultTerminalSet)],
                            'sin':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'neg')],defaultTerminalSet)]
                            }


        ideal_results = []
        for nb in xrange(nb_eval):
            ideal_results.append([all_x[nb]**3 + all_x[nb]**2 + math.cos(all_x[nb])])

        #Build the trees
        builder = buildtree.BuildTree(treeRules)
        self._trees = []
        for nb in xrange(100):
            self._trees.append(builder.AddHalfNode( (0,1,'root'), 0, 2, 10))

        #Store the evaluators
        fte = evalfitness.FitnessTreeEvaluation()
        fte.set_terminals(terminals)
        fte.set_functions(functions)
        fte.check_configuration()
        ffe = evalfitness.FinalFitness(ideal_results, nb_eval)

        def FitnessFunction(my_tree):
            return ffe.FinalFitness(
                fte.EvalTreeForAllInputSets(my_tree, xrange(nb_eval)))
        self._fitness1 = FitnessFunction

        def FitnessFunction2(my_tree):
            return ffe.FinalFitness(
                fte.EvalTreeForAllInputSetsCompiled(my_tree, xrange(nb_eval)))
        self._fitness2 = FitnessFunction2


    def test_tree_compilation_succed(self):
        """
        Test if the tree compilation works.
        """
        for tree in self._trees:
            fit1 = self._fitness1(tree)
            fit2 = self._fitness2(tree)

            self.assertEqual(fit1, fit2)


    def test_compilation_faster(self):
        """
        Test if compilation is faster than interpretation.
        Need to evaluate several times the tree
        """
        a, b = 0, 0
        t0 = time.clock()
        for tree in self._trees:
            fit1 = self._fitness1(tree)
        a = time.clock() -t0

        t0 = time.clock()
        for tree in self._trees:
            fit2 = self._fitness2(tree)
        b = time.clock() -t0

	print a, b
        self.assertTrue(a>b)

if __name__ == "__main__":
    unittest.main()
