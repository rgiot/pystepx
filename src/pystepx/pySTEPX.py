#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTHOR Romain Giot <romain.giot@ensicaen.fr>

"""
:mod:`pystepx.pySTEPX` -- Manager of the GP run
===============================================

Manager of the Genetic Programming Engine.
You can control the process by the help of this class.
"""

#import psyco

from pystepx.geneticoperators.crossoveroperator import CrossoverOperator
from pystepx.geneticoperators.mutationoperator import Mutator

#psyco.profile()


class PySTEPX(object):
    """
    Genetic Programming Engine Manager.
    """



    def __init__(self, db_path='/tmp/pySTEPX.sqlite', start_from_scratch=True):
        """
        Create the pySTEPX object.

        XXX Clean the way to specify the db (presents in evolver too)

        :param db_path: sqlite file_name
        :param restart_from_scratch: boolean indicating if we need to restart
        computation from scratch if a database already exists
        """
        self.__config__     = {}
        self.__evolver__    = None
        self.__settings__   = None

        #Initialize default values
        self.set_mutation_operator(Mutator())
        self.set_crossover_operator(CrossoverOperator())
        self.set_crossover_mapping([])
        self.set_strongly_typed_crossover_degree(False)
        self.set_substitute_mutation(False)
        self.set_db_name(db_path)
        self.set_start_from_scratch(start_from_scratch)
        self.set_low_memory_footprint(False)
        self.set_endofgeneration(None)

    def get_best_individual(self):
        """Returns the best individual of the whole population"""
        return self.__evolver__.get_best_individual(all=True)

    def set_fitness_function(self, function):
        """Set the fitness function to use"""
        self.__config__['fit_func'] = function


    def set_functions(self, functions):
        """Set the functions set"""
        self.__config__['functions'] = functions

    def set_terminals(self, terminals):
        """Set the terminal set"""
        self.__config__['terminals'] =  terminals


    def set_tree_rules(self, rules):
        """Set the tree rules"""
        self.__config__['rules'] = rules


    def set_mutation_operator(self, operator):
        """Set the mutation opertor"""
        self.__config__['mutation_operator']  = operator

    def set_crossover_operator(self, operator):
        """Set the crossover operator"""
        self.__config__['crossover_operator'] = operator

    def set_strongly_typed_crossover_degree(self, degree):
        """XXX"""
        self.__config__['strongly_typed_crossover_degree'] = degree

    def set_adf_ordered(self, value):
        """Specify if adf must be ordered (prevents infinite loop)"""
        self.__config__['adf_ordered'] = value

    def set_crossover_mapping(self, mapping):
        """Set the crossover mapping"""
        self.__config__['crossover_mapping'] = mapping

    def set_substitute_mutation(self, value):
        """Sit if we have to do a mutation when crossover fail"""
        self.__config__['substitute_mutation'] = value

    def set_low_memory_footprint(self, value):
        self.__config__['low_memory_footprint'] = value

    def set_db_name(self, value):
        """Set the dbname"""
        self.__config__['db_name'] = value

    def get_db_name(self):
        """Set the dbname"""
        return self.__config__['db_name']

    def set_start_from_scratch(self, value):
        """Set if we need to restart computation from scratch if the database
        already exists."""
        self.__config__['start_from_scratch']= value

    def get_last_generation_number(self):
        """
        Returns the actual generation.
        """
        return self.__evolver__._get_last_generation_number()

    def set_endofgeneration(self, handler):
        """Set the function to call at the end of a generation.
        """
        self.__config__['generationhandler'] = handler

    def set_evolver(self, evolver):
        """
        Set the evolver object of the gp engine.

        :param evolver: evolver to use
        """
        self.__evolver__ = evolver

    def get_evolver(self):
        """Returns teh evolver."""
        return self.__evolver__

    def __parametrize__(self):
        """
        Do all the necessary parametrization of the objects.
        """
        assert self.__evolver__ is not None, " you must define the evolver"

        #Set various variables
        self.__config__['crossover_operator'].set_tree_rules( self.__config__['rules'])
        self.__config__['crossover_operator'].set_strongly_typed_crossover_degree(\
                self.__config__['strongly_typed_crossover_degree'])
        self.__config__['crossover_operator'].set_crossover_mapping( \
                self.__config__['crossover_mapping'])
        self.__config__['mutation_operator'].set_tree_rules( self.__config__['rules'])

        #Inform evolver
        self.__evolver__._set_tree_rules(self.__config__['rules'])
        self.__evolver__._set_fitness_function(self.__config__['fit_func'])
        self.__evolver__._set_crossover_operator(self.__config__['crossover_operator'])
        self.__evolver__._set_mutation_operator(self.__config__['mutation_operator'])
        self.__evolver__._set_db_name(self.__config__['db_name'])
        self.__evolver__._set_start_from_scratch(self.__config__['start_from_scratch'])
        self.__evolver__._set_end_of_generation_handler(self.__config__['generationhandler'])
        self.__evolver__._set_low_memory_footprint(self.__config__['low_memory_footprint'])


    def evolve(self):
        """Launch the evoluation process.

        :param is_sequential: to set if we work sequentially or not.
        When False, evolution stops when the requirement is fit.
        When True, evolution stops after each generation
        """
        self.__parametrize__()
        self.__evolver__.Run()

    def sequentially_evolve(self):
        """
        Launch the evolution process sequentially.
        The process stops after each generation.
        This is a generator returning the best element after each generation
        """
        self.__parametrize__()
        gen = self.__evolver__.run_sequentially()
        while True:
            try:
                res = gen.next()
                yield res
            except StopIteration:
                #We reach the end (best fitness, or end generation)
                raise StopIteration()
