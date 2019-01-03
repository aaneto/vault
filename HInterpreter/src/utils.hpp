#ifndef UTILS_H_
#define UTILS_H_
#include <regex>
#include <string>
#include <vector>
#include <sstream>
#include <stdexcept>
#include <map>
#include <cmath>

bool isOperation(std::string c);
bool match_assignment(std::string expr);
bool match_double(std::string symbol);
bool match_double_function(std::string symbol, std::string function);
bool match_integer(std::string symbol);
bool match_integer_function(std::string symbol, std::string function);
bool match_variable(std::string symbol);
bool match_expr_ignoreBrackets(std::string expr);
bool bracket_check(std::string str);
std::vector<std::string> tokenize(std::string str, char separator);
double operateDouble(std::string operation, double lhand, double rhand);
long operateInteger(std::string operation, long lhand, long rhand);
std::string fitInput(std::string input);
bool lowerPrecedence(std::string lower, std::string higher);
std::vector<std::string> extractArguments(std::string symbol, std::string function);

#endif
