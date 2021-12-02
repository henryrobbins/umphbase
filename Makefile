# Set Make variables from .env file
include .env
export

# Pull and clean all setlist data from ATU
pull:
	python pull.py
	python clean.py

# Upload clean CSV data to a MySQL database
upload:
	python upload.py --path atu_cleaned --method args --host $(HOST) \
	--database $(DATABASE) --u $(USERNAME) -p $(PASSWORD)

# Update the setlist data in a MySQL database
update:
	python update.py --method args --host $(HOST) --database $(DATABASE) \
	--u $(USERNAME) -p $(PASSWORD)

# Make song codes
codes:
	python codes.py -s atu_cleaned/songs.pickle -c data/song_codes.csv -l 5

# Crete tex files from a MySQL database
.PHONY: tex
tex:
	python compile.py --method args --host $(HOST) --database $(DATABASE) \
	--u $(USERNAME) -p $(PASSWORD)

# Compile tex files to create book PDF
pdf:
	cd tex && pdflatex -shell-escape -extra-mem-bot=1000000000 \
	-interaction=nonstopmode umphbase.tex

# Crete tex file and compile PDF
book: tex pdf
