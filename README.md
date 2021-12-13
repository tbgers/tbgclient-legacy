# tbgclient
A TBG API wrapper for Python.

The name comes from CubeyTheCube's [scratchclient](https://github.com/CubeyTheCube/scratchclient), which this package is inspired by.

## Examples
**(This is unfinished, there's a lot of things I haven't added)**
### GETting and POSTing
```python
from tbgclient import TBGSession

session = TBGSession("Tymewalk", "something")

# Get a post
post = session.get_post(3)
print(post.text)

# Post a reply
session.get_topic(5716).post_reply("Hello, world!") 

# Greet a user
user = session.get_user(2)
session.get_topic(5716).post_reply("Hello, " + user.username) 
```

Documentation will come later. For now, above examples will suffice.