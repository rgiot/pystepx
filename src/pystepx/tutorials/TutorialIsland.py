#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This example is the same than the tutorial 1, except it runs on several islands,
instead of only one.
"""

import logging

from pystepx.island.pystepislands import PySTEPXIsland
import subprocess
import time

class Tutorial1Island(object):
    """Manage the tutorial example in an island mode.

    to launch 4 islands in local, type:
    ipcluster local -n 4

    It's up to you to launch the engine befoir launching gp.
    """

    def __init__(self):
        """Initialize the island computation.
        Each island must have the code in its classpath
        """

        #Launch cluster
        self._process = subprocess.Popen("ipcluster local -n 4", shell=True, stdout=subprocess.PIPE)
        time.sleep(10)


        init_script = """
from pystepx.tutorials.functions_tutorial_island import *;
        """

        self._pystepx = PySTEPXIsland(nb_islands=4, init_script=init_script)

    def run(self):
        self._pystepx.evolve()

def main():
    """
    Function: main
    ==============

    Launch  the set of tutorials
    """
    logging.basicConfig(level=logging.ERROR)

    logging.info('Launch tutorial 1 islands')
    t = Tutorial1Island()
    t.run()
    t._process.kill()


if __name__ == "__main__":
    main()
