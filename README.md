# ATP assignment 1 Interpreter

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
line: 19 / 23
##### Lambda-calculus:
file: 'codeExample.txt', <br>
line: 21

### Code Contains:
##### Class with inheritance:
file: 'interpreter.py', <br>
line: 210 <br>
Here a NamedTuple is used, which meet the inheritance requirement
##### Object-printing for each class:
Yes, Since all classes with class variables use NamedTuple
##### Decorator:
Created: <br>
file: 'interpreter.py', <br>
line: 128 <br>

Used: <br>
file: 'interpreter.py', <br>
line: 140 <br>
##### Type Annotations:
Yes

##### 3 Higher order functions:
getExtension() <br>
file: 'interpreter.py', <br>
line: 19 <br>

applyFuncToList() <br>
file: 'interpreter.py', <br>
line: 154 <br>

operationSearch() <br>
file: 'interpreter.py', <br>
line: 355 <br>

##### Functonality must-haves:
Functions: More than one per file <br>

Functions can call other functions: <br>
file: 'codeExample.txt', <br>
line: 6 <br>

Functions can show their results: <br>
Results of the functions are simply returned to the caller, allowing the user to display them how they like <br>
Example can be found in: <br> 
file: 'main.py', <br>
line: 8 <br>
