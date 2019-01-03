#include "BinaryExpressionTree.hpp"

BinaryExprNode::BinaryExprNode()
{
	this->value = "";
	this->left = nullptr;
	this->right = nullptr;
	this->parent = nullptr;
}

BinaryExprNode::BinaryExprNode(std::string val)
{
  this->value = val;
  this->left = nullptr;
  this->right = nullptr;
  this->parent = nullptr;
}

BinaryExprNode::BinaryExprNode(const BinaryExprNode& node)
{

	this->left = nullptr;
	this->right = nullptr;
	this->parent = nullptr;
	this->value = node.getValue();

	if(node.hasLeft())
	{
		this->addLeft(node.getLeft().getValue());
		recursiveCopy(node.getLeft(), this->getLeft());
	}
	else
	{
		this->left = nullptr;
	}

	if(node.hasRight())
	{
    this->addRight(node.getRight().getValue());
		recursiveCopy(node.getRight(), this->getRight());
	}
	else
	{
		this->right = nullptr;
	}
}

BinaryExprNode::~BinaryExprNode()
{
  delete this->left;
  delete this->right;
  this->parent = nullptr;
}

std::string BinaryExprNode::getValue() const
{
	return this->value;
}

void BinaryExprNode::setValue(std::string val)
{
	this->value = val;
}

void BinaryExprNode::addLeft(std::string val)
{
	if(this->left != nullptr)
		this->removeLeft();
	this->left = new BinaryExprNode(val);
	this->left->setParent(*this);
}

void BinaryExprNode::addLeft(BinaryExprNode node)
{
	if(this->left != nullptr)
		this->removeLeft();

	this->left = new BinaryExprNode(node);
	this->left->setParent(*this);
}

void BinaryExprNode::addRight(std::string val)
{
	if(this->right != nullptr)
		this->removeRight();
	this->right = new BinaryExprNode(val);
	this->right->setParent(*this);
}

void BinaryExprNode::addRight(BinaryExprNode node)
{
	if(this->right != nullptr)
		this->removeRight();
	this->right = new BinaryExprNode(node);
	this->right->setParent(*this);
}

void BinaryExprNode::addOperands(std::string val1, std::string val2)
{
	this->addLeft(val1), this->addRight(val2);
}

void BinaryExprNode::removeLeft()
{
  this->left->removeParent();
  delete this->left;
  this->left = nullptr;
}

void BinaryExprNode::removeRight()
{
  this->right->removeParent();
  delete this->right;
  this->right = nullptr;
}

void BinaryExprNode::removeOperands()
{
	this->removeLeft(), this->removeRight();
}

BinaryExprNode& BinaryExprNode::getLeft() const
{
  if(this->left != nullptr)
    return *(this->left);
  else
    throw std::runtime_error("Tentativa de acessar nó vazio.");
}

BinaryExprNode& BinaryExprNode::getRight() const
{
  if(this->right != nullptr)
    return *(this->right);
  else
    throw std::runtime_error("Tentativa de acessar nó vazio.");
}

BinaryExprNode& BinaryExprNode::getParent() const
{
  if(this->parent != nullptr)
    return *(this->parent);
  else
    throw std::runtime_error("Tentativa de acessar nó vazio.");
}

bool BinaryExprNode::hasLeft() const
{
	return this->left != nullptr;
}

bool BinaryExprNode::hasRight() const
{
	return this->right != nullptr;
}


std::string BinaryExprNode::getPrefix() const
{
	if(this->left == nullptr)
		return this->value;
	else
		return ("(" + this->value + " " +this->left->getPrefix() + " " + this->right->getPrefix() + ")");
}

std::string BinaryExprNode::getInfix() const
{
	if(this->left == nullptr)
		return this->value;
	else
		return ("(" + this->left->getInfix() + " " + this->value + " " + this->right->getInfix() + ")");
}

std::string BinaryExprNode::getPostfix() const
{
	if(this->left == nullptr)
		return this->value;
	else
		return ("(" + this->left->getPostfix() + " " + this->right->getPostfix() + " " + this->value + ")");
}

void BinaryExprNode::setParent(BinaryExprNode& node)
{
  this->parent = &node;
}

void BinaryExprNode::removeParent()
{
  this->parent = nullptr;
}

double BinaryExprNode::evaluateDouble(std::map<std::string, std::pair<std::string, std::string>> vars)
{
	if(this->left == nullptr)
	{
		return symbol2Double(this->value, vars);
	}
	else
	{
		return operateDouble(this->getValue(), this->getLeft().evaluateDouble(vars)
			, this->getRight().evaluateDouble(vars));
	}
}
long BinaryExprNode::evaluateInteger(std::map<std::string, std::pair<std::string, std::string>> vars)
{
	if(this->left == nullptr)
	{
		return symbol2Integer(this->value, vars);
	}
	else
	{
		return operateInteger(this->getValue(), this->getLeft().evaluateInteger(vars)
			, this->getRight().evaluateInteger(vars));
	}
}

