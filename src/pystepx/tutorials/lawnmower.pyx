#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: by Romain Giot
@version: 1.30
@copyright: (c) 2010 Romain Giot under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: giot.romain at gmail.com
"""


"""
Resolves the lawnmower problem.

"""

import traceback
import random
import logging
import copy
from collections import deque

import numpy as np
cimport numpy as np
from pystepx.tree.treeconstants import NODE_TYPE, \
                                    NODE_NAME, \
                                    NB_CHILDREN
from pystepx.tree.treeconstants import ROOT_BRANCH, \
                                    FUNCTION_BRANCH, \
                                    ADF_DEFINING_BRANCH, \
                                    VARIABLE_LEAF, \
                                    CONSTANT_LEAF, \
                             		    ADF_LEAF
import pystepx.pySTEPX as pySTEPX
import pystepx.evolver as evolver


GRID_WIDTH=8

cdef class Lawnmower(object):
    """Representation of the lawnmower.
    The lawnmower see at four directions:

     * 0: up
     * 1: right
     * 2: down
     * 3 : left
    """

    cdef object _grass
    cdef int _direction
    cdef dict _position

    def __init__(self, object grass):
        self._grass = grass
        self._direction = 0
        self._position = {'x': grass.get_width()/2, 'y': grass.get_height()/2}

    def jump( self, vec):
        """Jump the lownmower"""

        self._position['x'] += vec[0]
        self._position['y'] += vec[1]

        #check bounds
        self._position['x'] %= self._grass.get_width()
        self._position['y'] %= self._grass.get_height()


        self._cut()

    def mow(self):
        """Mow the grass.

        * Perform a step forward
        * Mow the grass

        """


        #move
        if self._direction == 0:
            self._position['y'] += 1
        elif self._direction == 1:
            self._position['x'] += 1
        elif self._direction == 2:
            self._position['y'] -= 1
        else:
            self._position['x'] -= 1


        #check bounds
        self._position['x'] %= self._grass.get_width()
        self._position['y'] %= self._grass.get_height()

        self._cut()
        return np.array( [0,0])

    def _cut(self):
        """Cut the grass"""
        self._grass.remove_grass_in(self._position)

    def turn_left(self):
        """Turn left"""
        self._direction = (self._direction - 1) % 4

        return np.array( [0,0])


cdef class Grass(object):
      """Representation of the grass.

       * 1 in the grass means there is grass
       * 0 in the grass means there is no grass
      """

      cdef np.ndarray _grass 

      def __init__(self, width=GRID_WIDTH, height=GRID_WIDTH):
          """Build the grass.
          """
          self._grass = np.ones( (width, height))

      cpdef is_there_any_grass_in( self, dict position):
          """Return tree if there is food at position.
          """
          return self._grass[position['x'],position['y']] == 1

      def remove_grass_in(self, dict position):
          """Remove the food at the required position.
          """
          self._grass[ position['x'], position['y']] = 0

      cpdef int get_width(self):
          return self._grass.shape[0]
      cpdef int get_height(self):
          return self._grass.shape[1]


      cpdef int nb_cutted_grass(self):
        """Return the quantity of cutted grasse"""

        return np.sum(self._grass == 0)

#definition of functions
cpdef _evaluate(dict context, my_tree):
    """Evaluate the tree.
    Each function call it.
    """


    if type(my_tree) is list:
        actual_node = my_tree[0]
    else:
        actual_node = my_tree

    node_name = actual_node[NODE_NAME]
    nb_children = actual_node[NB_CHILDREN]
    node_type = actual_node[NODE_TYPE]

    if node_type in [ROOT_BRANCH, FUNCTION_BRANCH]:
        return context['functions'][node_name](context, my_tree)
    elif node_type in [VARIABLE_LEAF, CONSTANT_LEAF]:
        return context['terminals'][node_name](context)
  
cpdef np.ndarray _add(dict context, tree):
    """
    Add two vectors together, with modulo
    """    

    a = _evaluate(context, tree[1])
    b = _evaluate(context, tree[2])

    res = a + b

    return res % [8, 8]

cpdef np.ndarray frog(dict context, tree):
    """Move the lawnmower of the vector given in argument and return it.
    This time, the branch must be evaluated before the node.
    """

    displacement = _evaluate(context, tree[1])
    
    lawnmower = context['lawnmower']
    lawnmower.jump(displacement)

    return displacement


cpdef np.ndarray progn_2(dict context, tree):
    """The first child is evaluated, then the second one."""
    logging.debug('progn_2')

    _evaluate(context, tree[1])
    return _evaluate(context, tree[2])

cpdef np.ndarray progn_3(dict context, tree):
    """The three childs are evaluated in order."""
    logging.debug('progn_3')
 
    _evaluate(context, tree[1])
    _evaluate(context, tree[2])
    return _evaluate(context, tree[3])



      

cpdef np.ndarray root_branch(dict context, tree):
    """The root branch do nothing.
    It call its single child"""
    logging.debug('root_branch')

    return _evaluate(context, tree[1])


#terminals
cpdef np.ndarray mow(dict context):
    """Move the lawnmower"""
    return context['lawnmower'].mow()

cpdef np.ndarray turn_left(dict context):
    """Rotate the lawnmower"""
    return context['lawnmower'].turn_left()

cpdef np.ndarray _random(dict context):
    """Turn right"""
    return np.array([ int(random.random()* GRID_WIDTH), int(random.random()*GRID_WIDTH)])

cdef dict functions = {
    'v8a': _add,
    'frog': frog,
    'progn_2': progn_2,
    'progn_3': progn_3,
    'root': root_branch,
   }

#Definition of terminals
cdef dict terminals = { 
    'mow': mow,
    'left': turn_left,
    'rv8': _random,
    }


#fitness evaluation
cpdef int fitness_function( my_tree):
    """
    In this fitness function, we evaluate the tree.
    The totality of the evaluation is done in this function.
    """

    cdef int nb_grass = GRID_WIDTH * GRID_WIDTH
    cdef Grass grass = Grass()
    cdef Lawnmower lawnmower = Lawnmower(grass)
    cdef dict context= {}

    try:
      context = {
          'lawnmower': lawnmower,
          'grass': grass,
          'functions': functions,
          'terminals': terminals
          }

      #evaluate one time program
      res = root_branch(context, my_tree)


      return nb_grass - grass.nb_cutted_grass()
    except:
      traceback.print_exc()
      exit()

cdef list default_function_set = [
        (1,2,'v8a'),
        (1,1,'frog'),
        (1,3,'progn_3'),
        (1,2,'progn_2'),
        ]

cdef list default_terminal_set = [
        (3,0,'mow'),
        (3,0,'left'),
        (3,0,'rv8'),
        ]


cdef dict tree_rules = {
    'root': [ (default_function_set, default_terminal_set) ], 
    'v8a': [ (default_function_set, default_terminal_set),   (default_function_set, default_terminal_set)], 
    'frog': [ (default_function_set, default_terminal_set)], 
    'progn_2': [ (default_function_set, default_terminal_set),(default_function_set, default_terminal_set), ], 
    'progn_3': [ (default_function_set, default_terminal_set),   (default_function_set, default_terminal_set), (default_function_set, default_terminal_set)], 
     }

# Build the engine
evolve = evolver.Evolver( \
        popsize=500,
        min_depth=3,
        max_depth=5,
        max_nb_runs=100,
        crossover_prob=0.7,
        mutation_prob=0.28,
        size=7,
        prob_selection=0.8)

gp_engine = pySTEPX.PySTEPX(start_from_scratch=True)
gp_engine.set_evolver(evolve)
gp_engine.set_tree_rules(tree_rules)
gp_engine.set_functions(functions)
gp_engine.set_terminals(terminals)
gp_engine.set_fitness_function(fitness_function)


def main():
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.ERROR)
    gp_engine.evolve()
if __name__ == "__main__":
  #  logging.basicConfig(level=logging.DEBUG)
    main()
