
cimport abstractoperator
cdef class Mutator(abstractoperator.AbstractGeneticOperator):
    cpdef mutate(self, int maxdepth, parent, p1_map,int p1_depth)