BinaryExpressionTree::BinaryExpressionTree()
{
  this->Root = new BinaryExprNode();
}

BinaryExpressionTree::BinaryExpressionTree(std::string val)
{
  this->Root = new BinaryExprNode(val);
}

BinaryExpressionTree::BinaryExpressionTree(const BinaryExprNode& node)
{
  this->Root = new BinaryExprNode(node);
}

BinaryExpressionTree::BinaryExpressionTree(const BinaryExpressionTree& tree)
{
	this->Root = new BinaryExprNode(tree.getRoot());
}

BinaryExpressionTree::~BinaryExpressionTree()
{
  delete this->Root;
}

void BinaryExpressionTree::setRoot(const BinaryExprNode& node)
{
	this->Root = new BinaryExprNode(node);
}

BinaryExprNode& BinaryExpressionTree::getRoot() const
{
  if(this->Root != nullptr)
    return *(this->Root);
  else
    throw std::runtime_error("Tentativa de acessar a raiz de arvóre vazia.");
}

void BinaryExpressionTree::fromPostfix(std::string postfix)
{
	BinaryExprNode* pNode = this->Root;

	if(!bracket_check(postfix))
		throw std::runtime_error("Parênteses não balanceados.");

	auto tokens = tokenize(postfix, ' ');
	for(auto token = tokens.begin();token != tokens.end();)
	{
		if(isOperation(*token))
		{
			if(pNode->getValue().empty())
				pNode->setValue(*token), token++;
			else if(!(pNode->hasLeft()))
				pNode->addLeft(*token), pNode = &(pNode->getLeft()), token++;
			else if(!(pNode->hasRight()))
				pNode->addRight(*token), pNode = &(pNode->getRight()), token++;
			else if(!isOperation(pNode->getRight().getValue()) && !isOperation(pNode->getLeft().getValue()))
				pNode = &pNode->getParent();
		}
		else
		{
			if(pNode->getValue().empty())
				pNode->setValue(*token), token++;
			else if(!(pNode->hasLeft()))
				pNode->addLeft(*token), token++;
			else if(!(pNode->hasRight()))
				pNode->addRight(*token), token++;
			else
				pNode = &pNode->getParent();
		}
	}
}


void BinaryExpressionTree::fromInfix(std::string infix)
{
	infix = fitInput(infix);
	if(!bracket_check(infix))
		throw std::runtime_error("Parênteses não balanceados.");
	std::stack<std::string> Stack;
	Stack.push(")");
	infix = "( " + infix;
	std::stack<std::string> B;
	auto tokens = tokenize(infix, ' ');
	std::reverse(tokens.begin(), tokens.end());
	for(auto v = tokens.begin();v != tokens.end();v++)
	{
		if(*v == ")")
			Stack.push(*v);
		else if(*v == "(")
		{
			while(Stack.top() != ")")
			{
				B.push(Stack.top());
				Stack.pop();
			}
			Stack.pop();
		}
		else if(!isOperation(*v))
			B.push(*v);

		else
		{
			//checar se Stack.top não é operação
			if(!isOperation(Stack.top()))
				Stack.push(*v);
			else
			{
				while(!lowerPrecedence(Stack.top(), *v))
				{
					B.push(Stack.top());
					Stack.pop();
					if(!Stack.empty())
					{
						if(!isOperation(Stack.top()))
							break;
					}
				}
				Stack.push(*v);
			}
		}
	}
	std::string output = "";
	while(!B.empty())
	{
		output = output + " " + B.top();
		B.pop();
	}
	this->fromPostfix(output);
}


std::string BinaryExpressionTree::getPrefix() const
{
  return this->Root->getPrefix();
}

std::string BinaryExpressionTree::getInfix() const
{
  return this->Root->getInfix();
}

std::string BinaryExpressionTree::getPostfix() const
{
  return this->Root->getPostfix();
}

BinaryExpressionTree& BinaryExpressionTree::operator=(const BinaryExpressionTree& tree)
{
	if(this->Root != nullptr)
		delete this->Root;
	this->Root = new BinaryExprNode(tree.getRoot());
	return *this;
}


double BinaryExpressionTree::evaluateDouble(std::map<std::string, std::pair<std::string, std::string>> vars)
{
	return this->Root->evaluateDouble(vars);
}

long BinaryExpressionTree::evaluateInteger(std::map<std::string, std::pair<std::string, std::string>> vars)
{
	return this->Root->evaluateInteger(vars);
}

