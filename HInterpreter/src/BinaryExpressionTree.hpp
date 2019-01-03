#ifndef BINARYEXPRESSIONTREE_H_
#define BINARYEXPRESSIONTREE_H_
#include "utils.hpp"
#include <cmath>
#include <stack>

class BinaryExprNode
{
public:
  BinaryExprNode();
  BinaryExprNode(std::string value);
  BinaryExprNode(const BinaryExprNode& node);
  ~BinaryExprNode();
  std::string getValue() const;
  void setValue(std::string val);
  void addLeft(std::string val);
  void addLeft(BinaryExprNode node);
  void addRight(std::string val);
  void addRight(BinaryExprNode node);
  void addOperands(std::string val1, std::string val2);
  void addOperands(BinaryExprNode node1, BinaryExprNode node2);
  void removeLeft();
  void removeRight();
  void removeOperands();
  BinaryExprNode& getLeft() const;
  BinaryExprNode& getRight() const;
  BinaryExprNode& getParent() const;
  bool isOperation() const;
  bool hasLeft() const;
  bool hasRight() const;
  std::string getPrefix() const;
  std::string getInfix() const;
  std::string getPostfix() const;
  double evaluateDouble(std::map<std::string, std::pair<std::string, std::string>> vars);
  long evaluateInteger(std::map<std::string, std::pair<std::string, std::string>> vars);
private:
  BinaryExprNode* left;
  BinaryExprNode* right;
  BinaryExprNode* parent;
  std::string value;
  void setParent(BinaryExprNode& node);
  void removeParent();
};

class BinaryExpressionTree
{
public:
  BinaryExpressionTree();
  BinaryExpressionTree(std::string val);
  BinaryExpressionTree(const BinaryExprNode& node);
  BinaryExpressionTree(const BinaryExpressionTree& tree);
  ~BinaryExpressionTree();
  void setRoot(const BinaryExprNode& node);
  BinaryExprNode& getRoot() const;
  void fromPostfix(std::string);
  void fromInfix(std::string);
  std::string getPrefix() const;
  std::string getInfix() const;
  std::string getPostfix() const;
  BinaryExpressionTree& operator=(const BinaryExpressionTree& tree);
  double evaluateDouble(std::map<std::string, std::pair<std::string, std::string>> vars);
  long evaluateInteger(std::map<std::string, std::pair<std::string, std::string>> vars);
private:
  BinaryExprNode* Root;
};
void recursiveCopy(BinaryExprNode&, BinaryExprNode&);
double symbol2Double(std::string symbol, std::map<std::string, std::pair<std::string, std::string>> vars);
long symbol2Integer(std::string symbol, std::map<std::string, std::pair<std::string, std::string>> vars);
#endif /* BINARYEXPRESSIONTREE_H_ */
