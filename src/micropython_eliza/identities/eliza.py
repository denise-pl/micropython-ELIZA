"""Python implementation of Joseph's Weizenbaum ELIZA script

Copyright (c) 2017-2023, Szymon Jessa
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the directory with this source file.

Example:
>>> import eliza
>>> agent = eliza.create()
>>> agent("hello")
'HOW DO YOU DO. PLEASE STATE YOUR PROBLEM'

Reference:
- Joseph Weizenbaum, "ELIZA - A Computer Program For the Study
of Natural Language Communication Between Man and Machine",
Communications of the Association for Computing Machinery,
Vol. 9, 1966, pp. 36-45
https://web.stanford.edu/class/linguist238/p36-weizenabaum.pdf

https://doi.org/10.1145/365153.365168
https://www.semanticscholar.org/paper/1896290

"""

import re

DEFAULT_NAME = "ELIZA"
"""Agent's default name
"""

KEYWORD_START = ""
"""Special keyword used to get the first message (before user input)
"""

KEYWORD_NONE = "NONE"
"""Special keyword used when no response could be generated
from the script rules (including memstack).
"""

tags = {
    "/BELIEF": r"FEEL|THINK|BELIEVE|WISH",
    "/FAMILY": r"MOTHER|FATHER|SISTER|BROTHER|WIFE|CHILDREN",
    "/NOUN": r"MOTHER|FATHER",
}
"""Tags are reused/evaluated within script decomposition (`regex`) rules
"""

script = dict()
"""Keywords with their properties and associated answer and memory rules:
- `rank` - priority of the keyword (`0` - default, lowest priority)
- `rules` - list of transformations (each with decomposition and reassembly)
    - `decomposition` - regular expression for text matching and extraction
    - `reassembly` - list of responses in the form of:
        - strings - passed to the `repl` argument of `re.sub()`
        - `=` - instruction to use another keyword (eg. `=WHAT`)
        - `NEWKEY` - instruction to drop current keyword from keystack
    - `pre` - regex applied between decomposition and reassembly
- `memory` - list of transformation rules to generate responses for later use
- `=` - keyword substitution, eg. `script["MOM"] = {"=": "mother"}`
"""

script[KEYWORD_START] = {
    "rules": [{"reassembly": ["How do you do. Please tell me your problem"]}]
}

script[KEYWORD_NONE] = {
    "rules": [
        {
            "reassembly": [
                "I am not sure I understand you fully",
                "Please go on",
                "What does that suggest to you",
                "Do you feel strongly about discussing such things",
            ]
        }
    ]
}

script["SORRY"] = {
    "rules": [
        {
            "reassembly": [
                "Please don't apologize",
                "Apologies are not necessary",
                "What feelings do you have when you apologize",
                "I've told you that apologies are not required",
            ]
        }
    ]
}

script["DONT"] = {"=": "don't"}
script["CANT"] = {"=": "can't"}
script["WONT"] = {"=": "won't"}

script["REMEMBER"] = {
    "rank": 5,
    "rules": [
        {
            # user input:           I   remember
            "decomposition": r"^.*\WYOU REMEMBER (.*)$",
            "reassembly": [
                r"Do you often think of \1",
                r"Does thinking of \1 bring anything else to mind",
                "What else do you remember",
                r"Why do you remember \1 just now",
                r"What in the present situation reminds you of \1",
                r"What is the connection between me and \1",
            ],
        },
        {
            # user input:          do you remember
            "decomposition": r"^.*\WDO I REMEMBER (.*)$",
            "reassembly": [
                r"Did you think I would forget \1",
                r"Why do you think I should recall \1 now",
                r"What about \1",
                "=WHAT",
                r"You mentioned \1",
            ],
        },
        {"reassembly": ["NEWKEY"]},
    ],
}

script["IF"] = {
    "rank": 3,
    "rules": [
        {
            "decomposition": r"^.*\WIF (.*)$",
            "reassembly": [
                r"Do you think its likely that \1",
                r"Do you wish that \1",
                r"What do you think about \1",
                r"Really, if \1",
            ],
        }
    ],
}

