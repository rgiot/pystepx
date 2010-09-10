
cimport abstractoperator


cdef class CrossoverOperator(abstractoperator.AbstractGeneticOperator):

    cpdef bint __strongly_typed_crossover_degree__
    cpdef list __crossover_mapping__


    cpdef set_strongly_typed_crossover_degree(self, bint value)
    cpdef set_crossover_mapping(self, list mapping)
    cpdef Koza1PointCrossover(self, int maxdepth, list p1, list p2, list p1_mp, list p2_mp, int p1_depth, int p2_depth)
    cpdef Koza2PointsCrossover(self, int maxdepth, list parent1, list parent2, list p1_map, list p2_map, int p1_depth, int p2_depth)
