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
:mod:`pystepx.island.pystepislands` -- pySTEP islands enable module
===================================================================



PySTEP version working with an island mode.
Several population evolve on different islands.
After each generation, some individuals can migrate in other islands.

The api is the same than PySTEPX.
"""

import logging

import numpy as np
from copy import copy

from IPython.kernel import client

import pystepx.pySTEPX

class PySTEPXIsland(object):
    """
    Manage the island model.
    the API is the same than PySTEPX.
    On evolver is built for each island.

    XXX allows an asynchronous process (no wait for ended generation, lost
    possibility during migration)
    XXX pull and push to the required servers (not all)
    """

    def __init__(self, nb_islands=3, init_script="", db_path='/tmp/pySTEPX%d.sqlite'):
        """
        Initialize the global manager.

        :param nb_islands: the number of islands in which the evolution occur
        :param init_script: script to launch on each insland
        :param db_path: model of the sqlie path. Must contains %d were to put the
        number of the island.
        :type nb_islands: integer
        :type init_script: string
        :type db_path: string

        .. warning:: Create the object only after launching the cluster of islands. You must have
                     created the same number of cluster than the number of islands.
        """
        assert db_path.find('%d') != -1, "db_path must contains %d to include the island number"
        self._nb_islands = nb_islands
        self._db_path = db_path

        #Configure multiengine client
        self._mec = client.MultiEngineClient()
        assert len(self._mec.get_ids()) == nb_islands, "Number of servers and required islands different %d/%d" %(len(self._mec.get_ids()),nb_islands)
        self._mec_ids = self._mec.get_ids()

        self.__init_script__ = init_script
        self.set_migration_operator(MigrationOperator())


    def set_migration_operator(self, operator):
        """
        Set the operator manaing the migration.

        :param operator: instance of the migration operator to use
        """
        self.__migration_operator__ = operator

    def __parametrize__(self):
        """
        Do all the necessary parametrization of the objects.
        """

        #Set path XXX change that
        self._mec.execute(self.__init_script__)

        self.__migration_operator__.set_mec( self._mec)
        self.__migration_operator__.set_nb_islands( self._nb_islands)

        #Set the right db name for each island
        for i in range(self._nb_islands):
            db_name = self._db_path % (i+1)
            logging.debug( '%d => %s' % ( i, db_name))
            self._mec.execute("gp_engine.set_db_name('%s')" %db_name, targets=[i])

    def evolve(self):
        """Launch the evoluation process.
        Each evolver operates in its own island.

        :returns: The best individual
        """
        #Configure properly each island
        self.__parametrize__()

        #Launch evolution
        self._mec.execute("gen = gp_engine.sequentially_evolve()", \
                targets=range(self._nb_islands))
        i = 0
        while True:
	    logging.info('Launch generation evolution')
            #Do generation computing
            self._mec.execute("chosen = gen.next()", \
                    targets=range(self._nb_islands))

            #Print best individual
	    logging.info('Get best individuals')
            self._mec.execute("best = gp_engine.get_best_individual()")
            bests = self._mec['best']

            print "Generation %d" % i
            print "="*15
            print "Island\t| fit\t"
            print "\n".join(\
                    [ "%d\t%f" % (j, bests[j][1]) \
                        for j in range(len(bests))])

            print "AVG\t%f" %np.mean( [bests[j][1]  for j in range(len(bests))])
            i = i + 1

            logging.info('Test if end of generation')
            #Test if the process is finished
            self._mec.execute('end=gp_engine.__evolver__.is_evolution_ended()',
                    targets=range(self._nb_islands))
            if np.any( self._mec['end']):
                break

            #Operate the migration
	    logging.info('Launch migration process')
            self.__migration_operator__.manage_migration()

            #loop again

        print 'Evolution terminated'
        return bests

class MigrationOperator(object):
    """
    Migration operator managing how the population migrates
    between islands.

    We suppose that islands are placed in a circle way.
    Migration is done in the island before and after.
    In this implementation, population migrates in an aleatory way
    in another island
    """

    def __init__(self):
        """
        Initialise the operator.
        """

        self.set_migration_probability(0.02)
        self.set_nb_islands(0)
        self.set_mec(None)
        self._move_east = []
        self._move_west = []

    def set_mec(self, mec):
        self._mec = mec

    def set_migration_probability(self, prob):
        """Set the migration probability.
        
        :param prob: probability of migration in each direction
        :type prob: float
        """
        self._prob = prob

    def set_nb_islands(self, value):
        """Set the number of islands involved in the process.
        
        :param value: number of islands involved
        :type value: integer
        """
        self._nb_islands = value

    def manage_migration(self):
        """
        Launch the migration process with:

        * selecting the individuals to migrate
        * moving these individuals in their new island
        """
        self.select_and_remove_individuals()
        self.replace_individuals()

        #Check popsize evolution
        self._mec.execute('nb=gp_engine.__evolver__.get_real_popsize()')

    def select_and_remove_individuals(self):
        """
        For each island, select the individuals to migrate and remove them from
        the island.
        """
        logging.info('Get individuals from islands')

        actions = [ \
"move_east = gp_engine.__evolver__.select_and_remove_individuals(%f);" % self._prob,
"move_west = gp_engine.__evolver__.select_and_remove_individuals(%f);" % self._prob,
]
        for action in actions:
            self._mec.execute( action, targets=range(self._nb_islands))
        self._move_east = self._mec['move_east']
        self._move_west = self._mec['move_west']


    def replace_individuals(self):
        """
        For each island, put its migrant in another island.
        """
        logging.info('Set new individuals in other islands')
        for island_source in range(self._nb_islands):
            #move to east
            island_destination = (island_source + 1) % self._nb_islands
            logging.info('%d => %d' % (island_source, island_destination))
            self._move_from_to(self._mec['move_east'][island_source], island_destination)

            #move to west
            island_destination = (island_source - 1) % self._nb_islands
            logging.info('%d => %d' % (island_source, island_destination))
            self._move_from_to(self._mec['move_west'][island_source], island_destination)

    def _move_from_to(self, trees, destination):
        """
        Copy the trees to the destination island.

        :param trees: List of trees to import
        :param destination: island destination id
        """

        logging.info('Send trees')
        logging.debug(trees)
        self._mec.push({'new_trees': trees}, targets=[destination])
        self._mec.execute('gp_engine.__evolver__.add_new_trees(new_trees);', targets=[destination])
