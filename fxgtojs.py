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
    child_sym = path(child, sprite)
    line("%s.add(%s)" % (sym, child_sym))
  for child in children(node, "Group"):
    child_sym = group(child, sprite)
    line("%s.add(%s)" % (sym, child_sym))
  return sym

def path(node, sprite):
  sym = gensym()
  data = attr(node, "data", "")
  line("var %s = new Kinetic.Path({x:0,y:0})" % sym)
  line("%s.setData('%s')" % (sym, data))
  for child in children(node, "fill"):
    fill(child, sym)
  return sym

def fill(node, path_sym):
  for child in children(node, "SolidColor"):
    color = attr(child, "color", None)
    alpha = attr(child, "alpha", None)
    if color:
      line("%s.setFill('%s')" % (path_sym, color))
    if alpha:
      line("%s.setOpacity(%s)" % (path_sym, float(alpha)))

def graphic(node, sprite):
  group_sym = group(node, sprite)
  line("%s.add(%s)" % ("layer", group_sym))




print "window.onload = function() {"
print "var stage = new Kinetic.Stage({container: 'container',width: 600,height: 500});"
print "var layer = new Kinetic.Layer();"

#print couple.parseString("23.3 4")
dom = xml.dom.minidom.parse("Bamboo.fxg")
graphic(dom.childNodes[0], None)

print "stage.add(layer);"
print "};"
