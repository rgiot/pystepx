# cython: profile=True

"""
Contains all sort of utilities to search and manipulate nested lists in the
context of strongly-typed crossover.
"""
"""
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


"""

from collections import deque
from copy import copy
import string


def BillSubtreeIndices( list tree_rep ):
    """
    gives the indexes of nested lists by depth
    original idea from bill at
    python-forum.org
 
    :param tree_rep: a nested list representing a tree
    
    :return: a list representing the indexes of the nested lists by depth
 
    """ 
    q = deque([ ([],tree_rep) ])
    list_of_index_lists = []
    while q:
        (indices, sub_tree) = q.popleft()
        list_of_index_lists.append(indices)
        for (ordinal, sst) in enumerate( sub_tree[1:] ):
            if isinstance( sst, list ):
                idxs = indices[:]
                idxs.append(ordinal+1)
                q.append( (idxs, sst) )
    return list_of_index_lists


def BillSubtreeIndices2( tree_rep ):
    """
    gives the indexes of nested lists by depth
    original idea from bill at
    python-forum.org
 
    :param tree_rep: a nested list representing a tree
    
    @:eturn: a dictionary representing the indexes of the nested lists by depth
 
    """ 
    q = [ ([],tree_rep) ]
    dict_of_index_lists = {}
    while q != []:
        (indices, sub_tree) = q.pop(0)
        dict_of_index_lists.setdefault(len(indices), []).append(indices)
        for (ordinal, sst) in enumerate( sub_tree[1:] ):
            if isinstance( sst, list ):
                q.append( (indices[:] + [ordinal+1], sst) )
    return dict_of_index_lists



cpdef list GetIndicesMappingFromTree( list tree ):
    """
    reuse bill's idea to gives the indexes of all nodes (may they be
    a sub tree or a single leaf) gives a list of indices of every sublist.
    To do that, I add one thing: the last element of an index is the length
    of the present list. e.g. 
        - get_indices_mapping_from_tree([1,2,3,4,5,6,7,8,9])
            gives: [([0], 9)]
        - get_indices_mapping_from_tree([1,[2,3],4,5,6,7,8,9])
            gives: [([0], 8), ([1], 2)]
        - get_indices_mapping_from_tree([1,[2,3,7],4,5,6,7,8,9])
            gives: [([0], 8), ([1], 3)]
        - get_indices_mapping_from_tree([1,[2,3,7],4,[5,[6,[7,8,9]]]])
            gives: [([0], 4), ([1], 3), ([3], 2), ([3, 1], 2), ([3, 1, 1], 3)]
    
 
    :param tree: a nested list representing a tree
    :return: a nested list representing the indexes of the nested lists by depth
 
    """ 
    cdef list list_of_index_lists
    cdef list indices
    cdef list sub_tree
    cdef int ordinal
    cdef list idxs
    cdef q

    q = deque([ ([],tree) ])
    list_of_index_lists = [([0],len(tree))]
    while q:
        (indices, sub_tree) = q.popleft()
        list_of_index_lists.append((indices, len(sub_tree)))
        for (ordinal, sst) in enumerate( sub_tree[1:] ):
            if isinstance( sst, list ):
                idxs = indices[:]
                idxs.append(ordinal + 1)
                q.append( (idxs, sst) )

    list_of_index_lists.pop(1)
    return list_of_index_lists


# only if the map of indices has been done
cpdef int GetDepthFromIndicesMapping(list list_indices):
    """
    Gives the depth of the nested list from the index mapping
    
    :param list_indices: a nested list representing the indexes of the nested lists by depth
    
    :return: depth
 
    """ 
    cpdef tuple x

    return max([len(x[0]) for x in list_indices]) + 1

# only if the map of indices has been done
cpdef list GetPackedListIndicesAtDepth(list list_indices, int depth):
    """
    gives the indexes of nested lists at a specific depth.
    Only works if the map of indices has been done
    
    :param list_indices: a nested list representing the indexes of the nested lists by depth
    :param depth: depth at which we wnat the indexes
    
    :return: a nested list representing the indexes of the nested lists
    at a specific depth
 
    """ 
    cdef list result
    cdef list temp
    cdef tuple x
    cdef int y
    cdef list temp1
    cdef tuple elem

    if depth == 0:
        return [(list_indices[0][0], 1)]
    elif depth == 1:
        result = []
        temp = copy(list_indices)
        temp.pop(0)
        temp1 = [x for x in temp if len(x[0]) == 1]
        if list_indices[0][1] > 1:
            for y in xrange(1, list_indices[0][1]):
                    if [y] not in [elem[0] for elem in temp1]:
                        result.append(([y], 1) )
        result.extend(temp1)
        return result
    else :
        list_indices.pop(0)
        return [x for x in list_indices if len(x[0]) == depth]


cpdef list UnpackIndicesFromList(list map_indices):
    """
    unpack_indices_from_list. e.g. ([([1], 6), ([2], 4)])
    gives: [[1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [2, 1], [2, 2], [2, 3]]
    
    :param map_indices: a nested list representing the indexes of the nested lists by depth
    :return: the indexes of different nodes in the tree as a flat list
 
    """ 
    cdef list result
    cdef tuple elem
    cdef list temp
    cdef int x

    result = []
    for elem in map_indices:
        if elem[0][0] == [0]:
            result.append(range(1, elem[1]))
        else:
            if elem[1] == 1:
                temp = copy(elem[0])
                result.append(temp)
            else:
                for x in xrange(1, elem[1]):
                    temp = copy(elem[0])
                    temp.append(x)
                    result.append(temp)
    return result


# slow way!
#def GetDepth(tree_rep):
#    """
#    GetDepth
#    ========
#    Gives the depth of the nested list. Slow recursive way.
#
#    @param tree_rep: a nested list representing a tree
#
#    @return: depth
#
#    """
#    return max([len(x[0]) for x in bill_subtree_indices3( tree_rep )])+1



cpdef str IndexLstToIndexStr(list index):
    """
    transform a list into an index element
    e.g. list named 'a' and index ref is [1,1,2], result is
    '[1][1][2]'

    :param index: a flat list of indexes

    :return: a string

    """
    return str(index).replace(',','][')

# this version is 15% faster
# transform a list into an index element
# e.g. list named 'a' and index ref is [1,1,2], result is
# '[1][1][2]'
cpdef str IndexLstToIndexStr2(index):
    """
    transform a list into an index element
    this version is 15% faster
    transform a list into an index element
    e.g. list named 'a' and index ref is [1,1,2], result is
    '[1][1][2]'
 
    :param index: a flat list of indexes
    
    :return: a string
 
    """
    return "[%s]" % string.join(map(str, index), "][")


