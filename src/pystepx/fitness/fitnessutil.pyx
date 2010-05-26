"""
fitnessutil
===========
Contains different methods used for problem specific fitness functions.
These are domain dependent utilities that are used for computing the fitness
function. e.g. the problem is about reading a list of motion capture frames and
we need a function that gives indexes of different groups of frames.

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

import copy
import csv

from pystepx.tree.treeutil import WrongValues

def GetIndexesOfGroupsInList(ml):
    """
    Function:  GetIndexesOfGroupsInList
    ===================================
    finds groups of identical elements in a list and gives their starting and last indexes.


    @param ml: a list of elements. e.g. ml=[1,1,1,1,1,2,2,3,4,5,5,5,6]

    returns: A list of tuples, where each tuple is of the form
    (group_discrete_val,group_first_ind,group_last_ind).
    e.g.  [(1, 0, 4), (2, 5, 6), (3, 7, 7), (4, 8, 8), (5, 9, 11), (6, 12, 12)]

    """
    temp = ml[0]
    output = []
    group_discrete_val = temp
    group_first_ind = 0
    group_last_ind = 0
    for i in xrange(1, len(ml)):
        if ml[i] == temp:
            group_last_ind = group_last_ind+1
        if ml[i] != temp:
            output.append((group_discrete_val, group_first_ind, group_last_ind))
            temp = ml[i]
            group_discrete_val = temp
            group_first_ind = i
            group_last_ind = i
        if i == len(ml)-1:
            output.append((group_discrete_val, group_first_ind, group_last_ind))
    return output

def GetInputDataFromFile(myfile):
    ifile  = open(myfile, "rb")
    reader = csv.reader(ifile, delimiter="\t")
    data=[]
    for row in reader:
        mystrline = row[0]
        y = eval(mystrline.strip())
        data.append(GetIndexesOfGroupsInList(list(y)))
    ifile.close()
    return data

def ReplaceUsingBinaryMask(listElem, binarymask, initial, replacement ):
    try:
        result = copy.deepcopy(listElem)
        for i in xrange(len(listElem)):
            for j in xrange(len(listElem[i][0])):
                if listElem[i][0][j][0] == initial and binarymask[i][j]:
                    result[i][0][j] = (replacement, listElem[i][0][j][1], listElem[i][0][j][2])

        return result
    except:
        raise WrongValues, "Wrong values sent to function node.\nCan't get result"
        exit

def UncompressList(listTuples):
    result=[]
    for elem in listTuples:
        #temp=[]
        for i in xrange(elem[1],elem[2]+1):
            result.append(elem[0])
    return result


