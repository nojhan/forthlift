#!/usr/bin/env python

import sys
import locale
import argparse

import tweepy


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


def on_twitter( data, api, asked, endline="\n"  ):
    lines = setup(data, asked)

    prev_status_id = None

    images = asked.twitter_images
    images.reverse()

    for line in lines:
        if images:
            img = images.pop()
        else:
            img = None

        if img:
            # API.update_with_media(filename[, status][, in_reply_to_status_id][, lat][, long][, source][, place_id][, file])
            status = api.update_with_media(img, line, prev_status_id)
        else:
            # API.update_status(status[, in_reply_to_status_id][, lat][, long][, source][, place_id])
            status = api.update_status(line, prev_status_id)

        if asked.chain:
            prev_status_id = status.id

        yield status.text + endline


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

# TODO option: rate at which to post lines

# API-dependant options

parser.add_argument("-c", "--chain", action="store_true",
        help="Chained actions. Whatever that means depends on the chosen API.")

# Twitter
parser.add_argument("--twitter-images", metavar="FILENAME(S)", nargs="+", type=str,
        help="Upload each given image files along with the corresponding tweets in sequence. If there are more images than tweets, they are silently ignored.")

asked = parser.parse_args()

# Consistency checks

if asked.ignore and asked.trim:
    if not asked.quiet:
        sys.stderr.write("WARNING: asking to trim AND to ignore is not logical, I will ignore.")
    assert( not (asked.ignore and asked.trim) )

if asked.twitter_images:
    if not asked.api == "twitter":
        if not asked.quiet:
            sys.stderr.write("WARNING: asking to upload images on twitter while not using the twitter API is not logical, I will ignore.")
        assert( not (asked.twitter_images and not asked.api=="twitter") )

    else: # Test readable images
        cannot=[]
        for img in asked.twitter_images:
            try:
                with open(img) as f:
                    f.read()
            except OSError:
                cannot.append(img)
        if cannot:
            print("Cannot open the following image files, I will not continue: ")
            for img in cannot:
                print(img)
            sys.exit(5) # I/O Error


# APIs

if asked.api == "stdout":

    operate( on_stdout, asked )


elif asked.api == "twitter":

    import ConfigParser

    config = ConfigParser.RawConfigParser()
    config.read('twitter.conf')

    consumer_key = config.get("Auth","key")
    consumer_secret = config.get("Auth","key_secret")

    try:
        verifier_code = config.get("Auth","code")
    except:
        access_token = config.get("Auth","token")
        access_token_secret = config.get("Auth","token_secret")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, "https://api.twitter.com/1.1/")
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    operate( on_twitter, api, asked )

