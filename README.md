# tbgclient
A TBG API wrapper for Python.
The name comes from [CubeyTheCube](https://scratch.mit.edu/users/Raihan142857/)'s [scratchclient](https://github.com/CubeyTheCube/scratchclient), which this package is inspired with.

(NOT DONE!)

## Examples
### Post a reply
```
from tbgclient import TBGSession

session = TBGSession("Tymewalk", "something")

session.post("Hello, world!", 5716)
```
### Get post
```
from tbgclient import TBGSession

session = TBGSession("Tymewalk", "something")

print(session.get(3).text)
```

Documentation will come after I fixed the code.
