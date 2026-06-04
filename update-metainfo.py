#!/usr/bin/env python3

import logging
import re

from bs4 import BeautifulSoup
from bs4.element import Tag

log = logging.getLogger()
logging.basicConfig()


def flatten_tags(soup, tag="p", recursive=True):
    try:
        tags = soup.find_all(tag, recursive=False)
    except AttributeError as e:
        return soup
    if not tags:
        if recursive:
            for s in soup:
                flatten_tags(s, tag)
        return soup
    for s in tags:
        for t in s.find_all(tag):
            t = t.extract()
            soup.append(t)
    return soup


def remove_empty_tags(soup):
    """remmoves all tags with no text-content"""
    # beware, this will remove self-closing tags like <br/> and <img src="foo.jpg"/>
    for x in soup.find_all():
        if len(x.get_text(strip=True)) == 0:
            x.extract()

    return soup

def extractReleaseNotes(filename):
    try:
        with open(filename) as f:
            soup = BeautifulSoup(f.read(), "lxml")
    except Exception as e:
        log.fatal(f"{filename}: {e}")
        return

    result = {}

    # remove all empty tags
    for section in soup.body.find_all("section", class_="releasenote"):
        remove_empty_tags(section)

    # mangle release-notes
    for section in soup.body.find_all("section", class_="releasenote"):
        for h in section.find_all("h4"):
            ID = h.get("id").strip()
            flattened = flatten_tags(section)
            for div in flattened.find_all("div"):
                div.name = "description"
            result[ID] = flatten_tags(flattened.contents[1:])
    return result


def getTagDates(filename):
    pat = re.compile(r"^[0-9]+\.[0-9]+-[0-9]+$")
    with open(filename) as f:
        tagdates = f.readlines()
    tagdates = [_.split() for _ in tagdates]
    return {k: v for k, v in tagdates if pat.match(k)}


def getMetainfo(filename):
    try:
        with open(filename) as f:
            soup = BeautifulSoup(f.read(), "xml")
    except Exception as e:
        log.fatal(f"{filename}: {e}")
        return
    return soup


def insertReleaseNotes(metainfo, relnotes, tagdates={}):
    # <releases>
    #  <release version="0.56-1" date="2025-08-22">
    #  </release>
    # </releases>
    tagdates = tagdates or {}
    releases = []
    releases = Tag(name="releases")
    for v in tagdates or relnotes:
        t = Tag(name="release")
        t["version"] = v
        if v in tagdates:
            t["date"] = tagdates[v]
        else:
            continue
        body = relnotes.get(v) or []
        for x in body:
            t.append(x)
        releases.append(t)

    meta = metainfo.component

    if meta.find(releases.name):
        log.fatal(f"{filename!r} already contains {releases.name!r}")
        return

    meta.append(releases)

    return metainfo


def writeMetainfo(metainfo, filename, pretty=True):
    with open(filename, "w") as f:
        if pretty:
           f.write(metainfo.prettify())
        else:
           f.write(str(metainfo))


def parseArgs():
    import argparse

    parser = argparse.ArgumentParser()

    p = parser.add_argument_group("logging")
    p.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="lower verbosity",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="raise verbosity",
    )

    p = parser.add_argument_group("output")
    p.add_argument(
        "-o",
        "--output",
        default="metadata.xml",
        help="file to write (e.g. %(default)r)",
    )
    p.add_argument(
        "--prettify",
        action="store_true",
        help="prettify output (might break XML validator!)",
    )

    p = parser.add_argument_group("input")
    p.add_argument(
        "releasenotes",
        default="doc/1.manual/5.current.status.htm",
        help="releasenotes (e.g. %(default)r) to read",
    )
    p.add_argument(
        "tagdates",
        default="tagdates.txt",
        help="tag/dates mapping file (e.g. %(default)r) to read",
    )
    p.add_argument(
        "metainfo",
        default="linux/org.puredata.pd-gui.metainfo.xml",
        help="metainfo to use as template (e.g. %(default)r)",
    )

    args = parser.parse_args()

    args.verbosity = args.verbose - args.quiet
    del args.verbose
    del args.quiet
    log.setLevel(logging.WARNING - (10 * args.verbosity))

    return args


def _main():
    args = parseArgs()

    relnotes = extractReleaseNotes(args.releasenotes)
    metainfo = getMetainfo(args.metainfo)
    tagdates = getTagDates(args.tagdates)

    meta2 = insertReleaseNotes(metainfo=metainfo, relnotes=relnotes, tagdates=tagdates)
    writeMetainfo(meta2, args.output, pretty=args.prettify)


if __name__ == "__main__":
    _main()
