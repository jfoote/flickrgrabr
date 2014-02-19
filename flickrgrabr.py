#!/usr/bin/env python

# Jonathan Foote
# jmfoote@loyola.edu
# 18 Feb 2014

import re, urllib2, sys, os, time

def dump_err_page(errdir, uri, page):
    '''
    If errdir is set, dumps page to disk file with name based on uri at errdir.
    Otherwise does nothing.
    '''
    if not errdir:
        return
    if not os.path.exists(errdir):
        os.makedirs(errdir)
    filename = [j for j in uri.split("/") if j][-1]+".html"
    filepath = os.path.join(errdir, filename)
    sys.stderr.write("dumping page to %s\n" % filepath)
    if os.path.exists(filepath):
        sys.stderr.write("warning: overwriting page at %s" % filepath)
    file(filepath, "wt").write(page)

def parse_photostream(uri, outdir=".", errdir="", sleep_sec=3):
    '''
    Parses Flickr photostream at uri. Downloads original image from link on page
    a uri to outdir. If errdir is set and parsing errors are detected, pages 
    triggering problems are downloaded to errdir. Returns a tuple of the 
    original image URI and the URI of the next page in the photostream.
    '''

    # download page
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    page = urllib2.urlopen(urllib2.Request(uri, None, headers)).read()

    # get original image URI
    img_uri = None
    regex = 'img src=&quot;(http(?:s)?\:\/\/.*_o?\.jpg)&quot'
    mobj = re.search(regex, page)
    if mobj:
        img_uri = mobj.groups()[0]
    else:
        sys.stderr.write("couldn't find original image uri for %s\n" % uri)
        dump_err_page(errdir, uri, page)

    # download image
    filename = os.path.join(outdir, img_uri.split("/")[-1])
    img = urllib2.urlopen(urllib2.Request(img_uri, None, headers)).read()
    file(filename, "wb").write(img)
    
    # get next page uri
    next_uri = None
    regex = '\<a id="nav-bar-next" data-track="next_button" class="Butt ' \
            'visible rapidnofollow" href="\/photos\/(.*)\/in\/photostream\/" ' \
            'tabindex="3"\>'
    mobj = re.search(regex, page)
    if mobj:
        keystr = mobj.groups()[0]
        next_uri = "http://www.flickr.com/photos/%s/in/photostream/" % keystr
    else:
        sys.stderr.write("couldn't find next page uri for %s\n" % uri)
        dump_err_page(errdir, uri, page)

    return img_uri, next_uri
    
def scrape(start, outdir, errdir, sleep_sec):
    '''
    Scrapes images from photostream with first page at start to outdir. 
    If errdir is set, pages that trigger parsing errors are downloaded to errdir
    '''
    next_uri = start
    while(next_uri):
        img_uri, next_uri = parse_photostream(next_uri, outdir, errdir, 
            sleep_sec)
        print "processed", next_uri, img_uri
        if sleep_sec:
            time.sleep(sleep_sec)
        
if __name__ == "__main__":
    import argparse
    desc = "Downloads your original photos from your Flickr photostream. " \
           "NOTE: This is a quick hack I used to get some of my photos back. "\
           "It currently doesn't work with all streams, " \
           "and will probably work with less as time goes on :|"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-o,--outdir', metavar="OUTDIR", dest="outdir", 
        default=".", help="Specify directory to download images to.")
    parser.add_argument('-e,--errdir', metavar="ERRDIR", dest="errdir", 
        default="", help="Specify a directory to output pages that fail to " \
        "parse correctly to.")
    parser.add_argument('-s,--sleep-time-sec', metavar="SLEEPTIME", 
        dest="sleep_sec", default="3", help="Number of seconds to wait " \
        "between getting pages from flickr.")
    parser.add_argument('STARTURI', help="URI of first page of photostream, " \
        "something like this: " \
        "http://www.flickr.com/photos/homatthew/12267802976")
    args = parser.parse_args()
    
    scrape(args.STARTURI, args.outdir, args.errdir, int(args.sleep_sec))
