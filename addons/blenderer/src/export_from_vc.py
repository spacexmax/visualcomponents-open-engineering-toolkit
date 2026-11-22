# -*- coding: utf-8 -*-
# Blenderer Addon version 2026-08 v2.6.0 (Blender 5.2)
# with VisualComponents
# ################Thanks for Tang ###########################
from __future__ import with_statement
import math, vcVector, vcMatrix
import os.path
import datetime
from PIL import Image
try:from vcScript import *
except:pass
try:from vcCommand import *
except:pass
from collections import defaultdict, deque

LINECHANGE = '\n'

def sanitizefilename(fname):
  # v2.6.1-fix: do NOT downgrade unicode -> str via default str() codec.
  # In IronPython 2, str(unicode_with_chinese) tries to encode via ASCII →
  # UnicodeEncodeError for any non-ASCII filename (Chinese, Japanese, accents,
  # Cyrillic, etc.). Keeping the value as unicode is safe because all
  # downstream consumers (os.path.join, open(), app.saveBitmap) accept
  # unicode strings with proper UTF-16 filesystem support on Windows.
  suspiciouscharacters = [r'/', '\\' ,'#',':',';','!','\x00','%','&','?','^','*',' ','\t']
  for c in suspiciouscharacters:
    fname = fname.replace(c,'_')
  return fname



def isRobotMaterial(app, material_name, node):
  controllers = node.Component.findBehavioursByType(VC_ROBOTCONTROLLER)
  if not controllers: return material_name # not a robot
  controller = controllers[0]
  if not controller.FlangeNode or node in [controller.FlangeNode, controller.FlangeNode.Parent]:
    return material_name # skip flange 
  mat = app.findMaterial(material_name)
  diffuse = mat.Diffuse
  avg = (diffuse.X + diffuse.Y + diffuse.Z)/3.0
  dispersion = max([diffuse.X, diffuse.Y, diffuse.Z])-min([diffuse.X, diffuse.Y, diffuse.Z])
  style = ''
  if controller.Name == 'CB3':
    if mat.Opacity > 0.95:
      style = '_pulver'
  else:
    if dispersion > 0.4 or avg > .6 and mat.Opacity > 0.95:
      style = '_cast_metal'
  material_name = material_name + style
  return material_name