script["DREAMT"] = {
    "rank": 4,
    "rules": [
        {
            # user input:           I   dreamt
            "decomposition": r"^.*\WYOU DREAMT (.*)$",
            "reassembly": [
                r"Really, \1",
                r"Have you ever fantasied \1 while you were awake",
                r"Have you dreamt \1 before",
                "=DREAM",
                "NEWKEY",
            ],
        }
    ],
}

# Special types of decomposition and assembly rules characterized
# by the appearance of "=" at the top of the rule list.
# The word following the equal sign indicated which new set
# of transformation rules is to be applied.
# Here: replace "dreamed" with "dreamt" in input message and
# use transformation rules associated with "DREAMT" keyword
script["DREAMED"] = {"rank": 4, "=": "DREAMT", "rules": [{"reassembly": ["=DREAMT"]}]}

script["DREAM"] = {
    "rank": 3,
    "rules": [
        {
            "reassembly": [
                "What does that dream suggest to you",
                "Do you dream often",
                "What persons appear in your dreams",
                "Don't you believe that dream has something to do with your problem",
                "NEWKEY",
            ]
        }
    ],
}

script["DREAMS"] = {"rank": 3, "=": "dream", "rules": [{"reassembly": ["=DREAM"]}]}

script["HOW"] = {"rules": [{"reassembly": ["=WHAT"]}]}

script["WHEN"] = {"rules": [{"reassembly": ["=WHAT"]}]}

script["ALIKE"] = {"rank": 10, "rules": [{"reassembly": ["=DIT"]}]}

script["SAME"] = {"rank": 10, "rules": [{"reassembly": ["=DIT"]}]}

script["CERTAINLY"] = {"rank": 10, "rules": [{"reassembly": ["=YES"]}]}

script["PERHAPS"] = {
    "rules": [
        {
            "reassembly": [
                "You don't seem quite certain",
                "Why the uncertain tone",
                "Can't you be more positive",
                "You aren't sure",
                "Don't you know",
            ]
        }
    ]
}

script["MAYBE"] = {"rules": [{"reassembly": ["=PERHAPS"]}]}

script["NAME"] = {
    "rank": 15,
    "rules": [
        {
            "reassembly": [
                "I am not interested in names",
                "I've told you before, I don't care about names - please continue",
            ]
        }
    ],
}

script["DEUTSCH"] = {"rules": [{"reassembly": ["=XFREMD"]}]}

script["FRANCAIS"] = {"rules": [{"reassembly": ["=XFREMD"]}]}

script["ITALIANO"] = {"rules": [{"reassembly": ["=XFREMD"]}]}

script["ESPANOL"] = {"rules": [{"reassembly": ["=XFREMD"]}]}

script["XFREMD"] = {"rules": [{"reassembly": ["I am sorry, I speak only english"]}]}

script["HELLO"] = {
    "rules": [{"reassembly": ["How do you do. Please state your problem"]}]
}

script["HI"] = {"rules": [{"reassembly": ["=HELLO"]}]}

script["COMPUTER"] = {
    "rank": 50,
    "rules": [
        {
            "reassembly": [
                "Do computer worry you",
                "Why do you mention computers",
                "What do you think machines have to do with your problem",
                "Don't you think computers can help people",
                "What about machines worries you",
                "What do you think about machines",
            ]
        }
    ],
}

script["MACHINE"] = {"rank": 50, "rules": [{"reassembly": ["=COMPUTER"]}]}

script["MACHINES"] = {"rank": 50, "rules": [{"reassembly": ["=COMPUTER"]}]}

script["COMPUTERS"] = {"rank": 50, "rules": [{"reassembly": ["=COMPUTER"]}]}

script["AM"] = {
    "=": "are",
    "rules": [
        {
            # user input:          am  I|me
            "decomposition": r"^.*\WARE YOU (.*)$",
            "reassembly": [
                r"Do you believe you are \1",
                r"Would you want to be \1",
                r"You wish I would tell you you are \1",
                r"What would it mean if you were \1",
                "=WHAT",
            ],
        },
        {"reassembly": ["Why do you say 'AM'", "I don't understand that"]},
    ],
}

