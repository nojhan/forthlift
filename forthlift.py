#!/usr/bin/env python

import sys
import locale
import argparse
import datetime
import ConfigParser

import tweepy


class AppKeyError(Exception):
    def __init__(self, msg):
        self.msg = msg


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


def setup_counter( data, asked ):
    assert(asked.counter)

    # unroll everything
    data = list(data)
    nb = len(data)
    # " int/int"
    counter_size = len(str(nb))*2 + 1 + 1

    for i,line in enumerate(data):
        counter = " %i/%i" % (i+1,nb)
        curmax = asked.max_len - len(counter)
        if len(line) > curmax:
            if asked.ignore:
                data[i] = line
            elif asked.trim:
                data[i] = line[:curmax]
        data[i] = data[i] + counter

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
    if asked.counter:
        f = setup_counter
    else:
        f = setup_hem

    for line in f(data, asked):
        yield line


def operate( func, *args ):
    for line in func( readline(sys.stdin), *args ):
        write(line)


#
# STDOUT API
#

def on_stdout( data, asked, endline="\n" ):
    lines = setup(data, asked)
    # You can do something on the whole set of lines if you want.

    for i,line in enumerate(lines):
        if endline:
            if line[-1] != endline:
                line += endline

        if asked.independent:
            yield line
        else:
            yield i + " " + line


#
# TWITTER API
#

def on_twitter( data, api, asked, endline="\n"  ):
    lines = setup(data, asked)

    prev_status_id = None

    for line in lines:
        # API.update_status(status[, in_reply_to_status_id][, lat][, long][, source][, place_id])
        status = api.update_status(line, prev_status_id)

        if asked.independent:
            prev_status_id = None
        else:
            prev_status_id = status.id

        yield status.text + endline


def setup_twitter(configfile="twitter.conf"):

    config = ConfigParser.RawConfigParser()

    # Authenticate the application.
    config.read(configfile)

    if not config.has_section("App"):
        raise AppKeyError("ERROR: did not found application keys, ask your distribution maintainer or get keys from Twitter first.")

    app_key = config.get("App","app_key")
    app_secret = config.get("App","app_key_secret")

    auth = tweepy.OAuthHandler(app_key, app_secret)


    # Authenticate the user.
    auth_url = auth.get_authorization_url()
    print "Copy and paste this URL in your browser while your are logged in the twitter account where you want to post."
    print "Authorization URL: " + auth_url

    print "Then paste the Personal Identification Number given by Twitter:"
    verifier = raw_input('PIN: ').strip()
    auth.get_access_token(verifier)
    # print 'ACCESS_KEY = "%s"' % auth.access_token.key
    # print 'ACCESS_SECRET = "%s"' % auth.access_token.secret

    # Authenticate and get the user name.
    auth.set_access_token(auth.access_token.key, auth.access_token.secret)
    api = tweepy.API(auth)
    username = api.me().name
    print "Authentication successful, ready to post to account: " + username


    # Save authentication tokens.
    if not config.has_section("Info"):
        config.add_section('Info')
    config.set('Info','account', username)
    config.set('Info','auth_date', datetime.datetime.utcnow().isoformat())

    if not config.has_section("Auth"):
        config.add_section('Auth')
    config.set('Auth', 'local_token', auth.access_token.key)
    config.set('Auth', 'local_token_secret', auth.access_token.secret)

    # Writing our configuration file to 'example.cfg'
    with open(configfile, 'wb') as fd:
        config.write(fd)


#
# CLI
#

if __name__=="__main__":

    errors = {"NO_ERROR":0, "UNKNOWN_ERROR":1, "NO_SETUP_NEEDED":2, "NO_APP_KEY":10}

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

    parser.add_argument("-c", "--counter", action="store_true",
            help="Add a counter of the form \" x/N\" at the end of the lines, \
                  with N being the number of lines read and x the current index of the line. \
                  NOTE: this necessitate to read all the input before processing it.")

    parser.add_argument("-q", "--quiet", action="store_true",
            help="Do not print errors and warnings on the standard error output.")

    # TODO option: rate at which to post lines

    # API-dependent options

    parser.add_argument("-s", "--setup", action="store_true",
            help="Setup the selected API (e.g. authenticate and get authorization to post).")

    parser.add_argument("-d", "--independent", action="store_true",
            help="Post each item independently from the previous one. \
                  The behaviour of this option depends on the selected API. \
                  For example on Twitter: do not post a line as an answer to the previous one but as a new tweet.")

    asked = parser.parse_args()


    # Setup
    if asked.setup:
        configfile = asked.api+".conf"
        if asked.api == "twitter":
            try:
                setup_twitter(configfile)
            except AppKeyError as e:
                if not asked.quiet:
                    sys.stderr.write(e.msg)
                sys.exit(errors["NO_APP_KEY"])
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise
            else:
                sys.exit(errors["NO_ERROR"])

        else: # other API
            if not asked.quiet:
                sys.stderr.write("This API does not need setup.")
            sys.exit(errors["NO_SETUP_NEEDED"])


    # Consistency checks

    if asked.ignore and asked.trim:
        if not asked.quiet:
            sys.stderr.write("WARNING: asking to trim AND to ignore is not logical, I will ignore.")
        assert( not (asked.ignore and asked.trim) )


    # APIs

    if asked.api == "stdout":

        operate( on_stdout, asked )


    elif asked.api == "twitter":

        # Authenticate
        config = ConfigParser.RawConfigParser()
        config.read('twitter.conf')

        app_key = config.get("App","app_key")
        app_secret = config.get("App","app_key_secret")

        try:
            verifier_code = config.get("Auth","code")
        except:
            access_token = config.get("Auth","local_token")
            access_token_secret = config.get("Auth","local_token_secret")

        auth = tweepy.OAuthHandler(app_key, app_secret, "https://api.twitter.com/1.1/")
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)

        # Post
        operate( on_twitter, api, asked )

