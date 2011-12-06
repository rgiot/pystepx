# cython: profile=True


"""
:mod:`pystepx.baseevolver` -- Optimized evolving
===============================================

This module contains the methods to start and finish a complete evolutionary
run.  The present version can run strongly-typed  Koza-based GP using tournament
selection.
"""
"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

@author: by Mehdi Khoury
@version: 1.00
@copyright: (c) 2009 Mehdi Khoury under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: mehdi.khoury at gmail.com

"""
# TODO try to parallelize here

import gc
import os
import sqlite3 as sqlite
import pprint
import math
import logging
import copy
import numpy as np


from pystepx.geneticoperators import selection, crossutil
from pystepx.tree import buildtree
import pystepx.writepop as writepop

cimport numpy as np


class EvolutionException(Exception):
    """Exception held during the evolution process"""
    pass

# Exceptions related to operator probability
class CrossoverProbError(EvolutionException):
    """Exception related to crossover"""
    pass
class MutationProbError(EvolutionException):
    """Exception related to mutation"""
    pass
class OperatorProbError(EvolutionException):
    """Exception related to operators"""
    pass

# Exceptions related to population size
class PopSizeError(EvolutionException):
    """Exception related to pop size"""


cdef class BaseEvolver(object):
    """Evolver object.
    Launch the fitness computing on the trees.
    Launch the next generation compatutation process.

        :param popsize: size of the population
        root_node: specify the root node and its arity (nb of children). e.g. (0,2,'root')
        :param mindepth: min tree depth (at the moment only 2 working)
        :param maxdepth: max depth of trees in new generation (should be >=3)
        :param buildmethod: which Koza method is used to build the trees (either
        'AddHalfNode' or 'AddFullNode' or 'AddGrowNodeMin' respectively for
        Ramped Half-n-Half, Full, or Half)
        :param max_nb_runs: the search will gon on until a maximum number of generations
        is reached
        :param fitness_criterion: the search will stop if the fitness found is <= to
        the ideal fitness
        :param crossover_prob: probability of crossover (will determine what proportion of
        the population will be replaced by crossover-generated offsprings)
        :param mutation_prob: probability of crossover (will determine what proportion of
        the population will be replaced by mutation-generated offsprings)
        :param dbname: path to database e.g. r'D:\3d_work\pythongp\pySTGP_0.51\src\pop_db'
    """

    cdef public int _popsize, _mindepth, _maxdepth, _max_nb_runs, _size, _last_generation
    cdef public float _crossover_prob, _mutation_prob, _prob_selection, _fitness_criterion, _current_best_fitness
    cdef public str __db_name__
    cdef public str _buildmethod
    cdef public list _tablename
    cdef public bint __Substitute_Mutation, 
    cdef public  _start_from_scratch_
    cdef public bint  __low_memory_footprint__

    cdef public tuple _root_node
    cdef public list _new_pop
    cdef public list trees

    cdef public __FitnessFunction
    cdef public __mutator__
    cdef public __crossover_operator__
    cdef public __end_of_generation_handler__

    cdef public _con
    cdef public _selected_table

    # Grammar of the trees
    cdef public dict __rules__

    def __init__( self,
                  int popsize = 200,
                  root_node = (0, 1, 'root'),
                  int min_depth = 2,
                  int max_depth = 8,
                  str buildmethod = 'AddHalfNode', #TODO use a class or an object
                  int max_nb_runs = 100,
                  float fitness_criterion = 0.0000001 ,
                  float crossover_prob = 0.5,
                  float mutation_prob = 0.49,
                  int size = 7,
                  float prob_selection = 0.8,
                  str dbname = '/tmp/pySTEPX.sqlite'
                  ):
        """
        Initialize the evolution object with the various parameters
        """

        assert popsize > size, \
                "Population size (%d) cannot be inferior to size of tournament (%d)" % (popsize, size)

        self._set_start_from_scratch( False)

        #Store parameters usefull after
        self._popsize     = popsize
        self._root_node   = root_node
        self._mindepth    = min_depth
        self._maxdepth    = max_depth
        self._buildmethod = buildmethod
        self._max_nb_runs = max_nb_runs
        self._fitness_criterion   = fitness_criterion
        self._crossover_prob      = crossover_prob
        self._mutation_prob       = mutation_prob
        self._size                = size
        self._prob_selection      = prob_selection

        self.__db_name__              = dbname

        self._tablename = []
        self._new_pop = []
        self.trees   = []
        self.__Substitute_Mutation = False
        self.__FitnessFunction = self.__default_fitness__

        self.__mutator__ = None
        self.__crossover_operator__ = None
        self._con = None
        self._selected_table = None
        self._current_best_fitness = 0

        self._last_generation = -1

    def _set_low_memory_footprint(self, value):
        self.__low_memory_footprint__ = value

    def _set_db_name(self, db_name):
        """Store the database name.
        It will be opened later.
        """
        self.__db_name__ = db_name

    def _get_db_name(self):
        """Returns the path of the db."""
        return self.__db_name__

    def _set_mutation_operator(self, operator):
        """
        Initialize the mutation operator.
        Called by pySTEP.PySTEP
        """
        operator.check_configuration()
        self.__mutator__ = operator

    def _set_end_of_generation_handler(self, handler):
        self.__end_of_generation_handler__ = handler

    def _set_crossover_operator(self, operator):
        """
        Initialize the crossover operator.
        Called by pySTEP.PySTEP
        """
        operator.check_configuration()
        self.__crossover_operator__ = operator

    cpdef _set_tree_rules(self, dict rules):
        """Set the tree rules.
        Called by pySTEP.PySTEP
        """
        self.__rules__ = rules

    def _set_start_from_scratch(self, bint value):
        """
        Set if we need to restart from scratch.
        Called by pySTEP.PySTEP.
        """
        assert value in [True, False]
        self._start_from_scratch_ = value

    def __default_fitness__(self, var):
        """Defualt fintess function"""
        raise Exception('You have not defined the fitness function !')

    cpdef _write_computed_population_to_db(self, tablename):
        """Write the computed population to the database.
        When using low memory footprint, this method can be called several times per generation.
        XXX move in the popwritter
        """

        self._popwriter.add_new_individuals(self._new_pop, tablename)


        del self._new_pop[:]
        del self._trees[:]
        self._popwriter.flush()



    cpdef _build_initial_population(self):
        """
        Generate the initial population, 
        compute its fitness and store it in database.

        When the evolver is configured to work with low memory footprint,
        the trees are append to the database while they are created, without keeping them in memory.
        """
        assert self.__rules__ is not None, "You must set tree rules"

        logging.info('Create initial population')
        try:
            #If database exists, it is suppressed.
            #XXX Another behaviour could be to suppress it if it is full or continue
            #the evolution if it has been stoped.
            os.remove(self.__db_name__)
        except Exception:
            pass

        cdef int i
        cdef list trees, fitnesses
        cdef list my_tree
        cdef float fitness

        self._con = sqlite.connect(self.__db_name__)
        self._popwriter = writepop.WritePop( self._con)


        self._tablename = []
        self._tablename.append('pop0')

        # Build the initial trees and compute their fitness
        trees, fitnesses = [], []
        i = 0
        method  = getattr(buildtree.BuildTree(self.__rules__), self._buildmethod)

        if not self.__low_memory_footprint__:

            #Classical way of creating
            while i < self._popsize:
                # create a tree individual
                my_tree = method(   self._root_node,
                                    0,
                                    self._mindepth,
                                    self._maxdepth)

                if my_tree not in trees:
                    trees.append(my_tree)
                    fitnesses.append(self.__FitnessFunction(my_tree))
                    i = i+1

            # Store them in database
            self._popwriter.write_initial_population(  trees,
                                                        fitnesses,
                                                        self._tablename[0])

        else:
            #Low memory footprint
            self._popwriter.create_new_table(self._tablename[0])

            while i < self._popsize:
                my_tree = method(   self._root_node,
                                    0,
                                    self._mindepth,
                                    self._maxdepth)

                #XXX Check if tree already exists ?

                i = i + 1
                fitness = self.__FitnessFunction(my_tree)
                self._popwriter.add_to_initial_population( my_tree, fitness, self._tablename[0])

                del my_tree[:]

                if i % 50 == 0:
                    self._popwriter.flush() #write db on disc to avoid swapping

            self._popwriter.flush() #write the final pop

    def _set_fitness_function(self, fitness):
        """Set the fitness function. (previously in settings.py"""
        self.__FitnessFunction = fitness

    def SetSubstituteMutation(self, value):
        """Set if we must substitute mutation"""
        self.__Substitute_Mutation = value

    def _get_last_generation_number(self):
        """
        Return the number of the last computed generation.
        """
        return self._last_generation

    def get_best_individual(self, all=False):
        """
        Returns information about the best individual.

        @todo use a method in writepop and optimize
        """

        cdef np.ndarray db_list = selection.GetDBKeysAndFitness(
                               self._con,
                               self._selected_table)
        chosen = selection.SelectDBOneFittest(db_list)

        if all is False:
            return chosen
        else:
            
            res = self._popwriter.get_individual(self._tablename[-1],chosen[0])
            return chosen[0], chosen[1], res[1]

    def print_end_generation(self, generation, chosen_one, verbose, print_tree):
        """Print if necessary information about the best tree of the
        generation.
        
        @todo set chosen_one with the tree and not its indice
        """

        if verbose is True:
            print ''.join([  'generation ' + str(generation) 
                           + ' (db table name = ' + self._tablename[generation] +'): -> '
                           +'best fit individual has id:',
                            str(chosen_one[0]),
                            ' and fitness:',
                            str(chosen_one[1])])

            if print_tree is True:
                data = self._popwriter.get_individual( self._tablename[generation], chosen_one[0], True)
                pprint.pprint(data[1])

    def _end_of_generation(self):
        """Method called when a generation is over."""

        if self.__end_of_generation_handler__ is not None:
            self.__end_of_generation_handler__()




    cpdef bint is_evolution_ended(self):
        """
        Look if the evolution is ended, because:
         - the maximum generation is get
         - the fitness is set
        """

        return len(self._tablename) >= self._max_nb_runs \
                or self._current_best_fitness < self._fitness_criterion


    def __read_from_db_if_possible__(self):
        """
        User ask to get results from the database.
        Here, we want to get the last population.
        """

        self._con = sqlite.connect(self.__db_name__)
        self._tablename = []

        self._popwriter = writepop.WritePop( self._con)

        cdef int i = 0
        while True:
            tablename = 'pop%d' % i
            if self._popwriter.is_generation_computed(tablename):
                self._tablename.append(tablename)
                self._last_generation = i
                i = i+1
            else:
                break


    cdef tuple _get_genetic_operations_size(self, float crossover_prob, float mutation_prob, int popsize):
        """
        Returns the real number of individual in the genetic operations of
         - crossover
         - mutation
         - reproduction

        The reproduction probability equal to:
        1 - (crossover_prob + mutation_prob)

        :param crossover_prob: probability of crossover
        :param mutation_prob:  probability of mutation
        :param popsize: the size of the population

        :return: crossover_size, mutation_size, reproduction_size
        """

        #Check number of individual to take into account
        if crossover_prob > 1 or crossover_prob < 0:
            raise CrossoverProbError, "Crossover Probability should be in interval [0,1]"
        if mutation_prob > 1 or mutation_prob < 0:
            raise MutationProbError, "Crossover Probability should be in interval [0,1]"

        reproduction_prob = 1-(crossover_prob + mutation_prob)

        if reproduction_prob > 1 or reproduction_prob < 0:
            raise OperatorProbError, "Sum of Mutation and Crossover Probability should be in interval [0,1]"
        if popsize < 3:
            raise PopSizeError, "The size of the population must be at least 3"

        self._new_pop, self._trees = [], []
        # build the appropriate size for the crossover offsprings,
        # mutation offsprings and reproduction offsprings

        cdef int crossover_size    = math.ceil(popsize * crossover_prob)
        cdef int mutation_size     = math.ceil(popsize * mutation_prob)
        cdef int reproduction_size = math.ceil(popsize * reproduction_prob)

        sizes = [crossover_size, mutation_size, reproduction_size]
        theoretical_size = sum(sizes)

        cdef int nb
        if theoretical_size > popsize:
            nb = theoretical_size - popsize
            if crossover_size > mutation_size and mutation_size >= reproduction_size:
                crossover_size = crossover_size - nb
            elif mutation_size > crossover_size and crossover_size >= reproduction_size:
                mutation_size = crossover_size - nb
            elif reproduction_size > crossover_size and crossover_size >= mutation_size:
                mutation_size = crossover_size - nb
            else:
                crossover_size = crossover_size - nb

        return crossover_size, mutation_size, reproduction_size

    cpdef int get_real_popsize(self):
        """
        Returns the real popsize
        """
        db_list = selection.GetDBKeysAndFitness(self._con, self._selected_table)
        return len(db_list)


    def TournamentSelectionEvolveDBPopulation2(
          self,
          int popsize,
          int maxdepth,
          float crossover_prob,
          float mutation_prob,
          int size,
          float prob_selection,
          con,
          str tablename,
          str tablename2):
        """
        create a new population of randomly generated trees and write this new generation
        to a new table of name 'tab'+generation number in the database.

       :param popsize: size of the population
       :param maxdepth: max depth of trees in new generation
       :param crossover_prob: probability of crossover (will determine what proportion of
        the population will be replaced by crossover-generated offsprings)
        :param mutation_prob: probability of crossover (will determine what proportion of
        the population will be replaced by mutation-generated offsprings)
        :param con: Connection to database
        param tablename: name of the database table of the initial population
        :param tablename2: name of the database table of the next generation

        """
        cdef int crossover_size, mutation_size, reproduction_size
        cdef int i
        cdef np.ndarray db_list, reprod, cross, mut

        (crossover_size,
        mutation_size,
        reproduction_size) = self._get_genetic_operations_size(
                                crossover_prob,
                                mutation_prob,
                                popsize
                            )

        self._popwriter.create_new_table(tablename2)

        logging.info('Get couples of fitness/keys')
        # get the ordered list of fitnesses with identifier keys
        db_list = selection.GetDBKeysAndFitness(con, tablename)

        # start by selecting fittest parents for reproduction
        # then select parents for crossover
        # then select parents for mutation
        logging.info('Select for reproduction')
        selected  = selection.SelectDBSeveralFittest(   int(reproduction_size), db_list)
        logging.info('Apply reproduction')
        self._do_reproduction_for(selected, tablename, tablename2)

        # Apply cross over
        logging.info('Apply cross-over')
        selected = selection.TournamentSelectDBSeveral(
                      int(crossover_size),
                      size,
                      prob_selection,
                      db_list)
        self._do_crossover_for(selected, tablename, tablename2, db_list)

        logging.info('Apply mutation')
        selected = selection.TournamentSelectDBSeveral(
                      int(mutation_size),
                      size,
                      prob_selection,
                      db_list)
        self._do_mutation_for(selected, tablename, tablename2)


        self._write_computed_population_to_db(tablename2)



    cpdef _do_reproduction_for(self, np.ndarray reprod, str tablename, str tablename2):
        """Apply the reproduction operator on this programs."""

        self._popwriter.copy_individuals_from_to(reprod, tablename, tablename2)


    def _do_mutation_for(self, np.ndarray mut, str tablename, str tablename2):
        """Apply the mutation operator on these programs."""

        cdef int nb_iter = 0
        cdef float result_fitness
        cdef long o_id
        cdef bint same_tree

        cdef list my_tree, my_tree_mapping
        cdef int my_treedepth

        for elem in mut:
            logging.debug('Mutation of %s', str(elem))

            o_id = elem[0]
            myresult, my_tree, \
                my_tree_mapping, my_treedepth, \
                my_evaluated, my_fitness = self._popwriter.get_individual(tablename, o_id, extract=True)
            same_tree       = True

            # First test of mutation, fail if the same or already exists
            mt = self.__mutator__.mutate(
                self._maxdepth,
                my_tree,
                my_tree_mapping,
                my_treedepth)
            same_tree = mt[0]

            if mt in self._trees:
                same_tree = True
            # make sure to try another mutation if the offspring is identical to the parent
            if same_tree == True:
                while same_tree == True:
                    mt = self.__mutator__.mutate(
                        self._maxdepth,
                        my_tree,
                        my_tree_mapping,
                        my_treedepth)
                    same_tree = mt[0]


            mt_map    = crossutil.GetIndicesMappingFromTree(mt[1])
            mt_depth  = crossutil.GetDepthFromIndicesMapping(mt_map)
            mt_evaluated = 1

            # get fitness of the tree
            try:
                result_fitness = self.__FitnessFunction(mt[1])
            except Exception, e:
                logging.error('Error while evaluating a mutated tree')
                logging.error(e)
                logging.error(mt[1])

            self._new_pop.append((o_id, mt[1], mt_map, mt_depth, mt_evaluated, result_fitness))

            nb_iter = nb_iter + 1
            if self.__low_memory_footprint__ and nb_iter%50 == 0:
                self._write_computed_population_to_db(tablename2)

        if self.__low_memory_footprint__:
            self._write_computed_population_to_db(tablename2)


    def get_tree(self, str tablename, int o_id):
        """Return the required tree.
        :TODO: move this in the right class
        """

        return self._popwriter.get_individual( tablename, o_id)


    def load_tree(self, str tablename, int o_id):
        """Load the information of the tree"""

        return self._popwriter.get_individual( tablename, o_id, extract=True)
 

    cdef _do_crossover_for(self, np.ndarray cross, str tablename, str tablename2, np.ndarray db_list):
        """
        Operate the crossover for the selected population.
        """
        cdef int i
        cdef int o_id, o_id2
        cdef np.ndarray parent2
        cdef np.ndarray elem, elem2
        cdef tuple cs

        cdef int nb_iter = 0
        cdef float offspring1_result_fitness = float('inf')
        cdef float offspring2_result_fitness = float('inf')

        cdef int my_evaluated1, my_evaluated2
        cdef int my_tree1depth, my_tree2depth
        cdef float my_fitness1,my_fitness2

        # Get the list of trees to treat
        trees = self._popwriter.get_individuals_iterator(tablename, cross, extract=True)

        # Loop over all trees and apply crossover
        idx_parent = -1 # pointer to obtain real o_id
        for (myresult1, cp_my_tree1, cp_my_tree1_mapping, my_tree1depth, my_evaluated1, my_fitness1)  in trees:

            idx_parent = idx_parent + 1
            # TODO remove this ugly management with idw_parent


            # select the second parent using tournament selection
            parent2 = selection.TournamentSelectDBSeveral(2, 7, 0.8, db_list, unique=True)
            #TODO configure that

            # make sure parent2 is different from parent1
#            if np.all(elem == parent2[0]):
#                elem2 = parent2[1]
#            else:
#                elem2 = parent2[0]


            o_id = cross[idx_parent][0]
            o_id2 = parent2[0][0]

            (myresult2,
                    cp_my_tree2,
                    cp_my_tree2_mapping,
                    my_tree2depth,
                    my_evaluated2,
                    my_fitness2) = self.load_tree(tablename, o_id2)
 
            # get fitness of the tree
            cs_evaluated = 1
            cs = ([0, 0, 0, 0],)
            i = 0

            #Try the crossover at maximum 100 times
            while cs[0] != [1, 1, 1, 1] and i < 100 :

                cs = self.__crossover_operator__.Koza1PointCrossover(
                                  self._maxdepth,
                                  cp_my_tree1,
                                  cp_my_tree2,
                                  cp_my_tree1_mapping,
                                  cp_my_tree2_mapping,
                                  my_tree1depth,
                                  my_tree2depth)
                i = i + 1

            # if after trying 100 times , the crossover cannot give a correct offspring, then
            # create a new offspring using mutation...
            if cs[0] != [1, 1, 1, 1] and self.__Substitute_Mutation == True:
                mt = self.__mutator__.mutate(
                                self._maxdepth,
                                cp_my_tree1,
                                cp_my_tree1_mapping,
                                my_tree1depth)
                mt_map        = crossutil.GetIndicesMappingFromTree(mt[1])
                mt_depth      = crossutil.GetDepthFromIndicesMapping(mt_map)
                mt_evaluated  = 1
                # get fitness of the tree
                result_fitness = self.__FitnessFunction(mt[1])
                self._new_pop.append( (o_id, mt[1], mt_map, mt_depth, mt_evaluated, result_fitness))

            else: #No mutation required
                try:
                    offspring1_result_fitness = self.__FitnessFunction(cs[1])
                except Exception, e:
                    logging.error(e)
                    logging.error('pb when applying fitness function to result 1 of crossover')
                    logging.error(cs[1])
                    logging.error(cs[0])

                try:
                    offspring2_result_fitness = self.__FitnessFunction(cs[2])
                except Exception, e:
                    logging.error(e)
                    logging.error('pb when applying fitness function to result 2 of crossover')
                    logging.error(cs[2])
                    logging.error(cs[0])


                if offspring1_result_fitness >= offspring2_result_fitness:
                    cs_map    = crossutil.GetIndicesMappingFromTree(cs[1])
                    cs_depth  = crossutil.GetDepthFromIndicesMapping(cs_map)
                    self._new_pop.append((o_id,
                                cs[1],
                                cs_map,
                                cs_depth,
                                cs_evaluated,
                                offspring1_result_fitness))
                if offspring1_result_fitness < offspring2_result_fitness:
                    cs_map    = crossutil.GetIndicesMappingFromTree(cs[2])
                    cs_depth  = crossutil.GetDepthFromIndicesMapping(cs_map)
                    self._new_pop.append((o_id,
                                cs[2],
                                cs_map,
                                cs_depth,
                                cs_evaluated,
                                offspring2_result_fitness))

            nb_iter = nb_iter + 1
            if self.__low_memory_footprint__ and nb_iter%25 == 0:
                self._write_computed_population_to_db(tablename2)

        if self.__low_memory_footprint__:
            self._write_computed_population_to_db(tablename2)


   
