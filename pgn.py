#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 20:27:24 2019

@author: xoff
"""
import matplotlib.pyplot as plt
import chess.pgn
import numpy as np
import opening.openings as op
import glob
import configparser as cp
from matplotlib.backends.backend_pdf import PdfPages
import time
import chess.engine
import datetime
def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])
# parse pgn file filename for player player, based on data stored in openings
def parseFile(player,filename,openings,tob,ton,allgames):
	pgn = open(filename)
	blanc10=0
	blanc12=0
	blanc01=0
	noir10=0
	noir12=0
	noir01=0
	while True:
		game = chess.pgn.read_game(pgn)
		eco="Z00"
		try:
			eco=game.headers["ECO"]
			if eco=="?":
				eco="Z00"
		except:
			pass
		if game == None:
			break
		# some games are null games, we try to avoid them
		if player.lower() in game.headers["White"].lower():
			prec=tob[eco]
			prec[0]=prec[0]+1
			if game.headers["Result"]=='1-0':
				blanc10=blanc10+1
				prec[1]=prec[1]+1
				allgames.append(game)
			elif game.headers["Result"]=='1/2-1/2':
				blanc12=blanc12+1
				prec[2]=prec[2]+1
				allgames.append(game)
			elif game.headers["Result"]=='0-1':
				blanc01=blanc01+1
				prec[3]=prec[3]+1
				allgames.append(game)
			
		elif player.lower() in game.headers["Black"].lower():
			prec=ton[eco]
			prec[0]=prec[0]+1
			if game.headers["Result"]=='1-0':
				noir10=noir10+1
				prec[1]=prec[1]+1
				allgames.append(game)
			elif game.headers["Result"]=='1/2-1/2':
				noir12=noir12+1
				prec[2]=prec[2]+1
				allgames.append(game)
			elif game.headers["Result"]=='0-1':
				noir01=noir01+1
				prec[3]=prec[3]+1
				allgames.append(game)

	return 	blanc10,blanc12,blanc01,noir10,noir12,noir01
# count average of moves by game
def nbcoupmoyen(allgames):
	total=0
	for item in allgames:
		mov=0
		for m in item.mainline_moves():
			mov=mov+1
		total=total+mov
	return total/len(allgames)

# result tendancies for player player
def tendanceGame(allgames,player,config):
	tendanceNumber = int(config.get('Main', 'tendanceNumber'))
	allgames.sort(key=lambda x: x.headers["Date"], reverse=True)
	sub=allgames[:tendanceNumber]
	tendance=0
	for game in sub:
		#☺print("tendance",game, tendance)
		if player.lower() in game.headers["White"].lower():
			
			if game.headers["Result"]=='1-0':
				tendance=tendance+1
			elif game.headers["Result"]=='1/2-1/2':
				tendance=tendance+0.5
			elif game.headers["Result"]=='0-1':
				tendance=tendance-1
			
		elif player.lower() in game.headers["Black"].lower():
			
			if game.headers["Result"]=='1-0':
				tendance=tendance-1
			elif game.headers["Result"]=='1/2-1/2':
				tendance=tendance+0.5
			elif game.headers["Result"]=='0-1':
				tendance=tendance+1
				
	return tendance/tendanceNumber
	
# analyze games of a player in order to detect crucial moment of blunder
# avec les blancs/ avec les noirs
# renvoie le nombre total de coup blanc avant erreur, idem pour noir
def analyzeGame(allgames,player,config):

	
	engine = chess.engine.SimpleEngine.popen_uci(config.get('Main', 'engine'))
	BLUNDER_GAP=1.
	ANALYSE_TIME=float(config.get('Main', 'analyzeTime'))
	blancnbcoup=0
	noirnbcoup=0
	compteur=0
	isBlunder=False
	date = datetime.datetime.now()
	nomfichier="log/f_"+str(date.year)+"_"+str(date.month)+"_"+str(date.day)+"_analyse games.log"
	fichier=open(nomfichier,"a")
	nbblanc=0
	nbnoir=0
	# charger le fichier des parties - blanc - numero coup

	file_game_ana=	player+"_game_analysis.txt"		
	hclefgame=dict()
	SEP="///***///"
	try:
		f=open(file_game_ana, "r")
		contenu=f.read()
		f.close()
		contenu=contenu.split(SEP)
		for line in contenu:
			hd=line.split(",")
			hclefgame[hd[0]]=[hd[1],hd[2]]
	except:
		pass
	for game in allgames:
		print("game#",compteur)
		compteur=compteur+1
		scoreBlanc=0.
		scoreNoir=0.
		numeroCoup=0
		board = chess.Board()
		# recherche si ça a deja ete fait
		exporter = chess.pgn.StringExporter(headers=False, variations=False, comments=False)
		pgn_string = game.accept(exporter)
		trouve=False
		try:
			eval=hclefgame[pgn_string] 
			trouve=True
		except:
			pass
		if trouve:
					eval=hclefgame[pgn_string] 
					numeroCoup=int(eval[1])
					#print("numero coup",numeroCoup)
					if eval[0]=='BLANC':
						blancnbcoup=blancnbcoup+numeroCoup
						nbblanc=nbblanc+1
					else:
						noirnbcoup=noirnbcoup+numeroCoup
						nbnoir=nbnoir+1

					
		else:

			for move in game.mainline_moves():
				board.push(move)
				#print(move)								
				if  board.is_game_over():
					break
				info = engine.analyse(board, chess.engine.Limit(time=ANALYSE_TIME))
				try:
					if numeroCoup%2==0:
						score=info["score"].white().score()/100.
					else:	
						score=info["score"].black().score()/100.
				except:
					#print(game)

					fichier.write("Erreur:"+game.headers["White"]+"--------vs----"+game.headers["Black"])
					pass
				
				if numeroCoup%2==0:
					try:
						score=info["score"].white().score()/100.
						if scoreBlanc-score>BLUNDER_GAP:
							isBlunder=True
							break
						scoreBlanc=score
					except:
						break
				else:
					try:
						score=info["score"].black().score()/100.
						if scoreNoir-score>BLUNDER_GAP:
							isBlunder=True
							break
						scoreNoir=score
					except:
						break
					
				numeroCoup=numeroCoup+1
				# fin for moves
			#print("str",pgn_string)
			if isBlunder:
				if player.lower() in game.headers["White"].lower():
					blancnbcoup=blancnbcoup+numeroCoup
					nbblanc=nbblanc+1
					t={}
					t[0]='BLANC'
					t[1]=numeroCoup
					
					hclefgame[pgn_string]=t	
				else:
					noirnbcoup=noirnbcoup+numeroCoup
					nbnoir=nbnoir+1
					t={}
					t[0]='NOIR'
					t[1]=numeroCoup
					hclefgame[pgn_string]=t
					
			isBlunder=False
	# fin for games
	
	#  mettre a jour le fichier des clefs file_game_ana
	f = open(file_game_ana,"w")
	
	for item in hclefgame:
		v=hclefgame[item]
		f.write(item+","+str(v[0])+","+str(v[1])+SEP)
	f.close()
	engine.quit()
	print("fend of analyze fame function")
	fichier.close()
	return [blancnbcoup/nbblanc/2,noirnbcoup/nbnoir/2],hclefgame
	
	
# load all pgn files of a folrder
def allFile(player,config):
	openings=op.loadOpening(config.get('Main', 'eco'))
	allgames=[]
	tob=op.initTableauOuverture()
	ton=op.initTableauOuverture()
	blanc10=0
	blanc12=0
	blanc01=0
	noir10=0
	noir12=0
	noir01=0
	debut=time.time()

	#print(config.get('Main', 'pgn'))    
	for filename in glob.iglob(config.get('Main', 'pgn') + '**/*.pgn', recursive=True):
		print("fichier=",filename)
		lblanc10,lblanc12,lblanc01,lnoir10,lnoir12,lnoir01=parseFile(player,filename,openings,tob,ton,allgames)

		blanc10=blanc10+lblanc10
		blanc12=blanc12+lblanc12
		blanc01=blanc01+lblanc01
		noir10=noir10+lnoir10
		noir12=noir12+lnoir12
		noir01=noir01+lnoir01

		#print("intermediaire:",len(allgames)," ---",(blanc10+blanc12+blanc01+noir10+noir12+noir01))


	print("total=",len(allgames), " games")
	print("Parse time ",truncate((time.time()-debut),2)," s")
	compteurBlanc=blanc10+blanc12+blanc01
	compteurNoir=noir10+noir12+noir01
	compteurGlobal=compteurBlanc+compteurNoir


	#  chart
	labelsG = 'Victoires', 'Nulles', 'Defaites'
	sizeblanc = [blanc10,blanc12,blanc01]
	sizenoir = [noir01,noir12,noir10]
	sizeglobal = [blanc10+noir01,blanc12+noir12,blanc01+noir10]
	with PdfPages(player+'.pdf') as pdf:

		plt.suptitle('Statistiques pour '+player, fontsize=16)
	
		plt.pie(sizeblanc, labels=labelsG, autopct='%1.1f%%',
			shadow=True, startangle=90)
		plt.title('Avec les blancs ('+str(compteurBlanc)+' parties)')
		
		pdf.savefig() 
		plt.figure()
		plt.pie(sizenoir, labels=labelsG, autopct='%1.1f%%',
			shadow=True, startangle=90)
		plt.title('Avec les noirs('+str(compteurNoir)+' parties)')
		
		pdf.savefig() 
		plt.figure()
		plt.pie(sizeglobal, labels=labelsG, autopct='%1.1f%%',
			shadow=True, startangle=90)
		plt.title('Globalement ('+str(compteurGlobal)+' parties)')
		
		pdf.savefig() 
		plt.figure()
		
		#ouvertures preferees
		oblanc=sorted(tob.items(),reverse=True, key=lambda t: t[1][0])
		cx=0
		#print("ouvertures favorites avec les blancs")
		besteob=[]
		for item in oblanc:
			cx=cx+1
			#print("item = ",item[0])
			besteob.append([item[0],op.trouveOuverture(item[0],openings),item[1][0]])
			if cx==5:
				break
		onoir=sorted(ton.items(),reverse=True, key=lambda t: t[1][0])
		cx=0
		#print("ouvertures favorites avec les noirs")
		besteon=[]
		for item in onoir:
			#print("item op",item)
			besteon.append([item[0],op.trouveOuverture(item[0],openings),item[1][0]])

			cx=cx+1
			if cx==5:
				break
			
			
		collabel=("ECO", "NOM", "#")
		plt.axis('tight')
		plt.axis('off')
		plt.title('Favorites openings with white ('+str(compteurBlanc)+' games)')
		plt.table(cellText=besteob,colLabels=collabel,bbox=[0.05,0.5,1,0.5])
		
		pdf.savefig() 
		plt.figure()
		
		cx=0
		#print("pour chaque ouverture preferee aves les blancs un camembert")
		for item in oblanc:
			cx=cx+1
			sizeglobal=[item[1][1],item[1][2],item[1][3]]
			plt.pie(sizeglobal, labels=labelsG, autopct='%1.1f%%',
				shadow=True, startangle=90)
			plt.title('With white pieces:  ('+item[0]+' Opening= '+op.trouveOuverture(item[0],openings)+ ' '+str(item[1][0])+' games)')
			
			pdf.savefig() 
			plt.figure()		
			if cx==5:
				break		
				
				
		plt.axis('tight')
		plt.axis('off')
		plt.table(cellText=besteon,colLabels=collabel,bbox=[0.05,0.5,1,0.5])
		plt.title('Favorites openings with black ('+str(compteurNoir)+' games)')
		
		pdf.savefig() 
		plt.figure()
		cx=0
		#print("pour chaque ouverture preferee aves les noirs un camembert")
		for item in onoir:
			cx=cx+1
			sizeglobal=[item[1][1],item[1][2],item[1][3]]
			plt.pie(sizeglobal, labels=labelsG, autopct='%1.1f%%',
				shadow=True, startangle=90)
			plt.title('With black:  ('+item[0]+' '+op.trouveOuverture(item[0],openings)+ ' '+str(item[1][0])+' games)')
			
			pdf.savefig() 
			plt.figure()		
			if cx==5:
				break
		# tendances forme du joueur
		tg=tendanceGame(allgames,player,config)

		plt.title("Tendency")		
		#plt.axes()
		plt.axis('off')
		if tg<0:
			plt.arrow(0, 0.8, 0.8, -0.5, head_width=0.15, head_length=0.1, fc='k', ec='k')
		elif tg==0:
			plt.arrow(0, 0,8, 0.8, 0., head_width=0.05, head_length=0.1, fc='k', ec='k')
		else:
			plt.arrow(0, 0, 0.8, 0.8, head_width=0.05, head_length=0.1, fc='k', ec='k')		
		pdf.savefig() 
		plt.figure()

		if config.get('Main', 'analyseForBlunder'):
			print(">>>Analyzing blunder on games")           
			labelsG = 'Victoires', 'Nulles', 'Defaites'
			plt.title("Divers")
			[x,y],hclef=analyzeGame(allgames,player,config)
			#en vrai les hclef values pour les blancs ou les noirs
			arrayblanc=[]
			arraynoir=[]
			for hk in hclef:
				if hclef[hk][0]=='BLANC':
				  arrayblanc.append(hclef[hk][1])
				else:
				  arraynoir.append(hclef[hk][1])
    
    
    
			plt.hist(arrayblanc,  bins =10)
			plt.title("Errors distribution with white")
			plt.axis('off')
    		
			plt.xlabel("Numero coup")	  
			plt.ylabel("#parties")
			pdf.savefig() 
			plt.figure()
			plt.hist(arraynoir,  bins = 10)
    
			plt.axis('off')
    		
			plt.xlabel("Numero coup")	  
			plt.ylabel("#parties")
			plt.title("Errors distribution with black")
			pdf.savefig() 
			plt.figure()
			messtats=[["Moves by games",truncate(nbcoupmoyen(allgames),2)],["Blunder after with white",truncate(x,2)],["Blunder after with black",truncate(y,2)]]
			plt.axis('tight')
			plt.axis('off')
			collabel=("Mesures", "Resultats")
			plt.table(cellText=messtats,colLabels=collabel,loc='center')
			pdf.savefig() 
			plt.figure()
			print("<<<Analyzing blunder on games")          
		plt.close()
		print("Generation OK: "+player+'.pdf')

# main start
debut=time.time()
config = cp.ConfigParser()

config.read('pgnstat.cfg')
valeur = config.get('Main', 'version')
print (config.get('Main', 'player'))

allFile( config.get('Main', 'player'),config)
print("Duration ",truncate((time.time()-debut),2)," s")
