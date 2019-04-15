#!/bin/sh
#antibody.macosclangrelease -fasta $1.truncated.fasta -antibody:grafting_database ~/Rosetta/tools/antibody-update -no_relax -antibody:exclude_pdb $1 -antibody:n_multi_templates 1
antibody.macosclangrelease -fasta $1.truncated.fasta -no_relax -antibody:exclude_pdb $1 -antibody:n_multi_templates 1
