data_management
===============

The package data_management provides modules for the interaction with the datafiles stored in the archive. The module measurement_management provides CRUD-Functions for the archive, while the hdf5_reader module can be used for reading and updating the measurement.h5-files.


measurement_management
----------------------
.. currentmodule:: specatalog.data_management.measurement_management

.. autosummary::
   :toctree: generated/
   :recursive:
   
   create_measurement_dir
   new_file_to_archive
   new_dataset_to_hdf5
   raw_data_to_folder
   raw_data_to_hdf5
   delete_element
   delete_measurement
   list_files
   measurement_path
   detect_supported_format

hdf5_reader
-----------
.. currentmodule:: specatalog.data_management.hdf5_reader

.. autosummary::
   :toctree: generated/
   :recursive:
   
   load_h5
   load_from_id


.. autosummary::
   :toctree: generated/
   :recursive:
   :template: full_class.rst
   
   H5Object
   

