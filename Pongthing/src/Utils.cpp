#ifndef UTILS_CPP
#define UTILS_CPP

#define PAD_WIDTH 15.0f
#define PAD_HEIGHT 160.0f
#define PAD_SPEED 0.8f

#define BALL_RADIUS 8.0f
#define BALL_SPEED 0.6f
#define BALL_ACC 1.05

#define WINDOW_WIDTH 800
#define WINDOW_HEIGHT 600

#include <SFML/Window.hpp>
#include <SFML/Graphics.hpp>

inline int get_axis(sf::Keyboard::Key up, sf::Keyboard::Key down) {
	bool go_up = sf::Keyboard::isKeyPressed(up);
	bool go_down = sf::Keyboard::isKeyPressed(down);

	return go_down - go_up;
}

inline float unitrand() {
	return std::rand() / (float) RAND_MAX;
}

inline sf::Font load_font(std::string filepath) {
	sf::Font font;

	if (!font.loadFromFile(filepath))
	{
		abort();
	}

	return font;
}

#endif