# Makefile for Parallel Dungeon Hunter (Submission)

# Default arguments (can be overridden)
ARGS ?= 100 0.2 0

# Java compiler/runtime
JAVAC = javac
JAVA = java
SRC = src
BIN = bin

# Source and class files
CLASSES = $(SRC)/DungeonHunterParallel.java $(SRC)/DungeonMapParallel.java $(SRC)/HuntParallel.java $(SRC)/DungeonHunter.java $(SRC)/Hunt.java $(SRC)/DungeonMap.java

# Default target
all: $(BIN)
	$(JAVAC) -cp $(SRC) -d $(BIN) $(CLASSES)

# Create bin directory if it doesn't exist
$(BIN):
	mkdir -p $(BIN)

# Run program with ARGS
run: all
	$(JAVA) -cp $(BIN) DungeonHunterParallel $(ARGS)

# Clean
clean:
	rm -rf $(BIN) *.png

# Show help
help:
	@echo "Available targets:"
	@echo "  all   - Compile all Java files to bin directory"
	@echo "  run   - Compile and run with default args ($(ARGS))"
	@echo "  clean - Remove bin directory and png files"
	@echo "  help  - Show this help message"
	@echo ""
	@echo "To run with custom arguments:"
	@echo "  make run ARGS='200 0.3 42'"

.PHONY: all run clean help