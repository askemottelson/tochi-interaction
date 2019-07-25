#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from dictionary import in_dictionary
from helpfunctions import make_session_regs, enc
from proceedings import get_proceedings

class CleanText(object):

    def __init__(self, paper):
        self.sessions = None

        self.text = paper.text
        self.id = paper.id
        self.year = paper.year

        # html and the like
        self.text = self.simple_fix(self.text)
        self.text = enc(self.text)

    def remove_month_year_lines(self):
        return re.sub(
            r'\n[ \.,]*(JANUARY|JAN|FEBRUARY|FEB|MARCH|MAR|APRIL|APR|MAY|JUNE|JUN|JULY|JUL|AUGUST|AUG|SEPTEMBER|SEPT?|OCTOBER|OCT|NOVEMBER|NOV|DECEMBER|DEC)[ \.,]+[0-9]{2,4}[ \.,]*\n',
            '',
            self.text)

    def remove_math_and_punctuation_lines(self):
        return re.sub(r'\n([=0-9\., +\-*/!()]+)\n', '', self.text)

    def remove_meta(self):
        res = self.text

        k1 = re.compile(r"(KEYWORDS|Keywords):.*\n?", re.IGNORECASE)
        k2 = re.compile(r"(KEYWORDS|Keywords)\n.*", re.IGNORECASE)
        k3 = re.compile(r"Author Keywords.*\n.*?([\s\S]{0,500}\n\n)?")
        k4 = re.compile(r"\nGeneral Terms(\n(.{0,20},)*.{0,20})")
        k5 = re.compile(r"(\nKeywords\s.{0,250}\n|ACM (Classification )?Keywords\s(.{0,250}))\s(\[.*\]\: .*\n|Miscellaneous\.[^\:])?")
        k6 = re.compile(r"ACM\s+Classi(fi|.)cation Keywords(\sH[\.\d].*)*")
        k7 = re.compile(r"Author\s+ACM\s+Classification\s+")
        k8 = re.compile(r"ACM Classification:?.*\s?(H.*)?")
        k9 = re.compile(r"Permission to (copy|make).*")
        k10 = re.compile(r"http://dx.doi.org/.*")
        k11 = re.compile(r"This work is licensed under a Creative Commons Attribution International \d+\.\d+\sLicense\.", re.IGNORECASE)

        for k in [k7, k6, k5, k4, k3, k2, k1, k8, k9, k10, k11]:
            res = k.sub("", res)

        if "KEYWORDS:" in res or "Author Keywords" in res or "ACM Classification" in res:
            print res
           # raise Exception("has keywords!" + str(self.id))

        return res

    def remove_until_abstract(self):
        if self.id in [80015048]:
            return self.text
        res = self.text

        pattern = re.compile(r"^(?:.*?)(ABSTRACT|Abst(r|t)act)\:?", re.DOTALL)

        res = pattern.sub(r"\1\n", res)
        return res

    def remove_references(self):
        res = self.text

        # remove appendices
        res = re.compile(r"\sAPPENDIX\s.*$", flags=re.DOTALL).sub("", res)

        # REFERENCES (See:
        # http://stackoverflow.com/questions/5616822/python-regex-find-all-overlapping-matches)
        pattern = re.compile(r"(?=([^P]R\s?E\s?F\s?E\s?R\s?E\s?N\s?C\s?E[^,]\s?S?.*$))",
            flags=re.DOTALL | re.IGNORECASE)

        matches = re.findall(pattern, res)
        count = sum(1 for m in matches)
        if count > 1:
            if(isinstance(matches[-1], tuple)):
                res = res.replace(str(matches[-1])[0], "")
            else:
                res = res.replace(str(matches[-1]), "")
            return res

        # If using Look-Ahead provided no matches, try with normal expression.
        pattern = re.compile(r"([^P]R\s?E\s?F\s?E\s?R\s?E\s?N\s?C\s?E[^,]\s?S?.*$)",
            flags=re.DOTALL | re.IGNORECASE)
        matches = re.findall(pattern, res)

        res = pattern.sub("", res)
        return res

    # I added an offset counter to this function, as "fixing" a hyphen, will cause all of the next
    # iterations to be off. This was the same reason I had a while loop in my code, as I chose to
    # re-search after each text edit, as I could guarantee correct placement
    # of new hits.
    def fix_hyphen(self, myStr=None):
        if myStr is None:
            myStr = self.text

        offset = 0
        res = myStr
        pattern = re.compile(r'-', re.DOTALL)
        for search in re.finditer(pattern, res):
            span = search.span()
            before = res[:span[0] - offset]
            fix = res[span[0]:span[1]]
            after = res[-offset + span[1]:]
            try:
                p1 = before.split()[-1]
            except BaseException:
                continue
            try:
                p2 = after.split()[0]
            except BaseException:
                continue
            if p1.isdigit() and p2.isdigit():
                # numbers shouldn't have their hyphen removed, it could be
                # math, it could be interval etc.
                pass
            elif in_dictionary(p1 + p2):
                # fix weird hyphenation, e.g., "affor-dance"
                fix = ""
                # fix 'sec- ond' -> 'second'
                if len(after) > 0:
                    if after[0].isspace():
                        after = after[1:]
                        offset += 2
                    # fix 'sec -ond' -> 'second'
                    elif before[-1].isspace():
                        before = before[:-1]
                        offset += 2
                    else:
                        offset += 1
            elif in_dictionary(p1) and in_dictionary(p2):
                # fix 'high- profile' -> 'high-profile'
                fix = "-"
                if len(after) > 0:
                    if after[0].isspace():
                        after = after[1:]
                        offset += 1
                        if after[0:4] == "and ":
                            fix = "- "
                            offset -= 1
            else:
                # keep it
                fix = "-"
                pass
            res = before + fix + after
        return res

    def remove_header(self, myStr=None):
        if myStr is None:
            myStr = self.text
        res = myStr

        p1 = re.compile(r"CH(I|1|l|r)(\s|')+\d\d+.*Proceed.*")
        p2 = re.compile(r"C\s?H\s?(I|1|l|r).*PROCEED.*(\n\nApril \d+)?")
        p3 = re.compile(r"CH(I|1|l|r)\s?'?\d+\s(\Proceed.*\d+\s?)?")
        p4 = re.compile(r"CH(I|1|l|r)'?\s?\d+,\s.*")
        p5 = re.compile(r"\d \d PROCEED N G S")

        patterns = [p1, p2, p3, p4, p5]

        # sessions were introduced in 2011 (Sorta, also in 2005+)
        if self.year >= 2011:
            patterns.append(re.compile(r"Session:.{0,100}(\.|\s)"))
            patterns.append(re.compile(r"CHI \d+\s+Session\:.*"))
        for pattern in patterns:
            res = pattern.sub("", res)

        if "PROCEEDINGS" in res or "SESSION:" in res or "Session:" in res:
            if self.id not in [
                    80886200,
                    80031347]:  # the capital word PROCEEDINGS is used to describe the subject
                # also, Section called Practive-Session: was wrongfully flagged
                print res
               # raise Exception("header " + str(self.id))

        return res

    def remove_misc(self):
        res = self.text

        m1 = re.compile(r"\n?\W?CH(I|i|l|1)(’?\d+ ?([p|P]roceedings|PROCEEDINGS) (April|May|MAY) ?\d+| \+ GI \d+| \d+ Proceedings (·|•) [\w+|\W]{0,100} \d+ (·|•) (Florence, Italy|San Jose, CA, USA)\n?| \d+ ‫׀‬ PAPERS: [\w| ]+ \d+–\d+ \W+ Portland, Oregon, USA\n?)")
        m2 = re.compile(r"()?C\s?H\s?(I|1|l)\s?'?\s?\d+\s?(P|p)\s?(R|r)\s?(O|o|0)\s?(C|c)\s?(E|e)\s?(E|e)\s?(D|d)\s?(I|i|l)\s?(N|n)\s?(G|g)\s?(S|s)(\s(MAY|May|April|APRIL)\s\d+\n?| D\s?e\s?cem\s?b\s?e\s?r\s?\d+)\n?")
        m2 = re.compile(r"()?(PAPERS )?(Cl-II|CH(I|1|l|)) \d+( l|\.| \.)? \d+-\d+ (MAY|APR(I|l)L) ?\d+( PAPERS)?")
        m3 = re.compile(r".*#chi4good, CHI \d+, San Jose, CA, USA(\s\d+\n)?")
        m4 = re.compile(r"CHI\d+ Proceedings( April| May)?\d*\n?")
        m5 = re.compile(r"(CHI \d+ Proceedings (•|\||·).*(•|\||·) (Montréal, Québec, Canada|)\n??)")
        m6 = re.compile(r"\sC(l-I|h)(I|i|l|1)('|’)\d+ Proceedings (April|May) \d+\s")
        m7 = re.compile(r"CHI \d+ Proceedings (·) .* (·) (\w+, \w+)\s?([0-9]+\n)")
        m8 = re.compile(r"CHI \d+ Proceedings\s·.*·\s\w+, \w+\s")
        m9 = re.compile(r"\nCHI \d+ • .*\d(–|-)\d+, \d+ • Vancouver, BC, Canada\.?\n")
        m10 = re.compile(r"\n.*CHI 2015, Crossings, Seoul, Korea")
        m11 = re.compile(r".?CHI(90 i’ncedim Aplil|90 proceedings Aplil|90 l’mceedngs Aplil1!390|90 Prweedngs Ppil1!390|90 Prcca\?dngs April 1990|‘90l’aeedim April1990)\n?")
        m12 = re.compile(r"Permission to (make digital or hard copies of |copy without fee )all or part of this (material |work for personal or classroom use )is granted( without fee)? provided that (the )?copies are not made or distributed for (direct commercial advantage, the ACM copyright notice and the title of the publication and (i|I)ts date appear, and notice (i|I)s given that copying is by permission of the Association for Computing Machinery. To copy otherwise, or to republish, requires a fee and\/or specific permission.|profit or commercial advantage and that copies bear this notice and the full citation on the first page.\s?(Copyrights for components of this work owned by others than ACM must be honored. Abstracting with credit is permitted. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee. Request permissions from Permissions@acm.org.|To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee.))(\n+CHI \d+, (April) \d+(–| - )(May)?\s?\d*,?\s?\d+,?\s?(Paris, France.|Toronto, ON, Canada|Florence, Italy)?|\n© \d+ ACM \d+-\d+-\d+-\d+\/\d+\/\d+-\d+ \d+\.\d+)?(\nCopyright \d+ ACM \d+-\d+-\d+-\d+-\d+\/\d+\/\d+(\.)*\$\d+\.\d+\.)?(\nhttp:\/\/dx.doi.org\/\d+\.\d+\/\d+\.\d+)?(\n©\d+\sACM-\d+-\d+-\d+-\d+\/\d+\/\d+\/\d+\s\$\d+\.\d+\s+\n?)")
        m13 = re.compile(r"Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\sCHI \d+, (May|April) \d+-\d+, \d+, (Montréal, Québec, Canada|Minneapolis, Minnesota, USA.)\.\sCopyright \d+ ACM \d+-\d+-\d+-\d+\/\d+\/\d+\.\.\.\$\d+\.\d+\.\s?")
        m14 = re.compile(r"(Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\s)?(\n?CHI \d+, (May|April) \d+(-|–))(May|April)?\s?\d+,\s?\d+, (San Jose, California, USA.\n?|Florence, Italy\.\n|Minneapolis, Minnesota, USA.\n?)?(Copyright \d+ ACM \d+-\d+-\d+-\d+(-\d+)?\/\d+\/\d+(\.*|…)\$\d+\.\d+\.\s?)?")
        m15 = re.compile(r"(Permission to copy without fee all or part of this material is granted provided that the copies are not made or distributed for direct commercial advantage, the ACM copyright notice and the title of the publication and its date appear, and notice is given that copying is by permission of the Association for Computing Machinery\. To copy otherwise, or to republish, requires a fee and\/or specific permission\.\s*){e<=1}(. \d+ ACM \d+-\d+-\d+\/\d+\/\d+\/\d+ \$\d+\.\d+\s)?(.?\d+ A\s?C\s?M\s?\d+(-\d+|\/\d+)+\s?\$\d+\.\d+)?", re.IGNORECASE)
        m16 = re.compile(r"(Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\s?)?(CHI \d+, (April|May) \d+(-\d+)?, \d+, (Florence, Italy)\.)?(\s?Copyright \d+ ACM \d+-\d+-\d+-\d+-\d+\/\d+\/\d+\.\.\.\$\d+\.\d+\.\s)?(CHI \d+ Proceedings .+ April \d+-\d+, \d+\s+(Florence, Italy)\s?)")
        m17 = re.compile(r"Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. Copyrights for components of this work owned by others than the author\(s\) must be honored. Abstracting with credit is permitted\. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\. Request permissions from permissions\@acm\.org\.(Toronto, Ontario, Canada\.)?\s(Copyright is held by the owner\/author\(s\)\. Publication rights licensed to ACM\.\sACM \d+-\d+-\d+-\d+-\d\/\d+\/\d+\.\.\.\$\d+\.\d+\. (http\:\/\/dx.doi.org\/\d+\.\d+\/\d+\.\d+\s)?(Session\: .*, One of a CHInd, Toronto, ON, Canada\s)?)")
        m18 = re.compile(r"Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. Copyrights for components of this work owned by others than\sACM must be honored\. Abstracting with credit is permitted\. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\. Request permissions from permissions\@acm\.org\.\s(CHI(´|’)\s?\d+, April \d+(-|–)May \d, \d+, Toronto, Canada\.\s)?(Copyright c\s?)?\s?(\s\d+ ACM ISBN\/\d+\/\d+\.\.\.\$\d+\.\d+\.\s)")
        m19 = re.compile(r"^(\w|\W)$", re.MULTILINE)
        m20 = re.compile(r"^([\“\&\/\\\;\~\.\,\_\−\-\—\w\=\(\)]{1,3}|[\“\&\/\\\;\~\.\,\_\−\-\—\w\=\(\)]{1,3}(\s[\“\&\/\\\;\~\.\,\_\−\-\—\w\=\(\)]{0,4})*)$", re.MULTILINE)
        m21 = re.compile(r"C\s?H\s?I\s?'\s?\d+\s?\d?\s?P\s?R\s?O\s?C\s?E\s?E\s?D\s?I\s?N\s?G\s?S\s?(APRIL|MAY)\s?\d+")
        m22 = re.compile(r"Permission to copy without fee all or p(a|e)rt of this material is granted provided that the copies .*\s?(Machinery)?\.\sTo copy otherwise, or to republish, requires a fee and\/or specific (parmiesion|permission)\.\s?")
        m23 = re.compile(r"(Permission to copy without (lee )?all or part of this material is granted provided that the copies are not made or distributed for direct commercial advantage, the\s?ACM copyright notice and the title of the publication and its date appear, and notice is given that copying is by permission of the Association for\s*Computing\s*Machinery\. To copy otherwise, or to republish requires a fee and\/or\s+specific permission\.\s?)?((0|.) \d+ ACM (O|\d)-\d+\s?-\d+-(O|\d)\/\d+\/\d+-\d+\s\d\.\d+\s)+")
        m24 = re.compile(r"(CHI\d+, April \d+\s+May \d+ \d+, Toronto, ON, Canada)|(Copyright is held by the owner\/author\(s\)\. Publication rights licensed to ACM\.\s|ACM \d+-\d+-\d+-\d+-\d+\/\d+\/\d+.\$\d+\.\d+\.( http\:\/\/dx\.doi\.org\/\d+\.\d+\/\d+\.\d+\s)?|Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\.\sCopyrights for components of this work owned by others than the author\(s\) must be honored\.\sAbstracting with credit is permitted\.\sTo copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee.\sRequest permissions from Permissions.acm\.org\.\s)")
        m25 = re.compile(r"(Permission to cop(y|v) without fee all or part of this material is granted provided that the copie(e|s) are not made or distributed for direct commercial advantage, the ACM copyright notice and the title of the publication and its date appear, and notice is given that copying is by permission of the\sAssociation for\sComputing(\sMachinery\.?\s?)?|To copy otherwise, or to republish, requires a fee and\/or (s|e)pecific permission\.\s?|.?\d+ ACM \d+-\d+-\d+-\d\/\d+\s+\d+\.\.\.\$\d+\.\d+\s)")
        m26 = re.compile(r"(Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\.\sTo copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\s|CHI\s+\d+, April \d+-\d+\s?,\s?\d+, Florence, Italy\.\s?(Copyright \d+)?)")
        m27 = re.compile(r"(\nPortland, Oregon, USA\.\n|Copyright \d+ ACM \d-\d+-\d+-\d+\/\d+\/\d+\.\.\.\$\d+\.\d+\.\n?)")
        m28 = re.compile(r"(CHI \d+, April \d+\s?-\s?May \d+ \d*, Toronto, ON, Canada\s|Copyright \d+ ACM \d+-\d+-\d+-\d+-\d+\/\d+\/\d+\.*\$\d+\.\d+\.(\shttp\:\/\/dx.doi.org\/\d+\.\d+\/\d+\.\d+\n?)?|Session: .+CHI \d+, One of a CHInd, Toronto, ON, Canada\.?)")
        m29 = re.compile(r"(Copyright \d+ ACM \d+-\d+-\d+-\d+-\d+\/\d+\/\d+\.*\$\d+\.\d+\.(\shttp\:\/\/dx.doi.org\/\d+\.\d+\/\d+\.\d+\n?)?)")
        m30 = re.compile(r"(Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\.\sCopyrights for components of this work owned by others than\sACM must be honored\.\sAbstracting with credit is permitted\.\sTo copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\sRequest permissions from (p|P)ermissions.acm\.org\.\n?|CHI \d+, April \d+ - May \d+, \d+, Toronto, ON, Canada\n?)")
        m31 = re.compile(r"\s?Copyright is held by the owner\/author\(s\)\.\s*Publication rights licensed to\s*ACM\.?")
        m32 = re.compile(r"Permission to make digital or hard copies of part or all of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\.\sCopyrights for thirdparty components of this work must be honored\.\sFor all other uses, contact the (O|o)wner\/(A|a)uthor\.\s?(Copyright is held by the owner\/author\(s\)\.\s?)")
        m33 = re.compile(r"Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\.\sCopyrights for components of this work owned by others than the authors must be honored\.\sAbstracting with credit is permitted\.\sTo copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\sRequest permissions from permissions.acm\.org\.\s*")
        m34 = re.compile(r"Papers\s*CHI\s*\d*.+5 APRIL")
        m35 = re.compile(r"Volume No\. \d, Issue No\. \d CHI \d+\s?|CHI \d+\s*\d+ MARCH\s*\d+ APRIL Papers(\sanyone\. anywhere\.)")
        m36 = re.compile(r"\s?SIGCHI.*, March.*Seattle, WA, USA\.\s?")
        m37 = re.compile(r"Copyright \d+ ACM \d+-\d+-\d+-\d+\/\d+\/\d+\.*\$\d+\.\d+\.\s?")
        m38 = re.compile(r"CHI 2001.*Papers anyone. anywhere.")
        m39 = re.compile(r"\s?minneapolis, minnesota, usa.+Paper:.+")
        m40 = re.compile(r"Volume No\. \d, Issue No\. \d?")
        m41 = re.compile(r"Paper\:.+CHI changing the world, changing ourselves\n")
        m42 = re.compile(r"\s?Copyright \d+ ACM \d+(-\d+)+(\/\d+).*\$\d+\.\d+\.\s?")
        m43 = re.compile(r"ACM\s+Classi(fi|.)cation Keywords(\sH\.\d+\.\d+.*)*")
        m44 = re.compile(r"Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for pro(fi|.)t or commercial advantage and that copies bear this notice and the full citation on the (fi|.)rst page\.\sCopyrights for components of this work owned by others than\sACM must be honored\.\sAbstracting with credit is permitted\.\sTo copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior speci(fi|.)c permission and\/or a fee\.\sRequest permissions from permissions.acm\.org\.")
        m45 = re.compile(r"CHI\s?....,\sApril\s.*, (Republic of )?Korea\.?(\sCopyright \d+ .)?")
        m46 = re.compile(r"\s+\d+ ACM ISBN(\/\d+)+\.+\$\d+\.\d+\.(\nDOI string from ACM form con(fi|.)rmation)?")
        m47 = re.compile(r"Copyright\s\d+\W+\s+ACM \d+(\d+-)+\d+(\/\d+)+\.+\$\d+\.\d+\.\s+http\:\/\/dx\.doi\.org\/\d+\.\d+\/\d+\.?")
        m48 = re.compile(r"Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for pro(fi|.)t or commercial advantage and that copies bear this notice and the full citation on the (fi|.)rst page\.\sCopyrights for components of this work owned by others than ACM must be honored\.\sAbstracting with credit is permitted\.\sTo copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior speci(fi|.)c permission and\/or a fee\. Request permissions from\s(P|p)ermissions.acm\.org\.")
        m49 = re.compile(r"\nGeneral Terms(\n(.{0,20},)*.{0,20})")
        m50 = re.compile(r"CHI\s*\d+,\s*April\s*\d+\s*-\s*\d+\s*\d+, \w+, (\w+\s*){0,3}")
        m51 = re.compile(r"Copyright \d+ ACM .*http:\/\/dx\.doi\.org\/\d+\.\d+\/\d+.?")
        m52 = re.compile(r"Permission to make digital or hard copies of part or all of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\.\sCopyrights for third.party components of this work must be honored\.\sFor all other uses, contact the (O|o)wner\/(A|a)uthor\.\sCopyright is held by the owner\/author\(s\)\.")
        m53 = re.compile(r"CHI \d+, Apr \d+-\d+, \d+, \w+,(\s\w+)+\n")
        m54 = re.compile(r"ACM \d+(-\d+)+(\/\d+)+\.\s+http\:\/\/dx\.doi\.org\/\d+\.\d+\/\d+\d.?")
        m55 = re.compile(r"Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\.\sCopyrights for components of this work owned by others than the author\(s\) must be honored\.\sAbstracting with credit is permitted\.\sTo copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\sRequest permissions from permissions.acm\.org\.")
        m56 = re.compile(r"CHI\d+, (May|April) \d+, \d+, \w+\s\w+, \w+, \w+\n")
        m57 = re.compile(r"ACM \d+(-\d+)*(\/\d+)*\.*\$\d+\.\d+\n?")
        m58 = re.compile(r"Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\.\sCopyrights\s?for components of this work owned by others than ACM must be honored.\sAbstracting with credit is permitted\. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\sRequest permissions from\s?(P|p)ermissions.acm\.org\.\n")
        m59 = re.compile(r"CHI'\d+, \w+ \d+\s?-\s?\d+, \d+, \w+(\s\w+)?, \w+(, \w+)?\n?")
        m60 = re.compile(r"(Copyright)?\s*\d*\s*ACM\.?\s*ISBN\/?\s*\d+(-\d+)*(\/\d+)*(\s|\.)*\$?\d+\.\d+\s*\.?")
        m61 = re.compile(r"Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page\.\sCopyrights for components of this work owned by others than the author\(s\) must be honored\.\sAbstracting with credit is permitted\.\sTo copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\sRequest permissions from permissions.acm\.org\.")
        m62 = re.compile(r"CHI \d+, May \d+(-\d+)?, \d+, \w+(\s\w+), \w+(, \w+).?\n?")
        m63 = re.compile(r"\s*\d*\s*ACM.? ISBN \d+((-|-\s|\s-)\d+)*(\/\d+)*\s*\.*\??\$?\d+\.\d+\d\.?\s*")
        m64 = re.compile(r"CHI\d+,\s*May\s*\d+-\d+,\s*\d+,\s\w+(\s\w+)?,\s\w+(,\s*\w+)?\s*")
        m65 = re.compile(r"CHI\d+,\s*May\s*\d+\s*May\s*\d+,\s*\d+,\s*\w+(\s*\w+)?,\s*\w+(,\s*\w+)?\.?")
        m66 = re.compile(r"\s*CHI\d+,\s*May\s*\d+\s*-\s*\d+,\s*\d+,\s*\w+(\s*\w+)?,\s*\w+,\s*\w+\s*")
        m67 = re.compile(r"\d+\s*ACM\.\s*ISBN\s*\d+(-\d+|\s*)*(\/\d+|\s*)*(\s*|\.)*\$\s*\d+\.\d+\s*")
        m68 = re.compile(r"CHI\d+,\s*May\s*\d+-\d+,\s*\d+,\s*\w+\s*\w+,\s*\w*,\s*USA")
        m69 = re.compile(r"\nDOI\: \d+\.\d+\/\d+\.\d+\n")
        m70 = re.compile(r"(.?CHI'\s*\d+S?\s*MOSAIC\s*OF\s*CREATIVITY\s*May\s*\d+-\d+\s*\d+\s*Design\s*Briefings){e<=3}", re.IGNORECASE)
        m71 = re.compile(r"(Design\s*Briefings\s*May\s*\d+\s*-\s*\d+\s*\d+\s*CHI'\s*\d+S?\s*MOSAIC\s*OF\s*CREATIVITY){e<=3}", re.IGNORECASE)
        m72 = re.compile(r"\n(Permission to copy without fee all or part of this material is granted provided that the copies are not made or distributed for direct commercial advantage.? the ACM copyright notice and the title of the publication and its date appear.? and notice is given that copying is by permission of ACM.?\s*To copy otherwise.? or to republish, requires a fee and.?or specific permission.?\s*CHI.? \d+S?, \w+, \w+, USA){e<=3}", re.IGNORECASE)
        m73 = re.compile(r"(\n\W?(papers)?\s*CH(I)?\s*\d+\s*.?\s*\d+-\d+\s*(tvl)?\s*\w+\s*\d+\s*(Papers)?){e<=3}", re.IGNORECASE)
        # m74 = re.compile(r"(Keywords\n((\w+\s?)+,\s?)+){e<=3}", re.IGNORECASE)
        m79 = re.compile(r"\nCHI\d+, May \d+, \d+,( \w+,)+ \w+\.\n", re.IGNORECASE)
        m80 = re.compile(r"\d+ Association for Computing Machinery\.\s+ACM acknowledges that this contribution was authored or co-authored by an employee, contractor or affiliate of the\s?United States government\. As such, the United States Government retains a nonexclu-?sive, royalty-free right to publish or reproduce this article, or to allow others to do so, for Government purposes only\.\s+CHI\d+, \w+ \d+, \d+, \w+( \w+)?(, \w+)+", re.IGNORECASE)
        m81 = re.compile(r"(Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full cita-?tion on the first page\.\s+Copyrights for com-?ponents of this work owned by others than(\s?ACM| the author\(s\)) must be honored\.\s?Abstracting with credit is permitted\.\s?To copy otherwise, or re-?publish, to post on servers or to redistribute to lists, requires prior specific permission and\/or a fee\.\s?Request permissions from\sPermissions.ac.\.org\.\s?(CHI\d+, \w+ \d+, \d+, \w+( \w+)?, \w+, USA)?){e<=3}", re.IGNORECASE)
        m82 = re.compile(r"CHI 2013: Changing.*, France", re.IGNORECASE)
        m83 = re.compile(r"\nCHI \d+, May .*, 2011, Vancouver, BC, Canada\.?", re.IGNORECASE)
        m84 = re.compile(r"\nCHI \d+, One of a CHInd, Toronto, ON, Canada", re.IGNORECASE)
        m85 = re.compile(r"((CHI \d+)?(, May \d+, \d+, |, May \d+.\d+, \d+, )?Austin, Texas, USA|Austin, TX, USA\.?)", re.IGNORECASE)
        m86 = re.compile(r".?CH(1|i|l)'\d+.*\n", re.IGNORECASE)
        m87 = re.compile(r"Copyright is held.*")
        m88 = re.compile(r"..ACM.\d\d\d\-.*")
        m89 = re.compile(r"classroom use is granted.*honored\.", flags=re.DOTALL)
        m90 = re.compile(r"May \d+(.\d+)?, \d+\s+Vancouver, BC, Canada", re.IGNORECASE)
        m91 = re.compile(r"\nGeneral Terms.*")
        m92 = re.compile(r"\nHuman Factors\n")
        m93 = re.compile(r"H5\.2\..*")
        m94 = re.compile(r".*@.*\.edu.*")
        m95 = re.compile(r".*@.*\.com.*")
        m96 = re.compile(r".*CHI\s?" + str(self.year) + ",.*")
        m97 = re.compile(r".*CHI\s?" + str(self.year)[2:4] + ",.*")
        m98 = re.compile(r".*C H I.*" +
                         " ".join(list(str(self.year)[2:4])) +
                         " PROCEEDINGS.*")

        m99 = re.compile(r".*Boston.*\d+-\d+, \d+")
        # Very specific, but very common unmatched occurence this year
        m100 = re.compile(r"April \d+-May 3, 2007 -? San Jose, CA, USA")
        m101 = re.compile(r".*APRIL 13-18, 1996 CHI 96.*")
        m102 = re.compile(r"\n.(DESIGN BRIEFINGS CH(1|I|l) \d+ . \d+-\d+ MARCH 1997)|(.CH(1|I|l)\s?\d+ . \d+-\d+ MARCH \d+ DESIGN BRIEFINGS)")  # 1997

        m103 = re.compile(r"\n(.+)?1987.+ACM.+00\.75", re.MULTILINE)  # 1987
        m104 = re.compile(r"\nCHI\+ GI 1987\s?\n")
        misces = [m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, m13, m14,
                  m15, m16, m17, m18, m19, m20, m21, m22, m23, m24, m25, m26, m27, m28,
                  m29, m30, m31, m32, m33, m34, m35, m36, m37, m38, m39, m40, m41, m42,
                  m43, m44, m45, m46, m47, m48, m49, m50, m51, m52, m53, m54, m55, m56,
                  m57, m58, m59, m60, m61, m62, m63, m64, m65, m66, m67, m68, m69, m70,
                  m71, m72, m73, m79, m80, m81, m82, m83, m84, m85, m86, m87, m88, m89,
                  m90, m91, m92, m93, m94, m95, m96, m97, m98, m99, m100, m101, m102,
                  m103, m104]

        for m in misces:
            res = m.sub("", res)

        return res

    def simple_fix(self, myStr):
        return myStr.replace(
            "",
            "").replace(
            "&amp;",
            "&").replace(
            "&lt;",
            "<").replace(
                "&gt;",
            ">")

    # Do we still need to "repair" broken lines?
    # sure but this one doesn't work :)
    def stitch_newlines(self, myStr=None):
        if myStr is None:
            myStr = self.text

        res = myStr

        broken_lines = re.compile(r"(?P<before_newline>[a-z]+,?)(?: ?\n+ ?)(?P<after_newline>[a-z])")
        res = broken_lines.sub(r"\g<before_newline> \g<after_newline>", res)
        return res

    def remove_in_text_references(self, myStr=None):
        if myStr is None:
            myStr = self.text

        res = myStr

        references = re.compile(r"\s?\[[\d |, | \n | i | l ]+\]")
        res = references.sub("", res)
        return res

    def remove_symbols(self, myStr=None):
        if myStr is None:
            myStr = self.text

        res = myStr
        res = res.translate(None, "{}$¤€`´¨^~•")
        return res

    def remove_sessions(self, ses, regs, myStr=None):
        if myStr is None:
            myStr = self.text
        res = myStr
        """
        There are a few ways the Header may look, hence there's four
        different regexes to choose from
        """
        for s, r in zip(ses, regs):
            if self.year in [2005, 2006, 2007, 2008, 2009, 2010, 2011]:
                r = r[0]
            elif self.year in [2012, 2013, 2014]:
                r = r[1]
            elif self.year == 2015:
                r = r[2]
            elif self.year == 2016:
                r = r[3]
            else:
                continue
            if res.lower().count(s.lower()) >= 4:
                res = r.sub("", res)
        return res

    def fix_ofthe(self, myStr=None):
        if myStr is None:
            myStr = self.text
        return myStr.replace(" ofthe ", " of the ")

    # removes all l's starting a line, these are often used when listing items
    def remove_l_listings(self, myStr=None):
        if myStr is None:
            myStr = self.text

        l_listings = re.compile(r"(\n)(l\s)")
        return l_listings.sub(r"\1", myStr)

def clean_papers(proceedings):
    ses, regs = make_session_regs()

    cleaned = []

    for paper in proceedings:
        cleaner = CleanText(paper)
        cleaner.text = cleaner.remove_symbols()
        cleaner.text = cleaner.remove_references()
        cleaner.text = cleaner.remove_until_abstract()
        cleaner.text = cleaner.remove_l_listings()
        cleaner.text = cleaner.stitch_newlines()
        cleaner.text = cleaner.remove_sessions(ses=ses, regs=regs)
        cleaner.text = cleaner.remove_meta()
        cleaner.text = cleaner.remove_misc()
        cleaner.text = cleaner.remove_header()
        cleaner.text = cleaner.remove_in_text_references()
        cleaner.text = cleaner.stitch_newlines()
        cleaner.text = cleaner.fix_hyphen()
        cleaner.text = cleaner.fix_ofthe()
        cleaner.text = cleaner.remove_month_year_lines()
        cleaner.text = cleaner.remove_math_and_punctuation_lines()

        cleaned.append(cleaner.text)

    return cleaned


if __name__ == "__main__":

    proceedings = get_proceedings()
    res = clean_papers(proceedings)
