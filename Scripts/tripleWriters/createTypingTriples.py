import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")

from Scripts import cleanCSV as cn
from Scripts.TripleMaker import TripleMaker as tm
import pandas as pd
from campyTM import campy as ctm
from labTM import lab as ltm


######################################################################################################
#
######################################################################################################
def createTypingTriples(df, row, isoTitle):

	triple = ""

	cols = list(df.columns.values) # Get all the column names

	genes = cols[cols.index("Asp"):cols.index("Oxford MOMP peptide")+1] # Extract gene names

	mlstGenes = genes[genes.index("Asp"):genes.index("Unc (atpA)")+1]

	cloComp = df["Clonal Complex"][row]

	st = df["ST"][row]

	mTitle = "mlst_"+isoTitle


	if not pd.isnull(cloComp) and cn.isGoodVal(cloComp):
		# The values ST-403 and ST_403 are in the csv. We'll standardize it to ST_403
		cloComp = cloComp.replace("-","_")
		triple += ltm.propTriple(mTitle,{"foundClonalComplex":cloComp},"string",True)


	# The value 'new' is in ST. We'll ignore it as well...for....now....
	if not pd.isnull(st) and cn.isGoodVal(st) and "new" not in st:
		st = cn.cleanInt(st)
		triple += ltm.propTriple(mTitle,{"foundST":st},"int",True)


	if not pd.isnull(st):
		triple += ltm.indTriple(mTitle,"MLST_test")	
		triple += tm.multiURI((isoTitle, "hasLabTest", mTitle), (ctm.uri, ctm.uri, ltm.uri))


	def allele_triple(g):

		triple = ""
		alIndex = cn.cleanInt(df[g][row])

		if not pd.isnull(alIndex) and cn.isNumber(alIndex):
			alTitle = "{}_{}".format(cn.cleanGene(g), alIndex)
			
			triple =  ltm.indTriple(alTitle,"TypingAllele") +\
			          ltm.propTriple(alTitle,{"isOfGene":cn.cleanGene(g)}) +\
			          ltm.propTriple(alTitle,{"hasAlleleIndex":alIndex},"int",True) +\
			          test_triple(g,alTitle)

		return triple


	def test_triple(g, alTitle):

		tClass = "{}_test".format(cn.cleanGene(g))

		tTitle = mTitle if g in mlstGenes else "{}_{}".format(tClass, isoTitle)
		
		triple = ltm.propTriple(tTitle,{"foundAllele":alTitle})

		if g not in mlstGenes:
			
			triple += ltm.indTriple(tTitle, tClass) +\
				      ltm.propTriple(tTitle, {"foundAllele":alTitle}) +\
				      tm.multiURI((isoTitle, "hasLabTest", tTitle), (ctm.uri, ctm.uri, ltm.uri))

		return triple



	triples = [ allele_triple(g) for g in genes ]

	triple += "".join(triples)

	"""
	# Go through all the genes, get the allele index, create allele, attach allele to gene,
	# add the allele index to the allele, attach the test to the allele.
	for g in genes:
		alIndex = df[g][row]
		if not pd.isnull(alIndex) and cn.isNumber(alIndex):
			alIndex = cn.cleanInt(alIndex)
			alTitle = cg.cleanGene(g)+"_"+alIndex
			testTriple += ltm.indTriple(alTitle,"TypingAllele")
			testTriple += ltm.propTriple(alTitle,{"isOfGene":cg.cleanGene(g)})
			testTriple += ltm.propTriple(alTitle,{"hasAlleleIndex":alIndex},"int",True)

			if g in mlstGenes:
				mTriple += ltm.propTriple(mTitle,{"foundAllele":alTitle})
			else:
				testClass = cg.cleanGene(g)+"test"
				testTitle = testClass+"_"+isoTitle
				testTriple += ltm.indTriple(testTitle,testClass)
				testTriple += ltm.propTriple(testTitle,{"foundAllele":alTitle})

				testTriple += ctm.addUri(isoTitle)+" "+ctm.addUri("hasLabTest")+" "\
						    +ltm.addUri(testTitle)+" ."

	"""

	return triple