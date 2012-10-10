
How to build ext_user.so
------------------------

* Must first compile a 32-bit version of python interpreter. i.e python-32bit
* Build the extent module
```bash
./python-32bit setup.py build
```
* Make a soft link of ext_user.so to the current directory.
```bash 

ln -s ./build/lib-xxxxx/ext_user.so ext_user.so

```
* Start the interpreter:

```bash

./python-32bit

```

```python

>>> import ext_user
>>> user = ext_user.GetUserRec('PASSWDS', 2)
>>> print user.userid
>>> ...

```


