#!/usr/bin/env python3

import logging
import re

from bs4 import BeautifulSoup
from bs4.element import Tag

log = logging.getLogger()
logging.basicConfig()

def extractReleaseNotes(filename):
    try:
        with open(filename) as f:
            soup = BeautifulSoup(f.read(), "html.parser")
    except Exception as e:
        log.fatal(f"{filename}: {e}")
        return

    result = {}
    for section in soup.body.find_all("section", class_="releasenote"):
        for h in section.find_all("h4"):
            ID = h.get("id").strip()
            result[ID] = section.contents[1:]
    return result

def getTagDates(filename):
    pat=re.compile(r"^[0-9]+\.[0-9]+-[0-9]+$")
    with open(filename) as f:
        tagdates=f.readlines()
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

def writeMetainfo(metainfo, filename):
    with open(filename, "w") as f:
        f.write(str(metainfo))
    

def parseArgs():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "releasenotes",
        default="doc/1.manual/resources/chapter5.htm",
        help="releasenotes (e.g. %(default)r) to read",
    )
    parser.add_argument(
        "tagdates",
        default="tagdates.txt",
        help="tag/dates mapping file (e.g. %(default)r) to read",
    )
    parser.add_argument(
        "metainfo",
        default="linux/org.puredata.pd-gui.metainfo.xml",
        help="metainfo to udpate (e.g. %(default)r)"
    )

    args = parser.parse_args()

    return args

def _main():
    args = parseArgs()

    relnotes = extractReleaseNotes(args.releasenotes)
    metainfo = getMetainfo(args.metainfo)
    tagdates = getTagDates(args.tagdates)
    
    meta2 = insertReleaseNotes(metainfo=metainfo, relnotes=relnotes, tagdates=tagdates)
    writeMetainfo(meta2, "metadata.xml")

if __name__ == "__main__":
    _main()
