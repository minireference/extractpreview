extractpreview
==============
A script to extract subset from a book to create a book prevew document (usually a sample chapter).


BRS
---
Given an source PDF (usually a 200-700 pages textbook), our goal is to extract a
subset of the PDF's pages to offer to readers as a free preview.

The specification about which pages to include in the preview can be specified
using command line arguments or in a file called `previewspec.json` and supports
the following types of include directives:
  - `pagerange`: a directive that includes start and stop directives, of the form:
    - `pagenumber`: 1-based page number
    - `pagecontains`: a unique substring to search for in the text content of the page 
  - `chapter`: parse the PDF's TOC to identify the top-level headings (chapters),
     and select from them based on `chapternumber` or `titlecontains`, then find
     the page range that covers all the pages associated with that chapter.
  - `section`: same as the `chapter` but based on the level 2 headings in TOC,
     and using `chapternumber` and `sectionnumber`, or `titlecontains`.


Install
-------
```python
virtualenv -p python3  venv
source venv/bin/activate
pip install -r requirements.txt
```

Usage
-----
To extract pages 1 through 4 and 7 though 10, run
```
./extractpreview.py --pagerange "1-4" --pagerange "7-10"  noBSmath.pdf  noBSmath_preview.pdf
```

Or to use a JSON preview spec file use
```
./extractpreview.py --spec previewspec.json   noBSmath.pdf  noBSmath_preview.pdf
```



Preview spec JSON schema
------------------------

```JSON
{
  "directives": [
      {
        "action: "include",
        "kind": "pagerange",
        "start": {"pagenumber":1},
        "end": {"pagenumber":4},
      },
      {
        "action: "include",
        "kind": "pagerange",
        "start": {"pagenumber":7},
        "end": {"pagenumber":10},
      }
  ]
}
```



Notes
-----
This is WIP

### POC
 - implement CLI args
 - basic pagerange directives in json spec
 - 


### Future
 - implement text parsing + noramlization so can be more reliable
 - implement same functionality for ePub based on ebooklib

