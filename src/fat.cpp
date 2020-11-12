#include <vector>
using namespace std;
#include "./item.hpp"

typedef struct Node {
  int nextBlock;
  string content;
} Node;

#define MAX 25000
class Fat {
  public:
    vector<Node> fatTable;
    
};

