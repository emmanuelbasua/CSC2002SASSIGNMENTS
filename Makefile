# Makefile for Parallel Dungeon Hunter (Submission)

# Default arguments (can be overridden)
ARGS ?= 100 0.2 0

# Java compiler/runtime
JAVAC = javac
JAVA = java
SRC=src
# Source and class files
CLASSES = $(SRC)/DungeonHunterParallel.java $(SRC)/DungeonMapParallel.java $(SRC)/HuntParallel.java


# Default target
all:
	$(JAVAC) $(CLASSES)
# Run program with ARGS
run:
	$(JAVA) -cp $(SRC) DungeonHunterParallel $(ARGS)
# Clean
clean:
	rm -f $(SRC)/*.class *.png


