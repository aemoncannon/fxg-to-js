import sys,os,math
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
  sys.stdout.write(line + "\n")

def statement(line):
  sys.stdout.write(line + ";\n")

ident_counter = itertools.count()
def gensym():
  return "sym" + str(next(ident_counter))

known_library_defs = set()

def symbol_instance(node):
  symbol_type = node.localName
  sym = gensym()
  statement("var %s = InstantiateSymbol_%s()" % (sym, symbol_type))
  common_transforms(node, sym)
  return sym

def group(node):
  sym = gensym()
  statement("var %s = new Kinetic.Group()" % sym)
  for child in node.childNodes:
    if child.localName == "Path":
      child_sym = path(child)
      statement("%s.add(%s)" % (sym, child_sym))
    elif child.localName == "Group":
      child_sym = group(child)
      statement("%s.add(%s)" % (sym, child_sym))
    elif child.localName in known_library_defs:
      child_sym = symbol_instance(child)
      statement("%s.add(%s)" % (sym, child_sym))
  common_transforms(node, sym)
  return sym

def path(node):
  sym = gensym()
  statement("var %s = new Kinetic.Path({x:0,y:0})" % sym)
  for data in attributes(node, "data"):
    cleaned = re.compile("[ \r\n\t]+").sub(" ", data)
    statement("%s.setData('%s')" % (sym, cleaned))
  trans = common_transforms(node, sym)
  for child in children(node, "fill"):
    fill(child, sym)
  for child in children(node, "stroke"):
    stroke(child, sym, trans)
  return sym

def common_transforms(node, sym):
  for rotation in attributes(node, "rotation"):
    statement("%s.setRotationDeg(%s)" % (sym, rotation))
  for x in attributes(node, "x"):
    statement("%s.setX(%s)" % (sym, x))
  for y in attributes(node, "y"):
    statement("%s.setY(%s)" % (sym, y))
  sx = float(attr(node, "scaleX", 1))
  sy = float(attr(node, "scaleY", 1))
  if sx != 1 or sy != 1:
    statement("%s.setScale(%s, %s)" % (sym, sx, sy))
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
          statement("%s.setOffset(%s, %s)" % (sym, tx, ty))
          #statement("%s.getTransform().m = [%s, %s, %s, %s, %s, %s]" % (sym, a, b, c, d, tx, ty))
  return {'sx':sx, 'sy':sy}

def fill(node, path_sym):
  for child in children(node, "SolidColor"):
    statement("%s.setFill('%s')" % (path_sym, attr(child, "color", "black")))
    statement("%s.setOpacity(%s)" % (path_sym, attr(child, "alpha", 1.0)))

  for child in children(node, "LinearGradient"):
    x = float(attr(child, "x", 0))
    y = float(attr(child, "y", 0))
    # scaleX interpreted as width in fxg
    scaleX = float(attr(child, "scaleX", 0))
    cx = x + scaleX / 2
    cy = y
    rotation_rads = math.radians(float(attr(child, "rotation", 0)))
    x1 = scaleX/2 * math.cos(rotation_rads + math.pi) + cx
    y1 = scaleX/2 * math.sin(rotation_rads + math.pi) + cy
    x2 = scaleX/2 * math.cos(rotation_rads) + cx
    y2 = scaleX/2 * math.sin(rotation_rads) + cy
    color_stops = []
    for entry in children(child, "GradientEntry"):
      ratio = float(attr(entry, "ratio", 0))
      color = str(attr(entry, "color", "black"))
      color_stops.append(ratio)
      color_stops.append(color)
    statement("%s.setFill({start:{x:%s,y:%s},end:{x:%s,y:%s},colorStops:%s})" % (path_sym, x1, y1, x2, y2, color_stops))

  for child in children(node, "RadialGradient"):
    color_stops = []
    for entry in children(child, "GradientEntry"):
      ratio = float(attr(entry, "ratio", 0))
      color = str(attr(entry, "color", "#ffffff"))
      color_stops.append(ratio)
      color_stops.append(color)
    statement("%s.setFill({start:{x:-10,y:-10,radius:0},end:{x:10,y:10,radius:70},colorStops:%s})" % (path_sym, color_stops))

def stroke(node, path_sym, transform):
  for child in children(node, "SolidColorStroke"):
    statement("%s.setStroke('%s')" % (path_sym, attr(child, "color", "black")))
    avg_scale = transform['sx']
    weight = float(attr(child, "weight", 1.0)) / avg_scale
    statement("%s.setStrokeWidth('%s')" % (path_sym, weight))
    if attr(child, "alpha"):
      statement("%s.setOpacity('%s')" % (path_sym, attr(child, "alpha", 1.0)))
    statement("%s.setLineJoin('round')" % path_sym)

def library_definition(node):
  name = attr(node, "name")
  assert name
  known_library_defs.add(name)
  line("function InstantiateSymbol_%s() {" % name)
  for child in children(node, "Group"):
    child_sym = group(child)
    statement("return %s" % child_sym)
  line("}")

def graphic(node):
  for child in children(node, "Library"):
    for definition in children(child, "Definition"):
      library_definition(definition)
  group_sym = group(node)
  statement("%s.add(%s)" % ("layer", group_sym))

print "window.onload = function() {"
print "var stage = new Kinetic.Stage({container: 'container',width: 600,height: 500});"
print "var layer = new Kinetic.Layer();"
print "layer.setScale(3,3);"

#print couple.parseString("23.3 4")
dom = xml.dom.minidom.parse(sys.argv[1])
graphic(dom.childNodes[0])

print "stage.add(layer);"
print "};"
