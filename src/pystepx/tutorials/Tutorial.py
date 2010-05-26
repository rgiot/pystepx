#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
:mod:`pystepx.tutorial.Tutorial` -- Tutorial 1 module
=====================================================

This module contains the :class:`pystepx.tutorial.Tutorial.Tutorial1` class, which manage the first tutorial case.


Contains all the classes providing the tutorial examples.
This examples are based on the tutorial of the original pySTEP.
"""

"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: by Romain Giot
@version: 1.00
@copyright: (c) 2010 Mehdi Khoury under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: romain.giot at ensicaen.fr
"""

import math
import random
import logging

import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness

import pystepx.tutorials.basetut as basetut




class Tutorial1(basetut.BaseTutorial):
    """
    Contains all parameters for the evolutionary run, grammar rules, constraints,
    and specifics about the terminal and function set of the trees in tutorial1.
    This example file gather all the settings for a simple polynomial regression
    using one variable x and the following mathematical operators: '+','-','neg','*','^2'(or square),'cos','sin'.
    We try to find a third degree polynomial: x^3 + x^2 + cos(x)
    from 2 sets of testing data (2 different values for x).
    Considering the constraints for building the trees, the root node will only have
    one child, and there will be no need for ADF in the function and terminal set.
    """

    def __init__(self):
        super(Tutorial1, self).__init__()

    def define_grammar(self):
        """
        Define the necessary grammar and returns:
        - the whole function set
        - the whole terminal set
        - the treeRules
        - mapping

        """

        logging.info('Generation of the functions')
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

        logging.info('Associate each function to its label')
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

        logging.info('Get the terminal nodes')
        # Definition of the terminal nodes
        # In this case, there is only x which is an array of two elements
        nb_eval = 2
        all_x = []
        for i in xrange(nb_eval):
            all_x.append(random.random()*10)

        logging.info('Set the terminal mapping')
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
        nb_eval = 2
        all_x = terminals['x']

        logging.info('Compute the ideal results')
        # Create the attended results
        # ideal polynomial to find
        ideal_results = []
        for nb in xrange(nb_eval):
            ideal_results.append([all_x[nb]**3 + all_x[nb]**2 + math.cos(all_x[nb])])

        logging.info('Create evolver')
        evolve = evolver.Evolver(
            crossover_prob=0.5, 
            mutation_prob=0.4)

        logging.info('Create and configure pySTEPX object')
        gp_engine = pySTEPX.PySTEPX()
        gp_engine.set_evolver(evolve)
        gp_engine.set_tree_rules(rules)
        gp_engine.set_functions(functions)
        gp_engine.set_terminals(terminals)


        logging.info('Set fitness evaluation')
        fte = evalfitness.FitnessTreeEvaluation()
        fte.set_terminals(terminals)
        fte.set_functions(functions)
        fte.check_configuration()
        ffe = evalfitness.FinalFitness(ideal_results, nb_eval)
        def FitnessFunction(my_tree):
            a = fte.EvalTreeForAllInputSets(my_tree, xrange(nb_eval))
            b = ffe.FinalFitness(a)
            return b

        gp_engine.set_fitness_function(FitnessFunction)

        return gp_engine


def main():
    """
    Function: main

    Launch  the set of tutorials
    """
    #logging.basicConfig(level=logging.DEBUG)

    logging.info('Launch tutorial 1')
    t = Tutorial1()
    t.run()


if __name__ == "__main__":
    main()
