#!/bin/sh

PDREPODIR="$1"
PDFLATPAKDIR="$(dirname $(realpath "$0"))"

oldimgurl="https://screenshots.debian.net/shrine/screenshot/12081/simage/large-f07fad807ae33903b32a38d2c7cedd66.png"
newimgurl="https://upload.wikimedia.org/wikipedia/commons/f/f8/Pure_Data_with_many_patches_open_%28showing_netpd_project%29.png"

usage() {
cat >/dev/stderr <<EOF
usage: $0 <path-to-pd-clone>

updates patches/metainfo.patch for the latest and greatest Pd release

EOF
if [ "$*" ]; then
  echo "$*"
  exit 1
else
 exit 0
fi
}

test -n "${PDREPODIR}" || usage
test -d "${PDREPODIR}/.git" || usage "it looks like ${PDREPODIR} is not a git repository"
test -d "${PDREPODIR}/linux" || usage "it looks like ${PDREPODIR} is not a clone of pd"

cd ${PDREPODIR}/linux

metainfo=""
for f in org.puredata.pd org.puredata.pd-gui; do
  if [ -e "${f}.metainfo.xml" ]; then
    metainfo="${f}.metainfo.xml"
    break
  fi
done

test -e "${metainfo}" || usage "it looks like there's no metainfo.xml file in ${PDREPODIR}"

echo "  <releases>" > releases.xml
git log --tags --simplify-by-decoration --pretty="format:%ai %d" | sed -e '/^\([0-9-]*\) .*tag. \(0\.[0-9][0-9]-[0-9]\)[,)].*/!d' -e 's|^\([0-9-]*\) .*tag. \(0\.[0-9][0-9]-[0-9]\)[,)].*|    <release version="\2" date="\1"/>|g' | sort -r >> releases.xml
echo "  </releases>" >> releases.xml
sed \
    -e "/<content_rating.*\/>/r releases.xml" \
    -e "s|${oldimgurl}|${newimgurl}|" \
    -i "${metainfo}"

git diff "${metainfo}" > "${PDFLATPAKDIR}/patches/metainfo.patch"

git checkout "${metainfo}"
rm releases.xml
