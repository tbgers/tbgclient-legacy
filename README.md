# tbgclient
A TBG API wrapper for Python.

The name comes from CubeyTheCube's [scratchclient](https://github.com/CubeyTheCube/scratchclient), which this package is inspired with.

**(This is unfinished, there's a lot of things I haven't added)**

## Examples
### Post a reply
```python
from tbgclient import TBGSession

session = TBGSession("Tymewalk", "something")

session.post("Hello, world!", 5716)
```
### Get post
```python
from tbgclient import TBGSession

session = TBGSession("Tymewalk", "something")

print(session.get(3).text)
```

Documentation will come later. For now, above examples will suffice.