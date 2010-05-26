#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classical evolver.
Contains code that can be compiled by cython.
"""

import pystepx.baseevolver

class Evolver(pystepx.baseevolver.BaseEvolver):
    """Evolver object.
    Launch the fitness computing on the trees.
    Launch the next generation compatutation process.

    XXX add probability of crossover points
    XXX add the choice for selection (tournament, elitism, ...)

        @param popsize: size of the population
        root_node: specify the root node and its arity (nb of children). e.g. (0,2,'root')
        @param mindepth: min tree depth (at the moment only 2 working)
        @param maxdepth: max depth of trees in new generation (should be >=3)
        @param buildmethod: which Koza method is used to build the trees (either
        'AddHalfNode' or 'AddFullNode' or 'AddGrowNodeMin' respectively for
        Ramped Half-n-Half, Full, or Half)
        @param max_nb_runs: the search will gon on until a maximum number of generations
        is reached
        @param fitness_criterion: the search will stop if the fitness found is <= to
        the ideal fitness
        @param crossover_prob: probability of crossover (will determine what proportion of
        the population will be replaced by crossover-generated offsprings)
        @param mutation_prob: probability of crossover (will determine what proportion of
        the population will be replaced by mutation-generated offsprings)
        @param dbname: path to database e.g. r'D:\3d_work\pythongp\pySTGP_0.51\src\pop_db'
    """


    def __init__( self,
                  popsize = 200,
                  root_node = (0, 1, 'root'),
                  min_depth = 2,
                  max_depth = 8,
                  buildmethod = 'AddHalfNode', #TODO use a class or an object
                  max_nb_runs = 100,
                  fitness_criterion = 0.0000001 ,
                  crossover_prob = 0.5,
                  mutation_prob = 0.49,
                  size = 7,
                  prob_selection = 0.8
                  ):
        super(Evolver, self).__init__( 
            popsize = popsize,
			      root_node = root_node,
			      min_depth = min_depth,
			      max_depth = max_depth,
			      buildmethod = buildmethod,
			      max_nb_runs = max_nb_runs,
			      fitness_criterion = fitness_criterion,
			      crossover_prob = crossover_prob,
			      mutation_prob = mutation_prob,
			      size = size,
			      prob_selection = prob_selection)

    def Run(self, verbose=True, print_tree=False):
        """Launch the evolution.
        Use the sequential way.
        """

        iter = self.run_sequentially()
        while True:
            #Compute new generation
            res = iter.next()

            #Print it if required
            self.print_end_generation(self._last_generation, res, verbose, print_tree)

            #Check problem resolved
            if  res[1] <= self._fitness_criterion:
                print ''.join(['found solution at generation ',
                                    str(self._last_generation),
                                    ', with fitness:',
                                    str(res[1])])
                self._popwriter.PrintPopFromDB(
                                self._tablename[self._last_generation],
                                'lastpop')
                break

            #Check end of evolution
            if self._last_generation ==  self._max_nb_runs:
                print ''.join(['Fitness stopping criterion not found.'
                                    +'Run ended at generation ',
                                    str(self._last_generation)])
                break

        data = self._popwriter.get_individual( self._tablename[self._last_generation], res[0], True)
        print(data[1])


        self._con.close()

    def run_sequentially(self, verbose=True, print_tree=True):
        """Run the evolution and stops yield each generation.
        The process never ends. It's up to the caller to ends its.
        """

        #Reload database if possible
        if self._start_from_scratch_ == False:
            self.__read_from_db_if_possible__()

        if self._last_generation == -1: #Nothing readed
            #First generation
            self._last_generation = 0
            self._build_initial_population()
            self._selected_table = self._tablename[0]
            chosen_one = self.get_best_individual()
            self._current_best_fitness = chosen_one[1]

            self._end_of_generation()
            yield chosen_one

        #Other generations
        while  True: #i < self._max_nb_runs and current_best_fitness > self._fitness_criterion:
            self._last_generation = self._last_generation + 1

            #Compute next generation
            self._selected_table = ''.join(['pop', str( self._last_generation)])
            self._tablename.append(self._selected_table)
            self.TournamentSelectionEvolveDBPopulation2(
                    self._popsize,
                    self._maxdepth,
                    self._crossover_prob,
                    self._mutation_prob,
                    self._size,
                    self._prob_selection,
                    self._con,
                    self._tablename[self._last_generation - 1],
                    self._tablename[self._last_generation])

            #Get best elem
            chosen_one = self.get_best_individual()
            self._current_best_fitness = chosen_one[1]

            self._end_of_generation()
            yield chosen_one

