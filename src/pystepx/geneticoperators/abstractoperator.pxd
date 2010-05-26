
cdef class AbstractGeneticOperator(object):
    cpdef __rules__
    cpdef set_tree_rules(self,dict rules)
    cpdef check_configuration(self)


