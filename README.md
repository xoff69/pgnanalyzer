# pgnanalyzer

Python tool to analyze chess at PGN Format.

Dependencies
You will need a UCI chess engine for analysis. stockfish is the default.https://stockfishchess.org/ 
and https://anaconda.org/hcc/stockfish

This tool needs the followings libs
- matplot (Python)
- python chess (Python)
- config parser  (Python)

 
 Information:
 - opening/openings.py is a lib to manage openings informations stored mainly in eco.txt (french names)
 - pgnstat.cfg contains configuration option, the player name mostly
 - <player>_game_analysis contains cache for analyzed game
 
 Running:
 - just run pgn.py, you can change settings in pgnstat.cfg before 
 the result is stored in a pdf file named <player>.pdf where player is set in pgnstat.cfg
 
 Todo/improvement:
 - add more internationalization
 - apparence of some arrays
 - improve table presentation
 - opening determination
 - remove graphs from console
 
 
 Legal
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.