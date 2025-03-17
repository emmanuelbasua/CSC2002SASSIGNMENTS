JFLAGS = -g
JC = javac
JDOC = javadoc
TARGET = bin
SOURCES = $(wildcard src/*.java)
CLASSES = $(patsubst src/%.java, bin/%.class, $(SOURCES))

all: $(CLASSES)

bin/%.class: src/%.java
	@mkdir -p bin
	$(JC) $(JFLAGS) -d bin $<

javadoc:
	@mkdir -p doc
	$(JDOC) -d doc -sourcepath src $(SOURCES)

clean:
	rm -rf bin/*.class doc
