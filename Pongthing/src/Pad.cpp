#ifndef PAD_CPP
#define PAD_CPP

#include "Utils.cpp"
#include <SFML/Graphics.hpp>

class Pad : public sf::RectangleShape {
public:
	sf::Vector2f size;

	Pad() {};

	Pad(sf::Vector2f size, sf::Vector2f position) : sf::RectangleShape(size) {
		sf::FloatRect bounds = getLocalBounds();
		setOrigin(bounds.width / 2, bounds.height / 2);
		setPosition(position);
		setFillColor(sf::Color::Blue);

		this->size = size;
	}

	void update(float amount) {
		move(0.0f, amount);

		float half_height = getGlobalBounds().height / 2;

		float up_offscreen = half_height - getPosition().y;
		float down_offscreen = getPosition().y + half_height - WINDOW_HEIGHT;

		if (up_offscreen > 0) {
			move(0.0, up_offscreen);
		}
		if (down_offscreen > 0) {
			move(0.0, -down_offscreen);
		}
	}
};

#endif