"""
evalfitness
===========
Contains methods to evaluate the fitness of a tree.

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

@author: Romain Giot
"""

from collections import deque
import logging

import sys
if sys.version_info < (2, 6):
  import numpy as math
else:
  import math

import fitnessutil
from pystepx.tree.treeutil import PostOrder_Search
from pystepx.tree.treeutil import WrongValues
from pystepx.tree.treeconstants import NODE_TYPE, \
                                    NODE_NAME, \
                                    NB_CHILDREN
from pystepx.tree.treeconstants import ROOT_BRANCH, \
                                    FUNCTION_BRANCH, \
                                    ADF_DEFINING_BRANCH, \
                                    VARIABLE_LEAF, \
                                    CONSTANT_LEAF, \
				    ADF_LEAF, \
            KOZA_ADF_DEFINING_BRANCH, \
            KOZA_ADF_FUNCTION_BRANCH, \
            KOZA_ADF_PARAMETER

#TODO Cleanup this module and move specific tutorial code elsewhere

class FitnessTreeEvaluation(object):
    """
    Class: FitnessEvaluation
    ========================

    Operate the various fitness evaluations of trees.
    """

    def __init__(self):
        """
        @param gp_engine: Genetic programming engine.
        """
        #XXX See if better to store gp_engine ?
        self.__terminals__ = None
        self.__functions__ = None

    def set_terminals(self, terminals):
        """
        Set the terminals
        """
        self.__terminals__ = terminals

    def set_functions(self, functions):
        """
        Set the function set
        """
        self.__functions__ =  functions

    def get_terminals(self):
        """Returns the terminals."""
        return self.__terminals__

    def get_functions(self):
        """Returns the functions."""
        return self.__functions__

    def check_configuration(self):
        """
        check_configuration
        ===================
        Check if the configuration is correct in order to use the object.
        """
        assert self.__terminals__ is not None, \
                """You must set the terminals"""
        assert self.__functions__ is not None, \
                """You must set the functions"""

    def EvalTreeForOneInputSet(self, my_tree, input_set_ref):
        """
        Function:  EvalTreeForOneInputSet
        =================================
        Function used to evaluate a tree by pluggin in
        one set of values (one learning example)

        @param my_tree: the nested list representing a tree
        @param input_set_ref: the set of values to plug into the tree
        @return: the fitness of the tree for this set of values
        """
        resultStack = deque()
        adfDict = {}

        # examine every node in the tree in pre-order taversal
        # (leaves first and then branches)
        for elem in PostOrder_Search(my_tree):
            # if the node is a leaf (variable, or constant),
            # add its value to the result stack
            if elem[NODE_TYPE] == VARIABLE_LEAF:
                resultStack.append(self.__terminals__[elem[NODE_NAME]][input_set_ref])
            elif elem[NODE_TYPE] == CONSTANT_LEAF:
                resultStack.append(self.__terminals__[elem[NODE_NAME]])
            # if the node is a function with n arguments, pop the result stack
            # n times. Get these popped elemnts as arguments for the function,
            # and replace the top of the stack by the result of the function
            elif elem[NODE_TYPE] == FUNCTION_BRANCH:
                nb          = elem[NB_CHILDREN]
                name        = elem[NODE_NAME]
                tempResult = deque()
                for i in xrange(0, nb):
                    tempResult.append(resultStack.pop())
                resultStack.extend(map(self.__functions__[name], [tempResult]))
            # if the node is an ADF branch, add the top of the stack to
            # the ADF dictionary
            elif elem[NODE_TYPE] == ADF_DEFINING_BRANCH:
                adfDict[elem[NODE_NAME]] = resultStack[-1]
            # if the node is an ADF terminal, add the corresponding ADF
            # branch value available in the dictionary to the result stack
            elif elem[NODE_TYPE] == ADF_LEAF:
                resultStack.append(adfDict[elem[2]])
            # if the node is a root, apply the root function to all
            # direct children and return the result.
            elif elem[NODE_TYPE] == ROOT_BRANCH:
                name = elem[NODE_NAME]
                tempResult = []
                while resultStack:
                    tempResult.append(resultStack.popleft())
                resultStack.extend(map(self.__functions__[name], [tempResult]))

        return resultStack[0]

    def EvalTreeForOneListInputSet(self, my_tree):
        """
        Function:  EvalTreeForOneInputSet
        =================================
        Function used to evaluate a tree by pluggin in
        one list of values (one list of data points).
        Works with Koza ADF

        @param my_tree: the nested list representing a tree
        @return: the fitness of the tree for this set of values
        """


        resultStack = deque()
        adfDict = {}

        # examine every node in the tree in pre-order taversal
        # (leaves first and then branches)
        for elem in PostOrder_Search(my_tree):

            # if the node is a leaf (variable, or constant),
            # add its value to the result stack
            if elem[NODE_TYPE] == VARIABLE_LEAF or \
               elem[NODE_TYPE] == CONSTANT_LEAF or \
               elem[NODE_TYPE] == KOZA_ADF_PARAMETER:
                resultStack.append(self.__terminals__[elem[NODE_NAME]])

            # if the node is a function with n arguments, pop the result stack
            # n times. Get these popped elemnts as arguments for the function,
            # and replace the top of the stack by the result of the function
            elif elem[NODE_TYPE] == FUNCTION_BRANCH:
                nb = elem[NB_CHILDREN]
                name = elem[NODE_NAME]
                tempResult = deque()
                for i in xrange(0, nb):
                    tempResult.append(resultStack.pop())
                resultStack.extend(map(self.__functions__[name],[tempResult]))

            # if the node is an ADF branch, add the top of the stack to
            # the ADF dictionary
            elif elem[NODE_TYPE] == ADF_DEFINING_BRANCH:
                adfDict[elem[2]] = resultStack[-1]

            # if the node is an ADF terminal, add the corresponding ADF
            # branch value available in the dictionary to the result stack
            elif elem[NODE_TYPE] == ADF_LEAF:
                if elem[2] not in adfDict:
                    print 'error in tree', my_tree
                resultStack.append(adfDict[elem[2]])

            # if the node is a root, apply the root function to all
            # direct children and return the result.
            elif elem[NODE_TYPE] == ROOT_BRANCH:
                name = elem[NODE_NAME]
                tempResult=[]
                while resultStack:
                    tempResult.append(resultStack.popleft())
                resultStack.extend(map(self.__functions__[name],[tempResult]))

            # We are calling a Koza adf
            elif elem[NODE_TYPE] == KOZA_ADF_FUNCTION_BRANCH:

                name = elem[NODE_NAME]
                nb = elem[NB_CHILDREN]

                #Get previously computed args
                tempResult = deque()
                for i in xrange(0, nb):
                    tempResult.append(resultStack.pop())

                resultStack.extend(map(self.__functions__[name],[tempResult]))


            else:
                print 'We do not know this node !'
                print elem
                quit()

        return resultStack[0]



    def compile_tree(self, my_tree, one_input_set=True):
        """
        Function:  compile_tree
        =======================

        Compile the tree, in order to evaluated it several times.

        @param my_tree: the nested list representing a tree
        @param one_input_set: if True, the tree is evaluated for each elem of the
        input set, instead of being evaluated on the whole set
        @return: a string representation of the tree
        """

        tree_string = self.get_tree_str(my_tree, one_input_set)
        return compile(tree_string, '<string>', 'eval')

    def get_tree_str(self, my_tree, one_input_set):
        """
        Function: get_tree_str
        ======================

        Returns a string representation of the tree.
        The aim of this string is to be evaluated.

        @param my_tree: the nested list representing a tree
        @param one_input_set: if True, the tree is evaluated for each elem of the
        input set, instead of being evaluated on the whole set

        """

        representation = ''

        if type(my_tree) is list:
            actual_node = my_tree[0]
        else:
            actual_node = my_tree

        node_name = actual_node[NODE_NAME]
        nb_children = actual_node[NB_CHILDREN]
        node_type = actual_node[NODE_TYPE]

        if node_type in [ROOT_BRANCH, FUNCTION_BRANCH, ADF_DEFINING_BRANCH]:
            #function call
            representation += "self.__functions__['%s']( (" % node_name

            res = [ self.get_tree_str(my_tree[i+1], one_input_set) for i in xrange(nb_children)]
            representation += ",".join(res)

            representation += ",) )"
        elif node_type in [VARIABLE_LEAF, CONSTANT_LEAF]:
            #terminals
            if one_input_set:
                representation += "self.__terminals__['%s'][input_set_indice]" % node_name
            else:
                representation += "self.__terminals__['%s']" % node_name
        else:
            raise Exception('Unable to manage this node' + str(actual_node))

        return representation

    def EvalTreeForOneListInputSet_tutorial8(self, my_tree):
        """
        Function:  EvalTreeForOneInputSet2
        ==================================
        Function used to evaluate a tree by pluggin in
        one list of values (one list of data points)

        @param my_tree: the nested list representing a tree
        @return: the fitness of the tree for this set of values
        """
        resultStack = deque()
        adfDict = {}
        # examine every node in the tree in pre-order taversal
        # (leaves first and then branches)
        for elem in PostOrder_Search(my_tree):
            # if the node is a leaf (variable, or constant),
            # add its value to the result stack
            if elem[0] == 3:
                resultStack.append(self.__terminals__[elem[2]])
            elif elem[0] == 4:
                resultStack.append(self.__terminals__[elem[2]])
            # if the node is a function with n arguments, pop the result stack
            # n times. Get these popped elemnts as arguments for the function,
            # and replace the top of the stack by the result of the function
            elif elem[0] == 1:
                nb = elem[1]
                name = elem[2]
                tempResult = deque()
                for i in xrange(nb):
                    tempResult.append(resultStack.pop())
                resultStack.extend(map(self.__functions__[name], [tempResult]))
                
            # if the node is an ADF branch, add the top of the stack to
            # the ADF dictionary
            elif elem[0] == 2:
                adfDict[elem[2]] = resultStack[-1]
            # if the node is an ADF terminal, add the corresponding ADF
            # branch value available in the dictionary to the result stack
            elif elem[0] == 5:
                resultStack.append(adfDict[elem[2]])
            # if the node is a root, apply the root function to all
            # direct children and return the result.
            elif elem[0] == 0:
                name = elem[2]
                tempResult = []
                while resultStack:
                    tempResult.append(resultStack.popleft())
                resultStack.extend(map(self.__functions__[name], [tempResult]))
        return resultStack[0]


    def EvalTreeForOneListInputSet_tutorial9(self, my_tree):
        """
        Function:  EvalTreeForOneInputSet2
        ==================================
        Function used to evaluate a tree by pluggin in
        one list of values (one list of data points)

        @param my_tree: the nested list representing a tree
        @return: the fitness of the tree for this set of values
        """
        resultStack = deque()
        adfDict = {}
        # examine every node in the tree in pre-order taversal
        # (leaves first and then branches)
        for elem in PostOrder_Search(my_tree):
            # if the node is a leaf (variable, or constant),
            # add its value to the result stack
            if elem[0] == 3:
                resultStack.append(self.__terminals__[elem[2]])
            elif elem[0] == 4:
                resultStack.append(self.__terminals__[elem[2]])
            # if the node is a function with n arguments, pop the result stack
            # n times. Get these popped elemnts as arguments for the function,
            # and replace the top of the stack by the result of the function
            elif elem[0] == 1:
                nb = elem[1]
                name = elem[2]
                tempResult = deque()
                for i in xrange(nb):
                    tempResult.append(resultStack.pop())
                resultStack.extend(map(self.__functions__[name], [tempResult]))
                
            # if the node is an ADF branch, add the top of the stack to
            # the ADF dictionary
            elif elem[0] == 2:
                adfDict[elem[2]] = resultStack[-1]
            # if the node is an ADF terminal, add the corresponding ADF
            # branch value available in the dictionary to the result stack
            elif elem[0] == 5:
                resultStack.append(adfDict[elem[2]])
            # if the node is a root, apply the root function to all
            # direct children and return the result.
            elif elem[0] == 0:
                name = elem[2]
                tempResult = []
                while resultStack:
                    tempResult.append(resultStack.popleft())
                resultStack.extend(map(self.__functions__[name], [tempResult]))
        return resultStack[0]


    def EvalTreeForAllInputSets(self, my_tree, input_sets):
        """
        Function:  EvalTreeForAllInputSets
        ==================================
        Function used to evaluate a tree by pluggin in
        several sets of values

        @param my_tree: the nested list representing a tree
        @param input_sets: the set of values to plug into the tree
        @return: the fitnesses of the tree over several sets of values
        """
        results = []
        val = len(input_sets)
        for elem in xrange(val):
            results.append(self.EvalTreeForOneInputSet(my_tree, elem))
        return results


    def EvalTreeForAllInputSetsCompiled(self, my_tree, input_sets):
        """
        Function:  EvalTreeForAllInputSetsCompiled
        ==========================================
        Function used to evaluate a tree by pluggin in
        several sets of values.

        Instead of interpreting each time the tree, it compile it and evaluate
        it.

        @param my_tree: the nested list representing a tree
        @param input_sets: the set of values to plug into the tree
        @return: the fitnesses of the tree over several sets of values
        """
        compiled_tree = self.compile_tree(my_tree, one_input_set=True)

        results = []
        val = len(input_sets)
        for input_set_indice in xrange(val):
            results.append( eval(compiled_tree,
                    {'input_set_indice': input_set_indice,
                        'results': results,
                        'self':self,
                        'WrongValues':WrongValues
                    }))
        return results


