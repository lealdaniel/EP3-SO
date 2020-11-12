#ifndef _ITEM_HPP
#define _ITEM_HPP

#include <string>
#include <iostream>
#include "./file.hpp"
#include "./directory.hpp"

using namespace std;

typedef struct Item {
  File archive;
  Directory directory;

} Item;

#endif