from os.path import isfile
from sqlite3 import connect

from apscheduler.triggers.cron import CronTrigger

path = "./data/db/database.db"
build_path = "./data/db/build.sql"

con = connect(path, check_same_thread=False)
cursor = con.cursor()


def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner


@with_commit
def build():
    if isfile(build_path):
        scriptexec(build_path)


def commit():
    con.commit()


def autosave(sched):
    sched.add_job(commit, CronTrigger(second=0))


def close():
    con.close()


def field(command, *values):
    cursor.execute(command, tuple(values))

    if (fetch := cursor.fetchone()) is not None:
        return fetch[0]


def record(command, *values):
    cursor.execute(command, tuple(values))

    return cursor.fetchone()


def records(command, *values):
    cursor.execute(command, tuple(values))

    return cursor.fetchall()


def column(command, *values):
    cursor.execute(command, tuple(values))

    return [item[0] for item in cursor.fetchall()]


def execute(command, *values):
    cursor.execute(command, tuple(values))


def multiexec(command, valueset):
    cursor.executemany(command, valueset)


def scriptexec(path):
    with open(path, "r", encoding="utf-8") as script:
        cursor.executescript(script.read())
