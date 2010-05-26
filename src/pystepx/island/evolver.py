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
:mod:`pystepx.island.evolver` -- Island specialized evolver
===========================================================


Specialized evolver in the case of distributed GP
"""

import math
import copy
import marshal

import pystepx.evolver 
from pystepx.geneticoperators import selection


class DistributedEvolver(pystepx.evolver.Evolver):
    """
    Distributed evolver.
    This evolver is able to add and suppress individuals
    from its population. This allows the possibility of migration.
    """

    def __init__( self,
                  popsize = 200,
                  root_node = (0, 1, 'root'),
                  min_depth = 2,
                  max_depth = 8,
                  buildmethod = 'AddHalfNode',
                  max_nb_runs = 100,
                  fitness_criterion = 0.0000001 ,
                  crossover_prob = 0.5,
                  mutation_prob = 0.49,
                  size = 7,
                  prob_selection = 0.8):

        super(DistributedEvolver, self).__init__(popsize,
                root_node,
                min_depth,
                max_depth,
                buildmethod,
                max_nb_runs,
                fitness_criterion,
                crossover_prob,
                mutation_prob,
                size,
                prob_selection)
        #self._oid_to_replace = [] # Store the list of oid of leaving trees
                                 # needed to store new ones

    def select_and_remove_individuals(self, prob):
        """
        Select several individuals from the population, remove them from the
        island and returns them.

        :param prob: probability of selection of individuals for migration
        """

        migration_size = max(2, math.ceil(self._popsize * prob))


        db_list = selection.GetDBKeysAndFitness(
                               self._con,
                               self._tablename[-1])
        #Select several uniq individuals
        migration = selection.TournamentSelectDBSeveral(
                      int(migration_size),
                      10, #tournament size
                      0.8, #selection probability
                      db_list,
                      unique=True)


        trees = []
        #self._oid_to_replace = [] # Reset
        for elem in migration:
            o_id = elem[0]
            #self._oid_to_repace.append(elem)

            #Read from table
            myresult, my_tree, \
                my_tree_mapping, my_treedepth, \
                my_evaluated, my_fitness = self._popwriter.get_individual(self._tablename[-1], o_id, True)
 
            #Add in the returning set
            trees.append( ( my_tree,
                            my_tree_mapping,
                            my_treedepth,
                            my_evaluated,
                            my_fitness))

            #todo ask to popwriter to do that
            self._con.execute("DELETE FROM %s WHERE o_id=%d;" % (self._tablename[-1], o_id))

        self._con.commit()
        return trees

    def add_new_trees(self, trees):
        """
        Import new individual from other islands.
        Do not compute again their threshold.

        :param trees: set of trees to import
        """
        #assert len(self._oid_to_repace) == len(trees), \
        #        "You must have as well as emigrant as imigrants"

        for tree in trees:
            self._popwriter.add_new_individual(tree, self._tablename[-1])

        self._popwriter.flush()
        self._popsize = self.get_real_popsize()
