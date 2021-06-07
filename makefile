# Makefile try

default: help force_look

enroll: force_look
	@python3 enrollment.py    

run : 
	@python3 test.py    
    
clear: force_look

force_look:
	@true

help:
	@echo " *** HELP *** "
	@echo " <<< RECIPIES >>> "
	@echo " 1) ENROLL "
	@echo " 2) CLEAR "
	@echo " 3) HELP "