script["ARE"] = {
    "rules": [
        {
            # user input:       (are|am)  you
            "decomposition": r"^.*\WARE I (.*)$",
            "reassembly": [
                r"Why are you interested in whether I am \1 or not",
                r"Would you prefer if I weren't \1",
                r"Perhaps I am \1 in your fantasies",
                r"Do you sometimes think I am \1",
                "=WHAT",
            ],
        },
        {
            # user input:       (are|am)
            "decomposition": r"^.*\WARE (.*)$",
            "reassembly": [
                r"Did you think they might not be \1",
                r"Would you like it if they were not \1",
                r"What if they were not \1",
                r"Possibly they are \1",
            ],
        },
    ]
}

script["YOUR"] = {
    "=": "my",
    "rules": [
        {
            # user input:         your
            "decomposition": r"^.*\WMY (.*)$",
            "reassembly": [
                r"Why are you concerned over my \1",
                r"What about your own \1",
                r"Are you worried about someone elses \1",
                r"Really, my \1",
            ],
        }
    ],
}

script["WAS"] = {
    "rank": 2,
    "rules": [
        {
            # user input:          was  I
            "decomposition": r"^.*\WWAS YOU (.*)$",
            "reassembly": [
                r"What if you were \1",
                r"Do you think you were \1",
                r"Were you \1",
                r"What would it mean if you were \1",
                r"What does '\1' suggest to you",
                "=WHAT",
            ],
        },
        {
            # user input:           I   was
            "decomposition": r"^.*\WYOU WAS (.*)$",
            "reassembly": [
                r"Were you really \1",
                r"Why do you tell me you were \1 now",
                r"Perhaps I already knew you were \1",
            ],
        },
        {
            # user input:          was you
            "decomposition": r"^.*\WWAS I (.*)$",
            "reassembly": [
                r"Would you like to believe I was \1",
                r"What suggests that I was \1",
                "What do you think",
                r"Perhaps I was \1",
                r"What if I had been \1",
            ],
        },
        {
            "reassembly": [
                "NEWKEY",
            ]
        },
    ],
}

script["WERE"] = {"=": "was", "rules": [{"reassembly": ["=WAS"]}]}

script["ME"] = {"=": "you"}

script["YOU'RE"] = {
    "=": "I'm",
    "rules": [
        {"decomposition": r"^.*\WI'M (.*)$", "pre": r"I ARE \1", "reassembly": ["=YOU"]}
    ],
}

script["I'M"] = {
    "=": "You're",
    "rules": [
        {
            "decomposition": r"^.*\WYOU'RE (.*)$",
            "pre": r"YOU ARE \1",
            "reassembly": ["=I"],
        }
    ],
}

script["MYSELF"] = {"=": "yourself"}
script["YOURSELF"] = {"=": "myself"}
script["MOM"] = {"=": "mother"}
script["DAD"] = {"=": "father"}

