import os, sys, json

# experimental script to generate Python classes based on text file routes.api

srcFile = "cityroutes/routes.api"

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
    output = []
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
        if typedef.startswith("{"):
            fields = extractObjectFields(typedef)
            body = "\n".join([ renderClassSlots(fields), "", renderClassConstructor(typename, extends, fields), renderClassRepr(typename, extends, fields)])
            output.append(renderClass(typename, extends, comment, body))
        elif typedef.startswith("enum("):
            enum = extractEnum(typedef)
            output.append(renderEnum(typename, comment, enum))
        else:
            print "Unsupported typedef", typedef
    return "\n".join(output)

def renderClassSlots(fields):
    return "    __slots__ = [%s]" % ", ".join(map(lambda x: "'%s'" % x["name"], fields))


def renderClassConstructor(name, inherits, fields):
    if len(fields):
        prot = "    def __init__(self, %s):" % ", ".join(map(lambda x: ("%s=%s" % (x["name"], x["default"]) if "default" in x else ("%s" % x["name"])), fields))
        rows = "\n".join(map(lambda x: "        self.%s = %s" % (x["name"], x["name"]), fields))
    else:
        return """    def __init__(self):
        pass"""

    return prot + "\n" + rows
    """
    def __init__(self, start, end, minDist=1, innerBorder=1, outerBorder=1):
        self.start = start
        self.end = end
        self.minDist = minDist
        self.innerBorder = innerBorder
        self.outerBorder = outerBorder
        self.axis = makeArcVectors(start.pt, end.pt, min_dist=minDist)
    """

def renderClassRepr(name, inherits, fields):
    out = """
    def __repr__(self):
        return '%s'
""" % name
    return out


def renderClass(name, inherits, comment, classBody):
    return """
# %s
class %s(%s):
%s
    """ % (comment or "Insert comment here...", name, inherits or "object", classBody or "")

def renderEnum(name, comment, fields):
    return """
# %s
class %s:
    %s
    """ % (comment or "Insert comment here...", name, (", ".join(fields) + " = range(%d)" % len(fields)))


########################################################################################################################

all = []
for line in content:
    all.append(extractType(line))

source = "\n".join(all)

with open("cityroutes/module.py", "w") as text_file:
    text_file.write(source)


