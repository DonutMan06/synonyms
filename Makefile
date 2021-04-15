
PYTHON = $(which python3)

.PHONY: matrix clean

clean:
	@echo Deletion of initial thesaurus and python sparse matrix
	rm -f ./data/step0/README_thes_fr.txt
	rm -f ./data/step0/thes_fr.dat
	rm -f ./data/step0/thes_fr.idx
	rm -f ./data/step1/thesaurus_entries.npz
	rm -f ./data/step1/thesaurus_matrix.npz
	
matrix: clean
	@echo Thesaurus download
	wget -q -O ./data/step0/thesaurus.zip https://grammalecte.net/download/fr/thesaurus-v2.3.zip && unzip -j -d ./data/step0/ ./data/step0/thesaurus.zip && rm -f /data/step0/thesaurus.zip
	@echo Sparse matrix creation
	$(PYTHON) ./synonyms/create_matrix.py
