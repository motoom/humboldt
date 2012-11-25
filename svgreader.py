
# Reads a SVG file written by InkScape 0.48
#
# Software by Michiel Overtoom, motoom@xs4all.nl
#

import xml.etree.ElementTree as ET
from collections import namedtuple as namtup

def parsesvgcoords(lines):
    """Given a path from SVG, extract the coordinates.
    Return a list of coordinates and an error message.
    The errormessage is None in case there was no error.
    """
    if len(lines) < 3:
        return None, "Not enough coordinates."
    if lines[0] != "m":
        return None, "First line should be 'm'."
    if lines[-1] != "z":
        return None, "Last line should be 'z'."
    lines = lines[1:-1]
    coords = []
    firstcoord = True
    currentx = currenty = None
    for line in lines:
        if line in ("c", "v"):
            return None, "Bezier curves are not supported, only polygons of straight lines."
        parts = line.split(",")
        if len(parts) != 2:
            return None, "Every line should be an X,Y coordinate."
        x, y = map(float, parts)
        if firstcoord:
            currentx, currenty = x, y
            firstcoord = False
        else:
            currentx += x
            currenty += y
        coords.append((currentx, currenty))
        # It's not necessary to close the path because Qt will do that.
    return coords, None


def readfile(fn):
    namespaces = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "cc": "http://creativecommons.org/ns#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "svg": "http://www.w3.org/2000/svg",
        "xlink": "http://www.w3.org/1999/xlink",
        "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",
        "inkscape": "http://www.inkscape.org/namespaces/inkscape",
        }
    tree = ET.parse(fn)
    root = tree.getroot()

    filetitle = "Untitled"
    title = root.find("svg:metadata/rdf:RDF/cc:Work/dc:title", namespaces=namespaces)
    if title is not None:
        filetitle = title.text

    width, height = root.attrib["width"], root.attrib["height"]
    background = None
    regions = []
    errors = []
    for groupnr, group in enumerate(root.findall("svg:g", namespaces=namespaces)):
        groupid, grouplabel = group.attrib["id"], group.attrib["{http://www.inkscape.org/namespaces/inkscape}label"]
        print "Group %s: %s" % (groupid, grouplabel)
        for item in group:
            if item.tag.endswith("image"): # Must be in layer1, Background
                assert groupnr == 0
                x = float(item.attrib["x"])
                y = float(item.attrib["y"])
                width = float(item.attrib["width"])
                height = float(item.attrib["height"])
                href = item.attrib["{http://www.w3.org/1999/xlink}href"] # item.attrib["xlink:href"] # namespace aliases in attributes don't seem to work.
                parts= href.split(";") # href = "data:image/png;base64,iVBORw0KGgoAAAANSUXYZXYZ...."
                if len(parts) != 2:
                    errors.append("Error in group %s, %s: Unexpected image data URL (too many parts)" % (groupid, grouplabel))
                    continue
                format, encoded = parts
                _, mime = format.split(":")
                parts = encoded.split(",")
                if len(parts) != 2:
                    errors.append("Error in group %s, %s: Unexpected image data URL (encoding, encoded data expected)" % (groupid, grouplabel))
                    continue
                encoding, encoded = parts
                img = encoded.decode(encoding)
                background = namtup("Background", "img mimetype x y width height")(img, mime, x, y, width, height)
            if item.tag.endswith("path"): # Must be in layer2, Regions
                assert groupnr == 1
                titleitem = item.find("svg:title", namespaces=namespaces)
                title = ""
                if titleitem is not None:
                    title = titleitem.text
                data = item.attrib["d"]
                datalines = data.split(" ")
                coords, error = parsesvgcoords(datalines)
                if not error:
                    regions.append((title, coords))
                else:
                    errors.append("Error in '%s': %s" % (title, error))

            # TODO: Idea: layer 3 = Features (rivers, lakes, parks) (paths), layer 4 = Cities (points)
    meta = (filetitle, width, height, errors)
    return meta, background, regions

if __name__ == "__main__":
    meta, background, regions = readfile("usa-states.svg")
    print "Background: %dx%d, %d bytes" % (background.width, background.height, len(background.img))
    print meta
    print "%d regions" % len(regions)
