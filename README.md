# ELIZA for MicroPython

ELIZA is a retro chatbot that simulates a psychotherapist, based on the original 'ELIZA' script created by Joseph Weizenbaum in 1966. The detailed output provides insights into the workings of this iconic dialogue system and supports learning basic natural language processing concepts.

## Reference

"ELIZA - A Computer Program For the Study of Natural Language Communication Between Man and Machine" by Joseph Weizenbaum, 1966.

DOI: [10.1145/365153.365168](https://doi.org/10.1145/365153.365168)
S2CID: [1896290](https://www.semanticscholar.org/paper/1896290)

## Example conversation

```
ELIZA: DO COMPUTER WORRY YOU
CLIENT: WHAT IF THEY START TO THINK
ELIZA: DO YOU THINK ITS LIKELY THAT THEY START TO THINK
CLIENT: ARE YOU THINKING YOURSELF
ELIZA: WHY ARE YOU INTERESTED IN WHETHER I AM THINKING MYSELF OR NOT
```

## Example log with processing information

```
CLIENT: YES BUT MAYBE EVERYONE HAS PROBLEMS EVEN A COMPUTER
Message: 'YES BUT MAYBE EVERYONE HAS PROBLEMS EVEN A COMPUTER'
	Text segmentation: 'YES BUT MAYBE EVERYONE HAS PROBLEMS EVEN A COMPUTER'
	Processing sentence: 'YES BUT MAYBE EVERYONE HAS PROBLEMS EVEN A COMPUTER'
	Tokens: 'YES', 'BUT', 'MAYBE', 'EVERYONE', 'HAS', 'PROBLEMS', 'EVEN', 'A', 'COMPUTER'
	Keystack (detected keywords): 'COMPUTER' (rank: 50), 'EVERYONE' (rank: 2), 'YES' (rank: 0), 'MAYBE' (rank: 0)
	Altered sentence: ' YES BUT MAYBE EVERYONE HAS PROBLEMS EVEN A COMPUTER'
	Processing rules associated with keyword: 'COMPUTER'
		No decomposition defined for rule (use top answer)
	Found response for keyword: 'COMPUTER' (ignoring remaining keywords)
Response: DO COMPUTER WORRY YOU
ELIZA: DO COMPUTER WORRY YOU
```

## How to install

```
python -m pip install --upgrade micropython_eliza
```

## How to run

Start chat in the console:
```
python -m micropython_eliza.chat
```

See an example conversation:
```
python -m micropython_eliza.demo
```

## How to use

```
import sys
from micropython_eliza import eliza

USERNAME_IN_CHAT = "YOU"

agent = eliza.create()
print("\n<press enter with no message to exit>")
print(f"{agent.name()}: {agent('')}")
print(f"{USERNAME_IN_CHAT}: ")
msg = sys.stdin.readline().strip()
while msg:
    print(f"{agent.name()}: {agent(msg)}")
    print(f"{USERNAME_IN_CHAT}: ")
    msg = sys.stdin.readline().strip()
```

To enable printing info and debug messages, provide log handlers, e.g.:
```
agent = eliza.create(log_info=print, log_debug=print)
```
