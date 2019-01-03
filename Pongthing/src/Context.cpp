#ifndef CONTEXT_CPP
#define CONTEXT_CPP

#include <SFML/Graphics.hpp>

enum class ContextEvent {
	Done, // This context is done
	Nothing // Do nothing
};

class Context {
public:
	virtual void update(float dt) = 0;
	virtual void draw(sf::RenderWindow& window) = 0;
	virtual ContextEvent event(sf::Event& event) = 0;
};

#endif