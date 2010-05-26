cimport numpy as np

cdef class BaseWritePop(object):
    cpdef object _con_  #sqlite connection

    cpdef get_connexion(self)
    cpdef get_tree_objects(self, myresult)
    cpdef ClearDBTable(self, table)
    cpdef is_generation_computed(self, tablename)
    cpdef create_new_table(self, tablename)
    cpdef add_to_initial_population(self, list tree, float fitness, str tablename, bool commit=*)
    cpdef add_new_individual(self, tuple indiv, str tablename)
    cpdef add_new_individuals(self, individuals, str tablename)
    cpdef copy_individuals_from_to(self, np.ndarray list, str source, str dest)
    cpdef get_individual(self, str tablename, int o_id, bool extract=*)
    cpdef get_best_individual(self, str tablename, bool extract=*)
    cpdef flush(self)
    cpdef write_initial_population(self, trees, fitnesses, tablename)
    
    
    
