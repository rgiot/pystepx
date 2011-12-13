"""
buildtree
=========
Contains strongly-typed versions of Koza-based tree building methods.
The buildTree() method is the constructor for a tree and contains the
relevant functions.

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



"""
import random
import logging


# Exceptions related to tree building
class TreeBuildingError(Exception):
    """Base class for the tree building exception"""
    pass
class NoTerminalSet(TreeBuildingError):
    """No terminal set has been found"""
    pass
class NoFunctionSet(TreeBuildingError):
    """No function has been found"""
    pass
class EmptyOrderedSet(TreeBuildingError):
    """XXX"""
    pass


# class that contains methods to build a random tree



cdef class BuildTree(object):
    """
    implement tree building methods described in Koza I/II.
    The buildTree() method is the constructor for a tree and contains the
    relevant functions.
    """

    cdef dict __rules__

    def __init__(self, dict rules):
        """Initialize various objects"""
        self.set_tree_rules(rules)

    def set_tree_rules(self, dict rules):
        """
        Method:: set_tree_rules
        =======================

        Set the tree rules.
        """
        self.__rules__ = rules

    cdef setRandomLeafChild(self, parent, int child_nb):
        """
        Function:  setRandomLeafChild
        =============================

        Set the a random leaf node

        @param parent: the parent node (generally a root node) e.g. (0,2,'root')
        @param child_nb: the child node position (0 for first, 1 for second and so on...)
        @return: the random leaf child node e.g. (3,0,'x')
        """
        random_leaf_child = []
        try:
            random_leaf_child = random.choice(self.__rules__[parent[2]][child_nb][1])
        except Exception, e:
            logging.debug('======= Empty terminal set! This parent has no leaf node to choose from!')
            logging.debug(str( e))
            logging.debug( ''.join([ 'problem with ', str(parent), ' at child ', str(child_nb)]))
            logging.debug( ''.join([ 'possible child', str(self.__rules__[parent[2]])]))
            logging.debug( 'Maybe a wrong rule ? Verify the number of children')
            logging.debug( ''.join(['Child nb', str(child_nb)]))
            logging.debug( ''.join(['Set for the child', str(self.__rules__[parent[2]][child_nb])]))
            logging.debug( ''.join(['Leaf set for the child', str(self.__rules__[parent[2]][child_nb][1])]))
            raise NoTerminalSet, "Empty terminal set! This parent has no leaf  node to choose from!" + str(parent)

        return random_leaf_child



    cdef setRandomBranchChild(self, parent, int child_nb):
        """
        Function:  setRandomBranchChild
        ===============================

        Set the a random branch node

        @param parent: the parent node (generally a root node) e.g. (0,2,'root')
        @param child_nb: the child node position (0 for first, 1 for second and so on...)
        @return: the random branch child node e.g. (1,2,'*')
        """
        random_branch_child = []
        try:
            random_branch_child = random.choice(self.__rules__[parent[2]][child_nb][0])
        except Exception, e:
            logging.debug('======= Empty function set! This parent has no branch node to choose from!')
            logging.debug(str( e))
            logging.debug( ''.join([ 'problem with ', str(parent), ' at child ', str(child_nb)]))
            logging.debug( ''.join([ 'possible child', str(self.__rules__[parent[2]])]))
            logging.debug( 'Maybe a wrong rule ? Verify the number of children')
            logging.debug( ''.join(['Child nb', str(child_nb)]))
            logging.debug( ''.join(['Set for the child', str(self.__rules__[parent[2]][child_nb])]))
            logging.debug( ''.join(['Leaf set for the child', str(self.__rules__[parent[2]][child_nb][0])]))
 
            raise NoFunctionSet, "Empty function set! This parent has no branch node to choose from!"

        return random_branch_child



    cdef setRandomBranchWithTerminalSet(self, list parent, int child_nb):
        """
        Function:  setRandomBranchWithTerminalSet
        =========================================

        Set an random branch child node which has terminals

        @param parent: the parent node (generally a root node) e.g. (0,2,'root')
        @param child_nb: the child node position (0 for first, 1 for second and so on...)
        @return: the branch child node e.g. (1,2,'*')
        """
        constraints = self.__rules__
        if not constraints[parent[2]][child_nb][0]:
            logging.debug('======= Empty function set! Impossible to create random branch with terminal set')
            logging.debug( ''.join([ 'problem with ', str(parent), ' at child ', str(child_nb)]))
            logging.debug( ''.join([ 'possible child', str(self.__rules__[parent[2]])]))
            logging.debug( 'Maybe a wrong rule ? Verify the number of children')
            logging.debug( ''.join(['Child nb', str(child_nb)]))
            logging.debug( ''.join(['Set for the child', str(self.__rules__[parent[2]][child_nb])]))
            logging.debug( ''.join(['Leaf set for the child', str(self.__rules__[parent[2]][child_nb][0])]))

            raise NoFunctionSet, "Empty function set! Root node has no function to choose from!"

        initial = constraints[parent[2]][child_nb][0]
        try:
            logging.debug('List to filter')
            logging.debug(str(initial))

            #filter functions (take aways those who don't have a terminal set)
            initial2 = [ x for x in initial if constraints[x[2]][child_nb][1] ]
            return random.choice(initial2)
        except:
            # if there are no functions with terminal set, use the other ones
            logging.debug('unable to choose a function')
            logging.debug(str(initial))
            logging.debug(str(initial2))
            return random.choice(self.__rules__[parent[2]][child_nb][0])


    cdef tuple setRandomBranchWithFunctionSet(self, parent, int child_nb):
        """
        Function:  setRandomBranchWithTerminalSet
        =========================================

        Set an random branch child node which has terminals

        @param parent: the parent node (generally a root node) e.g. (0,2,'root')
        @param child_nb: the child node position (0 for first, 1 for second and so on...)
        @return: the branch child node e.g. (1,2,'*')
        """
        constraints = self.__rules__
        if not constraints[parent[2]][child_nb][0]:
            raise NoFunctionSet, "Empty function set! Root node has no function to choose from!"

        initial = constraints[parent[2]][child_nb][0]
        try:
            #filter functions (take aways those who don't have a function set)
            initial = [ x for x in initial if constraints[x[2]][child_nb][0] ]
            return random.choice(initial)
        except:
            # if there are no functions with function set, use the other ones
            return random.choice(self.__rules__[parent[2]][child_nb][1])