def export_obj( app, 
                node, 
                materials, 
                material_file, 
                scale, 
                filename, 
                mat_mode, 
                mat_csv, 
                mat_dict, 
                SEP, 
                re_render,
                use_robot_materials):
  new_materials = {}
  dirM = vcMatrix.new()
  #filename = sanitizefilename(filename)
  basename, extension = os.path.splitext(os.path.basename(filename))
  dirname = os.path.dirname(filename)
  if not material_file:
    mtlfilename = dirname +'\\'+ "VC_to_Blender_materials.mtl"
  ii = 1
  hasgeometry = False
  for gs in node.Geometry.GeometrySets:
    if gs.Type == VC_TRIANGLESET:
      if gs.PointCount > 0:
        hasgeometry = True
        break
  else:
    # nothing to export return
    return None, materials, material_file

  # v2.6.1-fix (R4): unified UTF-8 binary write for OBJ/MTL files.
  # Previously the file was opened in text mode and only the `newmtl` line
  # was manually .encode('utf-8'); every other write (g / usemtl / #comment
  # / map_Kd / style / Kd etc.) containing a non-ASCII material name or
  # basename (Chinese, Japanese, Cyrillic, accents) would be auto-encoded by
  # IronPython 2 via the *default locale codec* (cp936 on Chinese Windows,
  # cp1252 on Western Windows). This caused two problems:
  #   1. On a non-CJK locale the write threw UnicodeEncodeError immediately.
  #   2. Even on a CJK locale the file ended up being mixed-encoded: the
  #      newmtl line was UTF-8 bytes while the usemtl/g lines above it were
  #      GBK bytes. import_to_blender.py reads the file with encoding='utf8'
  #      so the usemtl material name and the newmtl material name would be
  #      byte-for-byte DIFFERENT strings → dict lookup fails silently → the
  #      mesh renders with no material (all white / default grey).
  # The fix: open files in binary mode ("wb"/"ab") and send *everything* as
  # explicitly UTF-8 encoded bytes so OBJ writer and MTL reader agree.
  def _u(s):
    if isinstance(s, unicode):
      return s.encode('utf-8')
    if isinstance(s, bytes):
      return s
    return unicode(s).encode('utf-8')

  ##
  geosets_by_material = defaultdict(list)
  for gs in node.Geometry.GeometrySets:
    if gs.Type == VC_TRIANGLESET:
      if gs.Feature and not gs.Feature.Visible:
        continue
      if not gs.Material:
        material_name = 'orange'
        material = app.findMaterial(material_name)
      else:
        material_name = gs.Material.Name
        material = gs.Material
      using_styles = [material_name.endswith(x) for x in ['_pulver', '_cast_metal']]
      if use_robot_materials and not any(using_styles):
        material_name = isRobotMaterial(app, material_name, node)
      geosets_by_material[material_name].append(gs)
      new_materials[material_name] = material
  ##
  if not re_render:
    try:
      out = open(filename,"wb")
    except IOError:
      print 'cannot open file %s' % filename
      return None, materials, material_file
    with out:
      out.write(_u("# Visual Components OBJ Exporter v0.1c - (c)2018 Visual Components\n"))
      out.write(_u("# File Created: %s\n\n" % datetime.datetime.now().isoformat()))
      out.write(_u("mtllib %s\n\n" % ("VC_to_Blender_materials.mtl")))
      ii = 1
      # mp is identity matrix; multiplying each vertex by it is pure overhead.
      # Write scaled coordinates directly without vcVector creation or matrix mult.
      aaa = 0

      for material_name, geoset_list in geosets_by_material.iteritems():
        aaa += 1

        out.write(_u("#\n# object %s <%i geosets>\n#\n\n" % (material_name,len(geoset_list))))
        vertex_string = deque()
        text_coord_string = deque()
        face_string = deque()
        vertex_indexer = 0
        for gs in geoset_list:
          pos = gs.PositionTable
          npos = len(pos)
          for i in range(0, npos, 3):
            vertex_string.append("v %.4f %.4f %.4f" % (pos[i]*scale, pos[i+1]*scale, pos[i+2]*scale))
          tex = gs.TextureCoordinateTable
          if len(tex) > 0:
            for i in range(0, len(tex), 2):
              text_coord_string.append("vt %.4f %.4f 0.0000" % (tex[i], tex[i+1]))
          else:
            for i in range(gs.PointCount):
              text_coord_string.append("vt 0.0000 0.0000 0.0000")
          tt = gs.TriangleTable
          for i in range(0, len(tt), 3):
            a = tt[i] + ii
            b = tt[i+1] + ii
            c = tt[i+2] + ii
            face_string.append("f %d/%d/%d %d/%d/%d %d/%d/%d" % (a,a,a,b,b,b,c,c,c))
          ii += gs.PointCount
        vertex_string = '\n'.join(vertex_string)
        text_coord_string = '\n'.join(text_coord_string)
        face_string = '\n'.join(face_string)
        out.write(_u('\n'))
        out.write(_u(vertex_string))
        out.write(_u('\n'))
        out.write(_u(text_coord_string))
        out.write(_u('\n'))
        out.write(_u("g %s_%i\n" % ('geo_'+material_name, aaa)))
        #out.write(_u("usemtl %s\n" % sanitizefilename(material_name)))
        out.write(_u("usemtl %s\n" % material_name))
        out.write(_u(face_string))
        out.write(_u('\n'))


  # # # # # # # # # # # # # # # # # # # # #
  try:
    if material_file:
      out = open(material_file.name, 'ab')
    else:
      out = open(mtlfilename,"wb")
      out.write(_u("# Visual Components OBJ like material exporter - (c)2018 Visual Components\n"))
      out.write(_u("# File Created: %s\n\n" % datetime.datetime.now().isoformat()))
  except IOError:
    print 'cannot open file %s' % filename
    return None, materials, material_file
  with out:
    # # # # # # # # # # # # # # # # # # # # 
    # # # # # # # Materials # # # # # # # # 
    # # # # # # # # # # # # # # # # # # # # 

    for material_name, mat in new_materials.iteritems():
      if material_name in materials:
        # the material is already written to the mat file
        continue
      table_material = False
      if mat_mode == 'Read From Table' and mat.Name in mat_dict:
        table_material = True
        R = float(mat_dict[mat.Name]['R'])**2.2 #to be gamma corrected 
        G = float(mat_dict[mat.Name]['G'])**2.2 #to be gamma corrected 
        B = float(mat_dict[mat.Name]['B'])**2.2 #to be gamma corrected 
        metallic = float(mat_dict[mat.Name]['metallic'])
        roughness = float(mat_dict[mat.Name]['roughness'])
        bumpiness = float(mat_dict[mat.Name]['bumpiness'])
        clearcoat = float(mat_dict[mat.Name]['clearcoat'])
        clearcoat_rouhness = mat_dict[mat.Name]['clearcoat_rouhness'] # not implemented
        opacity = float(mat_dict[mat.Name]['opacity'])
        style = mat_dict[mat.Name]['style']
        #procedural_displacement = mat_dict[mat.Name]['procedural_displacement']
        #displacement_value = float(mat_dict[mat.Name]['displacement_value'])
        #displacement_scale = float(mat_dict[mat.Name]['displacement_scale'])
        color_map = mat_dict[mat.Name]['color_map']
        normal_map = mat_dict[mat.Name]['normal_map']
      new_line = "newmtl %s\n" % material_name
      out.write(_u(new_line))
      if table_material:
        out.write(_u("\td %.4f\n" % opacity))
      elif mat.OpacityType == VC_MATERIAL_TRANSPARENCY_CONSTANT:
          out.write(_u("\td %.4f\n" % mat.Opacity))
          opacity = mat.Opacity
      elif mat.OpacityType == VC_MATERIAL_TRANSPARENCY_NONE:
        out.write(_u("\td 1.0000\n"))
        opacity = 1.0
      out.write(_u("\tKa %.4f %.4f %.4f\n" % (mat.Ambient.X,mat.Ambient.Y,mat.Ambient.Z)))
      if table_material:
        out.write(_u("\tKd %.4f %.4f %.4f\n" % (R**(1/2.2),G**(1/2.2),B**(1/2.2)))) # HUOM! DOUBLE CHECK THE GAMMA CORRECTION
      else:
        try:
          out.write(_u("\tKd %.4f %.4f %.4f\n" % (mat.BaseColor.X,mat.BaseColor.Y,mat.BaseColor.Z)))
        except:
          out.write(_u("\tKd %.4f %.4f %.4f\n" % (mat.Diffuse.X,mat.Diffuse.Y,mat.Diffuse.Z)))
      out.write(_u("\tKs %.4f %.4f %.4f\n" % (mat.Specular.X,mat.Specular.Y,mat.Specular.Z)))
      out.write(_u("\tillum 3\n"))
      texturefilename = ''
      if False and table_material and color_map: #FALSE FORCED TO DISABLE 
        out.write(_u("\tmap_Kd %s\n" % sanitizefilename(color_map)))
        # MAP NEEDS TO BE COPIEND INT HE TEMPDATA FOLDER  !! NOT IMPLEMENTED YET HUOM!!
      elif mat.Texture:
        tname = basename + '_' + material_name + ".png"
        tname = sanitizefilename(tname)
        texturefilename = "file:///" + os.path.dirname(filename) +'\\'+ tname
        app.saveBitmap(mat.Texture, texturefilename)
        out.write(_u("\tmap_Kd %s\n" % tname))
      #
      if False and table_material and normal_map: #FALSE FORCED TO DISABLE 
        out.write(_u("\tmap_bump %s\n" % sanitizefilename(normal_map)))
        # MAP NEEDS TO BE COPIEND INT HE TEMPDATA FOLDER  !! NOT IMPLEMENTED YET HUOM!!
      else:
        try:
          mat.BumpMap
          bumpmapAvailable = True
        except:
          bumpmapAvailable = False
        bumptexturefilename = ''
        if bumpmapAvailable:
          tname = basename + '_' + material_name + '_BUMP' + ".png"
          tname = sanitizefilename(tname)
          bumptexturefilename = "file:///" + os.path.dirname(filename) +'\\'+ tname
          app.saveBitmap(mat.BumpMap, bumptexturefilename)
          #
          out.write(_u("\tmap_bump %s\n" % tname))
      #
      if table_material:
        out.write(_u("\tbumpiness %f\n" % bumpiness))
      else:
        try:
          bumpiness = mat.Bumbiness #typo in API should be bumpiness
        except:
          bumpiness = 0.0
        out.write(_u("\tbumpiness %f\n" % bumpiness))
      #
      if table_material:
        out.write(_u("\tmetallic %f\n" % metallic))
      else:
        try:
          metallic = mat.Metallic
        except:
          metallic = 0.0
        out.write(_u("\tmetallic %f\n" % metallic))
      # clearcoat
      if table_material:
        out.write(_u("\tclearcoat %f\n" % clearcoat))
      else:
        try:
          clearcoat = mat.Clearcoat
        except:
          clearcoat = 0.0
        out.write(_u("\tclearcoat %f\n" % clearcoat))
      # style
      if table_material:
        out.write(_u("\tstyle %s\n" % style))
      else:
        try:
          style = mat.Style
        except:
          style = 'N/A'
        out.write(_u("\tstyle %s\n" % style))
      #
      if table_material:
        out.write(_u("\troughness %f\n" % roughness))
      else:
        try:
          roughness = mat.Roughness
        except:
          roughness = 0.0
        out.write(_u("\troughness %f\n" % roughness))
      out.write(_u("\n"))
      if mat_mode == 'Write To Table' and mat_csv and mat.Name not in materials:
        # v2.6.1-fix (R4): CSV cells need to be UTF-8 bytes as well so the
        # material name (which may be Chinese) survives the write. See the
        # matching fix in Blenderer.py getMaterialFiles() for the read side
        # and for the CSV file handle being opened in binary mode there.
        def _c(v):
          if isinstance(v, unicode):
            return v.encode('utf-8')
          if isinstance(v, bytes):
            return v
          return unicode(v).encode('utf-8')
        mat_csv.write(_c(mat.Name) + _c(SEP))
        mat_csv.write(_c(str(mat.Diffuse.X)) + _c(SEP))
        mat_csv.write(_c(str(mat.Diffuse.Y)) + _c(SEP))
        mat_csv.write(_c(str(mat.Diffuse.Z)) + _c(SEP))
        mat_csv.write(_c(str(metallic)) + _c(SEP))
        mat_csv.write(_c(str(roughness)) + _c(SEP))
        mat_csv.write(_c(str(bumpiness)) + _c(SEP))
        mat_csv.write(_c(str(clearcoat)) + _c(SEP))
        mat_csv.write(_c('') + _c(SEP))
        mat_csv.write(_c(str(opacity)) + _c(SEP))
        mat_csv.write(_c(style) + _c(SEP))
        #mat_csv.write(_c(procedural_displacement) + _c(SEP))
        #mat_csv.write(_c(str(displacement_value)) + _c(SEP))
        #mat_csv.write(_c(str(displacement_scale)) + _c(SEP))
        mat_csv.write(_c(texturefilename) + _c(SEP))
        mat_csv.write(_c(bumptexturefilename) + _c(LINECHANGE))
        #material_table_csv.close()
      #materials[mat.Name] = mat
      materials[material_name] = mat
  return True, materials, out


