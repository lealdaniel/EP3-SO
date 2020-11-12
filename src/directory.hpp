#ifndef _DIRECTORY_HPP
#define _DIRECTORY_HPP

#include <string>
#include <iostream>
#include <vector>
#include "./file.hpp"
#include "./item.hpp"

using namespace std;

class Directory {
  public:
    string name;
    int timeCreated;
    int timeUpdated;
    int timeAcessed;
    vector<Item> files;
    int fatIndex;
    void saveState();
    void mkdir(string dirName);
    void rmdir(string dirName);
    void cat(string fileName);
    void touch(string fileName);
    void rm(string fileName);
    void ls(string fileName);
    void find(string fileName)
};

#endif

