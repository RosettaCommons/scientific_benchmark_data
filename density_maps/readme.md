# Adding new maps

Maps should be under 100 mb.  The maps here are general - please use them if you can. 

If you add new maps, please update this readme to include a description of the maps you have added.


# Current Maps


## Group 1

Glycan Modeling - used for Glycan[Tree]Modeler DeNovo glycan modeling paper


### List
 - 1gai_2mFo-DFc_map.ccp4
 - 1jnd_2mFo-DFc_map.ccp4
 - 3pfx_2mFo-DFc_map.ccp4
 - 3uue_2mFo-DFc_map.ccp4
 - 4nyq_2mFo-DFc_map.ccp4


### Inputs

PDBs were obtained directly from the PDB. cif files were used where possible, mtz files were used instead if there were errors.


### Corresponding PDBs in Scientific Data

Structures relaxed into the rosetta energy function using their crystal density are located in 'glycan_modeling'


### Generation

`phenix.maps` cmd was used with default settings.
