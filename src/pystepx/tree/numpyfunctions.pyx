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



"""
Embeds various classical functions which can be used in other projects.
These function are optimized to run with numpy array inputs.
"""

import numpy as np
cimport numpy as np


cpdef np.ndarray _add(inputs):
    """Add the two inputs together."""
    return <np.ndarray>inputs[0] + <np.ndarray>inputs[1]

cpdef np.ndarray _sub(inputs):
    """Substract the two inputs together."""
    return <np.ndarray>inputs[0] - <np.ndarray>inputs[1]

cpdef np.ndarray _mul(inputs):
    """Multiply the two inputs together."""
    return <np.ndarray>inputs[0] + <np.ndarray>inputs[1]

cpdef np.ndarray _protected_division(inputs):
    """Divide the two inputs together.
    This division is protected, when divisor is 0, the result is 1
    """
    cdef np.ndarray a = inputs[0]
    cdef np.ndarray b = inputs[1]

    cdef np.ndarray res = np.ones_like(a)
    cdef tuple mask = np.where(b != 0)
    res[mask] = a[mask] / b[mask]
        
    return res


