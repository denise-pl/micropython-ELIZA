"""Chat with ELIZA in a console

Copyright (c) 2017-2023, Szymon Jessa
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""

import sys
from .identities import eliza

USERNAME_IN_CHAT = "YOU"

def chat(log_info=None, log_debug=None):
    """Allows user interaction in console with a single chatbot (agent) in a loop:
    - start session with empty ("") message sent to the agent
    - read user message from console
    - get agent's response
    - write agent's response to console
    - exit if user presses enter without any input (message length is 0)
    """

    agent = eliza.create(log_info=log_info, log_debug=log_debug)

    print("\n<press enter with no message to exit>")
    print(f"{agent.name()}: {agent('')}")
    print(f"{USERNAME_IN_CHAT}: ")
    msg = sys.stdin.readline().strip()
    while msg:
        print(f"{agent.name()}: {agent(msg)}")
        print(f"{USERNAME_IN_CHAT}: ")
        msg = sys.stdin.readline().strip()


if __name__ == "__main__":
    chat()
