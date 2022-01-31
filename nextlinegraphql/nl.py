import sys
import asyncio

from pathlib import Path

from nextline import Nextline

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))


SCRIPT_PATH = _THIS_DIR.joinpath("script.py")
with open(SCRIPT_PATH) as f:
    statement = f.read()

del _THIS_DIR


nextline_holder = []


def get_nextline():
    if not nextline_holder:
        nextline_holder.append(Nextline(statement))
    return nextline_holder[0]


async def run_nextline():
    nextline = get_nextline()
    # print(nextline.global_state)
    if nextline.global_state == "initialized":
        nextline.run()
        asyncio.create_task(_wait(nextline))
    return


async def _wait(nextline):
    await nextline.finish()


def reset_nextline(statement=None):
    nextline = get_nextline()
    nextline.reset(statement=statement)


def pop_nextline():
    nextline = get_nextline()
    nextline_holder.clear()
    return nextline


async def close_nextline():
    nextline = pop_nextline()
    await nextline.close()
