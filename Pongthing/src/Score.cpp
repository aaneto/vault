#ifndef SCORE_CPP
#define SCORE_CPP

#include <SFML/Graphics.hpp>


class Score : public sf::Text {
public:
	Score() {};
	
	Score(sf::Font& font, sf::Vector2f position) : sf::Text(), score(0) {
		setFont(font);
		setString(std::to_string(score));
		setCharacterSize(34);
		setFillColor(sf::Color::White);
		setStyle(sf::Text::Bold);

		sf::FloatRect bounds = getLocalBounds();

		setOrigin(bounds.left + bounds.width / 2, bounds.top + bounds.height / 2);
		setPosition(position.x, position.y);
	}

	void increaseScore() {
		score = score > 999 ? score : score + 1;
		setString(std::to_string(score));
	}
private:
	int score;
};

#endif