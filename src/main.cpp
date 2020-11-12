#include <iostream>
#include <vector>
#include <string>
using namespace std;

int close = 0;
vector<string> read_input(string input);

int main() {
  string input;
  vector<string> commands;




  while (!close) {
    cout << "[ep3]: ";
    getline(cin, input);
    commands = read_input(input);

    cout << "\n"; 
  }

  return 0;
}

vector<string> read_input(string input) {
  vector<string> inputs;
  int index = input.find(" ");
  inputs.push_back(input.substr(0, index));
  string rest = input.substr(index + 1, input.size());

  if (inputs[0] == "find" || inputs[0] == "cp") {
    int newIndex = rest.find(" ");
    inputs.push_back(rest.substr(0, newIndex));
    rest = rest.substr(newIndex + 1, rest.size());
    inputs.push_back(rest);
  }

  else if (inputs[0] == "umount" || inputs[0] == "sai" || inputs[0] == "df")
    return inputs;

  else
    inputs.push_back(rest);

  return inputs;
}