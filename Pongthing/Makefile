CFLAGS = -O3 -Wall -std=c++14 -D NDEBUG
SFMLFLAGS = -L/usr/local/lib -lsfml-system -lsfml-graphics -lsfml-window
OBJS = Ball.o Utils.o Pad.o Score.o Pong.o Context.o Menu.o

main: src/main.cpp $(OBJS)
	g++ src/main.cpp $(OBJS) -o main $(CFLAGS) $(SFMLFLAGS)

%.o: src/%.cpp
	g++ -c -o $@ $< $(CFLAGS) $(SFMLFLAGS)

clean:
	rm *.o
	rm main

run: main
	export LD_LIBRARY_PATH=/usr/local/lib && ./main
