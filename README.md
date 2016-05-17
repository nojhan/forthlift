forthlift — post sequences of texts on social media
===================================================

Forthlift is a command line application to post sequences of text lines on social media.

Its main use case is to post on Twitter several status that you have prepared first in your text editor.

It is thus designed to ease automation and integration in existing tools
and had an Unix-like text-and-pipes command line interface.

For example, it makes it easy to post "chained" twitter status (that answer to each others)
from your text editor. Just send the selected text to its standard input, selecting the
twitter API, and voilà. Using Vim, you can tweet the visually-selected lines with:
`:'<,'>w !forthlift -a twitter`


## SYNOPSIS

`forthlift` [-h]

`forthlift` [-a {stdout,twitter}] [-m MAXLEN] [-i|-t] [-c] [-q] [-d] [-s]


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
  with its index in the input list.


While it is recommended to prepare the input text with other text-processing tools
(fold, fmt, tr, sed, grep, your text editor, etc.),
forthlift comes with some rough text-processing capabilities, among which:

* ignore or trim lines that are longer than a given size (see `--trim` and `--ignore`),

* add a counter of the form `<current index>/<total lines>` at the end of the lines (see `--counter`).


## OPTIONS

* -h, --help: show this help message and exit

* -a {stdout,twitter}, --api {stdout,twitter}: Name of the API to use.
  (default: stdout)

* -m MAXLEN, --max-len MAXLEN: Maximum number of characters in the lines.
  (default: 140)

* -i, --ignore: Ignore lines that are longer than MAXLEN (default: False)

* -t, --trim: Trim down lines that are longer than MAXLEN. (default: False)

* -c, --counter: Add a counter of the form " x/N" at the end of the lines,
  with N being the number of lines read and x the current index of the line.
  NOTE: this necessitate to read all the input before processing it.
  (default: False)

* -q, --quiet: Do not print errors and warnings on the standard error output.
  (default: False)

* -s, --setup: Setup the selected API (e.g. authenticate and get authorization to post).
  (default: False)

* -d, --independent: Post each item independently from the previous one
  The behaviour of this option depends on the selected API.
  For example on Twitter: do not post a line as an answer to the previous one but as a new tweet.
  (default: False)

* --twitter-images FILENAME(S) [FILENAME(S) ...]:
  Upload each given image files along with the corresponding tweets in the sequence.
  If there are more images than tweets, they are silently ignored.
  (default: None)


## INSTALLATION

### Twitter

1) Copy `twitter.conf-dist` as `twitter.conf` and indicate your developer's API keys in the corresponding fields.
2) Run `forthlift --api twitter --setup` and follow the instructions (go to the given URL, then paste the given PIN).

Why should you get developer's API keys? Because Twitter does not like open-source desktop applications, see:
http://arstechnica.com/security/2010/09/twitter-a-case-study-on-how-to-do-oauth-wrong/

