#ifndef _FILE_HPP
#define _FILE_HPP

#include <string>
#include <iostream>

using namespace std;

class File {
    string name;
    string content;
    int size;
    int timeCreated;
    int timeUpdated;
    int timeAcessed;
    int fatIndex;
    void saveState();
    
};

#endif