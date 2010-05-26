#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the hability to pystep to be able to continue an execution, if the process
has been stoped.

The test is splitted in two parts:

- run the evolution during one generation
- restart with the same database

In this case, the system must start at generation 2 and not 1.

AUTHOR Romain Giot <romain.giot@ensicaen.fr>
"""

import unittest
import os.path
import os
import random
import math

import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness


DB = '/tmp/continuation.sqlite'

class TestExecutionContinuation(unittest.TestCase):
    """
    Test the hability of the library to continue an execution.
    The goal is to:
    - allow the continuation after a bug
    - allow to shut down the computer before the end of the process
    """

    def __init__(self, a):
        """
        Suppress the database if exists.
        """
        super(TestExecutionContinuation, self).__init__(a)


    def setUp(self):
        """
        Parametrize the procedure.
        """
        if os.path.exists(DB):
            os.remove(DB)


        self._gp_engine = None


    def _create_gp(self, start_from_scratch):
        """
        Create the genetic programming engine and configure it.

        @param start_from_scratch: if True, start from scratch, if False, reload
        db
        """
        def add(listElem):
            try:
                return listElem[0]+listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def sub(listElem):
            try:
                return listElem[0]-listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def neg(listElem):
            try:
                return 0-listElem[0]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def multiply(listElem):
            try:
                return listElem[0]*listElem[1]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def square(listElem):
            try:
                return listElem[0]*listElem[0]
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def cos(listElem):
            try:
                return math.cos(listElem[0])
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def sin(listElem):
            try:
                return math.sin(listElem[0])
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def rootBranch(x):
            try:
                return x
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

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
        nb_eval = 2
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

        evolve = evolver.Evolver()

        gp_engine = pySTEPX.PySTEPX(db_path=DB,
                start_from_scratch=start_from_scratch)
        gp_engine.set_evolver(evolve)
        gp_engine.set_tree_rules(treeRules)
        gp_engine.set_functions(functions)
        gp_engine.set_terminals(terminals)


        fte = evalfitness.FitnessTreeEvaluation()
        fte.set_terminals(terminals)
        fte.set_functions(functions)
        fte.check_configuration()
        ffe = evalfitness.FinalFitness(ideal_results, nb_eval)
        def FitnessFunction(my_tree):
            return ffe.FinalFitness(
                fte.EvalTreeForAllInputSets(my_tree, xrange(nb_eval)))
        gp_engine.set_fitness_function(FitnessFunction)

        self._gp_engine = gp_engine


    def test_continuation_deactivated(self):
        """
        Test running with continuation is deactivated
        """

        #First generation
        self.assertFalse(os.path.exists(DB))

        self._create_gp(True)
        self.assertEqual( self._gp_engine.get_db_name(), DB)
        self.assertEqual( self._gp_engine.get_last_generation_number(), -1)

        gen = self._gp_engine.sequentially_evolve()
        gen.next()
        self.assertEqual( self._gp_engine.get_last_generation_number(), 0)
        gen.next()
        self.assertEqual( self._gp_engine.get_last_generation_number(), 1)

        #Second generation
        self.assertTrue(os.path.exists(DB))

        #Restart without re-loading the last generation
        self._create_gp(True)
        self.assertEqual( self._gp_engine.get_db_name(), DB)
        self.assertEqual( self._gp_engine.get_last_generation_number(), -1)

        gen = self._gp_engine.sequentially_evolve()
        gen.next()
        self.assertEqual( self._gp_engine.get_last_generation_number(), 0)
        gen.next()
        self.assertEqual( self._gp_engine.get_last_generation_number(), 1)

    def test_continuation_activated(self):
        """
        Test running with continuation is activated
        """

        #First generation
        self.assertFalse(os.path.exists(DB))

        self._create_gp(True)
        self.assertEqual( self._gp_engine.get_db_name(), DB)
        self.assertEqual( self._gp_engine.get_last_generation_number(), -1)

        gen = self._gp_engine.sequentially_evolve()
        gen.next()
        self.assertEqual( self._gp_engine.get_last_generation_number(), 0)
        gen.next()
        self.assertEqual( self._gp_engine.get_last_generation_number(), 1)

        #Second generation
        self.assertTrue(os.path.exists(DB))

        #Restart without re-loading the last generation
        self._create_gp(False)
        self.assertEqual( self._gp_engine.get_db_name(), DB)

        gen = self._gp_engine.sequentially_evolve()
        gen.next()
        self.assertEqual( self._gp_engine.get_last_generation_number(), 2)
        gen.next()
        self.assertEqual( self._gp_engine.get_last_generation_number(), 3)


if __name__ == "__main__":
    unittest.main()
