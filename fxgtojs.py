import sys
import xml.dom.minidom
import xml.dom
import itertools

def children(node, tag):
  for node in node.childNodes:
    if node.localName == tag:
      yield node

def attr(node, key, default=None):
  at = node.attributes.get(key, None)
  return at.value if at else default

def line(line):
  sys.stdout.write(line + ";\n")

ident_counter = itertools.count()
def gensym():
  return "sym" + str(next(ident_counter))

class Sprite(object):
  def __init__(self):
    pass

def group(node, sprite):
  sym = gensym()
  line("var %s = new Kinetic.Group()" % sym)
  for child in children(node, "Path"):
    path(child, sprite)
  for child in children(node, "Group"):
    child_sym = group(child, sprite)
    line("%s.add(%s)" % (sym, child_sym))
  return sym

def path(node, sprite):
  data = attr(node, "data", "")
  line("var path = new Kinetic.Path()")
  line("path.setData('%s')" % data)
  for child in children(node, "fill"):
    fill(child, sprite)

def fill(node, sprite):
  for child in children(node, "SolidColor"):
    color = attr(child, "color", None)
    alpha = attr(child, "alpha", None)
    if color:
      line("path.setFill('%s')" % color)
    if alpha:
      line("path.setOpacity(%s)" % float(alpha))

def graphic(node, sprite):
  for child in children(node, "Group"):
    group(child, sprite)

#print couple.parseString("23.3 4")
dom = xml.dom.minidom.parse("Bamboo.fxg")
graphic(dom.childNodes[0], None)
