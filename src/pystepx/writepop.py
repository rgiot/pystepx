#!/usr/bin/env python
# -*- coding: utf-8 -*-
# cython: profile=True


"""
writepop
========
Contains all classes used to write and extract individuals and populations 
on the SQLite database.

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

from pystepx.geneticoperators import crossutil
from pystepx.basewritepop import BaseWritePop

class WritePop(BaseWritePop):
    """WritePop with codes which do not compile with cython."""

    def __init__(self, con):
        BaseWritePop.__init__(self, con)

    def get_individuals_iterator(self, tablename, keys, extract=False):
        """Produce an iterator returning the required individuals.

        @param tablename, keys
        @param list: list of the attended keys
        @param extract: if extract is selected, extract the tree information

        @todo manage extract

        """

        cur = self.get_connexion().cursor()
        select = """
        SELECT tree, tree_mapping, treedepth, evaluated, fitness, o_id
        FROM %s
        WHERE o_id in (%s)
        """ % (tablename, ",".join([str(int(elem[0])) for elem in keys]))
        cur.execute(select)

        for myresult in cur:
            if not extract:
                yield myresult
            else:
                my_tree, my_tree_mapping, \
                  my_treedepth, my_evaluated, \
                  my_fitness = self.get_tree_objects(myresult)

                yield myresult, my_tree, my_tree_mapping, my_treedepth, my_evaluated, my_fitness
        cur.close()
        

