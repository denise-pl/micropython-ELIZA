"""Session management

Copyright (c) 2017-2023, Szymon Jessa
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""

class MultiAgentSession:
    """Allows interaction between multiple agents in a loop:
    - first agent gets empty ("") message
    - each agent response is passed as input message to next agent
    - last agent response is passed as input message to first agent
    """

    def __init__(self, *agents):
        self._agents = agents
        self._activeAgent = 0
        self._message = ""

    def next(self):
        self._message = self._agents[self._activeAgent](self._message)
        if self._message:
            # Normalization for MicroPython's re module which lacks IGNORECASE feature
            self._message = self._message.upper()
        result = (self._agents[self._activeAgent].name(), self._message)
        self._activeAgent = (self._activeAgent + 1) % len(self._agents)

        return result
