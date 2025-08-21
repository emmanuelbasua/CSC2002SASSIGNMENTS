# Extended Makefile for Development & Testing

ARGS ?= 50 0.2 42
JAVAC = javac
JAVA = java

SOURCES = DungeonHunterParallel.java DungeonMapParallel.java HuntParallel.java
CLASSES = $(SOURCES:.java=.class)

all: compile

compile: $(CLASSES)

%.class: %.java
	$(JAVAC) $<

run: compile
	$(JAVA) DungeonHunterParallel $(ARGS)

run2: compile
	$(JAVA) DungeonHunter $(ARGS)

clean:
	rm -f *.class *.png *.out

validate: compile
	@echo "Validating parallel vs serial..."
	# Run parallel version
	$(JAVA) DungeonHunterParallel 50 0.2 42 > parallel.out
	@mv output.png parallel.png 2>/dev/null || true
	# Run serial version
	$(JAVA) DungeonHunter 50 0.2 42 > serial.out
	@mv output.png serial.png 2>/dev/null || true
	# Compare text outputs
	@diff -q parallel.out serial.out && echo "Validation PASSED" || echo "Validation FAILED"
	@echo "Generated images: parallel.png and serial.png"

# ✅ Benchmarking different grid sizes
benchmark: compile
	@echo "Running benchmark tests..."
	@for size in 25 50 100; do \
	  echo "\nGrid size $$size:"; \
	  /usr/bin/time -p $(JAVA) DungeonHunterParallel $$size 0.2 42; \
	done

# ✅ Profiling across densities
densitytest: compile
	@echo "Testing different densities..."
	@for density in 0.05 0.1 0.2 0.5 1.0; do \
	  echo "\nDensity $$density:"; \
	  /usr/bin/time -p $(JAVA) DungeonHunterParallel 50 $$density 42; \
	done

# ✅ Profile sequential cutoff experiments
cutofftest: compile
	@echo "Testing different sequential cutoffs..."
	@for cutoff in 10 50 100 500; do \
	  echo "\nCutoff $$cutoff:"; \
	  $(JAVA) DungeonHunterParallel 50 0.2 42 $$cutoff; \
	done

help:
	@echo "Extended testing targets:"
	@echo "  validate     - Compare serial vs parallel output"
	@echo "  benchmark    - Run benchmarks on grid sizes"
	@echo "  densitytest  - Sweep search densities"
	@echo "  cutofftest   - Sweep sequential cutoff values"
	@echo "  clean        - Remove compiled files"
