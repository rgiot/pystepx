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
Resolves the problem of santa fe.

This example is more complicated: we need to go deeper in the process, it is necessary to rewrite from scratch the
fitness evaluation to interpret if needed to tree branches. We can't use a compiled
version of the tree.
The terminal nodes design an action.
Tree interpretation is done b y the functions themselves.

The functions call the subtrees themselves.
Each of them take into input:

  * the grid
  * the ant
  * the children of the node
  * the function list
  * the terminal list

We except the tree to be well formed.
"""

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


cdef class Ant(object):
    """Representation of an ant.
    The ant see at four directions:

     * 0: up
     * 1: right
     * 2: down
     * 3 : left
    """

    cdef object _grid
    cdef int _direction
    cdef dict _position
    cdef int _eaten_food
    cdef int _energy

    def __init__(self, object grid, int energy):
        self._grid = grid
        self._direction = 0
        self._position = {'x': 0, 'y':0}
        self._eaten_food = 0
        self._energy = energy

    def move(self):
        """Move one step.
        If the ant can not leave the grid.
        """

        if not self.has_energy_left():
            return # no more enerrgy to move

        self._energy -= 1

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
        self._position['x'] %= self._grid.get_width()
        self._position['y'] %= self._grid.get_height()


        self._eat_food_if_exists()

    cpdef bint has_energy_left(self):
        """Look if the ant has energy left.
        """

        return self._energy >= 1

    cpdef is_there_any_food_ahead(self):
        """Return true if there is food ahead the ant"""

        #Get the position to observe
        cdef dict pos2 = copy.copy(self._position)

        if self._direction == 0:
            pos2['y'] += 1
        elif self._direction == 1:
            pos2['x'] += 1
        elif self._direction == 2:
            pos2['y'] -= 1
        else:
            pos2['x'] -= 1

        pos2['x'] %= self._grid.get_width()
        pos2['y'] %= self._grid.get_height()


        return self._grid.is_there_any_food_in(pos2)

    def _eat_food_if_exists(self):
        """The ant eat the food of the case.
        """

        if self._grid.is_there_any_food_in( self._position):
            self._eaten_food += 1
            self._grid.remove_food_in(self._position)

    def turn_left(self):
        """Turn left"""
        self._energy -= 1
        self._direction = (self._direction - 1) % 4

    def turn_right(self):
        """Turn right"""
        self._energy -= 1
        self._direction = (self._direction + 1) % 4

    def get_number_of_eaten_food(self):
        """Returns the quantity of eaten food of the ant."""
        return self._eaten_food

cdef class Grid(object):
      """Representation of the grid.

       * 0 in the grid means nothing
       * 1 in the grid means there is food
      """

      cdef np.ndarray _grid 

      def __init__(self, width=32, height=32):
          """Build the grid.
          """
          self._grid = np.zeros( (width, height))

      cpdef is_there_any_food_in( self, dict position):
          """Return tree if there is food at position.
          """
          return self._grid[position['x'],position['y']] == 1

      def remove_food_in(self, dict position):
          """Remove the food at the required position.
          """
          self._grid[ position['x'], position['y']] = 0

      cpdef int get_width(self):
          return self._grid.shape[0]
      cpdef int get_height(self):
          return self._grid.shape[1]

      def initialize_content_32x32(self):
          """Put food in the grid."""
             
          self._grid[1][0] = 1
          self._grid[2][0] = 1
          self._grid[3][0] = 1

          self._grid[3][1] = 1
          self._grid[3][2] = 1
          self._grid[3][3] = 1
          self._grid[3][4] = 1
          self._grid[3][5] = 1
    
          self._grid[4][5] = 1
          self._grid[5][5] = 1
          self._grid[6][5] = 1
    
          self._grid[8][5] = 1
          self._grid[9][5] = 1
          self._grid[10][5] = 1
          self._grid[11][5] = 1
          self._grid[12][5] = 1
    
          self._grid[12][6] = 1
          self._grid[12][7] = 1
          self._grid[12][8] = 1
          self._grid[12][9] = 1
    
          self._grid[12][11] = 1
          self._grid[12][12] = 1
          self._grid[12][13] = 1
          self._grid[12][14] = 1
    
          self._grid[12][17] = 1
          self._grid[12][18] = 1
          self._grid[12][19] = 1
          self._grid[12][20] = 1
          self._grid[12][21] = 1
          self._grid[12][22] = 1
          self._grid[12][23] = 1
    
          self._grid[11][24] = 1
          self._grid[10][24] = 1
          self._grid[9][24] = 1
          self._grid[8][24] = 1
          self._grid[7][24] = 1
    
          self._grid[4][24] = 1
          self._grid[3][24] = 1
    
          self._grid[1][25] = 1
          self._grid[1][26] = 1
          self._grid[1][27] = 1
          self._grid[1][28] = 1
    
          self._grid[2][30] = 1
          self._grid[3][30] = 1
          self._grid[4][30] = 1
          self._grid[5][30] = 1
    
          self._grid[7][29] = 1
          self._grid[7][28] = 1
    
          self._grid[8][27] = 1
          self._grid[9][27] = 1
          self._grid[10][27] = 1
          self._grid[11][27] = 1
          self._grid[12][27] = 1
          self._grid[13][27] = 1
          self._grid[14][27] = 1
    
          self._grid[16][26] = 1
          self._grid[16][25] = 1
          self._grid[16][24] = 1
    
          self._grid[16][21] = 1
          self._grid[16][20] = 1
          self._grid[16][19] = 1
          self._grid[16][18] = 1
    
          self._grid[17][15] = 1
    
          self._grid[20][14] = 1
          self._grid[20][13] = 1
    
          self._grid[20][10] = 1
          self._grid[20][9] = 1
          self._grid[20][8] = 1
          self._grid[20][7] = 1
   
          self._grid[21][5] = 1
          self._grid[22][5] = 1
    
          self._grid[24][4] = 1
          self._grid[24][3] = 1
    
          self._grid[25][2] = 1
          self._grid[26][2] = 1
          self._grid[27][2] = 1
    
          self._grid[29][3] = 1
          self._grid[29][4] = 1
    
          self._grid[29][6] = 1
    
          self._grid[29][9] = 1
    
          self._grid[29][12] = 1

          self._grid[28][14] = 1
          self._grid[27][14] = 1
          self._grid[26][14] = 1
    
          self._grid[23][15] = 1
    
          self._grid[24][18] = 1
    
          self._grid[27][19] = 1
    
          self._grid[26][22] = 1

          self._grid[23][23] = 1

def _evaluate(Grid grid, Ant ant, my_tree, dict functions, dict terminals):
    """Evaluate the tree.
    Each function call it.
    """

    if not ant.has_energy_left():
        return #no more energy to work

    if type(my_tree) is list:
        actual_node = my_tree[0]
    else:
        actual_node = my_tree

    node_name = actual_node[NODE_NAME]
    nb_children = actual_node[NB_CHILDREN]
    node_type = actual_node[NODE_TYPE]

    if node_type in [ROOT_BRANCH, FUNCTION_BRANCH]:
        functions[node_name](grid, ant, my_tree, functions, terminals)
    elif node_type in [VARIABLE_LEAF, CONSTANT_LEAF]:
        terminals[node_name](ant)
    else:
        raise Exception('Unable to manage this node' + str(actual_node))

 
#definition of functions
def if_food_ahead(Grid grid, Ant ant, tree, dict functions, dict terminals):
    """Look if there is food in front of the ant.
    If true, the first child is evaluated, otherwise this is the second one.
    """    
    logging.debug('if_food_ahead')

    if ant.is_there_any_food_ahead():
        _evaluate(grid, ant, tree[1], functions, terminals)
    else:
        _evaluate(grid, ant, tree[2], functions, terminals)

def progn_2(Grid grid, Ant ant, tree, dict functions, dict terminals):
    """The first child is evaluated, then the second one."""
    logging.debug('progn_2')

    _evaluate(grid, ant, tree[1], functions, terminals)
    _evaluate(grid, ant, tree[2], functions, terminals)

def progn_3(Grid grid, Ant ant, tree, dict functions, dict terminals):
    """The three childs are evaluated in order."""
    logging.debug('progn_3')
 
    _evaluate(grid, ant, tree[1], functions, terminals)
    _evaluate(grid, ant, tree[2], functions, terminals)
    _evaluate(grid, ant, tree[3], functions, terminals)


def root_branch(Grid grid, Ant ant, tree, dict functions, dict terminals):
    """The root branch do nothing.
    It call its single child"""
    logging.debug('root_branch')

    _evaluate(grid, ant, tree[1], functions, terminals)

def move(Ant ant):
    """Move the ant"""
    ant.move()

def turn_left(Ant ant):
    """Rotate the ant"""
    ant.turn_left()

def turn_right(Ant ant):
    """Turn right"""
    ant.turn_right()


cdef dict functions = {'if_food_ahead': if_food_ahead,
    'progn_2': progn_2,
    'progn_3': progn_3,
    'root': root_branch,
   }

#Definition of terminals
cdef dict terminals = { 'move': move,
    'turn_left': turn_left,
    'turn_right': turn_right,
    }


#fitness evaluation
cpdef int fitness_function( my_tree):
    """
    In this fitness function, we evaluate the tree.
    The totality of the evaluation is done in this function.
    """

    #Initialize
    cdef int max_food = 89
    
    cdef Grid grid = Grid()
    grid.initialize_content_32x32()
    cdef Ant ant = Ant(grid, 600)
    cdef int i=0
  
    #evaluate program
    while ant.has_energy_left():
        root_branch(grid, ant, my_tree, functions, terminals)

    return max_food - ant.get_number_of_eaten_food()


cdef list default_function_set = [
        (1,2,'if_food_ahead'),
        (1,2,'progn_2'),
        (1,3,'progn_3'),
        ]

cdef list default_terminal_set = [
        (3,0,'move'),
        (3,0,'turn_left'),
        (3,0,'turn_right'),
        ]


cdef dict tree_rules = {
    'root': [ (default_function_set, default_terminal_set) ], 
    'if_food_ahead': [ (default_function_set, default_terminal_set),   (default_function_set, default_terminal_set)], 
    'progn_2': [ (default_function_set, default_terminal_set),   (default_function_set, default_terminal_set)], 
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
