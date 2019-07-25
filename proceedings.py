from sqlalchemy.sql.expression import func
from cleantext.helpfunctions import cache_load, cache_save

venue_CHI = 49865  # CHI


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


def get_proceedings(min_year=1981, max_year=2018):
    ''' we need to fetch the data one
        year at a time, otherwise
        mysql will not work (too much data)
    '''

    # data = []
    # for i in range(min_year, max_year + 1):
    #     try:
    #         my_year = cache_load("proceedings_"+str(i))
    #     except:
    #         raw = db.query(Paper).filter(
    #             Paper.venue_id == venue_CHI,
    #             Paper.year == i,
    #             func.length(Paper.clean_text) > 100
    #         ).all()
    #         my_year = [MockPaper(obj) for obj in raw]
    #         cache_save("proceedings_"+str(i), my_year)
    #     data.extend(my_year)


    # replace this with own implementation
    # e.g., retrieve from DB
    o = type('',(object,),{
        'text': "dummy data",
        'id': 0,
        'year': 2016
    })()  # dict -> obj
    data = [o]

    return data
