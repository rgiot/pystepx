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

from IPython.parallel import Client
import IPython

import pystepx.pySTEPX



if IPython.__version__ < 0.11:
    raise Error("Wrong Ipython version")

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
        Get the reference to the island processes, but does not launch
        initialisation script.

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
        self._rc = Client()
        assert len(self._rc.ids) == nb_islands, "Number of servers and required islands different %d/%d" %(len(self._rc.ids),nb_islands)
        self._rc_ids = self._rc.ids

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

        On each Island : execute the initilisation script.
        This script must create grammar and so on.

        On each island, configure the database name.

        Configure parallel objects.

        """

        #Set path XXX change that
        print logging.info(self.__init_script__)
        self._rc[:].execute(self.__init_script__, block=True)

        self.__migration_operator__.set_rc( self._rc)
        self.__migration_operator__.set_nb_islands( self._nb_islands)

        #Set the right db name for each island
        for i in range(self._nb_islands):
            db_name = self._db_path % (i+1)
            logging.debug( '%d => %s' % ( i, db_name))
            self._rc[i].execute("gp_engine.set_db_name('%s')" %db_name)

    def evolve(self):
        """Launch the evoluation process.
        Each evolver operates in its own island.

        :returns: The best individual
        """
        #Configure properly each island
        self.__parametrize__()

        # Get evolution generator of each island
        self._rc[:].execute("gen = gp_engine.sequentially_evolve()", block=True)

        # Loop over all the sessions
        i = 0
        while True:
            logging.info('Launch generation evolution')

            #Do generation computing
            self._rc[:].execute("chosen = gen.next()")

            #Print best individual
            logging.info('Get best individuals')
            self._rc[:].execute("best = gp_engine.get_best_individual()")
            bests = self._rc[:]['best']

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
            self._rc[:].execute('end=gp_engine.__evolver__.is_evolution_ended()')

            if np.any( self._rc[:]['end']):
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
        self.set_rc(None)
        self._move_east = []
        self._move_west = []

    def set_rc(self, mec):
        self._rc = mec

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
        self._rc[:].execute('nb=gp_engine.__evolver__.get_real_popsize()',
                            block=True)


    def select_and_remove_individuals(self):
        """
        For each island, select the individuals to migrate and remove them from
        the island.
        """
        logging.info('Get individuals from islands')

        # Build the command list
        actions = [ \
"move_east = gp_engine.__evolver__.select_and_remove_individuals(%f);" % self._prob,
"move_west = gp_engine.__evolver__.select_and_remove_individuals(%f);" % self._prob,
]

        # Launch the command list
        for action in actions:
            self._rc[:].execute( action, block=True)

        # Store the moving individuals
        self._move_east = self._rc[:]['move_east']
        self._move_west = self._rc[:]['move_west']


    def replace_individuals(self):
        """
        For each island, put its migrant in another island.
        """


        logging.info('Set new individuals in other islands')
        for island_source in range(self._nb_islands):

            #move to east
            island_destination = (island_source + 1) % self._nb_islands
            logging.info('Move from %d to %d' % (island_source, island_destination))
            self._move_from_to(self._rc[island_source]['move_east'], island_destination)

            #move to west
            island_destination = (island_source - 1) % self._nb_islands
            logging.info('Move from %d to %d' % (island_source, island_destination))
            self._move_from_to(self._rc[island_source]['move_west'], island_destination)


    def _move_from_to(self, trees, destination):
        """
        Copy the trees to the destination island.

        :param trees: List of trees to import
        :param destination: island destination id
        """

        print "Move %d trees to %d " %( len(trees), destination)

        logging.info('Send trees')
        logging.debug(trees)

        self._rc[destination]['new_trees'] =  trees
        self._rc[destination].execute('gp_engine.__evolver__.add_new_trees(new_trees);')
