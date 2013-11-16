#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""User interface toolkit
"""


def yesno(question):
    "Return true if the answer is 'yes'"
    answer = raw_input(question).lower()
    return answer in ('y', 'yes')


def ask(question, escape=True):
    "Return the answer"
    answer = raw_input(question)
    if escape:
        answer.replace('"', '\\"')
    return answer.decode('utf')
