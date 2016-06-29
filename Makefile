default:
	@echo "Dangerous without selecting clean."

clean:
	@echo "Cleaning..."
	@rm -rf *.pdf 2> /dev/null
	@rm -rf __pycache__/ 2> /dev/null
