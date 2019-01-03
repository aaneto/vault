#include <SFML/Window.hpp>
#include <SFML/Graphics.hpp>

#include "Utils.cpp"
#include "Context.cpp"
#include "Pong.cpp"
#include "Menu.cpp"

int main() {
	std::srand(std::time(nullptr));

	sf::RenderWindow window(sf::VideoMode(WINDOW_WIDTH, WINDOW_HEIGHT), "Pong Thing", sf::Style::Close);
	window.setVerticalSyncEnabled(true);

	PongGame game_context(
		PAD_WIDTH,
		PAD_HEIGHT,
		PAD_SPEED,
		BALL_RADIUS,
		BALL_SPEED,
		BALL_ACC,
		WINDOW_WIDTH,
		WINDOW_HEIGHT
	);

	Menu menu_context;

	sf::Event event;
	sf::Clock game_clock;
	Context* current_context = &menu_context;

	float dt = 0;

	while (window.isOpen()) {
		current_context->update(dt);

		while (window.pollEvent(event)) {
			if (event.type == sf::Event::Closed) {
				window.close();
			}
			else {
				ContextEvent result = current_context->event(event);

				if (result == ContextEvent::Done)
					current_context = &game_context;
			}
		}

		window.clear(sf::Color::Black);
		current_context->draw(window);
		window.display();

		dt = 1000 * game_clock.restart().asSeconds();
	}
	return 0;
}