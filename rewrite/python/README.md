- work in progress
- the ahk approach to windows api is only a temporary workaround
  - it may be replaced by a pure python approach, or
  - the whole rewrite may be replaced by another cpp rewrite
- all these rewrites are more of exercises for the programming languages, for the ahk version is just enough for daily use (but i have to admit that too many wheels have to be invented there), except for not supporting macos 

---

### Acknowledgement

This python re-write was initially a homework I assigned to [@mxqng](https://github.com/mxqng), who just finished learning [Python Crash Course](https://www.amazon.com/dp/1718502702) on my advice on the first book for learning Python. Comparing to AHK, Python has the advantage of calling API elegantly, and the API chapter is the summary chapter of its data visualization project, so it is a good choice as an integrated exercise based on. mxqng is interested in data analysis, and the projects’ part was the reason why I recommend that book to her. But the homework was done very quick by her in an afternoon so it was then extended to a re-write of the core functions of wfwp as it is now, where I only wrote the idw.ahk for her, as an interface, or workaround, of calling COM object directly from Python, which is somehow deep for both me and her. This re-write is an implementation of full core functions of wfwp excluding the GUI and timing part, which is basically a command line, or so-called nox, version of wfwp. mxqng’s work extended the initial aim of practicing API calling in Python to deep object-oriented programming skills like abstraction and encapsulation for a beginner, which can be seen from her beautiful code.

When she did this homework, mxqng never thought one day it can be used like this, so she didn’t take the credit via a proper PR. Now I am proud to write this acknowledgement for her to assist her applying to graduate programs. Before learning Python, she also learned C with me and finished all the exercises in the famous [K&R C](https://www.amazon.com/dp/0131103628). Wish her good luck.
