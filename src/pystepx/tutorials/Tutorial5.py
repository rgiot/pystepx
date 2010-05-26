#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
:mod:`pystepx.tutorial.Tutorial5` -- Tutorial 5 module
=====================================================

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

import sys
sys.path.append("./..")



import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver
from pystepx.tree.treeutil import WrongValues
from pystepx.fitness import evalfitness

import pystepx.tutorials.basetut as basetut





class Tutorial5(basetut.BaseTutorial):
    """

    Contains all parameters for the evolutionary run, grammar rules, constraints,
    and specifics about the terminal and function set of the trees in tutorial5.

    In this example, we evolve hybrid system: a model containing discrete values
    and logic operators and numerical operations.
    More specifically, we will evolve if_then_else types rules that will determine
    the application of different polynomials...
    from 20 sets of testing data (20 different values for x and y).

    Considering the constraints for building the trees, the root node will have
    3 children, and these will be ordered ADF defining branches (we simply won't use ADF terminals nodes)
    describing the structure of the if then else statement.

    The solution found should be the equivalent of this expression:
    if x>y then cos(x) else sin(y)

    """

    def __init__(self):
        super(Tutorial5, self).__init__()

    def define_grammar(self):
        """

        Define the necessary grammar and returns:
        - the whole function set
        - the whole terminal set
        - the treeRules
        - mapping

        """

        logging.info('Generation of the functions')
        #logical functions
        def equal_(listElem):
            try:
                if listElem[0] == listElem[1]:
                    return True
                else:
                    return False
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def superior_(listElem):
            try:
                if listElem[0] > listElem[1]:
                    return True
                else:
                    return False
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def inferior_(listElem):
            try:
                if listElem[0]<listElem[1]:
                    return True
                else:
                    return False
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def and_(listElem):
            try:
                 if listElem[0] and listElem[1]:
                     return True
                 else:
                     return False
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def or_(listElem):
            try:
                 if listElem[0] or listElem[1]:
                     return True
                 else:
                     return False
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"


        #numerical
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
                exit

        #adf
        def if_(x):
            try:
                return x
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def then_(x):
            try:
                return x
            except:
                raise WrongValues, "Wrong values sent to function node.\nCan't get result"

        def else_(x):
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
        # then, we create a set of functions and associate them with the corresponding
        # processing methods
        functions = {\
            '+': add,
            '-': sub,
            'neg': neg,
            '*': multiply,
            '^2': square,
            'cos': cos,
            'sin': sin,
            '=': equal_,
            '>': superior_,
            '<': inferior_,
            'and': and_,
            'or': or_,
            'if': if_,
            'then': then_,
            'else': else_,
            'root': rootBranch
            }

        logging.info('Get the terminal nodes')
        # we create the list of all possible values a variable can have in the learning examples
        nb_eval = 20
        all_x = []
        all_y = []
        for i in xrange(nb_eval):
            all_x.append(random.random() * 10)
            all_y.append(random.random() * 10)

        logging.info('Set the terminal mapping')
        # then, we create a mapping of terminals
        # the variables will be given a value coming from a set of examples
        # the constants will just be given as such or produced by a
        # random producer
        terminals = {
                'x':all_x,
                'y':all_y
                }

        crossover_mapping=[]

        # default function set applicable by for branches:
        defaultFunctionSet= [(1,2,'+'),(1,2,'*'),(1,1,'^2'),(1,2,'-'),(1,1,'cos'),(1,1,'sin'),(1,1,'neg')]
        # default terminal set applicable by for branches:
        defaultTerminalSet= [(3,0,'x'),(3,0,'y')]
        treeRules = {'root':[([(2,1,'if')],[]),([(2,1,'then')],[]),([(2,1,'else')],[])],
                            'if':[([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[])],
                            'then':[(defaultFunctionSet,defaultTerminalSet)],
                            'else':[(defaultFunctionSet,defaultTerminalSet)],
                            'and':[([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[]),([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[])],
                            'or':[([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[]),([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[])],
                            '=':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '>':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '<':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '+':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '*':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '^2':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            '-':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],
                            'neg':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'sin')],defaultTerminalSet)],
                            'cos':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'sin'),(1,1,'neg')],defaultTerminalSet)],
                            'sin':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'neg')],defaultTerminalSet)]
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
        nb_eval = 20
        all_x = terminals['x']
        all_y = terminals['y']

        logging.info('Compute the ideal results')
        # Create the attended results
        # ideal polynomial to find
        ideal_results = []
        for nb in xrange(nb_eval):
            if all_x[nb] > all_y[nb]:
                ideal_results.append([math.cos(all_x[nb])])
            else:
                ideal_results.append([math.sin(all_y[nb])])

        logging.info('Create evolver')
        evolve = evolver.Evolver(root_node=(0,3,'root'),
                fitness_criterion=0.1,
                min_depth=3,
                max_depth=8)

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
        print ideal_results
        def FitnessFunction(my_tree):
            return ffe.FinalFitnessIfThenElse(
                fte.EvalTreeForAllInputSets(my_tree, xrange(nb_eval)))
        gp_engine.set_fitness_function(FitnessFunction)

        return gp_engine


def main():
    """

    Launch  the set of tutorials
    """
    logging.basicConfig(level=logging.DEBUG)

    logging.info('Launch tutorial 5')
    t = Tutorial5()
    t.run()


if __name__ == "__main__":
    main()
