#include "utils.hpp"

bool isOperation(std::string c)
{
	if(c == "+" || c == "-" || c == "*" || c == "/" || c == "%" || c == "^")
		return true;
	else
		return false;
}

bool match_assignment(std::string expr)
{
	return std::regex_match(expr, std::regex("(.*)=(.*)"));
}

bool match_double(std::string symbol)
{
	std::string match_double = "(-)?([0-9]+(\\.([0-9]*))?)|(\\.([0-9]+))";
	return std::regex_match(symbol, std::regex(match_double));
}

bool match_integer(std::string symbol)
{
	std::string match_integer = "(-)?([0-9]+)";
	return std::regex_match(symbol, std::regex(match_integer));
}

bool match_variable(std::string symbol)
{
	std::string match_var = "(-)?([[:alpha:]]+)([[:alnum:]]*)";
	return std::regex_match(symbol, std::regex(match_var));
}

bool match_expr_ignoreBrackets(std::string expr)
{
  bool lastIsOperation = false;
  bool lastIsNumber = false;
  bool inNumber = false;
  for(char c: expr)
  {
    if(lastIsNumber && isOperation(std::string(1, c)))
    {
      lastIsNumber = false;
      inNumber = false;
      lastIsOperation = true;
    }
    else if(lastIsOperation && isdigit(c))
    {
      lastIsOperation = false;
      lastIsNumber = true;
      inNumber = true;
    }
    else if(!inNumber && lastIsNumber && isdigit(c))
    {
      return false;
    }
    else if(isdigit(c))
    {
      lastIsNumber = true;
      inNumber = true;
    }
    else if(isOperation(std::string(1, c)))
    {
      lastIsOperation = true;
      lastIsNumber = false;
      inNumber = false;
    }
    else if(c == ' ')
    {
      inNumber = false;
    }
		else
		{
			lastIsNumber = false;
			inNumber = false;
			lastIsOperation = false;
		}
  }
  return true;
}

bool match_double_function(std::string symbol, std::string function)
{
	return std::regex_match(symbol, std::regex("(" +function+ ")(\\()"+"(.*)"+"(\\))"));
}

bool match_integer_function(std::string symbol, std::string function)
{
	std::string match_integer = "([0-9]+)";
	std::string match_integer_sequence = match_integer+ "(," + match_integer+ ")*";
	return std::regex_match(symbol, std::regex("(" +function+ ")(\\()"+match_integer_sequence+"(\\))"));
}

bool bracket_check(std::string str)
{
	short closure = 0;
	for(char v: str)
	{
		if(v == '(')
			closure++;
		else if(v == ')')
			closure--;
		if(closure < 0)
		{
			return false;
		}
	}
	return closure == 0;
}

std::vector<std::string> tokenize(std::string str, char separator)
{
	std::vector<std::string> tokens;
	std::istringstream buffer(str);
	for(std::string token; getline(buffer, token, separator);)
	{
		tokens.push_back(token);
	}
	return tokens;
}

double operateDouble(std::string operation, double lhand, double rhand)
{
	if(operation == "+")
		return lhand + rhand;
	else if(operation == "-")
		return lhand - rhand;
	else if(operation == "*")
		return lhand * rhand;
	else if(operation == "/")
		return lhand / rhand;
	else if(operation == "%")
		throw std::runtime_error("Operação inválida para não inteiros.");
	else if(operation == "^")
		return pow(lhand, rhand);
	else
		throw std::runtime_error("Operação inválida.");
}

long operateInteger(std::string operation, long lhand, long rhand)
{
	if(operation == "+")
		return lhand + rhand;
	else if(operation == "-")
		return lhand - rhand;
	else if(operation == "*")
		return lhand * rhand;
	else if(operation == "/")
		return lhand / rhand;
	else if(operation == "%")
		return lhand % rhand;
	else if(operation == "^")
		return (long)pow(lhand, rhand);
	else
		throw std::runtime_error("Operação inválida.");
}

std::string fitInput(std::string input)
{
  if(!match_expr_ignoreBrackets(input))
  {
    throw std::runtime_error("Expressão inválida, " + input);
  }
	input.erase(std::remove(input.begin(), input.end(), ' '), input.end());
	std::string output = "";
	int isOnVar = 0;
	char lastChar= char(0);
	for(char c : input)
	{
		if(c == '(' && lastChar != ' ' && !isOperation(std::string(1, lastChar)) && lastChar != ')' && lastChar != '(')
		{
			isOnVar++;
			output.append("(");
		}
		else if(c == ')' && isOnVar > 0)
		{
			isOnVar--;
			output.append(")");
		}
		else if(c == '-' && (lastChar == '(' || isOperation(std::string(1, lastChar)) || lastChar == char(0)))
		{
			output.append("-");
		}
		else if(c == '(')
		{
			output.append("( ");
		}
		else if(c == ')')
		{
			if(isOnVar > 0)
				output.append(")");
			else
				output.append(" )");
		}

		else if(isOperation(std::string(1, c)))
		{
			if(isOnVar > 0)
				output.append(std::string(1, c));
			else
				output.append(" " + std::string(1, c) + " ");
		}
		else
		{
			output.append(std::string(1, c));
		}
		lastChar = c;
	}
	return output;
}

bool lowerPrecedence(std::string lower, std::string higher)
{
	if(lower == "+" || lower == "-")
	{
		if(higher == "+" || higher == "-")
			return false;
		else
			return true;
	}
	else if(lower == "%")
	{
		if(higher == "^" || higher == "*" || higher == "/")
			return true;
		else
			return false;
	}
	else if(lower == "*" || lower == "/")
	{
		if(higher == "^")
			return true;
		else
			return false;
	}
	else if(lower == "^")
	{
		return false;
	}
	return false;
}

std::vector<std::string> extractArguments(std::string symbol, std::string function)
{
	symbol = std::regex_replace(symbol, std::regex("("+function+")"), "", std::regex_constants::format_first_only);
	symbol = std::regex_replace(symbol, std::regex("(\\()"), "", std::regex_constants::format_first_only);
	symbol = std::regex_replace(symbol, std::regex(" "), "");
	symbol = std::regex_replace(symbol, std::regex(","), " ");
	symbol.pop_back();
	std::vector<std::string> args;
	for(std::string s: tokenize(symbol, ' '))
	{
		args.push_back(s);
	}
	return args;
}
