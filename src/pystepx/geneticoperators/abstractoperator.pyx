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
Abstract genetic operation.
"""


cdef class AbstractGeneticOperator(object):
    """
    Base class for the genetic operators
    """
    def __init__(self):
        """Do nothing"""
        self.__rules__ = None

    cpdef set_tree_rules(self, dict rules):
        """
        Defines the tree rules to respect when doing the genetic operations.
        """
        self.__rules__ = rules

    cpdef check_configuration(self):
        """
        Look if the object is correctly configured before being used.
        If it is not the case, an assertion stops the program
        """

        assert self.__rules__ is not None, \
                "You must define the tree rules of the operator"""




