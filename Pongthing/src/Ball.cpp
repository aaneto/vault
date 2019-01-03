#ifndef BALL_CPP
#define BALL_CPP

#define _USE_MATH_DEFINES

#include <cmath>

#include <SFML/Graphics.hpp>

#include "Utils.cpp"
#include "Pad.cpp"

enum class Offscreen {
	Left,
	Right,
	None,
};

class Ball : public sf::CircleShape {
public:
	sf::Vector2f velocity;
	float radius;
	float speed;
	float acc;

	Ball() {};

	Ball(float radius, float speed, float acc) : sf::CircleShape(radius) {
		setOrigin(radius / 2, radius / 2);
		setFillColor(sf::Color::White);

		this->radius = radius;
		this->speed = speed;
		this->acc = acc;

		reset(-1);
	}

	void reset(int direction) {
		setPosition(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2);
		
		float min_angle = M_PI / 32;
		float max_angle = M_PI / 4;
		float range_angle = max_angle - min_angle;

		float r = 2 * unitrand();
		float angle;

		if (r > 1.0) {
			angle = min_angle + range_angle * (r - 1.0);
		} else {
			angle = -(min_angle + range_angle * r);
		}

		velocity.x = direction * speed * cos(angle);
		velocity.y = direction * speed * sin(angle);
	}

	bool collided(Pad& pad, sf::Vector2f& p0, sf::Vector2f& p1, float& scale) {
		sf::Vector2f ds = p1 - p0;

		float distance = sqrt(ds.x * ds.x + ds.y * ds.y);

		float dx = abs(p0.x - pad.getPosition().x) - pad.size.x / 2 - radius;
		scale = (dx / distance);
		float dy = ds.y * scale;

		float y = getPosition().y + dy;

		return y < pad.getPosition().y + pad.size.y / 2 
			&& y > pad.getPosition().y - pad.size.y / 2;
	}

	Offscreen update(float dt, Pad& lpad, Pad& rpad) {
		Offscreen offscreen = Offscreen::None;

		sf::Vector2f ds = dt * velocity;

		sf::Vector2f p0 = getPosition();
		sf::Vector2f p1 = getPosition() + ds;

		bool on_left_collide_region = p1.x < lpad.getPosition().x + radius + lpad.size.x / 2;
		bool on_right_collide_region = p1.x > rpad.getPosition().x - radius - rpad.size.x / 2;

		bool on_left_lost_region = p0.x < lpad.getPosition().x;
		bool on_right_lost_region = p0.x > rpad.getPosition().x;

		bool on_left_offscreen = p0.x < -radius;
		bool on_right_offscreen = p0.x > WINDOW_WIDTH + radius;

		float scale;

		if (on_left_offscreen) {
			offscreen = Offscreen::Left;
			reset(1);
		}
		else if (on_right_offscreen) {
			offscreen = Offscreen::Right;
			reset(-1);
		}
		else if (on_left_lost_region || on_right_lost_region) {
			move(ds);
		}
		else if (on_left_collide_region && collided(lpad, p0, p1, scale)) {
			move(scale * ds);
			velocity.x = - acc * velocity.x;
		}
		else if (on_right_collide_region && collided(rpad, p0, p1, scale)) {
			move(scale * ds);
			velocity.x = -acc * velocity.x;
		}
		else {
			move(ds);
		}

		bool on_up_offscreen = getPosition().y < radius;
		bool on_down_offscreen = getPosition().y > WINDOW_HEIGHT - radius;

		if (on_up_offscreen) {
			setPosition(p1.x, radius);
			velocity.y = -velocity.y;
		}
		if (on_down_offscreen) {
			setPosition(p1.x, WINDOW_HEIGHT - radius);
			velocity.y = -velocity.y;
		}

		return offscreen;
	}
};

#endif