# The FULL method (see KOZA GP Vol I and II)
    cpdef list AddFullNode(self, tuple parent, int depth, int maxdepth):
        """
        Function:  AddFullNode2
        =======================
        Build a tree using Koza Full Algorithm

        @param parent: the parent node (generally a root node) e.g. (0,2,'root')
        @param depth: starting depth (0 when building a tree from scratch)
        @param maxdepth: max tree depth (in principle unlimited - careful with memory limitation through :))
        @return: returns a tree built using Koza Full
        """
        cdef list result
        cdef int myDepth
        cdef list listdepth


        result = [parent]
        myDepth = depth
        # stopping condition - when maximum depth is reached
        if myDepth == maxdepth:
            return parent
        # add branch upon branch until before maximum depth,
        # then, build leafs
        else:
            # if the parent node is a function,
            result = [parent]
            # get the number of children of this function (arity)
            nbChildren = parent[1]
            listdepth = []

            # for every child
            for i in xrange(nbChildren):
                # add a new depth counter
                listdepth.append(myDepth)

                # if near max depth add a leaf
                if maxdepth - listdepth[i] == 1:
                    result.append(self.setRandomLeafChild(parent, i))

                # if 2 nodes from max depth, only use functions which have a terminal set
                elif maxdepth - listdepth[i] == 2:
                    try:
                        result.append(self.AddFullNode( \
                                        self.setRandomBranchWithTerminalSet(parent, i),
                                        listdepth[i] + 1,
                                        maxdepth))
                        listdepth[i] = listdepth[i] + 1
                    except:
                        try:
                            result.append(self.AddFullNode( \
                                        self.setRandomBranchChild(parent, i),
                                        listdepth[i] + 1,
                                        maxdepth))
                            listdepth[i] = listdepth[i] + 1
                        except:
                            result.append(self.setRandomLeafChild(parent, i))

                # else add a branch
                else:
                    try:
                        result.append(self.AddFullNode( \
                                        self.setRandomBranchWithFunctionSet(parent, i),
                                        listdepth[i] + 1,
                                        maxdepth))
                        listdepth[i] = listdepth[i]+1
                    except:
                        try:
                            result.append(self.AddFullNode( \
                                    self.setRandomBranchChild(parent, i),
                                    listdepth[i] + 1,
                                    maxdepth))
                            listdepth[i] = listdepth[i]+1
                        except:
                            result.append(self.setRandomLeafChild(parent, i))

        return result


