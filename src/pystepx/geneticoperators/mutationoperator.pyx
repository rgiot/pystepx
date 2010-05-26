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

@author: by Mehdi Khoury
@author: by Romain Giot
@version: 1.30
@copyright: (c) 2010 Romain Giot under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: mehdi.khoury at gmail.com
@contact: giot.romain at gmail.com
"""

"""
Basic mutation operations.
"""

import copy
import random

from pystepx.tree import buildtree
from pystepx.geneticoperators.abstractoperator import AbstractGeneticOperator
import pystepx.geneticoperators.crossutil as crossutil

cimport abstractoperator

cdef class Mutator(abstractoperator.AbstractGeneticOperator):
    """
    Class doing mutation with respect of the tree rule
    """


    cpdef mutate(self, int maxdepth, parent, p1_map,int p1_depth):
        """
        create a mutated individual from a parent tree using Koza styled mutation

        :param maxdepth: maximum depth of the mutated offspring
        :param parent: parent tree e.g. a=buildtree.buildTree().AddHalfNode((0,2,'root'),0,2,7)
        :param p1_map: parent tree index mapping e.g a_map=crossutil.get_indices_mapping_from_tree(a)
        :param p1_depth: parent tree depth e.g. a_depth=crossutil.get_depth_from_indices_mapping(a_map)

        :return: a tuple containing two elements.
            - The first one is a boolean indicating if the mutated tree is identical to the parent
                (if identical, returns True)
            - The second one is the mutated tree

        """
        #Generated vars
        fragment_p1     = None
        subtree1_parent = None

        # get a random depth for parent1
        if p1_depth >= 1:
            p1_mutation_depth = 1
        else:
            p1_mutation_depth = random.randint(1, p1_depth-1)

        # get a random depth in p2 such that the resulting
        # offspring lenght is <= offspring maxdepth
        mychoice1 = crossutil.UnpackIndicesFromList(\
                crossutil.GetPackedListIndicesAtDepth(p1_map, p1_mutation_depth))
        p1_point = random.choice(mychoice1)
        parent1_clone = copy.deepcopy(parent)
        fragment_p1 = eval("parent1_clone%s" %crossutil.IndexLstToIndexStr2(p1_point), globals(), locals())

        # first we need to extract the top node of each subtree
        if isinstance(fragment_p1, list):
            firstnode_p1 = fragment_p1[0]
        if isinstance(fragment_p1, tuple):
            firstnode_p1 = fragment_p1
        # get the parent node of each sub tree (context of each parent)
        subtree1_parent_s = crossutil.IndexLstToIndexStr2(p1_point)
        # if the first node is not an ADF, the string version of the
        # index of the subtree is just the index of upper node in the tree
        if firstnode_p1[0] != 2:
            subtree1_parent_s = subtree1_parent_s[:-3]
        # get the subtree using the index we just obtained
        subtree1_parent = eval("parent1_clone%s" % subtree1_parent_s, globals(), locals())
        # get the flat list of permitted nodes for the parent tree
        # for that first get the list of permitted branch nodes...
        context_p1 = self.__rules__[subtree1_parent[0][2]]
        context = copy.deepcopy(context_p1)
        # and extend to it the list of permitted leaf nodes
        context[p1_point[-1]-1][0].extend( context[p1_point[-1]-1][1])
        if len(context[p1_point[-1]-1][0])>1 and firstnode_p1[0]==2:
            context[p1_point[-1]-1][0].remove(firstnode_p1)
        # get the context from grammar rules for each parent

        # min_mutation_depth for the subtree has to be extracted by looking when is the next child with a terminal
        min_mutation_depth = 1
        #print context[p1_point[-1]-1][0]
        #flag = random.choice(context[p1_point[-1]-1][0])
        if not self.__rules__[subtree1_parent[0][2]][p1_point[-1]-1][1]:
            min_mutation_depth = 2
        #print flag

        mutant_fragment = buildtree.BuildTree(self.__rules__).AddHalfNode(\
                random.choice(  context[p1_point[-1]-1][0]) ,
                                p1_mutation_depth,
                                p1_mutation_depth + min_mutation_depth,
                                maxdepth)

        # make sure that the mutant fragment is different from the previous fragment
        if len(mutant_fragment) ==1 and isinstance(mutant_fragment[0], tuple):
            mutant_fragment = mutant_fragment[0]



        exec("parent1_clone%s=mutant_fragment" % crossutil.IndexLstToIndexStr2(p1_point)) in  globals(), locals()

        identical = False
        if mutant_fragment == fragment_p1:
            identical = True
        # no branch nor leaf compatible from fragment to parent nodes
        return (identical, parent1_clone)