script["I"] = {
    "=": "you",
    "rank": 0,
    "rules": [
        {
            # user input:            I   (want|need)
            "decomposition": r"^.*\WYOU (WANT|NEED) (.*)$",
            "reassembly": [
                r"What would it mean to you if you got \2",
                r"Why do you want \2",
                r"Suppose you got \2 soon",
                r"What if you never got \2",
                r"What would getting \2 mean to you",
                r"What does wanting \2 have to do with this discussion",
            ],
        },
        {
            # user input:           I   am       (sad|unhappy|depressed|sick)
            "decomposition": r"^.*\WYOU ARE (.*) (SAD|UNHAPPY|DEPRESSED|SICK) (.*)$",
            "reassembly": [
                r"I am sorry to hear you are \2",
                r"Do you think coming here will help you not to be \2",
                r"I'm sure its not pleasant to be \2",
                r"Can you explain what made you \2",
            ],
        },
        {
            # user input:           I   am       (happy|elated|glad|better)
            "decomposition": r"^.*\WYOU ARE (.*) (HAPPY|ELATED|GLAD|BETTER) (.*)$",
            "reassembly": [
                r"How have I helped you to be \2",
                r"Has your treatment made you \2",
                r"What makes you \2 just now",
                r"Can you explain why you are suddenly \2",
            ],
        },
        {
            # user input:           I   was
            "decomposition": r"^.*\WYOU WAS (.*)$",
            "reassembly": ["=WAS"],
        },
        {
            # user input:           I    feel|think|believe|wish I
            "decomposition": r"^.*\WYOU ("+tags['/BELIEF']+r") (.*)$",
            "reassembly": [
                "Do you really think so",
                r"But you are not sure you \2",
                r"Do you really doubt you \2",
            ],
        },
        {
            # user input:           I         feel|think|believe|wish  I
            "decomposition": r"^.*\WYOU (.*) ("+tags['/BELIEF']+r") (.*) YOU (.*)$",
            "reassembly": ["=YOU"],
        },
        {
            # user input:           I   am
            "decomposition": r"^.*\WYOU ARE (.*)$",
            "reassembly": [
                r"Is it because you are \1 that you came to me",
                r"How long have you been \1",
                r"Do you enjoy being \1",
            ],
        },
        {
            # user input:           I   (can't|cannot)
            "decomposition": r"^.*\WYOU (CAN'T|CANNOT) (.*)$",
            "reassembly": [
                r"How do you know you can't \2",
                "Have you tried",
                r"Perhaps you could \2 now",
                r"Do you really want to be able to \2",
            ],
        },
        {
            # user input:           I   don't
            "decomposition": r"^.*\WYOU DON'T (.*)$",
            "reassembly": [
                r"Don't you really \1",
                r"Why don't you \1",
                r"Do you wish to be able to \1",
                "Does that trouble you",
            ],
        },
        {
            # user input:           I   feel
            "decomposition": r"^.*\WYOU FEEL (.*)$",
            "reassembly": [
                "Tell me more about such feelings",
                r"Do you often feel \1",
                r"Do you enjoy feeling \1",
                r"Of what does feeling \1 remind you",
            ],
        },
        {
            "reassembly": [
                "You say I",
                "Can you elaborate on that",
                "Do you say I for some special reason",
                "That's quite interesting",
            ]
        },
    ],
}

script["YOU"] = {
    "=": "I",
    "rank": 0,
    "rules": [
        {
            # user input:         You remind me  of
            "decomposition": r"^.*\WI REMIND YOU OF .+",
            "reassembly": ["=DIT"],
        },
        {
            # user input:         You are
            "decomposition": r"^.*\WI ARE (.*)$",
            "reassembly": [
                r"What makes you think I am \1",
                r"Does it please you to believe I am \1",
                r"Do you sometimes wish you were \1",
                r"Perhaps you would like to be \1",
            ],
        },
        {
            # user input:         You      I|me
            "decomposition": r"^.*\WI (.*) YOU",
            "reassembly": [
                r"Why do you think I \1 you",
                r"You like to think I \1 you - don't you",
                r"What makes you think I \1 you",
                r"Really, I \1 you",
                r"Do you wish to believe I \1 you",
                r"Suppose I did \1 you - what would that mean",
                r"Does someone else believe I \1 you",
            ],
        },
        {
            # user input:          You
            "decomposition": r"^.*\WI (.*)$",
            "reassembly": [
                "We were discussing you - not me",
                r"Oh, I \1",
                "You're not really talking about me - are you",
                "What are your feelings now",
            ],
        },
    ],
}

script["YES"] = {
    "rules": [
        {
            "reassembly": [
                "You seem quite positive",
                "You are sure",
                "I see",
                "I understand",
            ]
        }
    ]
}

script["NO"] = {
    "rank": 0,
    "rules": [
        {
            "reassembly": [
                "Are you saying 'no' just to be negative",
                "You are being a bit negative",
                "Why not",
                "Why 'no'",
            ]
        }
    ],
}

script["MY"] = {
    "=": "your",
    "rank": 2,
    "rules": [
        {
            # user input:           my    (wife|mother|sister)
            "decomposition": r"^.*\WYOUR ("+tags['/FAMILY']+r") (.*)$",
            "reassembly": [
                "Tell me more about your family",
                r"Who else if your family \2",
                r"Your \1",
                r"What else comes to mind when you think of your \1",
            ],
        },
        {
            # user input:           my
            "decomposition": r"^.*\WYOUR (.*)$",
            "reassembly": [
                r"Your \1",
                r"Why do you say your \1",
                "Does that suggest anything else which belongs to you",
                r"Is it important to you that your \1",
            ],
        },
    ],
    "memory": [
        {
            # user input:           my   brother|dog|application|future|life|job|...
            "decomposition": r"^.*\WYOUR (.*)$",
            "reassembly": [
                r"Lets discuss further why your \1",
                r"Earlier you said your \1",
                r"But your \1",
                r"Does that have anything to do with the fact that your \1",
            ],
        }
    ],
}

