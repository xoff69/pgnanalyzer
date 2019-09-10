# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 18:25:03 2019

@author: xoffp
"""
# charge les code eco + nom ouverture à partir du fichier
def loadOpening(filename):
	dicoeco=dict()
	dicoeco["Z00"]="Inconnu"
	f = open(filename, "r")
	for ligne in f:
	  enreg=ligne.split(":")
	  #print(enreg[0],"-",enreg[1])
	  nom=enreg[1]
	  if len(enreg)>2:
	      nom=nom+enreg[2]
	  dicoeco[enreg[0]]=nom
	return dicoeco
#renvoie le nom de l'ouverture
def trouveOuverture(eco,openings):
	#print("to",eco)
	return openings[eco]
# initialise le tableau des ouvertures avec clef=ECO, valeur = tableau [total, blanc,nul, noir]
def initTableauOuverture():
	tableauECO_OCC={}
	tableauECO_OCC['Z00']=[0,0,0,0]
	for i in range(0,100):
		clef=str(i)
		if i<10:
			clef='0'+str(i)
		tableauECO_OCC['A'+clef]=[0,0,0,0]
		tableauECO_OCC['B'+clef]=[0,0,0,0]
		tableauECO_OCC['C'+clef]=[0,0,0,0]
		tableauECO_OCC['D'+clef]=[0,0,0,0]
		tableauECO_OCC['E'+clef]=[0,0,0,0]
	return tableauECO_OCC

