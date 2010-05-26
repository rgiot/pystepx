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

@author: by Romain Giot
@version: 1.30
@copyright: (c) 2010 Romain Giot under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: giot.romain at gmail.com
"""



#Definition of constants of the node
#cdef enum _NODE_INDICE:
#    NODE_TYPE = 0
#    NB_CHILDREN = 1
#    NODE_NAME = 2

NODE_TYPE = 0
NB_CHILDREN = 1
NODE_NAME = 2


#Definition of constants of type of node
ROOT_BRANCH = 0
FUNCTION_BRANCH = 1
ADF_DEFINING_BRANCH = 2
VARIABLE_LEAF = 3
CONSTANT_LEAF = 4
ADF_LEAF = 5

KOZA_ADF_DEFINING_BRANCH = 6
KOZA_ADF_FUNCTION_BRANCH = 7
KOZA_ADF_PARAMETER = 8