script["CAN"] = {
    "rules": [
        {
            # user input:          can you
            "decomposition": r"^.*\WCAN I (.*)$",
            "reassembly": [
                r"You believe I can \1 don't you",
                "=WHAT",
                r"You want me to be able to \1",
                r"Perhaps you would like to be able to \1 yourself",
            ],
        },
        {
            # user input:          can I|me
            "decomposition": r"^.*\WCAN YOU (.*)$",
            "reassembly": [
                r"Whether or not you can \1 depends on you more than on me",
                r"Do you want to be able to \1",
                r"Perhaps you don't want to \1",
                "=WHAT",
            ],
        },
    ]
}

script["WHAT"] = {
    "rules": [
        {
            "reassembly": [
                "Why do you ask",
                "Does that question interest you",
                "What is it you really want to know",
                "Are such questions much on your mind",
                "What answer would please you most",
                "What do you think",
                "What comes to your mind when you ask that",
                "Have you asked such question before",
                "Have you asked anyone else",
            ]
        }
    ]
}

script["BECAUSE"] = {
    "rules": [
        {
            "reassembly": [
                "Is that the real reason",
                "Don't any other reasons come to mind",
                "Does that reason seem to explain anything else",
                "What other reasons might there be",
            ]
        }
    ]
}

script["WHY"] = {
    "rules": [
        {
            # user input:           why don't you
            "decomposition": r"^.*\WWHY DON'T I (.*)$",
            "reassembly": [
                r"Do you believe I don't \1",
                r"Perhaps I will \1 in good time",
                r"Should you \1 yourself",
                r"You want me to \1",
                "=WHAT",
            ],
        },
        {
            # user input:          why can't I|me
            "decomposition": r"^.*\WWHY CAN'T YOU (.*)$",
            "reassembly": [
                r"Do you think you should be able to \1",
                r"Do you want to be able to \1",
                r"Do you believe this will help you to \1",
                r"Have you any idea why you can't \1",
                "=WHAT",
            ],
        },
    ]
}

script["EVERYONE"] = {
    "rank": 2,
    "rules": [
        {
            # user input:           (everyone|everybody|nobody|noone)
            "decomposition": r"^.*\W(EVERYONE|EVERYBODY|NOBODY|NOONE) (.*)$",
            "reassembly": [
                r"Really, \1",
                r"Surely not \1",
                "Can you think of anyone in particular",
                "Who, for example",
                "You are thinking of a very special person",
                "Who, may I ask",
                "Someone special perhaps",
                "You have a particular person in mind, don't you",
                "Who do you think you're talking about",
            ],
        }
    ],
}

script["EVERYBODY"] = {"rank": 2, "rules": [{"reassembly": ["=EVERYONE"]}]}

script["NOBODY"] = {"rank": 2, "rules": [{"reassembly": ["=EVERYONE"]}]}

script["NOONE"] = {"rank": 2, "rules": [{"reassembly": ["=EVERYONE"]}]}

script["ALWAYS"] = {
    "rank": 1,
    "rules": [
        {
            "reassembly": [
                "Can you think of a specific example",
                "When",
                "What incident are you thinking of",
                "Really, always",
            ]
        }
    ],
}

script["LIKE"] = {
    "rank": 10,
    "rules": [
        {
            # user input:           (am|is|are|was)      like
            "decomposition": r"^.*\W(AM|IS|ARE|WAS) (.*) LIKE (.*)$",
            "reassembly": ["=DIT"],
        },
        {"reassembly": ["NEWKEY"]},
    ],
}

script["DIT"] = {
    "rules": [
        {
            "reassembly": [
                "In what way",
                "What resemblance do you see",
                "What does that similarity suggest to you",
                "What other connections do you see",
                "What do you suppose that resemblance means",
                "What is the connection, do you suppose",
                "Could there really be some connection",
                "How",
            ]
        }
    ]
}