class FinalFitness(object):
    """
    Class: FinalFitness
    ===================

    Compute the final fitness.
    """

    def __init__(self, ideal_results, nb_eval):
        self.__nb_eval__        = nb_eval
        self.__ideal_results__  = ideal_results

    
    def ClassificationFitness(self, intermediate_outputs):
        """
        Function:  ClassificationFitness
        ================================

        Compute the classification tree performance.
        For each possible label, compute the recognition rate
        The final fitness is the mean error of each possible label

        @param intermediate_outputs: the fitnesses of the tree over several sets of
        values
        @return: global fitness
        """
        import numpy as np

        intermediate_outputs = np.array(intermediate_outputs)

        error_rates = []
        for label in np.unique(self.__ideal_results__):
            idx = self.__ideal_results__ == label
            error_rates.append(np.mean(intermediate_outputs[idx] != label))

        return np.mean(error_rates)


    
    
    def FinalFitness(self, intermediate_outputs):
        """
        Function:  FinalFitness
        =======================
        Compute global fitness of an individual. Intended when wanting to refine
        the fitness score.

        @param intermediate_outputs: the fitnesses of the tree over several sets of
        values
        @return: global fitness
        """
        final_output = 0
        # each element represents one different sample or set of input data
        # the size of each represents the number of examples
        #each sub-element represents the value(s) obtained at the top of a three for one input
        #In this particular case, we simply add the difference of all results with an ideal solution

        # the ideal solution is : [adf1 = x+y adf2 = add1*(y-x)]
        # build a corresponding list of two-elements sub lists
        # then evaluate the sum of the difference with our built models
        for nb in xrange(self.__nb_eval__):
            ideal_results = self.__ideal_results__[nb]
            obtained_results = intermediate_outputs[nb]

            for el in obtained_results:
                try:
                    if math.isinf(el):
                        return el
                except:
                    return float('inf')

            # sum the absolute values of the differences over one example
            diff = sum( [math.fabs(ideal_results[x] - obtained_results[x])
                            for x in xrange(len(ideal_results))])
            final_output = final_output + diff
        return final_output

    def FinalFitness2(self, intermediate_outputs):
        """
        Function:  FinalFitness2
        ========================
        Compute global fitness of an individual. Intended when wanting to refine
        the fitness score.

        @param intermediate_outputs: the fitnesses of the tree over one of value
        @return: global fitness
        """
        final_output = 0
        # each element represents one different sample or set of input data
        # the size of each represents the number of examples
        #each sub-element represents the value(s) obtained at the top of a three for one input
        #In this particular case, we simply add the difference of all results with an ideal solution

        # the ideal solution is : [adf1 = x+y adf2 = add1*(y-x)]
        # build a corresponding list of two-elements sub lists
        # then evaluate the sum of the difference with our built models
        ideal_results    = self.__ideal_results__
        obtained_results = intermediate_outputs
        for res in xrange(len(self.__ideal_results__)):
            for el in obtained_results[res]:
                try:
                    if math.isinf(el):
                        return el
                except:
                    return float('inf')
            # sum the absolute values of the differences over one example
            diff = sum( [math.fabs(ideal_results[res][x]-obtained_results[res][x])
                            for x in xrange(self.__nb_eval__)])
            final_output = final_output+diff
        return final_output

    def FinalFitnessIfThenElse(self, intermediate_outputs):
        """
        Function:  FinalFitness3
        ========================
        Compute global fitness of an individual. Intended when wanting to refine
        the fitness score.

        In this case, the root of the tree contains three nodes:
        -if
        -then
        -else

        So, the results of the tree depend on these 3 adfs

        @param intermediate_outputs: the fitnesses of the tree over several sets of
        values
        @return: global fitness
        """
        final_output = 0
        # each element represents one different sample or set of input data
        # the size of each represents the number of examples
        #each sub-element represents the value(s) obtained at the top of a three for one input
        #In this particular case, we simply add the difference of all results with an ideal solution

        for nb in xrange(self.__nb_eval__):
            ideal_results    = self.__ideal_results__[nb]
            obtained_results = intermediate_outputs[nb]

            for el in obtained_results:
                try:
                    if math.isinf(el):
                        return el
                except:
                    return float('inf')

            # sum the absolute values of the differences over one example
            # here we use a very very puzzling python list comprehension... This deserve a bit of explanation.
            # In general, the expression "T if C is true, or F if C is false" can be written as (F, T)[bool(C)].
            # This single line could be replaced by a simpler but slower expression of the type:
            #z=[]
            #for i in range(10):
            #    if  C:
            #        z.append(T)
            #    else:
            #        z.append(F)
            # In our case, if the first element of obtained_resultsis is True (the result of the if statement)
            # then use the result produce by the second branch, otherwise use the result produced by the third
            # branch.
            # As far as we are concerned, list comprehension are faster + compact + more memory efficient.
            # so for this crucial fitness calculation bit, I chose this solution...
            # May the deities of the Python programming pantheon forgive me (Sorry Guido...).
            diff = sum( [(  math.fabs(ideal_results[x] - obtained_results[1]) , #then
                            math.fabs(ideal_results[x] - obtained_results[2]) ) #else
                            [obtained_results[0]]                               #if
                                for x in xrange(len(ideal_results))
                        ])
            final_output = final_output + diff
        return final_output


    def FinalFitness4(self, intermediate_outputs):
        """
        Function:  FinalFitness3
        ========================
        Compute global fitness of an individual. Intended when wanting to refine
        the fitness score.

        @param intermediate_outputs: the fitnesses of the tree over several sets of
        values
        @return: global fitness
        """
        final_output = 0
        # each element represents one different sample or set of input data
        # the size of each represents the number of examples
        #each sub-element represents the value(s) obtained at the top of a three for one input
        #In this particular case, we simply add the difference of all results with an ideal solution

        # the ideal solution is : [adf1 = x+y adf2 = add1*(y-x)]
        # build a corresponding list of two-elements sub lists
        # then evaluate the sum of the difference with our built models
        for nb in xrange(len(intermediate_outputs)):
            for el in intermediate_outputs[nb]:
                for el2 in el:
                    try:
                        if isinstance(el2, bool):
                            pass
                        elif math.isinf(el2):
                            return el2
                    except:
                        return float('inf')
        # sum the absolute values of the differences over one example
        # here we use a very very puzzling python list comprehension... This deserve a bit of explanation.
        # In general, the expression "T if C is true, or F if C is false" can be written as (F, T)[bool(C)].
        # This single line could be replaced by a simpler but slower expression of the type:
        #z=[]
        #for i in range(10):
        #    if  C:
        #        z.append(T)
        #    else:
        #        z.append(F)
        # In our case, if the first element of obtained_resultsis is True (the result of the if statement)
        # then use the result produce by the second branch, otherwise use the result produced by the third
        # branch.
        # As far as we are concerned, list comprehension are faster + compact + more memory efficient.
        # so for this crucial fitness calculation bit, I chose this solution...
        # May the deities of the Python programming pantheon forgive me (Sorry Guido...).
        final_output = sum([(   math.fabs(self.__ideal_results__[x][y] - intermediate_outputs[2][x][y]),
                                math.fabs(self.__ideal_results__[x][y] -
                                    intermediate_outputs[1][x][y])) [intermediate_outputs[0][x][y]]
                                    for x in xrange(len(intermediate_outputs[1]))
                                        for y in xrange(len(intermediate_outputs[1][x]))
                            ])

        return final_output