void recursiveCopy(BinaryExprNode& copyFrom, BinaryExprNode& copyTo)
{
	copyTo.setValue(copyFrom.getValue());
	if(copyFrom.hasLeft())
	{
		copyTo.addLeft(0);
		recursiveCopy(copyFrom.getLeft(), copyTo.getLeft());
	}
	if(copyFrom.hasRight())
	{
		copyTo.addRight(0);
		recursiveCopy(copyFrom.getRight(), copyTo.getRight());
	}
}

double symbol2Double(std::string symbol, std::map<std::string, std::pair<std::string, std::string>> vars)
{
	if(match_double(symbol))
	{
		return std::stod(symbol);
	}
	else if(match_variable(symbol))
	{
    if(vars.find(symbol) != vars.end())
    {
      return std::stod(vars[symbol].second);
    }
		else if(vars.find(symbol.substr(1)) != vars.end())
		{
			return -1 * std::stod(vars[symbol.substr(1)].second);
		}
    else
    {
      throw std::runtime_error("Variável " + symbol + " não declarada.");
    }
	}
	else if(match_double_function(symbol, "cos"))
	{
		std::string arg = extractArguments(symbol, "cos")[0];
		if(match_variable(arg))
			return cos(std::stod(vars[arg].second));
		else if(match_double(arg))
			return cos(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return cos(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "sin"))
	{
		std::string arg = extractArguments(symbol, "sin")[0];
		if(match_variable(arg))
			return sin(std::stod(vars[arg].second));
		else if(match_double(arg))
			return sin(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return sin(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "tan"))
	{
		std::string arg = extractArguments(symbol, "tan")[0];
		if(match_variable(arg))
			return tan(std::stod(vars[arg].second));
		else if(match_double(arg))
			return tan(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return tan(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "acos"))
	{
		std::string arg = extractArguments(symbol, "acos")[0];
		if(match_variable(arg))
			return acos(std::stod(vars[arg].second));
		else if(match_double(arg))
			return acos(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return acos(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "asin"))
	{
		std::string arg = extractArguments(symbol, "asin")[0];
		if(match_variable(arg))
			return asin(std::stod(vars[arg].second));
		else if(match_double(arg))
			return asin(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return asin(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "atan"))
	{
		std::string arg = extractArguments(symbol, "atan")[0];
		if(match_variable(arg))
			return atan(std::stod(vars[arg].second));
		else if(match_double(arg))
			return atan(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return atan(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "exp"))
	{
		std::string arg = extractArguments(symbol, "exp")[0];
		if(match_variable(arg))
			return exp(std::stod(vars[arg].second));
		else if(match_double(arg))
			return exp(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return exp(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "log"))
	{
		std::string arg = extractArguments(symbol, "log")[0];
		if(match_variable(arg))
			return log(std::stod(vars[arg].second));
		else if(match_double(arg))
			return log(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return log(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "sqrt"))
	{
		std::string arg = extractArguments(symbol, "sqrt")[0];
		if(match_variable(arg))
			return sqrt(std::stod(vars[arg].second));
		else if(match_double(arg))
			return sqrt(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return sqrt(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "log2"))
	{
		std::string arg = extractArguments(symbol, "log2")[0];
		if(match_variable(arg))
			return log2(std::stod(vars[arg].second));
		else if(match_double(arg))
			return log2(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return log2(Tree.evaluateDouble(vars));
		}
	}
	else if(match_double_function(symbol, "logb"))
	{
		std::string arg = extractArguments(symbol, "logb")[0];
		if(match_variable(arg))
			return logb(std::stod(vars[arg].second));
		else if(match_double(arg))
			return logb(std::stod(arg));
		else
		{
			BinaryExpressionTree Tree;
			Tree.fromInfix(arg);
			return logb(Tree.evaluateDouble(vars));
		}
	}

	else
	{
		throw std::runtime_error("Simbolo não reconhecido: " + symbol);
	}
}

long symbol2Integer(std::string symbol, std::map<std::string, std::pair<std::string, std::string>> vars)
{
	if(match_integer(symbol))
	{
		return std::stol(symbol);
	}
	else if(match_variable(symbol))
	{
    if(vars.find(symbol) != vars.end())
    {
      return std::stol(vars[symbol].second);
    }

		else if(vars.find(symbol.substr(1)) != vars.end())
		{
			return -1 * std::stod(vars[symbol.substr(1)].second);
		}
    else
    {
      throw std::runtime_error("Variável " + symbol + " não declarada.");
    }
	}
	else
	{
    throw std::runtime_error("Simbolo não reconhecido: " + symbol);
	}
}
