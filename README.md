forthlift — post sequences of texts on social media
===================================================

NOTE: FORTHLIFT IS IN AN EARLY PRE-ALPHA STAGE.

Forthlift is a command line application to post sequences of text lines on social media.
It is designed to ease automation and integration in existing tools.

For example, it makes it easy to post "chained" twitter status (that answer to each others)
from your text editor. Just send the selected text to its standard input, selecting the
twitter API, and voilà. Using Vim, you can tweet the selected lines with:
`:'<,'>w !forthlift -a twitter --chain`


## SYNOPSIS

`forthlift` [-h]

`forthlift` [-a {stdout,twitter}] [-m MAXLEN] [-i] [-t] [-d] [-q] [-c]


## DESCRIPTION

### A generic tool

Generally speaking, it's a Unix-like command that operate a sequence of pre-programmed
chained actions on its text input.

It comes with some existing actions:
* `stdout`: print the input text on the standard output,
* `twitter`: send the input text as status on twitter.


### Features

The main feature of forthlift is its ability to *chain* actions.
Depending on the chosen API, this could means different things:

* for twitter, this mean that the sequence of status will be posted
  as a sequence of *answers* and not as a list of independent tweets.

* for the "stdout" API, this means that each printed line will start
  with as many spaces as its index in the input list.


While it is recommended to prepare the input text with other text-processing tools
(fold, fmt, tr, sed, grep, your text editor, etc.),
forthlift comes with some rough text-processing capabilities, among which:

* ignore or trim lines that are longer than a given size,

* add a counter of the form `<current index>/<total lines>` at the end of the lines.


## OPTIONS

TODO


## INSTALLATION

### Twitter

Copy `twitter.conf-dist` as `twitter.conf` and indicate your developer's API keys and tokens.

