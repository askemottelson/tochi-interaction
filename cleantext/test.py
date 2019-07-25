import unittest
from cleantext import CleanText, clean_papers
from helpfunctions import make_session_regs
from proceedings import get_proceedings
import numpy as np


class MockPaper():
    text = u""
    clean_text = None
    id = 0
    year = 0

    def __init__(self, y):
        self.year = y


class CleanTextTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.proceedings = get_proceedings(1981, 2016)

        # random subset
        np.random.shuffle(self.proceedings)
        self.proceedings = self.proceedings[0:100]

        # test that the combination runs without errs
        clean_papers(self.proceedings)

    def test_fix_hyphen(self):
        cleaner = CleanText(MockPaper(1981))
        t0 = ("little red riding hood", "little red riding hood")
        t1 = ("a rash of other stories of high-\nprofile account", "a rash of other stories of high-profile account")
        t2 = ("spec-tacular is a rather long word", "spectacular is a rather long word")
        t3 = ("he is origi- nating from", "he is originating from")
        t4 = ("sec- ond", "second")
        t5 = ("faux mirror and swiv- els it until", "faux mirror and swivels it until")
        t6 = ("simu- lated optics workbench", "simulated optics workbench")
        t7 = ("(qualitatively and sta- tistically)", "(qualitatively and statistically)")
        t8 = ("To test this hy- pothesis", "To test this hypothesis")
        t9 = ("impact of ACES on partici- pants' empathy","impact of ACES on participants' empathy")
        t10 = ("In par- ticular, the mean response","In particular, the mean response")
        t11 = ("For ex- ample: `birthday' is replaced", "For example: `birthday' is replaced")
        t12 = ("the quick br-\nown fox jumps over the lazy dog", "the quick brown fox jumps over the lazy dog")

        self.assertEqual(cleaner.fix_hyphen(t0[0]), t0[1])
        self.assertEqual(cleaner.fix_hyphen(t1[0]), t1[1])
        self.assertEqual(cleaner.fix_hyphen(t2[0]), t2[1])
        self.assertEqual(cleaner.fix_hyphen(t3[0]), t3[1])
        self.assertEqual(cleaner.fix_hyphen(t4[0]), t4[1])
        self.assertEqual(cleaner.fix_hyphen(t5[0]), t5[1])
        self.assertEqual(cleaner.fix_hyphen(t6[0]), t6[1])
        self.assertEqual(cleaner.fix_hyphen(t7[0]), t7[1])
        self.assertEqual(cleaner.fix_hyphen(t8[0]), t8[1])
        self.assertEqual(cleaner.fix_hyphen(t9[0]), t9[1])
        self.assertEqual(cleaner.fix_hyphen(t10[0]), t10[1])
        self.assertEqual(cleaner.fix_hyphen(t11[0]), t11[1])
        self.assertEqual(cleaner.fix_hyphen(t12[0]), t12[1])


    def test_remove_header(self):
        cleaner = CleanText(MockPaper(2011))

        # (test_string, will-be-the-same-after-removal)
        t0 = ("Session: Risks and Security CHI 2014, One of a CHInd, Toronto, ON, Canada", False)
        t1 = ("Your nice friend", True)
        t2 = ("By using video recording equipment and an informal, interactive evaluation session, the \"cognitive jogthrough\" procedure revealed significant", True)
        t3 = ("I'm calling the system session: a way to go forward", True)
        t4 = ("Session: Some session CHI 1960, CHI, USA", False)
        t5 = ("Participant P8's TA ranking was 15. Examples of negative comments expressed in the TA session:", True)
        t6 = ("Two researchers were present for each cooking session: one to conduct the session and one to observe", True)
        t7 = ("CHI 2011 ˇ Session: Privacy", False)
        t8 = ("CHI 2011 ˇ Session: 3D Interaction", False)

        self.assertEqual(cleaner.remove_header(t0[0]) == t0[0], t0[1])
        self.assertEqual(cleaner.remove_header(t1[0]) == t1[0], t1[1])
        self.assertEqual(cleaner.remove_header(t2[0]) == t2[0], t2[1])
        self.assertEqual(cleaner.remove_header(t3[0]) == t3[0], t3[1])
        self.assertEqual(cleaner.remove_header(t4[0]) == t4[0], t4[1])
        self.assertEqual(cleaner.remove_header(t5[0]) == t5[0], t5[1])
        self.assertEqual(cleaner.remove_header(t6[0]) == t6[0], t6[1])
        self.assertEqual(cleaner.remove_header(t7[0]) == t7[0], t7[1])
        self.assertEqual(cleaner.remove_header(t8[0]) == t8[0], t8[1])


    def test_references(self):
        # test that the method works for ALL papers
        # will raise exception if it doesnt find the references
        for paper in self.proceedings:
            cleaner = CleanText(paper)
            cleaner.remove_references()

    def test_meta(self):
        mystr = u"Author Keywords\n2D and 3D visualization, display design, empirical study, experiment, orientation and relative position tasks.\nACM Classification Keywords\nH.5.2 User Interfaces - Graphical User Interfaces (GUI), Screen Design, Evaluation/Methodology, I.3.3 Picture/ Image Generation - Display Algorithms, J. Computer Applications (e.g., CAD, Medical Imaging)\nINTRODUCTION"
        
        p = MockPaper(1981)
        p.text = mystr
        c = CleanText(p)
        self.assertEqual( c.remove_meta().strip() , "INTRODUCTION")
        
        mystr2 = u"ould support a variety of advances in human computer\ninteraction and computer-mediated communication.\nAuthor Keywords\nSituationally appropriate interaction, managing human\nattention, sensor-based interfaces, context-aware computing,\nmachine learning.\nACM Classification Keywords\nH5.2. Information interfaces and presentation: User Interfaces;\nH1.2. Models and Principles: User/Machine Systems.\nINTRODUCTION"
        p.text = mystr2
        c = CleanText(p)
        self.assertEqual( c.remove_meta().strip(), "ould support a variety of advances in human computer\ninteraction and computer-mediated communication.\nINTRODUCTION")

        # will raise exception if it doesnt find the meta
        for paper in self.proceedings:
            cleaner = CleanText(paper)
            cleaner.remove_meta()

    def test_stitch_newlines(self):
        cleaner = CleanText(MockPaper(1988))
        t0 = ("the quick brown fox jumps over the lazy dog", "the quick brown fox jumps over the lazy dog")
        t1 = ("the quick\n brown fox jumps over the\n lazy dog", "the quick brown fox jumps over the lazy dog")
        t2 = ("the \nquick \nbrown \nfox \njumps over the lazy dog", "the quick brown fox jumps over the lazy dog")
        t3 = ("\nthe\nquick\nbrown\nfox\njumps\nover\nthe\nlazy\ndog\n", "\nthe quick brown fox jumps over the lazy dog\n")
        t4 = ("the quick brown fox jumps over the\n Lazy dog", "the quick brown fox jumps over the\n Lazy dog")
        t5 = ("the quick brown fox\n\njumps over the lazy dog", "the quick brown fox jumps over the lazy dog")
        t6 = ("the quick,\n brown fox,\n\njumps over the lazy dog", "the quick, brown fox, jumps over the lazy dog")

        self.assertEqual(cleaner.stitch_newlines(t0[0]), t0[1])
        self.assertEqual(cleaner.stitch_newlines(t1[0]), t1[1])
        self.assertEqual(cleaner.stitch_newlines(t2[0]), t2[1])
        self.assertEqual(cleaner.stitch_newlines(t3[0]), t3[1])
        self.assertEqual(cleaner.stitch_newlines(t4[0]), t4[1])
        self.assertEqual(cleaner.stitch_newlines(t5[0]), t5[1])
        self.assertEqual(cleaner.stitch_newlines(t6[0]), t6[1])

    def test_remove_in_text_references(self):
        cleaner = CleanText(MockPaper(1988))
        t0 = ("the quick brown fox[1] jumps over the lazy dog[2, 3]", "the quick brown fox jumps over the lazy dog")
        t1 = ("the quick brown fox[1] jumps over the lazy dog[2,\n 3]", "the quick brown fox jumps over the lazy dog")
        t2 = ("the quick brown fox[which is oh so cute] jumps over the lazy dog", "the quick brown fox[which is oh so cute] jumps over the lazy dog")
        self.assertEqual(cleaner.remove_in_text_references(t0[0]), t0[1])
        self.assertEqual(cleaner.remove_in_text_references(t1[0]), t1[1])
        self.assertEqual(cleaner.remove_in_text_references(t2[0]), t2[1])

    def test_remove_symbols(self):
        cleaner = CleanText(MockPaper(1988))
        t0 = ("`th€e qu{ick br$own ¨fox¤ ~jumps^ over the la}zy dog´", "the quick brown fox jumps over the lazy dog")
        self.assertEqual(cleaner.remove_symbols(t0[0]), t0[1])

    def test_session(self):
        ses, regs = make_session_regs()
        cleaner = CleanText(MockPaper(2005))
        t0 = """Long
CHI 2005  PAPERS: Technology in the Home
boring, but CHI 2005  PAPERS: Technology in the Home somehow interesting
text CHI 2005  PAPERS: Technology in the Home
Even more text after the header
CHI 2005  PAPERS: Technology in the Home hi
""", """Long

boring, but somehow interesting
text
Even more text after the header
 hi
"""
        self.assertEqual(cleaner.remove_sessions(ses=ses, regs=regs, myStr=t0[0]), t0[1])
        cleaner = CleanText(MockPaper(2012))
        t1 = """Long
Session: Teaching with new interfaces
boring, but Session: Teaching with new interfaces somehow interesting
text Session: Teaching with new interfaces
Even more text after the header
Session: Teaching with new interfaces hi
""", """Long

boring, but somehow interesting
text
Even more text after the header
 hi
"""
        self.assertEqual(cleaner.remove_sessions(ses=ses, regs=regs, myStr=t1[0]), t1[1])


    def text_l_listing(self):
        cleaner = CleanText(MockPaper(1988))
        t0 = ("""For code, there is a separate set of problems:
l There has not been much work on interesting displays or ways to show progress.
l Like all the other Visual systems, there is the problem of the size of the pictures. Ways must be found to decide what code to display and how to compress procedures to fit on the screen.
l When code and data are animated together, it is difficult for the user to tell what data is being manipulated by what parts of the code, so some way must be found to show the relationships of variables to the displayed data.
7. Conclusion.""")
        t0_clean = ("""For code, there is a separate set of problems:
There has not been much work on interesting displays or ways to show progress.
Like all the other Visual systems, there is the problem of the size of the pictures. Ways must be found to decide what code to display and how to compress procedures to fit on the screen.
When code and data are animated together, it is difficult for the user to tell what data is being manipulated by what parts of the code, so some way must be found to show the relationships of variables to the displayed data.
7. Conclusion.""")
        self.assertEqual(cleaner.remove_l_listings(t0), t0_clean)

    @classmethod
    def tearDownClass(self):
        pass


if __name__ == '__main__':

    unittest.main()
