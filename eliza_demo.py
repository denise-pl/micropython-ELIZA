"""Dummy agent to demonstrate ELIZA's algorithm

Copyright (c) 2023, Szymon Jessa
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the directory with this source file.

"""

DEFAULT_NAME = "Client"
"""Agent's default name
"""

script = [
    "hello Eliza, nice to meet you. how are you?",
    "no",
    "no",
    "no no no",
    "just no",
    "no",
    "nej",
    "perhaps we can look into natural language understanding problem, why not",
    "yes but maybe everyone has problems even a computer",
    "what if they start to think",
    "are you thinking yourself",
    "because my children have fun talking to chatbots",
    "you remind me of a family member",
    "hmm",
]


class Chatbot:
    """Demo chatbot"""

    def __init__(self, name=DEFAULT_NAME, data=script):
        self._name = name
        """Chatbot name (may be used in chat)
        """
        self._script = script
        self._idx = 0
        """Current message index
        """

    def name(self):
        """Get chatbot name"""
        return self._name

    def start(self):
        """Make the chatbot start the conversation"""
        self._idx = 0
        return self.__call__()

    def __call__(self, msg=None):
        """Return next message."""
        if self._idx == len(self._script):
            return None

        resp = self._script[self._idx]
        self._idx += 1

        return str(resp)


def create(name=DEFAULT_NAME):
    """Returns default agent object"""
    return Chatbot(name, script)


def length():
    """Get example length"""
    return len(script)


def example(length):
    """Example conversation for script validation and debugging

    >>> agent = Chatbot()
    >>> agent("How do you do. Please tell me your problem")
    'hello Eliza, nice to meet you. how are you?'
    >>> agent("How do you do. Please state your problem")
    'no'
    >>> agent("Are you saying 'no' just to be negative")
    'no'
    >>> agent("You are being a bit negative")
    'no no no'
    >>> agent("Why not")
    'just no'
    >>> agent("Why 'no")
    'no'
    >>> agent("Are you saying 'no' just to be negative")
    'nej'
    >>> agent("I am not sure I understand you fully")
    'perhaps we can look into natural language understanding problem, why not'
    >>> agent("You don't seem quite certain")
    'yes but maybe everyone has problems even a computer'
    >>> agent("Do computer worry you")
    'what if they start to think'
    >>> agent("Do you think its likely that they start to think")
    'are you thinking yourself'
    >>> agent("Why are you interested in whether I am thinking myself or not")
    'because my children have fun talking to chatbots'
    >>> agent("Tell me more about your family")
    'you remind me of a family member'
    >>> agent("you remind me of a family member")
    'hmm'
    >>> agent("Lets discuss further why your children have fun talking to chatbots")
    """

    agent = Chatbot()
    for idx, msg in enumerate(script[:length], 1):
        yield f"****** Round #{idx} ******"
        yield f"User: {msg}"
        yield f"{agent.name()}: {agent(msg)}"
        yield ""


if __name__ == "__main__":
    print("Run tests: python -m doctest -v eliza_demo.py")
    print("If you don't see any errors, you are fine.")
