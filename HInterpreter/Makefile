CC			= g++
FLAGS		= -Wall
LIBS		= BinaryExpressionTree.o utils.o
EXEC		= Interpreter

%.o: src/%.cpp
	g++ -c -o $@ $< $(FLAGS)

main: src/main.cpp $(LIBS)
	$(CC) src/main.cpp $(LIBS) -o $(EXEC) $(FLAGS) -lreadline

clean:
	rm *.o
	rm $(EXEC)

run: main
	./$(EXEC)