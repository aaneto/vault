#include <iostream>
#include <utility>
#include "BinaryExpressionTree.hpp"
//Versionamento adicionado após começo de projeto,
//Versão aproximada.
#define VERSION "0.5.7"

#ifdef _WIN32
char* readline(char* notUsed)
{
  std::string out;
  std::cout << "=>";
  std::getline(std::cin, out);
  return out.c_str();
}

void add_history(char* notUsed) {}
#else

#include <readline/history.h>
#include <readline/readline.h>
#endif


static std::map<std::string, std::pair<std::string, std::string>> vars;
double resolveDouble(std::string input)
{
	BinaryExpressionTree Tree;
	Tree.fromInfix(input);
	return Tree.evaluateDouble(vars);
}

long resolveInteger(std::string input)
{
	BinaryExpressionTree Tree;
	Tree.fromInfix(input);
	return Tree.evaluateDouble(vars);
}

bool checkIfDouble(std::string expr)
{
  for(auto item : vars)
  {
    if (std::regex_search(expr, std::regex("(" + item.first + ")")) && item.second.first == "Double")
    {
      return true;
    }
  }
	return std::regex_search(expr, std::regex("(\\.)|(pi)|(cos)|(sin)|(tan)|(acos)|(asin)|(atan)|(log)|(log2)|(sqrt)|(exp)|(logb)"));
}

void defineConstants()
{
  vars["pi"] = std::make_pair("Double", "3.141592653589793");
}

int main(int argc, char const *argv[])
{
	//Loop Principal
  defineConstants();
  bool zeroConverge = true;
  bool disableIntegers = false;
  for(int i = 1;i < argc;i++)
  {
    if(std::string(argv[i]) == "disableZeroConvergence")
    {
      zeroConverge = false;
    }
    else if(std::string(argv[i]) == "disableIntegers")
    {
      disableIntegers = true;
    }
  }
	std::cout << "YetAnotherInterpreter - " << VERSION
            << std::endl
            << "Data: " <<__DATE__
            << std::endl
            << "Hora: " << __TIME__
            << std::endl;
  std::string entry = "";
  while(entry != "exit()" && entry != "exit")
  {
    try
    {
      char* input;
      input = readline("=>");
      add_history(input);
      if(input != nullptr)
      {
        entry = std::string(input);
        if(entry == "exit" || entry == "exit()")
          break;
      }
      else
        entry = "";


      if(match_assignment(entry))
      {
        std::vector<std::string> assignment = tokenize(entry, '=');
        assignment[0].erase(std::remove(assignment[0].begin(), assignment[0].end(), ' '), assignment[0].end());
        if(match_variable(assignment[0]))
        {
          if(!checkIfDouble(assignment[1]) && !disableIntegers)
          {
            vars[assignment[0]] = std::make_pair("Integer", std::to_string(resolveInteger(assignment[1])));
          }
          else
          {
            vars[assignment[0]] = std::make_pair("Double", std::to_string(resolveDouble(assignment[1])));
          }
          std::cout << vars[assignment[0]].second << std::endl;
        }
        else
        {
          throw std::runtime_error("Lado esquerdo não é uma variável.");
        }
      }
      else if(!checkIfDouble(entry) && !disableIntegers)
      {
        long output = resolveInteger(entry);
        std::cout << output << std::endl;
      }
      else
      {
        double output = resolveDouble(entry);
        if(zeroConverge && fabs(output) < 1e-10)
        {
          output = 0;
        }
        std::cout << output << std::endl;
      }
      free(input);
    }
    catch(const std::runtime_error& error)
    {
    std::cout << "Comando ignorado, " << error.what() << std::endl;
    }
  }
	return 0;
}
