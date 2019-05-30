from fuzzywuzzy import process

string = "guarantor name"
list_of_strings = ['guarantor name prannoy sarkar','guarantor name prannoy sarkar guarantor number 18888883838']
Ratios = process.extract(string,list_of_strings)
print(Ratios)
# You can also select the string with the highest matching percentage
[address,score] = process.extractOne(string,list_of_strings)
print(address,score)
