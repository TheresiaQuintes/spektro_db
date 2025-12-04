The organisation of the archive
===============================

The archive directory
---------------------

When using specatalog, your data are organised systematically in an archive directory. It hast the following structure::

	base_dir/
	├── data/
	│   ├── M1/
	│   ├── M2/
	│   ├── M3/
	│   ├── ...
	│   └── M{ms_id}/
	│       ├── additional_info/
	│       ├── figures/
	│       ├── literature/
	│       ├── raw/
	│       ├── scripts/
	│       └── measurement_M{ms_id}.h5
	├── molecules/
	│   ├── MOL1/
	│   ├── MOL2/
	│   ├── MOL3/
	│   ├── ...
	│   └── MOL{mol_id}/
	│       ├── file_with_structure.cdxml
	│       └── file_with_structure.pdf
	│
	├── allowed_values.py
	└── specatalog.db


base_dir/
^^^^^^^^^
This is the basis folder in which all data are stored. The absolute path to the folder can be set by the user in ``~/.specatalog/defaults.json``. The whole directory can be created by ``specatalog-init-db``.

data/
^^^^^
The data-directory contains all files that are related to measurements. The measurements are organised in subdirectories (one directory for each measurement) and are allocated to a number. The subdirectory is named M{ms_id}, where ms_id is the number of the measurement.

In the directory of a measurement the files are organised:

- **raw/ :** save files with raw data as returned by the spectrometer here
- **scripts/ :** save important scripts for data correction and evaluation here
- **figures/ :** save figures of your data here
- **additional_info/ :** save additional information like metadata
- **literature/ :** save literature concerning the measurement here

In each Folder you will find an automatically generated hdf5-file: **measurement_M{ms_id}.h5**. This file contains the raw data as arrays. They can be easilly loaded from this file and evaluations and corrections can also be saved in the hdf5-file using the HDF5Object-class. Find more details at the documentation of the HDF5Object from  the: :doc:`data_management` package.


molecules/
^^^^^^^^^^
The molecules-directory contains a folder for each molecule named MOL{mol_id} where mol_id is a unique number, which references the molecule. You should place an image of the structural formula of the molecule inside this folder.

allowed_values.py
^^^^^^^^^^^^^^^^^
This file is created, when the archive-directory is set up by specatalog for the first time. It contains allowed values for several metadata, that are stored in the database. If it is necessary these lists of allowed values can be adapted. This is explained in detail in :doc:`tutorial_allowed_values`.

specatalog.db
^^^^^^^^^^^^^
This is the main database file, which is created when the archive directory is set up by specatalog for the first time




The database
------------
