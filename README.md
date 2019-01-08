
# transitions-table
## Description
This package is support tool for [transitions](https://github.com/pytransitions/transitions) package.
You can ake a state transition table from a state machine made by transitions package.

## Install
You can get transitions_table from GitHub.

```bash
$ git clone https://github.com/nocatech/transitions_table.git .
```

And you can install the package using Python install.

```bash
$ python setup.py install
```

Note that 'transitions' and 'pandas' packages are installed if you have not installed.

## Usage
Please import transitions_table to use this package. 
For example:

```Python
from transitions_table import TransitionsTable
```

You write code in order to get a transitions table.

1. Make a state machine object (machine) using "transitions" package.
1. Make a TransitionsTable object using this package and the machine object.
1. Get a state transition table with the "get_table" method of the TransitionsTable object.

### Sample code
This is a sample code for a state transition table by transitions_table.

```Python
# make a state transition using transitons package
from transitions import Machine
from transitions_table import TransitionsTable

states = ['A', 'B', 'C']
transitions = [
    {'trigger': 'fromAtoB', 'source': 'A', 'dest': 'B'},
    {'trigger': 'fromBtoC', 'source': 'B', 'dest': 'C'},
]

class Model(object):
    pass

model = Model()
machine = Machine(model=model,
                  states=states, transitions=transitions, initial=states[0],
                  auto_transitions=False, ordered_transitions=False)

# make a transitions table using TransitionsTable
transitions_table = TransitionsTable(machine)
table = transitions_table.get_table()
print(table)
```

Python result is:

```Python
            A    B   C
fromAtoB    B  NaN NaN
fromBtoC  NaN    C NaN
```
A state transition table is made from "get_table" method and the "table" is DataFrame of Pandas.
The column titles is "source" state and the row titles is "events", the contents are "dest" state in this table.

### Options
TransitionsTable class has some options and these can set arguments in the class when make a TransitionsTable instance.
The class arguments summary is bellow:

| optional arg | default | summary |
|:-------------|:--------|:--------|
| internal_id  | '[internal]' | Internal transition results are replaced to internal_id.|
| undefined_id | pd.np.nan | Undefined transition results are replaced to undefined_id.|

#### Replacing internal string(internal_id)
You can set the 'dest' fo  None if you want to imprement a internal transition in a state machine by the transitions package.
Then, result of the internal transition is shown as '[internal]' in transitions_table by default.

For example:

```Python
# make a state transition using transitons package
from transitions import Machine
from transitions_table import TransitionsTable

states = ['A']
transitions = [
    {'trigger': 'internal', 'source': 'A', 'dest': None},
]

class Model(object):
    pass

model = Model()
machine = Machine(model=model,
                  states=states, transitions=transitions, initial=states[0],
                  auto_transitions=False, ordered_transitions=False)

# make a transitions table using TransitionsTable
transitions_table = TransitionsTable(machine)
table = transitions_table.get_table()
print(table)
```
Result is:

```Python
source             A
internal  [internal]
```
You can change the string of '[internal]' using internal_id argument.

```Python
transitions_table = TransitionsTable(machine, internal_id='---')
table = transitions_table.get_table()
print(table)
```

Replaced result is:

```Python
source      A
internal  ---
```

#### Undefined transition result(undefined_id)
Undefined transitions means MachineError in a state transition in transitions package.
You can replace the undefined transition results other strings.

```Python
# make a state transition using transitons package
from transitions import Machine
from transitions_table import TransitionsTable

states = ['A', 'B']
transitions = [
    {'trigger': 'fromAtoB', 'source': 'A', 'dest': 'B'},
    {'trigger': 'fromBtoA', 'source': 'B', 'dest': 'A'},
]

class Model(object):
    pass

model = Model()
machine = Machine(model=model,
                  states=states, transitions=transitions, initial=states[0],
                  auto_transitions=False, ordered_transitions=False)

# make a transitions table using TransitionsTable
transitions_table = TransitionsTable(machine)
table = transitions_table.get_table()
print(table)
```
In this case, the state machine cannot transit from state 'B' to 'A' on 'fromAtoB' event, and from state 'B to 'A' on 'fromBtoA'. It means causing MachineError.
Result of the execution is:

```Python
source      A    B
fromAtoB    B  NaN
fromBtoA  NaN    A
```

Undefined transition in transitions_table show 'NaN' in the table by default and 'NaN' is null of Pandas.
You can change the 'NaN' using undefined_id argument:

```Python
transitions_table = TransitionsTable(machine, undefined_id='xxx')
table = transitions_table.get_table()
print(table)
```

Note that internal_id is replaced using str type.
Replaced result is:

```Python
source      A    B
fromAtoB    B  xxx
fromBtoA  xxx    A
```

## Tests
You can some test in:

```Python
python setup.py test
```

I tested on Python 3.6 and all results were pass.

## Requirement
Pandas, transitions

## License
MIT License