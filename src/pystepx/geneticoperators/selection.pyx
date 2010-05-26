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
@version: 1.00
@copyright: (c) 2009 Mehdi Khoury under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: mehdi.khoury at gmail.com
"""

"""
Contains methods to select individuals from a population.
So far fittest selection and tournament selection are supported.
"""

import timeit
import cPickle
import random
import operator
import numpy as np
cimport numpy as np

from pystepx.fitness import evalfitness
#import pystepx.wchoice as wchoice

cpdef GetDBKeysAndFitness(con, str tablename):
    """
    the list of fitnesses with associated unique ids obtained
    from the database. A lengthy operation. Should be only called once
    and used as an argument for the tournament or fitness selection functions.

    :param conn: connection to the database
    :param tablename: name of the databse table

    :returns: the list of fitnesses with associated unique ids obtained
    from the database

    """
    SELECT = """
      SELECT o_id, fitness 
      FROM %s 
      ORDER BY fitness ASC
      """ %tablename
 #   SELECT = "SELECT o_id, fitness FROM %s " %tablename

    cur = con.cursor()
    cur.execute(SELECT)
    result = cur.fetchall()
    cur.close()
    #sorted_result = sorted(result, key=operator.itemgetter(1))
    #return np.array(sorted_result)
    return np.array(result)



def SelectFileFittest(pop_file):
    """
    Select the fittest individual from a file

    :param pop_file: population file

    :returns: the reference of one selected individual with

    """
    # read the content of the file and evaluate add the fitness of each element in a list
    fileinput = open(pop_file,'rb')
    u = cPickle.Unpickler(fileinput)

    temp=u.load()
    result=[]
    # evaluate fitess of each element and store in in a list
    while temp:
        result.append(evalfitness.EvalFitness(). \
                FinalFitness(evalfitness.EvalFitness(). \
                    EvalTreeForAllInputSets(temp,xrange(2))))
        try:
            temp=u.load()
        except:
            break
    fileinput.close()
    # select 'size' random indexes of elements
    mysample=xrange(len(result))
    # create the corresponding list of associated fitnesses
    mysample_fitnesses=[result[el] for el in mysample]
    ref_sample=[]
    # asssociate both in one data structure
    for i in xrange(len(mysample)):
        ref_sample.append((mysample[i],mysample_fitnesses[i]))
    # sort them by fitness score
    ref_sample=sorted(ref_sample, key=operator.itemgetter(1))
    selected_individual=ref_sample[0]
    #print selected_individual
    return selected_individual

def SelectDBOneFittest(db_list):
    """
    Select fittest individual.
    ATTENTION: based on the assumption that db_list is already sorted
 
    :param db_list: the ordered list of fitnesses with associated unique ids obtained from the database
    
    :returns: the reference of the one fittest individual
 
    """ 
    return db_list[0]

def SelectDBSeveralFittest(int n, db_list):
    """
    Select n fittest individual
    
    :param n: the number of fittest individuals
    :param db_list: the ordered list of fitnesses with associated unique ids obtained from the database
    
    :return: the reference of the one fittest individual
 
    """ 
    return db_list[:n]






    
def TournamentSelectFileOne(int size, pop_file, prob_selection_fittest):
    """
    Select one individual from a file using Tournament selection
    appropriate and fast when using a small population (<=1000)
 
    :param size: number of individual choosen at random from the population
    :param pop_file: population file
    :param prob_selection_fittest: prob of selecting the fittest of the group
    
    :return: the reference of one selected individual with :

     * prob of choosing fittest=p
     * prob of choosing second fittest= p*(1-p)
     * prob of choosing third fittest= p*((1-p)^2)...
 
    """ 
    # read the content of the file and evaluate add the fitness of each element in a list
    fileinput = open(pop_file,'rb')
    u = cPickle.Unpickler(fileinput)
        
    temp=u.load()
    result=[]
    # evaluate fitess of each element and store in in a list
    while temp:
        result.append(evalfitness.EvalFitness(). \
                FinalFitness(evalfitness.EvalFitness(). \
                    EvalTreeForAllInputSets(temp,xrange(2))))
        try:
            temp=u.load()
        except:
            break
    fileinput.close()
    # select 'size' random indexes of elements
    mysample=random.sample(xrange(len(result)), size)
    # create the corresponding list of associated fitnesses
    mysample_fitnesses=[result[el] for el in mysample]
    ref_sample=[]
    # asssociate both in one data structure
    for i in xrange(len(mysample)):
        ref_sample.append((mysample[i],mysample_fitnesses[i])) 
    # sort them by fitness score
    ref_sample=sorted(ref_sample, key=operator.itemgetter(1))
    prob_selection=prob_selection_fittest
    # if probability of choosing fittest = 1 return fittest
    if prob_selection==1:
        selected_individual=ref_sample[0]
    # otherwise choose one element regarding the probability
    # prob of choosing fittest=p
    # prob of choosing second fittest= p*(1-p)
    # prob of choosing third fittest= p*((1-p)^2)...
    else:
        selection = _get_weight(size, prob_selection) 
        val = random.random()
        pos = np.searchsorted(selection, val)
        selected_individual = ref_sample[pos]

    #print selected_individual
    return selected_individual
    
def TournamentSelectDBOne(int size, float prob_selection, db_list):
    """
    Select one individual from a database using Tournament selection
 
    :param size: number of individual choosen at random from the population
    :param prob_selection: prob of selecting the fittest of the group
    :param db_list: the list of fitnesses with associated unique ids obtained from the database
    
    :return: the reference of one selected individual with :
  
    * prob of choosing fittest=p
    * prob of choosing second fittest= p*(1-p)
    * prob of choosing third fittest= p*((1-p)^2)...
 
    """ 
    
    ref_sample = random.sample(db_list, size)
    ref_sample = sorted(ref_sample, key=operator.itemgetter(1))
    #print ref_sample
    if prob_selection==1:
        selected_individual=[ref_sample[0]]
    else:
        selection = _get_weight(size, prob_selection) 
        val = random.random()
        pos = np.searchsorted(selection, val)
        selected_individual = ref_sample[pos]


    return selected_individual


_weight_cache = {}

cdef np.ndarray _get_weight(int size, float prob_selection):
    """
    Return the array of weights.
    """
    cdef np.ndarray selection

    if (size, prob_selection) not in _weight_cache:
        selection = np.array([prob_selection*((1 - prob_selection)**x) for x in xrange(1, size)])
        selection = np.insert(selection, 0, prob_selection)
        selection = selection / np.sum(selection) #normalize
        selection = np.cumsum(selection)

        _weight_cache[ (size, prob_selection)] = selection

    return _weight_cache[ (size, prob_selection)]

cpdef np.ndarray TournamentSelectDBSeveral(int nb_outputs, 
        int size, 
        float prob_selection, 
        np.ndarray db_list,
            unique=False):
    """
    Select several individuals from a database using Tournament selection

   :param nb_outputs: repeat the tournament selection nb_outputs times, to
    return a list nb_outputs selected individuals
    :param size: number of individual choosen at random from the population
    :param prob_selection: prob of selecting the fittest of the group
    :param db_list: the list of fitnesses with associated unique ids obtained from the database
    :param unique: if True, an individual can only be selected one time

    :return: return a list nb_outputs of references of individuals selected by
    tournament
    """
    
    cdef np.ndarray selection_result = np.array([])

    #weights
    cdef np.ndarray selection = _get_weight(size, prob_selection)


    cdef int i = 0
    cdef float val
    cdef int pos

    while i < nb_outputs:
        #Get size random samples ordered by fitness
        ref_sample = random.sample(db_list, size)
        ref_sample = sorted(ref_sample, key=operator.itemgetter(1))
        #assert len(ref_sample) == size

        if prob_selection == 1:
            selected_individual = [ref_sample[0]]
        else:
            #Get individual depending on probabilities
            val = random.random()
            pos = np.searchsorted(selection, val)
            selected_individual = ref_sample[pos]

        if unique == False or selected_individual[0] not in selection_result:
            #Add to list
            if i == 0:
                selection_result = np.array(selected_individual[0])
            else:
                selection_result = np.vstack( (selection_result, selected_individual[0]) )
            i = i+1

    return selection_result





