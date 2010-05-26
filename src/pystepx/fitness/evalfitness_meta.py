"""Module containing metaprogramming for the fitness evaluation.
This is an ugly hack because, for the momement, cython is not able to compile code with closures.

@author: by Romain Giot
@version: 1.30
@copyright: (c) 2010 Romain giot under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: romain.giot at ensicaen.fr
"""

import logging

import pystepx.fitness.evalfitness

from pystepx.tree.treeconstants import ROOT_BRANCH, \
                                    FUNCTION_BRANCH, \
                                    ADF_DEFINING_BRANCH, \
                                    VARIABLE_LEAF, \
                                    CONSTANT_LEAF, \
				    ADF_LEAF, \
            KOZA_ADF_DEFINING_BRANCH, \
            KOZA_ADF_FUNCTION_BRANCH
from pystepx.tree.treeconstants import NODE_TYPE, \
                                    NODE_NAME, \
                                    NB_CHILDREN

class FitnessTreeEvaluation_meta(pystepx.fitness.evalfitness.FitnessTreeEvaluation):
    """FitnessTreeEvaluation with code uncompilable on cython.
    This code manage the Koza adfs.
    SO, you need to use this fitness evaluation class only in this case.
    """

    def eval_with_adf(self, tree):
        """Eval the tree with adfs.
        The tree must follow this scheme:
        - if root has only one children, it is the program
        - if it has more, it contains several adf at the begining.
        XXX intesively debug.
        """

        root = tree[0]
        nb_adfs = root[NB_CHILDREN] -1

        #Build each adf function
        for i in xrange(nb_adfs):
            logging.debug('Build ADF %d' %i)
            self._build_adf(tree[i+1])

        #eval the main program
        logging.debug('Eval main program')
        logging.debug(tree[-1])
        res = self.EvalTreeForOneListInputSet(tree[-1])
        logging.debug('get')
        logging.debug(res)
        return res


    def _build_adf(self, tree):
        """
        Construct the function of the ADF which will by called
        by the main program (or the other adfs).
        The name of the parameters is build with the name of the adf.
        For adf0, the two first params are:
        adf0_PARAM0, adf0_PARAM1.

        XXX For the moment, works only with adf with 1 child

        @param tree: tree symbolising the ADF
        """


        #Get the params name
        adf = tree[0]
        name = adf[NODE_NAME]
        params = self._get_parameters_for_adf(name)
        nb_params = len(params)


        def adf_call(inputs):
            #Populate parameters
            assert len(inputs) == nb_params

            #Override terminal values
            for i in xrange(nb_params):
                self.__terminals__[params[i]] = inputs[i]

            #execute the function
            return self.EvalTreeForOneListInputSet(tree)


        #print 'This adf has ' + str(nb_params) + 'parameters'
        self.__functions__["_"+name] = adf_call

    def _get_parameters_for_adf(self, adf_name):
        """Returns the number of parameters for the required adf.
        The format of the parameters is adf_name + _PARAM + parameter_indice,
        with parameter_indice starting from 0.
        This list of parameters is stored in the terminals list
        """

        return sorted([val for val in self.__terminals__  if val.startswith("%s_PARAM" % adf_name)])