# The HALF method (see KOZA GP Vol I and II)
    cpdef list AddGrowNodeMin(self, tuple parent, int depth, int mindepth, int maxdepth):
        """
        Function:  AddFullNode2
        =======================
        Build a tree using Koza Half Algorithm

        @param parent: the parent node (generally a root node) e.g. (0,2,'root')
        @param depth: starting depth (0 when building a tree from scratch)
        @param mindepth: min tree depth 
        @param maxdepth: max tree depth (in principle unlimited - careful with memory limitation through :))
        @return: returns a tree built using Koza Full
        """
        cdef list result, listdepth
        cdef int myDepth
  
        myDepth = depth
        # stopping condition - when maximum depth is reached
        if myDepth == maxdepth:
            return parent
        # add branch upon branch until before maximum depth,
        # then, build leafs
        else:
            # if the parent node is a function,

            result = [parent]
            # get the number of children of this function (arity)
            nbChildren = parent[1]
            listdepth = []
            # for every child
            for i in xrange(nbChildren):
                # add a new depth counter
                listdepth.append(myDepth)

                # if near max depth add a leaf
                if maxdepth - listdepth[i] == 1:
                    result.append(self.setRandomLeafChild(parent, i))

                # if 2 nodes from max depth, only use functions which have a terminal set
                elif maxdepth - listdepth[i] == 2 \
                    or depth - mindepth-1 <= -1:
                    try:
                        result.append(self.AddGrowNodeMin( \
                                self.setRandomBranchWithTerminalSet(parent, i),
                                listdepth[i] + 1,
                                mindepth,
                                maxdepth))
                    except:
                        logging.debug("Unable to build a branch with a terminal set")
                        try:
                            result.append(self.AddGrowNodeMin( \
                                            self.setRandomBranchChild(parent, i),
                                            listdepth[i] + 1,
                                            mindepth,
                                            maxdepth))
                            listdepth[i] = listdepth[i] + 1
                            logging.debug("Unable to build a branch with a branch")
                        except:
                            result.append(self.setRandomLeafChild(parent, i))


                # else in normal cases, add randomly a branch or a leave
                else:
                    chosenType = random.randint(0, 1)
                    if chosenType:
                        result.append(self.AddGrowNodeMin( \
                                            self.setRandomBranchChild(parent, i),
                                            listdepth[i] + 1,
                                            mindepth,
                                            maxdepth))
                        listdepth[i] = listdepth[i] + 1
                    else:
                        result.append(self.setRandomLeafChild(parent, i))

        return result


    cpdef list AddHalfNode(self, tuple parent, int depth, int mindepth, int maxdepth):
        """
        Function:  AddHalfNode
        ======================

        Build a tree using Koza Ramped Half-n-Half

        @param parent: the parent node (generally a root node) e.g. (0,2,'root')
        @param depth: starting depth (0 when building a tree from scratch)
        @param mindepth: min tree depth (only works with 2 in the present version)
        @param maxdepth: max tree depth (in principle unlimited - careful with memory limitation through :))
        @return: returns a tree built using Koza Ramped Half-n-Half
        """
        cdef int randomDepth = random.randint(mindepth, maxdepth)
        prob = random.random()< 0.5
        if prob:
            return self.AddFullNode(parent, depth, randomDepth)
        else:
            return self.AddGrowNodeMin(parent, depth, mindepth, randomDepth)

