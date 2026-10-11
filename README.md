# generate_password.py

## Description
Secure password generator in Python.

It builds the password by using the Python library [secrets](https://docs.python.org/es/3.8/library/secrets.html).

Passwords generated always meet the following conditions:

- The first and the last characters are alphanumeric.
- At least one character is numerical.
- At least one character is non-alphanumeric.

Length can be selected by introducing an argument. Default: 10 characters.

## Help Text
~~~
$ generate_password.py --help
usage: generate_password.py [-h] [-c] [length]

positional arguments:
  length           Password length

options:
  -h, --help       show this help message and exit
  -c, --clipboard  Copy password to clipboard
~~~

## Output Examples
~~~
$ generate_password.py
M9u&CKpY82
$ generate_password.py 8
l$ny4g&g
$ generate_password.py -c
OqP!*4vWl8

Password copied into clipboard!
$
~~~
