#ifndef PONG_CPP
#define PONG_CPP

#include "Pad.cpp"
#include "Ball.cpp"
#include "Score.cpp"
#include "Context.cpp"

class PongGame : public Context {
private:
	bool paused;
	Pad lpad;
	Pad rpad;
	Ball ball;
	sf::Font font;
	Score left_score;
	Score right_score;
	sf::RectangleShape divisor;
	Offscreen point;

public:
	PongGame(
		float pad_w,
		float pad_h,
		float pad_s,
		float ball_r,
		float ball_s,
		float ball_acc,
		int window_w,
		int window_h
	) {
		lpad = Pad(
			sf::Vector2f(pad_w, pad_h), // Size
			sf::Vector2f(5.0f + pad_w, window_h / 2) // Position
		);

		rpad = Pad(
			sf::Vector2f(pad_w, pad_h), // Size
			sf::Vector2f(window_w - pad_w - 5.0f, window_h / 2) // Position
		);

		ball = Ball(ball_r, ball_s, ball_acc);
		font = load_font("res/arial.ttf");

		left_score = Score(font, sf::Vector2f(40 + window_w / 2, 120));
		right_score = Score(font, sf::Vector2f(-40 + window_w / 2, 120));

		divisor = sf::RectangleShape(sf::Vector2f(3.0f, window_h));
		divisor.move(window_w / 2 - divisor.getGlobalBounds().width / 2, 0.0f);
		divisor.setFillColor(sf::Color::Blue);

		point = Offscreen::None;
		paused = false;
	}

	virtual void draw(sf::RenderWindow& window) override final {
		window.draw(divisor);
		window.draw(lpad);
		window.draw(rpad);
		window.draw(ball);
		window.draw(left_score);
		window.draw(right_score);
	}

	virtual void update(float dt) override final {
		if (paused)
			return;

		int lpad_direction = get_axis(sf::Keyboard::W, sf::Keyboard::S);
		int rpad_direction = get_axis(sf::Keyboard::Up, sf::Keyboard::Down);

		lpad.update(lpad_direction * PAD_SPEED * dt);
		rpad.update(rpad_direction * PAD_SPEED * dt);
		
		point = ball.update(dt, lpad, rpad);

		switch(point) {
			case Offscreen::Right:
				right_score.increaseScore();
				break;
			case Offscreen::Left:
				left_score.increaseScore();
				break;
			case Offscreen::None:
				break;
		}
	}

	virtual ContextEvent event(sf::Event& event) override final {
		if (event.type == sf::Event::KeyPressed) {
			if (event.key.code == sf::Keyboard::Space) {
				paused = !paused;
			}
		}

		return ContextEvent::Nothing;
	};
};

#endif