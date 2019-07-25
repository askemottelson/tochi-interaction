### Python tools for `What Do We Mean by “Interaction”? An Analysis of 35 Years of CHI`

This repo contains the scripts to clean text from CHI papers (from PDF extraction); and to extract modifiers about interaction. The repo does not contain the actual data itself, why you need to implement `get_proceedings` in `proceedings.py`, such that it returns the raw texts from the papers you want to analyze.

Developed for Python 2.7; install required packages using `pip install -r requirements.txt`

### `cleantext/`  
Tools for turning extracted text from CHI PDFs into cleaned strings to perform analysis.
The tools remove ill-formed OCR, lexical optimizations, and remove headers, author info
and other meta data from strings.

See `cleantext/cleantext.py` for how to clean your own extracted CHI PDFs

**Run tests**:  
`python -m cleantext.test`


### `modifiers/`  
Extracting 'interaction' modifiers. Implement `get_proceedings` in `proceedings.py` first.

Run it:  
`python -m modifiers.noun_phrases`


Citation:
```
@article{Hornbaek:2019:WMX:3341168.3325285,
 author = {Hornb{\ae}k, Kasper and Mottelson, Aske and Knibbe, Jarrod and Vogel, Daniel},
 title = {What Do We Mean by \&\#x0201C;Interaction\&\#x0201D;? An Analysis of 35 Years of CHI},
 journal = {ACM Trans. Comput.-Hum. Interact.},
 issue_date = {July 2019},
 volume = {26},
 number = {4},
 month = jul,
 year = {2019},
 issn = {1073-0516},
 pages = {27:1--27:30},
 articleno = {27},
 numpages = {30},
 url = {http://doi.acm.org/10.1145/3325285},
 doi = {10.1145/3325285},
 acmid = {3325285},
 publisher = {ACM},
 address = {New York, NY, USA},
 keywords = {Interaction. history, quality, style},
}
```