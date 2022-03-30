# ATP assignment 2 Compiler

### Chosen Language: 
Self created language: Checkpoint

### Turing Complete
In order for a language to be counted it needs to meet a select amount of criteria (as for as I could find). <br>
Below i'll note what that criteria is and a code example of how this language meet it.

##### A way to read and write some form of storage
```
var x = 10
```

##### A way to calculate new variables from old ones
```
var x = 10
x = 5
var y = x - 5
```

##### A form of conditional repetition or conditional jump
```
var x = 10

checkpoint one      # Sets a checkpoint to which you can return
?(x >= 10){
    x = x - 1
    >>> one         # Return to checkpoint 'one'
}
```

### Language Supports:
##### Goto-statements:
file: 'codeExample.txt', <br>
line: 22 / 26
##### Lambda-calculus:
file: 'codeExample.txt', <br>
line: 5

### Code Contains:
##### Class with inheritance:
file: 'compiler.py', <br>
line: 210 <br>
Here a NamedTuple is used, which meet the inheritance requirement
##### Object-printing for each class:
Yes, Since all classes with class variables use NamedTuple
##### Decorator:
Created: <br>
file: 'compiler.py', <br>
line: 133 <br>

Used: <br>
file: 'compiler.py', <br>
line: 145 <br>
##### Type Annotations:
Yes

##### 3 Higher order functions:
getExtension() <br>
file: 'compiler.py', <br>
line: 19 <br>

applyFuncToList() <br>
file: 'compiler.py', <br>
line: 159 <br>

operationSearch() <br>
file: 'compiler.py', <br>
line: 361 <br>

##### Functonality must-haves:
Functions: More than one per file <br>

Functions can call other functions: <br>
file: 'codeExample.txt', <br>
line: 6 <br>

Functions can show their results: <br>
Results of the functions are simply returned to the caller, allowing the user to display them how they like <br>
Example can be found in: <br> 
file: 'main.cpp', <br>
line: 11 <br>

There must be Unit tests: <br>
Unit tests can be found in 'main.cpp' <br>

There must be a Makefile that compiles the code which in turn goes through unit tests: <br>
This makefile is adequately dubbed 'Makefile2'.  <br>
This Makefile compiles the Checkpoint code, after doing this it runs another makefile which compiles the c++ code along with the assembly code. <br>

##### Librarys:
While the python code is library free the c++ code requires hwlib in order to function. <br>
Additionally the c++ Makefile requires other Makefiles to be present. <br>
It is assumed that the user is working within a hwlib enviroment and thus has the other Makefiles present. <br>

##### Could have's:
Besides the standard functionality of the assignment the compiler also generates commenets detailing what the .asm code translates too. <br>
The comments present the given input code above the translated .asm code which makes it easy to see what the .asm code means. <br> 

