#include <vector>
using namespace std;

#define MAX 25000
class Bitmap {
  public:
    bool bitmap[25000];
    Bitmap();
    int spaceLeft(int size);

};

Bitmap::Bitmap() {
  for (int i = 0; i < 25000; i++) {
    bitmap[i] = 0;
  }
}

int Bitmap::spaceLeft(int size) {
  int space = 0;
  int i = 0;
  int found = 0;
  while (found == 0 && i < 25000) {
    if (!bitmap[i])
      space += 4096;

    if (space >= size)
      found = 1;

    i++;
  }

  return found;
}


