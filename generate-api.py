import os, sys, json

# experimental script to generate Python classes based on text file routes.api

srcFile = "city-routes/routes.api"

# 1. load file as list of lines
with open(srcFile) as f:
    content = f.readlines()
content = [x.strip() for x in content]

# 2. extract type definitions
#    for now, there can be only a single type per single line


types = {}

def extractTypeComment(line):
    head, sep, tail = line.partition('#')
    comment = None
    if not head:
        return None
    if tail:
        comment = tail

    head = head.strip()
    comment = comment.strip() if comment else None
    return (head, comment)


def extractDefaultValue(defn):
    ndx = defn.find("(")
    if ndx>0:
        val = defn[:ndx]
        default = defn[ndx+1:defn.find(")")]
    else:
        val = defn
        default = None
    return { "value": val, "default": default }


def extractObjectFields(defn):
    body = defn[1:len(defn)-1].strip()
    parts = filter(lambda x: x, map(lambda x: x.strip(), body.split(",")))
    fieldpairs = map(lambda x: extractFieldPair(x), parts)
    return fieldpairs


def extractFieldPair(defn):
    parts = defn.split(":")
    name = parts[0].strip()
    type = parts[1].strip()
    dd = extractDefaultValue(type)
    out = { "name": name, "type": dd["value"] }
    if "default" in dd and dd["default"]:
        out["default"] = dd["default"]
    return out


def extractEnum(defn):
    body = defn[5:len(defn)-1].strip()
    parts = map(lambda x: x.strip(), body.split(","))
    return parts


def extractType(line):
    # remove comments...
    tc = extractTypeComment(line)
    if tc:
        typestr = tc[0]
        comment = tc[1]

        # extract header (Name(Extends)) and typedef
        ndx = typestr.find(" ")
        header = typestr[:ndx]
        typedef = typestr[ndx+1:]

        # extract class name and parent class name if specified
        ndx = header.find("(")
        if ndx>0:
            typename = header[:ndx]
            extends = header[ndx+1:header.find(")")]
        else:
            typename = header
            extends = None

        # extract type definition
        print typename, extends, typedef, comment
        if typedef.startswith("{"):
            fields = extractObjectFields(typedef)
            print "Object:", fields
        elif typedef.startswith("enum("):
            enum = extractEnum(typedef)
            print "Enum:", enum
        else:
            print "Unsupported typedef", typedef




for line in content:
    extractType(line)
