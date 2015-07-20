#!/usr/bin/env python

import sys
import locale
import argparse


def write(data, stream = sys.stdout):
    """
    Write "data" on the given stream, then flush, silently handling broken pipes.
    """
    try:
        stream.write(data)
        stream.flush()

    # Silently handle broken pipes
    except IOError:
        try:
            stream.close()
        except IOError:
            pass


def readline( stream_in ):
    while True:
        try:
            line = stream_in.readline().decode(stream_in.encoding or locale.getpreferredencoding(True)).strip()
        except UnicodeDecodeError:
            continue
        except KeyboardInterrupt:
            break
        if not line:
            break
        yield line

    raise StopIteration


def setup_adorn( data, asked ):
    assert(asked.adorn)

    # unroll everything
    data = list(data)
    nb = len(data)
    # " int/int"
    adorn_size = len(str(nb))*2 + 1 + 1

    for i,line in enumerate(data):
        adorn = " %i/%i" % (i+1,nb)
        curmax = asked.max_len - len(adorn)
        if len(line) > curmax:
            if asked.ignore:
                data[i] = line
            elif asked.trim:
                data[i] = line[:curmax]
        data[i] = data[i] + adorn

    return data


def setup_hem(data, asked):
    for line in data:
        if len(line) > asked.max_len:
            if asked.ignore:
                pass
            elif asked.trim:
                line = line[:asked.max_len]

        yield line


def setup( data, asked ):
    if asked.adorn:
        f = setup_adorn
    else:
        f = setup_hem

    for line in f(data, asked):
        yield line


def on_stdout( data, asked, endline="\n" ):
    lines = setup(data, asked)
    # You can do something on the whole set of lines if you want.

    if asked.chain:
        prefix = " "
    else:
        prefix = ""

    for i,line in enumerate(lines):
        if endline:
            if line[-1] != endline:
                line += endline
        yield prefix*i + line


def operate( func, *args ):
    for line in func( readline(sys.stdin), *args ):
        write(line)



usage = "Post text read on the standard input to a website or an API."
apis =["stdout", "twitter"] # TODO "http_post", "http_get",

parser = argparse.ArgumentParser( description=usage,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-a", "--api", choices=apis, default="stdout",
        help="Name of the API to use.")

# Generic options

parser.add_argument("-m", "--max-len", metavar="MAXLEN", type=int, default=140,
         help="Maximum number of characters in the lines.")

parser.add_argument("-i", "--ignore", action="store_true",
        help="Ignore lines that are longer than MAXLEN")

parser.add_argument("-t", "--trim", action="store_true",
        help="Trim down lines that are longer than MAXLEN.")

parser.add_argument("-d", "--adorn", action="store_true",
        help="Add a counter of the form \" x/N\" at the end of the lines, \
              with N being the number of lines read and x the current index of the line. \
              NOTE: this necessitate to read all the input before processing it.")

parser.add_argument("-q", "--quiet", action="store_true",
        help="Do not print errors and warnings on the standard error output.")

# API-dependant options

parser.add_argument("-c", "--chain", action="store_true",
        help="Chained actions. Whatever that means depends on the chosen API.")

asked = parser.parse_args()


# Consistency checks

if asked.ignore and asked.trim:
    if not asked.quiet:
        sys.stderr.write("WARNING: asking to trim AND to ignore is not logical, I will ignore.")
    assert( not (asked.ignore and asked.trim) )


# APIs

if asked.api == "stdout":

    operate( on_stdout, asked )


elif asked.api == "twitter": # TODO

    import tweepy

    consumer_key = ""
    consumer_secret = ""

    access_token = ""
    access_token_secret = ""

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, "https://api.twitter.com/1.1/")
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print "#########################################"
        print tweet.text

