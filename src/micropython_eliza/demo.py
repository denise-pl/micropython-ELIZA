"""Demonstration of a conversation with ELIZA

Copyright (c) 2017-2023, Szymon Jessa
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""

from .session import MultiAgentSession
from .identities import eliza, eliza_demo

def demo(_print=print, log_info=None, log_debug=None):
    session = MultiAgentSession(
        eliza.create(name="ELIZA", log_info=log_info, log_debug=log_debug),
        eliza_demo.create(name="CLIENT")
    )

    idx = 0
    while True:
        if idx % 2 == 0:
            _print(f"****** ROUND #{int(idx/2)+1} ******")
        name, msg = session.next()
        if msg == None:
            _print(f"{name}: (END)")
            break

        _print(f"{name}: {msg}")
        idx += 1

if __name__ == "__main__":
    demo()
