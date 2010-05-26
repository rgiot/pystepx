#!/usr/bin/env python
# -*- coding: utf-8 -*-
# cython: profile=True



"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: by Mehdi Khoury
@author: by Romain Giot
@version: 1.30
@copyright: (c) 2010 Romain Giot under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: mehdi.khoury at gmail.com
@contact: giot.romain at gmail.com
"""


"""
Basic crossover operations.
"""

import random
import logging

import copy

import crossutil
from pystepx.tree import treeutil, buildtree
from pystepx.geneticoperators.abstractoperator import AbstractGeneticOperator
cimport abstractoperator
from pystepx.tree.treeconstants import *

import psyco
psyco.profile()

cdef class CrossoverOperator(abstractoperator.AbstractGeneticOperator):
    """
    Embed all crossover related operations.
    In the context of strongly-typed Genetic
    Programming, this operator is heavily modified to produce offsprings that
    are compliant with multiple rules and constraints set by the user.
    In the present version, only a strongly-typed version of Koza 1 point
    crossover is supported.
    """


    def __init__(self):
        """"""
        super(CrossoverOperator, self).__init__()

        self.set_strongly_typed_crossover_degree(False)
        self.set_crossover_mapping(None)

    cpdef check_configuration(self):
        """
        Does the test of AbstractGeneticOperator and checked the presence
        of __strongly_typed_crossover_degree__ and __crossover_mapping__
        """

        #AbstractGeneticOperator.check_configuration(self)
        assert self.__strongly_typed_crossover_degree__ is not None, \
                """You have to specify is we have to use a strongly typed
                crossover degre"""
        assert self.__crossover_mapping__ is not None, \
                "You have to specify a crossover mapping"

    cpdef set_strongly_typed_crossover_degree(self, bool value):
        """
        """
        self.__strongly_typed_crossover_degree__ = value

    cpdef set_crossover_mapping(self, list mapping):
        """
        Set the crossover mapping
        """
        self.__crossover_mapping__ = mapping



    cpdef Koza1PointCrossover(self, int maxdepth, list p1, list p2, list p1_mp, list p2_mp, int p1_depth, int p2_depth):
        """
        create 2 offsprings from 2 parents using a modified version of Koza-1-point
        crossover. This version try to produce offsprings compliant with the
        constraints and rules used to build an individual. If it does not manage,
        it produce a report showing if the offsprings produced are compatible.

        :param maxdepth: maximum depth of the mutated offspring
        :param p1: parent tree 1  e.g. a=buildtree.buildTree().AddHalfNode((0,2,'root'),0,2,7)
        :param p2: parent tree 2  e.g. a=buildtree.buildTree().AddHalfNode((0,2,'root'),0,2,7)
        :param p1_mp: parent tree index mapping e.g a_map=crossutil.get_indices_mapping_from_tree(a)
        :param p2_mp: parent tree index mapping e.g a_map=crossutil.get_indices_mapping_from_tree(a)
        :param p1_depth: parent tree depth e.g. a_depth=crossutil.get_depth_from_indices_mapping(a_map)
        :param p2_depth: parent tree depth e.g. a_depth=crossutil.get_depth_from_indices_mapping(a_map)

        :return: a tuple containing 3 elements
            - The first one is a list of 1 and 0 indicating if the first and second offspring are rule
            compliant.
            [1,1,1,1] frag2_leaf_compatible_p1 and frag1_leaf_compatible_p2 and frag2_branch_compatible_p1 and frag1_branch_compatible_p2
            [1,0,1,1] frag2_leaf_compatible_p1 and not frag1_leaf_compatible_p2 and frag2_branch_compatible_p1 and frag1_branch_compatible_p2
            [1,1,0,1] frag2_leaf_compatible_p1 and frag1_leaf_compatible_p2 and not frag2_branch_compatible_p1 and frag1_branch_compatible_p2
            and so on... This information can be use to decide if we want to introduce non-compliant offsprings into the population.
            - The second one is the first offspring
            - The third one is the second offspring
        """

        logging.debug('New crossover')

        cdef list p1_map, p2_map
        cdef list parent1_clone, parent2_clone
        cdef int p1_cross_depth, p2_cross_depth
        cdef int fragment_p1_depth, fragment_p2_depth
        cdef tuple firstnode_p1, firstnode_p2
        cdef str subtree1_parent_s, subtree2_parent_s
        cdef list context_p1, context_p2
        cdef bool frag1_leaf_compatible_p2, frag2_leaf_compatible_p1, frag1_branch_compatible_p2, frag2_branch_compatible_p1
        cdef list frag1, frag2
        cdef str temp1, temp2

        p1_map = copy.deepcopy(p1_mp)
        p2_map = copy.deepcopy(p2_mp)

        # get a random depth for parent1
        p1_cross_depth = random.randint(1, p1_depth - 1)

        # get a random depth in p2 such that the resulting
        # offspring lenght is <= offspring maxdepth
        fragment_p1_depth = p1_depth-1 - p1_cross_depth

        if p2_depth > (maxdepth - fragment_p1_depth):
            if maxdepth-fragment_p1_depth > 0:
                p2_cross_depth = random.randint(1, (maxdepth - fragment_p1_depth))
            else:
                p2_cross_depth = 1
        else:
            p2_cross_depth = random.randint(1, p2_depth-1)

        mychoice1 = crossutil.UnpackIndicesFromList(\
                crossutil.GetPackedListIndicesAtDepth(p1_map, p1_cross_depth))
        mychoice2 = crossutil.UnpackIndicesFromList(\
                crossutil.GetPackedListIndicesAtDepth(p2_map, p2_cross_depth))
        p1_point  = random.choice(mychoice1)
        p2_point = random.choice(mychoice2)

        parent1_clone = copy.deepcopy(p1)
        parent2_clone = copy.deepcopy(p2)
        fragment_p1 = eval("parent1_clone%s" % crossutil.IndexLstToIndexStr2(p1_point), globals(), locals())
        fragment_p2 = eval("parent2_clone%s" % crossutil.IndexLstToIndexStr2(p2_point), globals(), locals())

        # Having selected a sub tree, we need to check structural integrity and compatibility
        # first we want to know if the sub-tree is located under a specific ADF defining branch

        # first we need to extract the top node of each subtree
        if isinstance(fragment_p1, list):
            firstnode_p1 = fragment_p1[0]
        elif isinstance(fragment_p1, tuple):
            firstnode_p1 = fragment_p1

        if isinstance(fragment_p2, list):
            firstnode_p2 = fragment_p2[0]
        elif isinstance(fragment_p2, tuple):
            firstnode_p2 = fragment_p2

        # get the parent node of each sub tree (context of each parent)
        subtree1_parent_s = crossutil.IndexLstToIndexStr2(p1_point)
        if firstnode_p1[NODE_TYPE] != ADF_DEFINING_BRANCH:
            subtree1_parent_s = subtree1_parent_s[:-3]

        subtree2_parent_s = crossutil.IndexLstToIndexStr2(p2_point)
        if firstnode_p2[NODE_TYPE] != ADF_DEFINING_BRANCH:
            subtree2_parent_s = subtree2_parent_s[:-3]

        subtree1_parent, subtree2_parent = None, None
        subtree1_parent = eval("parent1_clone%s" % subtree1_parent_s, globals(), locals())
        subtree2_parent = eval("parent2_clone%s" % subtree2_parent_s, globals(), locals())


        # get the context from grammar rules for each parent
        # print buildtree.buildTree().treeSets
        context_p1 = self.__rules__[subtree1_parent[0][NODE_NAME]]
        context_p2 = self.__rules__[subtree2_parent[0][NODE_NAME]]

        # check that the subtree are compatible with their new parents
        frag1_leaf_compatible_p2 = True
        frag2_leaf_compatible_p1 = True
        frag1_branch_compatible_p2 = True
        frag2_branch_compatible_p1 = True


        #TODO create an inline function
        # extract all terminal nodes of the fragment subtrees in flat lists
        frag1, frag2 = [], []
        if list(treeutil.LeafNodes_Search(fragment_p1)):
            if isinstance(list(treeutil.LeafNodes_Search(fragment_p1))[0], tuple):
                frag1 = list(treeutil.LeafNodes_Search(fragment_p1))
            else:
                frag1 = [tuple(fragment_p1)]
        else:
            frag1 = fragment_p1

        if list(treeutil.LeafNodes_Search(fragment_p2)):
            if isinstance(list(treeutil.LeafNodes_Search(fragment_p2))[0], tuple):
                frag2 = list(treeutil.LeafNodes_Search(fragment_p2))
            else:
                frag2 = [tuple(fragment_p2)]
        else:
            frag2 = fragment_p2

        #TODO create an inline function
        # check if the fragments have terminal nodes incompatible with parent context
        for elem_frag2 in frag2:
            if elem_frag2 not in context_p1[p1_point[-1]-1][1]:
                frag2_leaf_compatible_p1 = False
                break
        for elem_frag1 in frag1:
            if elem_frag1 not in context_p2[p2_point[-1]-1][1]:
                frag1_leaf_compatible_p2 = False
                break

        #TODO create an inline function
        # extract all branch nodes of the fragment subtrees in flat lists
        frag1, frag2 = [], []
        if isinstance(list(treeutil.BranchNodes_Search(fragment_p1))[0], tuple):
            frag1 = list(treeutil.BranchNodes_Search(fragment_p1))
        else:
            frag1 = [tuple(fragment_p1)]

        if isinstance(list(treeutil.BranchNodes_Search(fragment_p2))[0], tuple):
            frag2 = list(treeutil.BranchNodes_Search(fragment_p2))
        else:
            frag2 = [tuple(fragment_p2)]

        # if no branch node in subtree, then branch is all compatible...
        for elem_frag1 in frag1:
            if len(frag1) == 1 and frag1[0][0] != 1:
                frag1_branch_compatible_p2 = True
            elif elem_frag1 not in context_p2[0]:
                frag1_branch_compatible_p2 = False
                break
            else:
                frag1_branch_compatible_p2 = True

        for elem_frag2 in frag2:
            if len(frag2) == 1 and frag2[0][0] != 1:
                frag2_branch_compatible_p1 = True
            elif elem_frag2 not in context_p1[0]:
                frag2_branch_compatible_p1 = False
                break
            else:
                frag2_branch_compatible_p1 = True

        # if the automatic replacement of compatible branch operators is authorized
        # do it to make the offspring compatible wit hthe grammar rules...
        copy_fragment_p1 = copy.deepcopy(fragment_p1)
        copy_fragment_p2 = copy.deepcopy(fragment_p2)

        #TODO write inline functions
        if  frag1_branch_compatible_p2 == False \
            and frag1_leaf_compatible_p2 == True \
            and self.__strongly_typed_crossover_degree__ == True:

            frag1 = list(set(frag1))
            temp1 = str(copy_fragment_p1)
            for elem_frag1 in frag1:
                for elem_p2 in context_p2[p2_point[-1]-1][0]:
                    for elem_crossover_mapping in self.__crossover_mapping__:
                        if elem_crossover_mapping[1] == str(elem_p2[2]) \
                            and elem_crossover_mapping[0] == str(elem_frag1[2]):
                            temp1 = temp1.replace(elem_crossover_mapping[0], elem_crossover_mapping[1])
            copy_fragment_p1 = eval("%s"%temp1,  globals(), locals())

        if  frag2_branch_compatible_p1 == False \
           and frag2_leaf_compatible_p1 == True \
           and self.__strongly_typed_crossover_degree__ == True:

            frag2 = list(set(frag2))
            temp2 = str(copy_fragment_p2)
            for elem_frag2 in frag2:
                for elem_p1 in context_p1[p1_point[-1]-1][0]:
                    for elem_crossover_mapping in self.__crossover_mapping__:
                        if elem_crossover_mapping[1] == str(elem_p1[2])\
                                and elem_crossover_mapping[0] == str(elem_frag2[2]):
                            temp2 = temp2.replace(elem_crossover_mapping[0], elem_crossover_mapping[1])
            copy_fragment_p2 = eval("%s" %temp2, globals(), locals())


        frag1_leaf_compatible_p2 = True
        frag2_leaf_compatible_p1 = True
        frag1_branch_compatible_p2 = True
        frag2_branch_compatible_p1 = True

        # extract all terminal nodes of the fragment subtrees in flat lists
        frag1, frag2 = [], []
        if list(treeutil.LeafNodes_Search(fragment_p1)):
            if isinstance(list(treeutil.LeafNodes_Search(fragment_p1))[0], tuple):
                frag1 = list(treeutil.LeafNodes_Search(fragment_p1))
            else:
                frag1 = [tuple(fragment_p1)]
        else:
            frag1 = fragment_p1
        if list(treeutil.LeafNodes_Search(fragment_p2)):
            if isinstance(list(treeutil.LeafNodes_Search(fragment_p2))[0], tuple):
                frag2 = list(treeutil.LeafNodes_Search(fragment_p2))
            else:
                frag2 = [tuple(fragment_p2)]
        else:
            frag2 = fragment_p2

        # check if the fragments have terminal nodes incompatible with parent context
        for elem_frag2 in frag2:
            if elem_frag2 not in context_p1[p1_point[-1]-1][1]:
                frag2_leaf_compatible_p1 = False
                break
        for elem_frag1 in frag1:
            if elem_frag1 not in context_p2[p2_point[-1]-1][1]:
                frag1_leaf_compatible_p2 = False
                break

        #XXX Simplify
        # return the offspring resulting from the crossover with indicators of
        # structural compliance of the offspring.
        # [1,1,1,1] frag2_leaf_compatible_p1 and frag1_leaf_compatible_p2 and frag2_branch_compatible_p1 and frag1_branch_compatible_p2
        # [1,0,1,1] frag2_leaf_compatible_p1 and not frag1_leaf_compatible_p2 and frag2_branch_compatible_p1 and frag1_branch_compatible_p2
        # [1,1,0,1] frag2_leaf_compatible_p1 and frag1_leaf_compatible_p2 and not frag2_branch_compatible_p1 and frag1_branch_compatible_p2
        # and so on...
        # This information can be use to decide if we want to introduce non-compliant offsprings into the population.
        pattern = [0, 0, 0, 0]

        if frag2_leaf_compatible_p1 \
                and frag1_leaf_compatible_p2 \
                and frag2_branch_compatible_p1 \
                and frag1_branch_compatible_p2:
            pattern = [1, 1, 1, 1]

        elif frag2_leaf_compatible_p1 \
                and not frag1_leaf_compatible_p2 \
                and frag2_branch_compatible_p1 \
                and frag1_branch_compatible_p2:
            pattern = [1, 0, 1, 1]

        elif not frag2_leaf_compatible_p1 \
                and frag1_leaf_compatible_p2\
                and frag2_branch_compatible_p1 \
                and frag1_branch_compatible_p2:
            pattern = [0, 1, 1, 1]

        elif not frag2_leaf_compatible_p1 \
                and not frag1_leaf_compatible_p2 \
                and frag2_branch_compatible_p1 \
                and frag1_branch_compatible_p2:
            pattern = [0, 0, 1, 1]

        elif frag2_leaf_compatible_p1 \
                and frag1_leaf_compatible_p2 \
                and not frag2_branch_compatible_p1 \
                and frag1_branch_compatible_p2:
            pattern = [1, 1, 0, 1]

        elif frag2_leaf_compatible_p1 \
                and frag1_leaf_compatible_p2 \
                and frag2_branch_compatible_p1 \
                and not frag1_branch_compatible_p2:
            pattern = [1, 1, 1, 0]

        elif frag2_leaf_compatible_p1 \
                and frag1_leaf_compatible_p2 \
                and not frag2_branch_compatible_p1 \
                and not frag1_branch_compatible_p2 :
            pattern = [1, 1, 0, 0]

        elif frag2_leaf_compatible_p1 \
                and not frag1_leaf_compatible_p2 \
                and not frag2_branch_compatible_p1 \
                and not frag1_branch_compatible_p2 :
            pattern = [1, 0, 0, 0]

        elif not frag2_leaf_compatible_p1 \
                and frag1_leaf_compatible_p2 \
                and not frag2_branch_compatible_p1 \
                and not frag1_branch_compatible_p2 :
             pattern = [0, 1, 0, 0]

        exec("parent1_clone%s=fragment_p2" % crossutil.IndexLstToIndexStr2(p1_point))  in globals(), locals()
        exec("parent2_clone%s=fragment_p1" % crossutil.IndexLstToIndexStr2(p2_point))  in globals(), locals()

        return (pattern, parent1_clone, parent2_clone)

    cpdef Koza2PointsCrossover(self, int maxdepth,list parent1, list parent2, list p1_map, list p2_map, int p1_depth, int p2_depth):
        """???"""
        first_p_cross = []
        for i in xrange(10):
            cp1_copy_parent1 = copy.deepcopy(parent1)
            cp1_copy_parent2 = copy.deepcopy(parent2)
            cp1_copy_p1_map = copy.deepcopy(p1_map)
            cp1_copy_p2_map = copy.deepcopy(p2_map)
            first_p_cross = self.Koza1PointCrossover( maxdepth,
                                                 cp1_copy_parent1,
                                                 cp1_copy_parent2,
                                                 cp1_copy_p1_map,
                                                 cp1_copy_p2_map,
                                                 p1_depth,
                                                 p2_depth)
            if first_p_cross[0]==[1,1,1,1]:
                break

        second_p_cross = []
        for i in xrange(10):
            cp2_copy_parent1 = copy.deepcopy(first_p_cross[1])
            cp2_copy_parent2 = copy.deepcopy(first_p_cross[2])
            cp2_copy_p1_map = crossutil.GetIndicesMappingFromTree(cp2_copy_parent1)
            cp2_copy_p2_map = crossutil.GetIndicesMappingFromTree(cp2_copy_parent2)
            cp2_copy_p1_depth = crossutil.GetDepthFromIndicesMapping(cp2_copy_p1_map)
            cp2_copy_p2_depth = crossutil.GetDepthFromIndicesMapping(cp2_copy_p2_map)

            second_p_cross = self.Koza1PointCrossover(maxdepth,
                                                 cp2_copy_parent1,
                                                 cp2_copy_parent2,
                                                 cp2_copy_p1_map,
                                                 cp2_copy_p2_map,
                                                 cp2_copy_p1_depth,
                                                 cp2_copy_p2_depth)
            if second_p_cross[0]==[1,1,1,1]:
                break
        return second_p_cross


