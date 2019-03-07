import glob
import os
import sys

AA3toAA1= {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K', 'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N', 'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 'ALA': 'A', 'VAL':'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}


def pdb_to_fasta( cwd ):
	pdb_list = glob.glob(cwd+'*.pdb')
	for pdb in sorted(pdb_list):
		name1 = pdb.strip('.pdb')
		name2 = name1.split('/')[-1]
		outfilename = name1+'.fasta'
		#print outfilename
		if os.path.isfile(outfilename) == False:
			outfile = open(outfilename, 'w')
			pdbfile = open(pdb, 'r')
			pdbnum = name2.split('_')[-1]
			pdbname = name2.split('_')[0]
			chains = {}
			chain_order = []
			for line in pdbfile:
				if (line[:4] == "ATOM" or line[:4] == "HETA"):
					chain = line[21]
					if chain not in chains:
						chains[chain]={}
						chain_order.append(chain)
					resnum = int(line[23:26].strip())
					threeLetRes = line[17:20]
					#print threeLetRes
					try:
						oneLetRes = AA3toAA1[threeLetRes]
					except KeyError:
						oneLetRes = '-'
					chains[chain][resnum]=oneLetRes
			pdbfile.close()
			seq = ""
			try:
				A_min = 0#min(chain_A.keys()) -1
				A_max = max(chains.keys())
			except ValueError:	
				print "error"
				print pdb
			for chain in chain_order:
				#seq += ">{0}|{1}\n".format(pdbnum,chain)
				seq += ">{0}|{1}\n".format(name1.split('/')[-1],chain)
				ungapped_resnum = 1
				for resnum in sorted(chains[chain]):
					#print 'resnum={0}'.format(resnum)
					while resnum > ungapped_resnum:
						seq += '-'
						ungapped_resnum += 1
					if resnum == ungapped_resnum:
						seq += chains[chain][resnum]
						ungapped_resnum += 1
				seq +=  "\n"
			outfile.write(seq)
			outfile.close()

cwd = sys.argv[1]
pdb_to_fasta( cwd )
