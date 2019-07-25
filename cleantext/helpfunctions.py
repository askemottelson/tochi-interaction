# -*- coding: utf-8 -*-

import re
import pickle
import unicodedata
import numpy as np
import glob


def cache_save(key, data):
    with open("pkls/"+key+".pkl", "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def cache_load(key): 
    with open("pkls/"+key+".pkl", "rb") as f:
        return pickle.load(f)

def enc(txt):
    return unicodedata.normalize('NFKD', unicode(txt)).encode('ascii', 'ignore')


def words(text): return re.findall(r'[^\s]+', text.lower())


def toWords(mystr):
    return re.findall(r'[\d\w-]+', mystr)


# doubleMADsfromMedian
def outlier(y, thresh=3.5):
    # warning: this function does not check for NAs
    # nor does it address issues when
    # more than 50% of your data have identical values
    m = np.median(y)
    abs_dev = np.abs(y - m)
    left_mad = np.median(abs_dev[y <= m])
    right_mad = np.median(abs_dev[y >= m])
    y_mad = left_mad * np.ones(len(y))
    y_mad[y > m] = right_mad
    modified_z_score = 0.6745 * abs_dev / y_mad
    modified_z_score[y == m] = 0
    return modified_z_score > thresh


def make_session_regs():
    """
    A session from 2005 - 2011 are structured as follows:
    {optional symbol}CHI {YEAR} {some formatting} {Session name} normal text
    2012, 2013, 2014 are:
    {optional symbol} Session: {Session name} normal text
    2015 is
    {Session name} {CHI 2015, Crossings, Seoul, Korea}
    and is currently being matched in m10 in the remove_misc function.
    2016 is
    {Session name} {#chi4good, CHI 2016, San Jose, CA, USA}
    previously handled in m3 in the remove_misc function.

    This holds true for all articles in the scope that was randomly verified.
    The goal now is to remove these sessions,
    while leaving the "normal text" undisturbed
    :return: Two lists, first a sessions as plain text,
    second accompanying regex for finding said sessions.
    """
    sessions = []
    for file in glob.glob("cleantext/etc/table_of_contents/*.html"):
        # The HTML file for 2013 is a bit different from all the others, in
        # that it preceeds with 'Papers:'
        if "13 - Proceedings.html" in file:
            pattern = r'(?:SESSION: <strong>Papers\: )(.*)(?:</strong></td>)'
        else:
            pattern = '(?:SESSION: <strong>)(.*)(?:</strong></td>)'
        with open(file, 'r', ) as f:
            read = f.read()
            m = re.findall(pattern, read)
            sessions += m
    sessions = map(
        lambda x: x.lower().replace(
            "", ""
        ).replace(
            "&amp;", "&"
        ).replace(
            "&lt;", "<"
        ).replace(
            "&gt;", ">"
        ),
        sessions
    )
    regs = []

    # size does matter, match for longest first.
    sessions.sort(key=len, reverse=True)
    for session in sessions:
        pattern1 = str(r".?CHI\s+\d+.*" + re.escape(session))
        pattern2 = str(r".?Session\:\s+.{0,3}" + re.escape(session))
        pattern3 = str(
            re.escape(session) +
            r"\s*CHI 2015, Crossings, Seoul, Korea")
        pattern4 = str(
            re.escape(session) +
            r"\s*#chi4good, CHI 2016, San Jose, CA, USA")
        r1 = re.compile(pattern1, re.IGNORECASE)
        r2 = re.compile(pattern2, re.IGNORECASE)
        r3 = re.compile(pattern3, re.IGNORECASE)
        r4 = re.compile(pattern4, re.IGNORECASE)
        regs.append((r1, r2, r3, r4))
    return (sessions, regs)
