from sqlalchemy.sql.expression import func
from cleantext.helpfunctions import cache_load, cache_save


class MockPaper():
    def __init__(self, obj):
        self.id = obj.id
        self.title = obj.title
        self.DOI = obj.DOI
        self.text = obj.text
        self.clean_text = obj.clean_text
        self.year = obj.year

        self.authors = [MockPaperAuthor(o) for o in obj.paper_authors]


class MockPaperAuthor():
    def __init__(self, obj):
        self.id = obj.id
        self.rank = obj.rank

        if obj.author:
            self.name = obj.author.name
            self.affiliation = obj.author.affiliation
        else:
            self.name = None
            self.affiliation = None

'''
    This method should return a list
    of Paper objects representing the papers in the
    proceedings you wish to analyze.
    The paper class definition can be seen in MockPaper
'''
def get_proceedings(min_year=1981, max_year=2018):
    # example implementation
    # of fetching CHI paper texts from MySQL
    # and caching in a pkl format
    # data = []
    # for i in range(min_year, max_year + 1):
    #     # we need to fetch the data one
    #     # year at a time, otherwise
    #     # mysql will not work
    #     try:
    #         my_year = cache_load("proceedings_"+str(i))
    #     except Exception:
    #         raw = db.query(Paper).filter(
    #             Paper.venue_id == 49865,  # CHI
    #             Paper.year == i,
    #             func.length(Paper.clean_text) > 100
    #         ).all()
    #         my_year = [MockPaper(obj) for obj in raw]
    #         cache_save("proceedings_"+str(i), my_year)
    #     data.extend(my_year)

    DUMMY implementation
    o = type('',(object,),{
        'title': 'dummy paper',
        'text': 'dummy text',
        'clean_text': 'dummy text data',
        'id': 0,
        'DOI': 'X',
        'year': 2016
    })()  # dict -> obj
    data = [o]
    raise Exception("Please implement get_proceedings!")

    return data
