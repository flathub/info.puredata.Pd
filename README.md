Pure Data packaged for Flatpak
==============================

This is the Flatpak application for [Pure Data](https://puredata.info) (aka "Pd"),
open source visual programming language for multimedia, developed by Miller Puckette et al.

This is the "vanilla" flavour of Pd.


# How to build


This Flatpak uses the standard
[flatpak-builder](https://docs.flatpak.org/en/latest/flatpak-builder-command-reference.html)
tool to build.

You can run a command like the following to build the package from this repo
and install it in your 'user' Flatpak installation:

    flatpak-builder --install ./build info.puredata.Pd.yml --force-clean --user

During development you can also run a build without installing it, like this:

    flatpak-builder --run build info.puredata.Pd.yml pd

See the [Flatpak manual](http://docs.flatpak.org/en/latest/) for more information.


# Version update process

There's no formalized way to update the versions, but something along these lines should work:

```bash
cd ${PDREPODIR}/linux
echo "<releases>" > releases.xml
git log --tags --simplify-by-decoration --pretty="format:%ai %d" | sed -e '/^\([0-9-]*\) .*tag. \(0\.[0-9][0-9]-[0-9]\)[,)].*/!d' -e 's|^\([0-9-]*\) .*tag. \(0\.[0-9][0-9]-[0-9]\)[,)].*|<release version="\2" date="\1"/>|g' | sort -r >> releases.xml
echo "</releases>" >> releases.xml
sed -e "/<content_rating.*\/>/r releases.xml" -i org.puredata.pd.metainfo.xml

git diff org.puredata.pd.metainfo.xml > ${PDFLATPAKDIR}/patches/metainfo.patch

git checkout org.puredata.pd.metainfo.xml
rm relases.xml
cd -
```

The script `update-metainfo-patch.sh` should do this for you.