def deepcopy(obj):
    if isinstance(obj, dict):
        return {key: deepcopy(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [deepcopy(item) for item in obj]
    elif isinstance(obj, str) or isinstance(obj, int):
        return obj
    elif isinstance(obj, int):
        return obj
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")


class Chatbot:
    """ELIZA - algorithm implementation."""

    def __init__(self, name=DEFAULT_NAME, data=script, log_info=None, log_debug=None):
        self._name = name
        """Chatbot name (may be used in chat)
        """
        self._script = deepcopy(data)
        """Local copy of the script is required,
        because the script is modified be the chatbot
        """
        self._memstack = []
        """Memory Stack - list of responses created during conversation,
        used when response couldn't be generated using transformation rules
        """
        self._print_info = log_info
        """Handler for passing log INFO messages
        """
        self._print_debug = log_debug
        """Handler for passing log DEBUG messages
        """

    def name(self):
        """Get chatbot name"""
        return self._name

    def start(self):
        """Make the chatbot start the conversation"""
        return self.__call__(KEYWORD_START)

    def _debug(self, msg, *args):
        if self._print_debug:
            self._print_debug(msg % args)

    def _info(self, msg, *args):
        if self._print_info:
            self._print_info(msg % args)

    def __call__(self, msg):
        """Return chatbot response for given input message."""

        # handle start of a session
        if msg == KEYWORD_START or msg is None:
            self._debug("Empty input - use welcome message")
            keyword_rules = self._get_rules(KEYWORD_START)
            resp, _ = self._get_response(keyword_rules, msg)
            return str(resp)

        msg = msg.upper()
        self._info("Message: '%s'", msg)

        keystack, altered_sentence = self._process_input(msg)

        # NATURAL LANGUAGE GENERATION
        # try to generate response given the keystack
        # and altered sentence (with applied substitutions)
        resp = ""
        if keystack:
            self._add_to_memstack(keystack, altered_sentence)
            resp = self._process_keystack(keystack, altered_sentence)

        # FALLBACK SCENARIO
        # if keywords weren't found or no decomposition rule could be applied
        if resp == "":
            self._debug("\tNo answer from keyword rules")
            resp = self._fallback_response()

        self._info("Response: %s", resp)

        return str(resp)

    def _process_input(self, msg):
        # TEXT SEGMENTATION
        # Only single phrases or sentences are used for transformation
        all_sentences = self._get_sentences(msg)
        self._info(
            "\tText segmentation: %s", ", ".join([f"'{s}'" for s in all_sentences])
        )

        keystack, altered_sentence = None, None
        for sentence in all_sentences:
            self._info("\tProcessing sentence: '%s'", sentence)

            # TOKENIZATION
            tokens = list(self._get_tokens(sentence))
            self._info("\tTokens: %s", ", ".join([f"'{t}'" for t in tokens]))

            # KEYWORDS DETECTION (FEATURE EXTRACTION, INTENT CLASSIFICATION)
            keystack, altered_sentence = self._scan_sentence(tokens)

            # if at least one keyword has been found in current sentence
            # accept it as the keystack and ignore the remaining sentences
            if keystack:
                break

        return keystack, altered_sentence

    def _scan_sentence(self, tokens):
        """Scan sentence left to right looking for keywords.
        If script defines a substitution it is performed here.

        Returns keystack ordered by the keyword order and priority
        and list of tokens after substitution.
        """
        keystack = None
        altered_tokens = []
        for token in tokens:
            key = token.upper()
            if key not in self._script:
                altered_tokens.append(token)
                continue

            if "=" in self._script[key]:
                token_repl = self._script[key]["="].upper()
                altered_tokens.append(token_repl)
                self._debug(
                    "\t\tSubstitution: '%s' => '%s' " "(altered sentence: '%s')",
                    token,
                    token_repl,
                    " ".join(altered_tokens),
                )
            else:
                altered_tokens.append(token)

            if "rules" in self._script[key]:
                rank = self._script[key].get("rank", 0)
                if keystack is None:
                    keystack = [(key, rank)]
                elif rank > keystack[0][1]:
                    keystack.insert(0, (key, rank))
                else:
                    keystack.append((key, rank))

        if keystack:
            keyword_rank = ", ".join(
                [f"'{keyword}' (rank: {rank})" for keyword, rank in keystack]
            )
        else:
            keyword_rank = "-"

        altered_sentence = " ".join(altered_tokens)
        # Leading space for first word boundary detection - micropython doesn't support \b
        altered_sentence = " " + altered_sentence

        self._info("\tKeystack (detected keywords): %s", keyword_rank)
        self._debug("\tAltered sentence: '%s'", altered_sentence)

        return keystack, altered_sentence

    def _add_to_memstack(self, keystack, altered_sentence):
        """Try to generate responses for memstack.
        Only top keyword's 'memory' transformations are considered.
        """

        if keystack is None or len(keystack) == 0:
            return

        top_keyword = keystack[0][0].upper()
        if "memory" in self._script[top_keyword]:
            self._debug(
                "\tMemstack: trying to generate response " "for keyword: '%s'",
                top_keyword,
            )
            memresp, _ = self._get_response(
                self._script[top_keyword]["memory"], altered_sentence
            )
            if memresp != "":
                self._memstack.append(memresp)
                self._debug("\tMemstack: added response: '%s'", memresp)
            else:
                self._debug("\tMemstack: couldn't generate response")

    def _process_keystack(self, keystack, altered_sentence):
        """Process keystack keywords to get a response.
        It processes all the associated script rules and special instructions:
        - `=` redirection
        - `NEWKEY`
        - `pre`
        """

        if keystack is None:
            return ""

        for keyword, _ in keystack:
            self._info("\tProcessing rules associated with keyword: '%s'", keyword)
            # find a response based on the keyword and altered user input
            keyword_rules = self._get_rules(keyword)
            resp, rule = self._get_response(keyword_rules, altered_sentence)
            if resp == "NEWKEY":
                self._debug(
                    "\t\tNEWKEY in reassembly - " "dropping keyword: '%s'", keyword
                )
                resp = ""
            else:
                while resp.startswith("="):
                    self._debug("\t\tRedirecting: %s%s", keyword, resp)
                    if "pre" in rule:
                        altered_sentence = re.sub(
                            rule["decomposition"],
                            rule["pre"].upper(),
                            altered_sentence
                        )
                        self._debug(
                            "\t\tPRE before redirect: %s " "(altered sentence: '%s')",
                            rule["pre"].upper(),
                            altered_sentence,
                        )
                    keyword = resp[1:]
                    keyword_rules = self._get_rules(keyword)
                    resp, rule = self._get_response(keyword_rules, altered_sentence)
                    if resp == "NEWKEY":
                        self._debug(
                            "\t\tNEWKEY in reassembly - " "dropping keyword: '%s'",
                            keyword,
                        )
                        resp = ""
                        break

            if resp != "":
                self._info(
                    "\tFound response for keyword: '%s' "
                    "(ignoring remaining keywords)",
                    keyword,
                )
                break

        return resp

    def _fallback_response(self):
        """Generate fallback response using:
        - memstack
        - default response associated with KEYWORD_NONE
        """
        resp = ""
        # try to use memory
        if len(self._memstack) > 0:
            resp = self._memstack.pop(0)
            self._debug("\t\tFallback: Use response from memstack")
        # and if there are no responses in memory,
        elif KEYWORD_NONE in script:
            # use default responses associated with special KEYWORD_NONE
            self._info("\t\tFallback: Use response from KEYWORD_NONE")
            kw_rules = self._get_rules(KEYWORD_NONE)
            resp, _ = self._get_response(kw_rules, "")
        else:
            logging.error("\t\tNo fallback: missing KEYWORD_NONE in script")

        return resp

    def _get_rules(self, keyword):
        """Get list of transformation rules for the given keyword"""
        keyword = keyword.upper()
        if "rules" not in self._script.get(keyword):
            logging.error("No rules associated with keyword: '%s'", keyword)
            return None

        return self._script[keyword]["rules"]

    def _get_response(self, transformation_rules, altered_sentence):
        """Get response and the rule used to generate it,
        given the list of transformation rules and input message.

        After use, the response is put on the bottom of the reassembly list.
        """
        if transformation_rules is None:
            return "", None

        # get first matching decomposition rule for the given keyword
        for rule in transformation_rules:
            # if there is no decomposition defined, go straight to the answers
            if "decomposition" not in rule:
                self._debug(
                    "\t\tNo decomposition defined " "for rule (use top answer)"
                )
                # use top answer from the list and move it to the end (rotate)
                resp = rule["reassembly"].pop(0)
                rule["reassembly"].append(resp)
                return resp.upper(), rule

            # if decomposition rule exists and matches the user input
            if re.search(rule["decomposition"], altered_sentence):
                self._debug('\t\tDecomposition matched: r"%s"', rule["decomposition"])
                # get the top reassembly rule and move it to the end (rotate)
                trans = rule["reassembly"].pop(0)
                rule["reassembly"].append(trans)
                trans = trans.upper()
                # generate response
                #             pattern                replacement    input string
                resp = re.sub(rule["decomposition"], trans, altered_sentence)
                self._debug(
                    "\t\tTransformation: "
                    're.sub(r"%s", r"%s", "%s")',
                    rule["decomposition"],
                    trans.replace('"', r"\""),
                    altered_sentence.replace('"', r"\""),
                )

                return resp, rule

        return "", None

    def _get_tokens(self, text):
        """Split text into tokens, keeping punctuation marks as separate tokens
        >>> list(Chatbot()._get_tokens("I'm first. second. You're"))
        ["I'm", 'first', '.', 'second', '.', "You're"]
        """

        token = []
        for c in text:
            if c == " ":
                if len(token) > 0:
                    yield "".join(token)
                    token = []
            elif c in ".,?!;":
                if len(token) > 0:
                    yield "".join(token)
                    token = []
                yield c
            else:
                token.append(c)

        if len(token) > 0:
            yield "".join(token)

    def _get_sentences(self, text):
        """Text segmentation - split text into sentences
        >>> Chatbot()._get_sentences("first sentence. second part, last words? maybe")
        ['first sentence', ' second part', ' last words', ' maybe']
        >>> Chatbot()._get_sentences("first. second?")
        ['first', ' second']
        """

        regex = re.compile(r"[\.\,\?]")
        sentences = [s for s in regex.split(text) if len(s) > 0]
        return sentences


def create(name=DEFAULT_NAME, log_info=None, log_debug=None):
    """Returns default agent object"""
    return Chatbot(name, script, log_info=log_info, log_debug=log_debug)


def example(length):
    """Example conversation for script validation and debugging

    >>> agent = Chatbot()
    >>> agent("")
    'HOW DO YOU DO. PLEASE TELL ME YOUR PROBLEM'
    >>> agent("hello Eliza, nice to meet you. how are you?")
    'HOW DO YOU DO. PLEASE STATE YOUR PROBLEM'
    >>> agent("no")
    "ARE YOU SAYING 'NO' JUST TO BE NEGATIVE"
    >>> agent("no")
    'YOU ARE BEING A BIT NEGATIVE'
    >>> agent("no no no")
    'WHY NOT'
    >>> agent("just no")
    "WHY 'NO'"
    >>> agent("no")
    "ARE YOU SAYING 'NO' JUST TO BE NEGATIVE"
    >>> agent("nej")
    'I AM NOT SURE I UNDERSTAND YOU FULLY'
    >>> agent("perhaps we can look into natural language understanding problem, why not")
    "YOU DON'T SEEM QUITE CERTAIN"
    >>> agent("yes but maybe everyone has problems even a computer")
    'DO COMPUTER WORRY YOU'
    >>> agent("what if they start to think")
    'DO YOU THINK ITS LIKELY THAT THEY START TO THINK'
    >>> agent("are you thinking yourself")
    'WHY ARE YOU INTERESTED IN WHETHER I AM THINKING MYSELF OR NOT'
    >>> agent("because my children have fun talking to chatbots")
    'TELL ME MORE ABOUT YOUR FAMILY'
    >>> agent("you remind me of a family member")
    'IN WHAT WAY'
    >>> agent("hmm")
    'LETS DISCUSS FURTHER WHY YOUR CHILDREN HAVE FUN TALKING TO CHATBOTS'
    """
    messages = [
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

    agent = Chatbot()
    for idx, msg in enumerate(messages[:length], 1):
        yield f"****** Round #{idx} ******"
        yield f"You: {msg}"
        yield f"{agent.name()}: {agent(msg)}"
        yield ""


if __name__ == "__main__":
    print("Run tests: python -m doctest -v eliza.py")
    print("If you don't see any errors, you are fine.")
