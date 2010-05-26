16 apr 2010: Romain Giot <romain.giot@ensicaen.fr>
   End of writting of the 6_sym, Tutorial3_koza_adf.py and twoboxes_adf.py

10 apr 2010: Romain Giot <romain.giot@ensicaen.fr>
  First version of Koza ADF implementation

01 apr 2010 Romain Giot <romain.giot@ensicaen.fr>
 - Modification of the library in order to ease its re-use and adaptation
 - Exchange sqlite2 for sqlite3
 - Suppress the different useless (maybe time consuming ?) connections to the database
 - Suppress the different useless commits when no modification is done on the databse


Mehdi Kouhry
  - The Koza Strongly-Typed flavoured build methods have been simplified and optimized (around 10 times faster for a code length reduced by five!) 
  - It is now possible to use a specific function-terminal sets for each of the children node. And these children node are built in the order they appear in the tree constraints (this feature only existed for ADF in the previous version). This makes pySTEP very competitive and gives it a serious advantage over existing Strongly typed GP packages :) 
  - It is now possible to specify what happens after the system has tried 100 times to produced rules-compliant offsprings using crossover but has failed (this might happens if we use a lot of constraining rules). Either we accept the unfit offsprings with Substitute_Mutation=0 or we substitute them with a mutated tree by setting Substitute_Mutation=1.
  - The parameters of the tournament selection are integrated in the main function that calls the evolutionary run. 
  - Code for crossover and mutation is now simplified and clearer. 
  - Changed the comments on the code to comply with the new documentation.
  - Also changed the default path of the database to     dbname=r'C:\pop_db'
