#ifndef MENU_CPP
#define MENU_CPP

#include <SFML/Graphics.hpp>

#include "Utils.cpp"
#include "Context.cpp"

class Menu : public Context {
public:
	Menu() {
		start_button = sf::RectangleShape(sf::Vector2f(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4));
		sf::FloatRect bounds = start_button.getLocalBounds();
		start_button.setOrigin(bounds.width / 2, bounds.height / 2);
		start_button.setPosition(WINDOW_WIDTH / 2, bounds.height + 50.0f);
		start_button.setFillColor(sf::Color(120, 120, 120));

		font = load_font("res/arial.ttf");

		start_text.setFont(font);
		start_text.setString("Start");
		start_text.setCharacterSize(64);
		start_text.setFillColor(sf::Color::White);
		start_text.setStyle(sf::Text::Bold);

		sf::FloatRect text_bounds = start_text.getLocalBounds();

		start_text.setOrigin(text_bounds.left + text_bounds.width / 2, text_bounds.top + text_bounds.height / 2);
		start_text.setPosition(WINDOW_WIDTH / 2, bounds.height + 50.0f);


		pause_text.setFont(font);
		pause_text.setString("Press SPACE to pause the game");
		pause_text.setCharacterSize(32);
		pause_text.setFillColor(sf::Color::White);
		pause_text.setStyle(sf::Text::Bold);

		sf::FloatRect pause_text_bounds = pause_text.getLocalBounds();

		pause_text.setOrigin(pause_text_bounds.left + pause_text_bounds.width / 2, pause_text_bounds.top + pause_text_bounds.height / 2);
		pause_text.setPosition(WINDOW_WIDTH / 2, WINDOW_HEIGHT - bounds.height - 80.0f);
	}

	virtual void update(float dt) override final {};

	virtual void draw(sf::RenderWindow& window) override final {
		window.draw(start_button);
		window.draw(start_text);
		window.draw(pause_text);
	};

	virtual ContextEvent event(sf::Event& event) override final {
		if (event.type == sf::Event::MouseButtonPressed) {
		    if (event.mouseButton.button == sf::Mouse::Left) {
		    	sf::FloatRect bounds = start_button.getGlobalBounds();
		    	int x = event.mouseButton.x;
		    	int y = event.mouseButton.y;

		    	if (x > bounds.left && x < bounds.left + bounds.width && bounds.top + bounds.height > y && bounds.top < y) {
		    		return ContextEvent::Done;
		    	}
		    }
		}

		return ContextEvent::Nothing;
	};

private:
	sf::RectangleShape start_button;
	sf::Text start_text;
	sf::Text pause_text;

	sf::Font font;
};

#endif