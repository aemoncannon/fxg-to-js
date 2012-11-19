import sys
import xml.dom.minidom
import xml.dom
import itertools
import re

def children(node, tag):
  for node in node.childNodes:
    if node.localName == tag:
      yield node

def attr(node, key, default=None):
  at = node.attributes.get(key, None)
  return at.value if at else default

def attributes(node, key):
  at = node.attributes.get(key, None)
  if at:
    yield at.value

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
  common_transforms(node, sym)
  return sym

def path(node, sprite):
  sym = gensym()
  line("var %s = new Kinetic.Path({x:0,y:0,lineCap:'round'})" % sym)
  for data in attributes(node, "data"):
    cleaned = re.compile("[\r\n\t]").sub("", data)
    line("%s.setData('%s')" % (sym, cleaned))
  for child in children(node, "fill"):
    fill(child, sym)
  for child in children(node, "stroke"):
    stroke(child, sym)
  common_transforms(node, sym)
  return sym

def common_transforms(node, sym):
  for rotation in attributes(node, "rotation"):
    line("%s.setRotationDeg(%s)" % (sym, rotation))
  for x in attributes(node, "x"):
    line("%s.setX(%s)" % (sym, x))
  for y in attributes(node, "y"):
    line("%s.setY(%s)" % (sym, y))
  sx = attr(node, "scaleX", 1)
  sy = attr(node, "scaleY", 1)
  if sx != 1 or sy != 1:
    line("%s.setScale(%s, %s)" % (sym, sx, sy))
  for child in children(node, "transform"):
    for child in children(child, "Transform"):
      for child in children(child, "matrix"):
        for mat in children(child, "Matrix"):
          a = attr(mat, "a", 1)
          b = attr(mat, "b", 0)
          c = attr(mat, "c", 0)
          d = attr(mat, "d", 1)
          tx = attr(mat, "tx", 0)
          ty = attr(mat, "ty", 0)
          line("%s.setOffset(%s, %s)" % (sym, tx, ty))
          #line("%s.getTransform().m = [%s, %s, %s, %s, %s, %s]" % (sym, a, b, c, d, tx, ty))

def fill(node, path_sym):
  for child in children(node, "SolidColor"):
    line("%s.setFill('%s')" % (path_sym, attr(child, "color", "black")))
    line("%s.setOpacity(%s)" % (path_sym, attr(child, "alpha", 1.0)))

def stroke(node, path_sym):
  for child in children(node, "SolidColorStroke"):
    line("%s.setStroke('%s')" % (path_sym, attr(child, "color", "black")))
    line("%s.setStrokeWidth('%s')" % (path_sym, attr(child, "weight", 1.0)))

def graphic(node, sprite):
  group_sym = group(node, sprite)
  line("%s.add(%s)" % ("layer", group_sym))

print "window.onload = function() {"
print "var stage = new Kinetic.Stage({container: 'container',width: 600,height: 500});"
print "var layer = new Kinetic.Layer();"
print "layer.setScale(5,5);"

#print couple.parseString("23.3 4")
dom = xml.dom.minidom.parse("AuroraFern.fxg")
graphic(dom.childNodes[0], None)

print "stage.add(layer);"
print "};"
