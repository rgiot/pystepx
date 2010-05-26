#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base class of the tutorials.

AUTHOR Romain Giot <romain.giot@ensicaen.fr>
"""

import logging

class BaseTutorial(object):
    """
    BaseTutorial
    ============

    Base class for the various tutorials.
    To do a tutorial, create an instance of the class,
    then run the go method.
    """

    def __init__(self):
        logging.info('Initalize tutorial')
        functions, terminals, rules ,\
            mapping = self.define_grammar()
        self.gp_engine = self.build_engine( \
                            functions,
                            terminals,
                            rules)

    def define_grammar(self):
        """
        define_grammar
        ==============

        Define the necessary grammar and returns:
        - the whole function set
        - the whole terminal set
        - the treeRules

        """
        pass

    def build_engine(self):
        """Build the gp engine and returns it"""
        pass

    def run(self):
        """
        Launch the tutorial
        """

        logging.info('Launch evolution process')
        self.gp_engine.evolve()
        logging.info('End evolution process')

