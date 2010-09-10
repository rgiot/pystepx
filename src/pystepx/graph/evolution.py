#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Show the evolution"""

# AUTHOR Romain Giot <romain.giot@ensicaen.fr>

import matplotlib.pyplot as plt

import pystepx.writepop

import psyco
psyco.profile()


class ReadFitnessEvolution(object):
    """
    Class: ReadFitnessEvolution
    =========================

    Read information in pySTEP database
    """

    def __init__(self, pop, tabname='pop'):
        """
        @param path: path to the sqlite database
        @param tabname: name of the tables
        """

        self.max, self.min, self.mean, self.std = [], [], [], []

        self._pop = pop
        self._tabname = tabname


    def getFitnessInfo(self):
        """
        getFitnessInfo
        ==============

        Read the fitness information in the datbase
        """

        i = 0

        while True:
            try:
                max, min, mean, std = self._get_fitness_info_for(i)
                self.max.append(max)
                self.min.append(min)
                self.mean.append(mean)
                self.std.append(std)
                i = i+1
            except Exception, e:
                print e
                break

    def _get_fitness_info_for(self, generation):
        """
        _get_fitness_info_for
        =====================

        Returns the required information for the attended generation.

        @param generation: generation number to check.

        @returns max, min, mean values of the fitness
        """

        print 'Check generation %d => %s%d' % (generation, self._tabname, generation)


        return self._pop.get_fitness_stats_for_table("%s%d" %(self._tabname, generation))

class FitnessEvolutionGraph(object):
    """
    Class: FitnessEvolutionGraph
    ============================

    Class allwing plotting of fitness res.
    """

    def __init__(self, data):
        """
        @param data: Instance of ReadFitnessEvolution
        """
        self._data = data

    def buildFigure(self):
        """
        buildFigure
        ===========

        Build the Figure.
        """
        assert len(self._data.max) == len(self._data.min) == len(self._data.mean) == len(self._data.std), 'Error in size of data'

        plt.xlabel('Generation (#)')
        plt.ylabel('Fitness score Min/Avg/Max')

        gen = range( len(self._data.max) )

        #plt.fill_between( gen, self._data.min, self._data.max, color='gray', linewidth=2)
        plt.plot( gen, self._data.min, linewidth=2, color='k', label='min')
        plt.plot( gen, self._data.max, linewidth=2, color='k', linestyle='dashed',
                label='max')
        plt.plot( gen, self._data.mean, linewidth=2, color='k',
                linestyle='dashdot',
                label='mean')
        plt.plot( gen, self._data.std, linewidth=2, linestyle='dotted', color='k',
                label='std')
        plt.legend()

def main():
    import sqlite3
    db = sqlite3.connect('/tmp/pySTEPX3.sqlite')
    pop = pystepx.writepop.WritePop(db)

    inter = ReadFitnessEvolution(pop)
    inter.getFitnessInfo()

    graph = FitnessEvolutionGraph(inter)

    plt.figure()
    graph.buildFigure()
    plt.savefig('fitnessevo.eps' )
    plt.show()

if __name__ == "__main__":
    main()
