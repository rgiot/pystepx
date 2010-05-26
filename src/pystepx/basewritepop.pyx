#!/usr/bin/env python
# -*- coding: utf-8 -*-
# cython: profile=True


"""
writepop
========
Contains all classes used to write and extract individuals and populations 
on the SQLite database.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: by Mehdi Khoury
@version: 1.00
@copyright: (c) 2009 Mehdi Khoury under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: mehdi.khoury at gmail.com


@author: by Romain Giot
@version: 1.30
"""

import gc
import sqlite3
import logging
import copy

#import marshal
import cPickle


from pystepx.geneticoperators import crossutil

cimport numpy as np

cdef inline str list_to_db(list list):
    """Transfert the list in the right way to the db"""
#    return buffer(marshal.dumps(list, -1)) #marshal
    return cPickle.dumps(list) #cPickle

cdef inline db_to_list( field):
    """Transfert the db field to the list"""
#    return copy.deepcopy(marshal.loads(field)) #marshal
    return cPickle.loads(field.encode('ascii','ignore')) #cPickle


cpdef impl_list_to_db(list list):
    return list_to_db(list)

cpdef impl_db_to_list(field):
    return db_to_list(field)


#TODO Rename this class ?
cdef class BaseWritePop(object):
    """

    Manage the saving of the population in database.
    XXX Add new columns (source for example, raw_fitness, ...)
    """
    
    #cpdef object _con_ #sqlite3 connection

    #TODO Look if it will be better to provide the path instead of the
    #connection
    def __init__(self, con):
        """
        Initialize the object by providing it the reference to the
        sqlite connection.

        @param con: Connection to database
        """
        self._con_ = con
        self._con_.text_factory = str

    cpdef get_connexion(self):
        return self._con_

    cpdef get_tree_objects(self, myresult):
        """Extract information from the db tree representation.
        """
        cdef list my_tree, my_tree_mapping
        cdef int my_treedepth, my_evaluated
        cdef float my_fitness

        my_tree         = impl_db_to_list(myresult[0])
        my_tree_mapping = impl_db_to_list(myresult[1])
        my_treedepth    = myresult[2]
        my_evaluated    = myresult[3]
        my_fitness      = myresult[4]

        return my_tree, my_tree_mapping, my_treedepth, my_evaluated, my_fitness

    cpdef ClearDBTable(self, table):
        """
        Function:  ClearDBTable
        =======================
        clear the table of the database

        @param table: name of the database table

        """
        con = self._con_
        con.execute("drop table %s"%table)
        con.commit()

    cpdef is_generation_computed(self, tablename):
        """
        Return true if the population exists.
        XXX An improvment would be to see if the population is complete.
        Otherwise, it could be deleted.
        """

        query = """
        SELECT *
        FROM sqlite_master
        WHERE type='table'
        AND name='%s'
        """ %tablename
        cur = self._con_.cursor()
        cur.execute(query)
        myresult = cur.fetchall()
        cur.close()

        return len(myresult) == 1

    cpdef create_new_table(self, tablename): 
        """Create a new table."""
        #Create the new table
        self._con_.execute("""
            CREATE TABLE %s (
             o_id INTEGER PRIMARY KEY,
             tree TEXT,
             tree_mapping TEXT,
             treedepth INTEGER,
             evaluated INTEGER,
             fitness FLOAT)
            """ % tablename)



    cpdef add_to_initial_population(self, list tree, float fitness, str tablename, bool commit=False):
        """Add the individual to the initial population.

        @param tree: tree to add
        @param fitness: fitness of the tree
        @param tablename: name of the table used to store
        """

        my_tree_indices = crossutil.GetIndicesMappingFromTree(tree)
        depth = crossutil.GetDepthFromIndicesMapping(my_tree_indices)

        
        try:
            self._con_.execute("""
                INSERT INTO %s(o_id, tree, tree_mapping, treedepth, evaluated, fitness)
                VALUES (NULL,?,?,?,?,?)
                """ % tablename, ( list_to_db(tree),
                                   list_to_db(my_tree_indices),
                                  depth,
                                  1,
                                  fitness))
        except sqlite3.InterfaceError, e:
            print 'Error while saving :'
            print fitness
            print e
            quit()

        if commit == True:
            self.flush()

    cpdef add_new_individual(self, tuple indiv, str tablename):
        """Add the new individual to requires generation"""

        self._con_.execute("""
            INSERT INTO %s(o_id,tree,tree_mapping,treedepth,evaluated,fitness)
            VALUES (NULL,?,?,?,?,?)
            """ % tablename,
            ( list_to_db(indiv[1]),
              list_to_db(indiv[2]),
              indiv[3],
              indiv[4],
              indiv[5]))

        
    cpdef add_new_individuals(self, individuals, str tablename):
        """Add the new individuals to the required generation.
        
        @params individuals: list of tuples containing the information
        @param tablename: Name of table to use
        """
 
        logging.info('Write pop : %d indiv' % len(individuals))

        cdef tuple indiv
        for indiv in individuals:
            self.add_new_individual( indiv, tablename)

    cpdef copy_individuals_from_to(self, np.ndarray list, str source, str dest):
        """Copy individuals from source to destination.
        Operate the copy only with an sql query.
        """
        cdef np.ndarray elem
        cdef str query = """
          INSERT INTO %s (tree, tree_mapping, treedepth, evaluated, fitness)
            SELECT tree, tree_mapping, treedepth, evaluated, fitness
            FROM %s
            WHERE o_id in (%s) 
          """ % ( dest, 
                  source, 
                  ",".join([str(int(<float>elem[0])) for elem in list])
                )
        self._con_.execute(query)

        self.flush()


    cpdef get_individual(self, str tablename, int o_id, bool extract=False):
        """Returns an individual.

        @param tablename: Source table
        @param o_id: id of the individual
        @param extract: if extract is selected, extract the tree information
        """

        cur = self._con_.cursor()
        select = """
        SELECT tree, tree_mapping, treedepth, evaluated, fitness
        FROM %s
        WHERE o_id = %d
        """ % (tablename, o_id)
        cur.execute(select)


        myresult = cur.fetchone()
        cur.close()

        if not extract:
            return myresult
        else:
            my_tree         = db_to_list(myresult[0])
            my_tree_mapping = db_to_list(myresult[1])
            my_treedepth    = myresult[2]
            my_evaluated    = myresult[3]
            my_fitness      = myresult[4]


            return myresult, my_tree, my_tree_mapping, my_treedepth, my_evaluated, my_fitness

    cpdef get_best_individual(self, str tablename, bool extract=False):
        """Returns the best individual.

        @param tablename: Source table
        @param extract: if extract is selected, extract the tree information

        @todo implement
        """

        pass



    cpdef flush(self):
        """Commit all the modifications on disc."""
        logging.info('Flush db to disc')
        self._con_.commit()
        logging.debug( gc.collect())


    cpdef write_initial_population(self, trees, fitnesses, tablename):
        """
        Function:  write_initial_population
        ====================================

        Store the initial population generated by the evolver.

        @param trees: List of the generated trees
        @param fitnesses: Fitness values of the trees
        @param tablename: name of the database table

        """
        assert len(trees) == len(fitnesses), "Error in the size of input"
        cdef int i
        cdef list my_tree
        cdef float resultfitness

        #Create the new table
        self.create_new_table(tablename)

        #Store the individuals
        for i in xrange(len(trees)):
            my_tree = trees[i]
            resultfitness = fitnesses[i]

            self.add_to_initial_population(my_tree, resultfitness, tablename)

        self.flush()


    def PrintPopFromDB(self, tablename, filename):
        """
        Function:  PrintPopFromDB
        =========================
        print the population of trees with id references, tree depth and fitness scores

        @param tablename: name of the database table

        """
        con = self._con_

        SELECT = """
            SELECT o_id, tree, treedepth, fitness
            FROM %s
            ORDER BY fitness
            """ % tablename
        cur = con.cursor()
        cur.execute(SELECT)
        con.commit()
        myresult = cur.fetchall()

        output = open(filename,'w')
        for elem in myresult:
            output.write(''.join([str(elem[0]),
                                    str(db_to_list(elem[1])),
                                    str(elem[2]),
                                    str(elem[3]),
                                    '\n']))
        output.close()



    def GetPopStatFromDB(self, tablename):
        """
        Function:  GetPopStatFromDB
        ===========================
        get statistical data about the population

        @param con: path to database e.g. r'D:\3d_work\pythongp\pySTGP_0.51\src\pop_db'
        @param tablename: name of the database table

        """
        con = self._con_

        SELECT = """
            SELECT o_id, tree, treedepth, fitness
            FROM %s
            ORDER BY fitness
            """ % tablename
        cur = con.cursor()
        cur.execute(SELECT)
        con.commit()
        myresult = cur.fetchall()


        depths = []
        fit = []
        trees = []
        for elem in myresult:
            ntree = db_to_list(elem[1])
            if ntree not in trees:
                trees.append(ntree)
            depths.append(elem[2])
            #fit.append(elem[3])
        lengt = len(depths)
        uniques_trees = len(trees)
        av_depth = sum(depths)/len(myresult)
        #av_fit = sum(fit)/len(myresult)
        print ''.join(['average depth: ',
                        str(av_depth),
                        ' nb of unique trees: ',
                        str(uniques_trees),
                        ' over ',
                        str(lengt)])


