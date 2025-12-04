crud_db
=======

The crud_db-package provides modules for the manipulation of the database. This includes creation, reading, update and deletion.


create
------
.. currentmodule:: specatalog.crud_db.create

.. autosummary::
   :toctree: generated/
   :recursive:

   create_new_measurement
   create_new_molecule

read
----
.. currentmodule:: specatalog.crud_db.read

.. autosummary::
   :toctree: generated/
   :recursive:

   run_query

FilterModels
^^^^^^^^^^^^
.. currentmodule:: specatalog.crud_db.read

.. autosummary::
   :toctree: generated/
   :recursive:
   :nosignatures:
   :template: class_docstring_only.rst
   
   MeasurementFilter
   CWEPRFilter
   TREPRFilter
   PulseEPRFilter
   MoleculeFilter
   SingleMoleculeFilter
   RPFilter
   TDPFilter
   TTPFilter

OrderingModels
^^^^^^^^^^^^^^
.. currentmodule:: specatalog.crud_db.read

.. autosummary::
   :toctree: generated/
   :recursive:
   :nosignatures:
   :template: class_docstring_only.rst
   
   MeasurementOrdering
   CWEPROrdering
   TREPROrdering
   PulseEPROrdering
   MoleculeOrdering
   SingleMoleculeOrdering
   RPOrdering
   TDPOrdering
   TTPOrdering
   

update
------
.. currentmodule:: specatalog.crud_db.update

.. autosummary::
   :toctree: generated/
   :recursive:

   update_model
   automatic_name_update
  
UpdateModels
^^^^^^^^^^^^
.. currentmodule:: specatalog.crud_db.update

.. autosummary::
   :toctree: generated/
   :recursive:
   :nosignatures:
   :template: class_docstring_only.rst
   
   MeasurementUpdate
   CWEPRUpdate
   TREPRUpdate
   PulseEPRUpdate
   MoleculeUpdate
   SingleMoleculeUpdate
   RPUpdate
   TDPUpdate
   TTPUpdate

  
delete
------
.. currentmodule:: specatalog.crud_db.delete

.. autosummary::
   :toctree: generated/
   :recursive:

   delete_object
   delete_molecule
   delete_measurement
