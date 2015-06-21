# -*- coding: utf-8 -*-
# pep8: disable-msg=E501
# pylint: disable=C0301

from mml import __version__, log
import argparse
import __builtin__


def main():
    log.info("MML v" + __version__)
