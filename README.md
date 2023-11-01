# ELIZA for MicroPython

ELIZA is a retro chatbot that simulates a psychotherapist, based on the original 'ELIZA' script created by Joseph Weizenbaum in 1966. The detailed output provides insights into the workings of this iconic dialogue system and supports learning basic natural language processing concepts.

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

See the [src/micropython_eliza/chat.py](chat.py) file:

```
import sys
from micropython_eliza.identities import eliza

USERNAME_IN_CHAT = "YOU"

# Enable printing info and debug messages
agent = eliza.create(log_info=print, log_debug=print)
print("\n<press enter with no message to exit>")
print(f"{agent.name()}: {agent('')}")
print(f"{USERNAME_IN_CHAT}: ")
msg = sys.stdin.readline().strip()
while msg:
    print(f"{agent.name()}: {agent(msg)}")
    print(f"{USERNAME_IN_CHAT}: ")
    msg = sys.stdin.readline().strip()
```