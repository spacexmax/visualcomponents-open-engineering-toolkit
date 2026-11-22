# -*- coding: utf-8 -*-
# Blenderer Addon version 2026-08 v2.6.0 (Blender 5.2)
# with VisualComponents
# ################Thanks for Tang ###########################
import bpy, os.path, math


# ---------------------------------------------------------------------------
# NEW material pipeline helpers
# ---------------------------------------------------------------------------

def _srgb_to_linear(c):
  """Standard sRGB -> linear RGB conversion (per IEC 61966-2-1).

  Replaces the legacy x**2.2 approximation used by the OLD pipeline.
  VC stores BaseColor in sRGB space; Blender Principled BSDF Base Color
  input expects linear RGB, so this conversion is mandatory for accurate
  colour reproduction in the NEW pipeline.
  """
  if c <= 0.04045:
    return c / 12.92
  return ((c + 0.055) / 1.055) ** 2.4


def _convert_color_srgb(col):
  """Apply standard sRGB->Linear to a 3-channel colour list."""
  return [_srgb_to_linear(float(x)) for x in col]


def setupMaterialNew(mat_name,
          col,
          color_map,
          metallic,
          roughness,
          normal_map,
          bumpiness,
          clearcoat,
          clearcoat_rouhness,
          transparency,
          style,
          monochrome,
          simple_transparents = False,
          specular = (1.0, 1.0, 1.0),
          emission = 0.0,
          emission_color = (0.0, 0.0, 0.0)):
  """NEW material pipeline: accurate VC<->Blender correspondence.

  Improvements over OLD setupMaterial:
    * Standard sRGB->Linear conversion (IEC 61966-2-1) replaces x**2.2.
    * VC Specular color (Ks) drives Principled 'Specular IOR Level' (luminance).
    * Emission: VC Ke > 0 enables emissive shader with proper sRGB conversion.
    * Transparency: Alpha = opacity directly; glass-like (opacity<0.2) gets
      Transmission Weight, IOR=1.45, and reduced roughness for clean refraction.
    * No colour brightening (x*0.8+0.2) or roughness scaling (x*0.3) - the
      NEW pipeline trusts VC's values as-is.
    * backface culling disabled to avoid holes on single-sided VC geometry.
    * Texture colorspace explicitly set to sRGB for correct display->linear.
  """
  mat = bpy.data.materials.new(name=mat_name)
  mat.use_nodes = True
  mat.use_backface_culling = False
  nodes = mat.node_tree.nodes
  if monochrome:
    col = [float(x) for x in monochrome.split('|')]
    color_map = ''
    metallic = 0.0
    roughness = 1.0
    normal_map = ''
    bumpiness = 0
    clearcoat = 0
    clearcoat_rouhness = 0
    style = '__monochrome__'
    transparency = 1.0
  if style in ['N/A', '']:
    if '_cast_metal' in mat.name:
      style = 'castmetal'
    elif '_pulver' in mat.name:
      style = 'pulver'
  for node in nodes:
    nodes.remove(node)

  # Principled shader
  node_principled = nodes.new(type="ShaderNodeBsdfPrincipled")
  node_principled.location = 200,0
  node_principled.inputs['Metallic'].default_value = metallic
  node_principled.inputs['Roughness'].default_value = max(roughness, 0.01)
  node_principled.inputs['Coat Weight'].default_value = clearcoat
  node_principled.inputs['Coat Roughness'].default_value = max(clearcoat_rouhness, 0.1)

  node_output = nodes.new(type='ShaderNodeOutputMaterial')
  node_output.location = 600,0

  # Specular color (Ks) -> Specular IOR Level (driven by luminance, 0..1)
  # White specular (1,1,1) keeps default 0.5; darker specular reduces it.
  if specular and len(specular) >= 3:
    spec_lum = 0.2126*specular[0] + 0.7152*specular[1] + 0.0722*specular[2]
    node_principled.inputs['Specular IOR Level'].default_value = max(min(spec_lum * 0.5, 1.0), 0.0)

  # Emission (Ke) - enable emissive channel when VC provides it
  node_emission = None
  if emission > 0.0:
    # Convert emission color from sRGB to linear for correct output
    em_col = _convert_color_srgb(list(emission_color[:3])) if emission_color else [0.0, 0.0, 0.0]
    em_strength = emission
    # Mix emission on top of base via Principled 'Emission Color' + 'Emission Strength'
    if len(em_col) == 3:
      em_col = tuple(em_col + [1.0])
    node_principled.inputs['Emission Color'].default_value = em_col
    node_principled.inputs['Emission Strength'].default_value = em_strength

  # Base color or texture
  node_texture = None
  if color_map and os.path.exists(color_map):
    node_texture = nodes.new(type='ShaderNodeTexImage')
    node_texture.location = -600,100
    texture_img = bpy.data.images.load(color_map)
    node_texture.image = texture_img
    # Ensure texture is interpreted as sRGB so Blender's display->linear matches VC
    if texture_img.colorspace_settings.name != 'sRGB':
      texture_img.colorspace_settings.name = 'sRGB'
  else:
    if len(col) == 3:
      ccolor = [0,0,0,1]
      ccolor[:3] = col
      col = tuple(ccolor)
    # NEW: standard sRGB->Linear conversion
    col = _convert_color_srgb(col)
    node_principled.inputs['Base Color'].default_value = col

  # Transparency: direct Alpha correspondence, glass-specific transmission
  if transparency < 1.0:
    mat.blend_method = 'BLEND'
    if simple_transparents:
      mat = setup_transparent_shader(mat, col, transparency)
      return mat
    # Glass-like: opacity < 0.2 enables transmission for refraction effect
    if transparency < 0.2:
      # Real glass: high transmission, low roughness, IOR for refraction
      node_principled.inputs['Transmission Weight'].default_value = 0.9
      node_principled.inputs['IOR'].default_value = 1.45
      # Glass surfaces are typically smooth; reduce roughness for clean refraction
      node_principled.inputs['Roughness'].default_value = max(min(roughness, 0.05), 0.01)
    elif transparency < 0.5:
      # Semi-transparent: moderate transmission, keep VC roughness
      node_principled.inputs['Transmission Weight'].default_value = 0.4
      node_principled.inputs['IOR'].default_value = 1.45
    else:
      node_principled.inputs['Transmission Weight'].default_value = 0.0
    # Direct Alpha = opacity (no colour brightening, no roughness scaling)
    node_principled.inputs['Alpha'].default_value = max(transparency, 0.01)
  else:
    node_principled.inputs['Transmission Weight'].default_value = 0.0

  # Styles (castmetal / pulver) - shared logic with OLD pipeline
  style_vals = style.lower().split('|')
  node_normalmap = None
  if normal_map and os.path.exists(normal_map):
    node_normalmap = nodes.new(type='ShaderNodeTexImage')
    node_normalmap.location = -600,-300
    normalmap_img = bpy.data.images.load(normal_map)
    node_normalmap.image = normalmap_img
    normalmap_img.colorspace_settings.name = 'Non-Color'
    node_normalvector = nodes.new(type="ShaderNodeNormalMap")
    node_normalvector.location = -300,-300
    node_normalvector.inputs[0].default_value = bumpiness*2
  elif style_vals[0] == 'castmetal':
    try:
      strength = float( style_vals[1] )
    except:
      strength = 0.05
    try:
      text_scale = float(style_vals[2])
    except:
      text_scale = 400.0
    coordinates_node = nodes.new(type="ShaderNodeTexCoord")
    coordinates_node.location = -1600,-300
    node_principled.inputs['Roughness'].default_value = max(roughness*.6, .2)
    mapping_node = nodes.new(type="ShaderNodeMapping")
    mapping_node.location = -1400,-300
    mapping_node.inputs['Scale'].default_value[0] = text_scale
    mapping_node.inputs['Scale'].default_value[1] = text_scale
    mapping_node.inputs['Scale'].default_value[2] = text_scale
    voronoi_node = nodes.new(type="ShaderNodeTexVoronoi")
    voronoi_node.location = -1000,-300
    voronoi_node.inputs[1].default_value = 200
    noise_node = nodes.new(type="ShaderNodeTexNoise")
    noise_node.location = -1000,-600
    noise_node.inputs[1].default_value = 600.0
    noise_node.inputs[2].default_value = 2.0
    noise_node.inputs[3].default_value = 5.0
    noise_node2 = nodes.new(type="ShaderNodeTexNoise")
    noise_node2.location = -1000,-900
    noise_node2.inputs[1].default_value = 10.0
    noise_node2.inputs[2].default_value = 2.0
    noise_node2.inputs[3].default_value = 80.0
    colorramp_node = nodes.new(type="ShaderNodeValToRGB")
    colorramp_node.location = -800,-300
    colorramp_node.color_ramp.elements[0].position = 0.5
    colorramp_node.color_ramp.elements[1].position = 0.65
    colorramp_node.color_ramp.elements[0].color = (1, 1, 1, 1)
    colorramp_node.color_ramp.elements[1].color = (0, 0, 0, 1)
    colorramp_node2 = nodes.new(type="ShaderNodeValToRGB")
    colorramp_node2.location = -800,-600
    colorramp_node2.color_ramp.elements[0].position = 0.25
    colorramp_node2.color_ramp.elements[1].position = 0.8
    colorramp_node2.color_ramp.elements[0].color = (1, 1, 1, 1)
    colorramp_node2.color_ramp.elements[1].color = (0, 0, 0, 1)
    colorramp_node3 = nodes.new(type="ShaderNodeValToRGB")
    colorramp_node3.location = -800,-900
    colorramp_node3.color_ramp.elements[0].position = 0.51
    colorramp_node3.color_ramp.elements[1].position = 0.675
    colorramp_node3.color_ramp.elements[0].color = (1, 1, 1, 1)
    colorramp_node3.color_ramp.elements[1].color = (0, 0, 0, 1)
    mix_node1 = nodes.new(type="ShaderNodeMixRGB")
    mix_node1.location = -400,-600
    mix_node1.blend_type = 'VALUE'
    mix_node1.inputs[0].default_value = 0.5
    mix_node2 = nodes.new(type="ShaderNodeMixRGB")
    mix_node2.location = -200,-300
    mix_node2.blend_type = 'VALUE'
    mix_node2.inputs[0].default_value = 0.66
    bump_node = nodes.new(type="ShaderNodeBump")
    bump_node.location = 0,-300
    bump_node.inputs[0].default_value = strength
    bump_node.inputs[1].default_value = 1.0
    links = mat.node_tree.links
    link = links.new(coordinates_node.outputs[3], mapping_node.inputs[0])
    link = links.new(mapping_node.outputs[0], voronoi_node.inputs[0])
    link = links.new(voronoi_node.outputs[0], colorramp_node.inputs[0])
    link = links.new(colorramp_node.outputs[0], mix_node2.inputs[1])
    link = links.new(mapping_node.outputs[0], noise_node.inputs[0])
    link = links.new(mapping_node.outputs[0], noise_node2.inputs[0])
    link = links.new(noise_node.outputs[0], colorramp_node2.inputs[0])
    link = links.new(noise_node2.outputs[0], colorramp_node3.inputs[0])
    link = links.new(colorramp_node2.outputs[0], mix_node1.inputs[1])
    link = links.new(colorramp_node3.outputs[0], mix_node1.inputs[2])
    link = links.new(mix_node1.outputs[0], mix_node2.inputs[2])
    link = links.new(mix_node2.outputs[0], bump_node.inputs['Height'])
    link = links.new(bump_node.outputs[0], node_principled.inputs['Normal'])
  elif style_vals[0] == 'pulver':
    try:
      strength = float( style_vals[1] )
    except:
      strength = 0.08
    try:
      text_scale = float(style_vals[2])
    except:
      text_scale = 1.0
    coordinates_node = nodes.new(type="ShaderNodeTexCoord")
    coordinates_node.location = -1400,-300
    mapping_node = nodes.new(type="ShaderNodeMapping")
    mapping_node.location = -1100,-300
    mapping_node.inputs['Scale'].default_value[0] = 200*text_scale
    mapping_node.inputs['Scale'].default_value[1] = 200*text_scale
    mapping_node.inputs['Scale'].default_value[2] = 200*text_scale
    noise_node = nodes.new(type="ShaderNodeTexNoise")
    noise_node.location = -700,-300
    noise_node.inputs[1].default_value = 5.0
    noise_node.inputs[2].default_value = 2.0
    noise_node.inputs[3].default_value = 0.0
    bump_node = nodes.new(type="ShaderNodeBump")
    bump_node.location = 0,-300
    bump_node.inputs[0].default_value = strength
    bump_node.inputs[1].default_value = 1.0
    links = mat.node_tree.links
    link = links.new(coordinates_node.outputs[3], mapping_node.inputs[0])
    link = links.new(mapping_node.outputs[0], noise_node.inputs[0])
    link = links.new(noise_node.outputs[0], bump_node.inputs['Height'])
    link = links.new(bump_node.outputs[0], node_principled.inputs['Normal'])

  # Link nodes together
  links = mat.node_tree.links
  if node_texture:
    link = links.new(node_texture.outputs[0], node_principled.inputs['Base Color'])
  if node_normalmap:
    link = links.new(node_normalmap.outputs[0], node_normalvector.inputs[1])
    link = links.new(node_normalvector.outputs[0], node_principled.inputs['Normal'])
  link = links.new(node_principled.outputs[0], node_output.inputs[0])
  return mat



def setupSparks(mat_name,col):
  mat = bpy.data.materials.new(name=mat_name)
  mat.use_nodes = True
  nodes = mat.node_tree.nodes
  for node in nodes:
    nodes.remove(node)
  # create principled
  node_emission = nodes.new(type="ShaderNodeEmission")
  node_emission.location = 200,0
  node_emission.inputs[1].default_value = 50.0
  node_emission.inputs[0].default_value = col
  # create output node
  node_output = nodes.new(type='ShaderNodeOutputMaterial')   
  node_output.location = 600,0
  links = mat.node_tree.links
  link = links.new(node_emission.outputs[0], node_output.inputs[0])
  return mat


def setupMaterial(mat_name,
          col,
          color_map,
          metallic,
          roughness,
          normal_map,
          bumpiness, 
          clearcoat,
          clearcoat_rouhness,
          transparency,
          style,
          monochrome,
          simple_transparents = False):
  
  node_noise,node_math = None, None
  mat = bpy.data.materials.new(name=mat_name)
  mat.use_nodes = True
  nodes = mat.node_tree.nodes
  if monochrome:
    col = [float(x) for x in monochrome.split('|')]
    color_map = ''
    metallic = 0.0
    roughness = 1.0
    normal_map = ''
    bumpiness = 0
    clearcoat = 0
    clearcoat_rouhness = 0
    style = '__monochrome__' #this force skips and styling code
    transparency = 0.0
  if style in ['N/A', '']:
    if '_cast_metal' in mat.name:
      style = 'castmetal'
    elif '_pulver' in mat.name:
      style = 'pulver'
  for node in nodes:
    nodes.remove(node)
  #
  # Create principled shader
  #
  node_principled = nodes.new(type="ShaderNodeBsdfPrincipled")
  node_principled.location = 200,0
  node_principled.inputs['Metallic'].default_value = metallic
  # Blender 4.0+/5.x: 'Specular' input removed (replaced by 'Specular IOR Level', default 0.5 is fine)
  node_principled.inputs['Roughness'].default_value = max(roughness, 0.01)
  node_principled.inputs['Coat Weight'].default_value = clearcoat
  node_principled.inputs['Coat Roughness'].default_value = max(clearcoat_rouhness, 0.1)
  # create output node
  node_output = nodes.new(type='ShaderNodeOutputMaterial')   
  node_output.location = 600,0
  #
  # Base color or texture
  #
  node_texture = None
  if color_map and os.path.exists(color_map):
    node_texture = nodes.new(type='ShaderNodeTexImage')
    node_texture.location = -600,100
    texture_img = bpy.data.images.load(color_map)
    node_texture.image = texture_img
  else:
    # text color
    if len(col) == 3:
      ccolor = [0,0,0,1]
      ccolor[:3] = col
      col = tuple(ccolor)
    col = [x**2.2 for x in col] # gamma correction
    node_principled.inputs['Base Color'].default_value = col
  #
  # Transparency | Opacity
  #
  if transparency < 1.0: #opacity
    # Use BLEND (alpha blending) for smooth, noise-free transparency.
    # HASHED mode uses stochastic alpha sampling and introduces grain/noise
    # even with moderate sample counts. BLEND works perfectly in EEVEE Next
    # as long as the Principled BSDF Alpha input carries the opacity value.
    mat.blend_method = 'BLEND'
    if simple_transparents: #Force use tranparency shader
      mat = setup_transparent_shader(mat, col, transparency)
      return mat
    # Transmission Weight: keep near-zero for semi-transparent VC materials
    # (typical 30-95% opacity) so we see the surface shading, not pure refraction.
    # Only very transparent surfaces (<20% opacity) get noticeable refraction,
    # which is appropriate for thin glass/film-like objects.
    if transparency < 0.2:
      trans_weight = 0.9
    elif transparency < 0.5:
      trans_weight = 0.4
    else:
      trans_weight = 0.0
    node_principled.inputs['Transmission Weight'].default_value = trans_weight
    # Critical: set Alpha = opacity so EEVEE Next alpha-blends this fragment.
    # This single setting is what makes BLEND work instead of rendering black:
    # the surface alpha value directly controls what shows through.
    node_principled.inputs['Alpha'].default_value = max(transparency, 0.01)
    col = [x*0.8 + 0.2 for x in col] #make it brighter
    while len(col) < 4:
      col.append(0)
    node_principled.inputs['Base Color'].default_value = col
    # roughness scaling as VC renders quite rough materials still as transparent
    scale_roughness_down = 0.3
    minimum_roughness = 0.1
    node_principled.inputs['Roughness'].default_value = max(roughness * scale_roughness_down, minimum_roughness)
    # Boost specular reflection so glass/glossy transparent surfaces catch
    # environment reflections from the SPHERE lightprobe and direct light
    # specular highlights. Default Specular IOR Level is 0.5; raising it to
    # 0.7 for very-transparent (glass-like) materials gives a stronger, more
    # realistic mirror-like reflection without making the surface look metallic.
    if transparency < 0.5:
      node_principled.inputs['Specular IOR Level'].default_value = 0.7
    else:
      node_principled.inputs['Specular IOR Level'].default_value = 0.5
  else:
    node_principled.inputs['Transmission Weight'].default_value = 0.0 #transmission
  #
  # Styles
  #
  style_vals = style.lower().split('|')
  node_normalmap = None
  if normal_map and os.path.exists(normal_map):
    node_normalmap = nodes.new(type='ShaderNodeTexImage')
    node_normalmap.location = -600,-300
    normalmap_img = bpy.data.images.load(normal_map)
    node_normalmap.image = normalmap_img
    normalmap_img.colorspace_settings.name = 'Non-Color'
    #
    node_normalvector = nodes.new(type="ShaderNodeNormalMap")
    node_normalvector.location = -300,-300
    node_normalvector.inputs[0].default_value = bumpiness*2
  elif style_vals[0] == 'castmetal':
    try:
      strength = float( style_vals[1] )
    except:
      strength = 0.05
    try:
      text_scale = float(style_vals[2])
    except:
      text_scale = 400.0
    coordinates_node = nodes.new(type="ShaderNodeTexCoord")
    coordinates_node.location = -1600,-300

    node_principled.inputs['Roughness'].default_value = max(roughness*.6, .2) # decreasing the roughness a little but clmaping it above .2

    mapping_node = nodes.new(type="ShaderNodeMapping")
    mapping_node.location = -1400,-300
    mapping_node.inputs['Scale'].default_value[0] = text_scale
    mapping_node.inputs['Scale'].default_value[1] = text_scale
    mapping_node.inputs['Scale'].default_value[2] = text_scale

    voronoi_node = nodes.new(type="ShaderNodeTexVoronoi")
    voronoi_node.location = -1000,-300
    voronoi_node.inputs[1].default_value = 200

    noise_node = nodes.new(type="ShaderNodeTexNoise")
    noise_node.location = -1000,-600
    noise_node.inputs[1].default_value = 600.0
    noise_node.inputs[2].default_value = 2.0
    noise_node.inputs[3].default_value = 5.0

    noise_node2 = nodes.new(type="ShaderNodeTexNoise")
    noise_node2.location = -1000,-900
    noise_node2.inputs[1].default_value = 10.0
    noise_node2.inputs[2].default_value = 2.0
    noise_node2.inputs[3].default_value = 80.0

    colorramp_node = nodes.new(type="ShaderNodeValToRGB")
    colorramp_node.location = -800,-300
    colorramp_node.color_ramp.elements[0].position = 0.5
    colorramp_node.color_ramp.elements[1].position = 0.65
    colorramp_node.color_ramp.elements[0].color = (1, 1, 1, 1)
    colorramp_node.color_ramp.elements[1].color = (0, 0, 0, 1)

    colorramp_node2 = nodes.new(type="ShaderNodeValToRGB")
    colorramp_node2.location = -800,-600
    colorramp_node2.color_ramp.elements[0].position = 0.25
    colorramp_node2.color_ramp.elements[1].position = 0.8
    colorramp_node2.color_ramp.elements[0].color = (1, 1, 1, 1)
    colorramp_node2.color_ramp.elements[1].color = (0, 0, 0, 1)

    colorramp_node3 = nodes.new(type="ShaderNodeValToRGB")
    colorramp_node3.location = -800,-900
    colorramp_node3.color_ramp.elements[0].position = 0.51
    colorramp_node3.color_ramp.elements[1].position = 0.675
    colorramp_node3.color_ramp.elements[0].color = (1, 1, 1, 1)
    colorramp_node3.color_ramp.elements[1].color = (0, 0, 0, 1)

    mix_node1 = nodes.new(type="ShaderNodeMixRGB")
    mix_node1.location = -400,-600
    mix_node1.blend_type = 'VALUE'
    mix_node1.inputs[0].default_value = 0.5

    mix_node2 = nodes.new(type="ShaderNodeMixRGB")
    mix_node2.location = -200,-300
    mix_node2.blend_type = 'VALUE'
    mix_node2.inputs[0].default_value = 0.66

    bump_node = nodes.new(type="ShaderNodeBump")
    bump_node.location = 0,-300
    bump_node.inputs[0].default_value = strength
    bump_node.inputs[1].default_value = 1.0

    links = mat.node_tree.links
    link = links.new(coordinates_node.outputs[3], mapping_node.inputs[0])
    link = links.new(mapping_node.outputs[0], voronoi_node.inputs[0])
    link = links.new(voronoi_node.outputs[0], colorramp_node.inputs[0])
    link = links.new(colorramp_node.outputs[0], mix_node2.inputs[1])
    link = links.new(mapping_node.outputs[0], noise_node.inputs[0])
    link = links.new(mapping_node.outputs[0], noise_node2.inputs[0])
    link = links.new(noise_node.outputs[0], colorramp_node2.inputs[0])
    link = links.new(noise_node2.outputs[0], colorramp_node3.inputs[0])
    link = links.new(colorramp_node2.outputs[0], mix_node1.inputs[1])
    link = links.new(colorramp_node3.outputs[0], mix_node1.inputs[2])
    link = links.new(mix_node1.outputs[0], mix_node2.inputs[2])
    link = links.new(mix_node2.outputs[0], bump_node.inputs['Height'])
    link = links.new(bump_node.outputs[0], node_principled.inputs['Normal'])

  elif style_vals[0] == 'pulver':
    try:
      strength = float( style_vals[1] )
    except:
      strength = 0.08
    try:
      text_scale = float(style_vals[2])
    except:
      text_scale = 1.0
    coordinates_node = nodes.new(type="ShaderNodeTexCoord")
    coordinates_node.location = -1400,-300

    mapping_node = nodes.new(type="ShaderNodeMapping")
    mapping_node.location = -1100,-300
    mapping_node.inputs['Scale'].default_value[0] = 200*text_scale
    mapping_node.inputs['Scale'].default_value[1] = 200*text_scale
    mapping_node.inputs['Scale'].default_value[2] = 200*text_scale


    noise_node = nodes.new(type="ShaderNodeTexNoise")
    noise_node.location = -700,-300
    noise_node.inputs[1].default_value = 5.0
    noise_node.inputs[2].default_value = 2.0
    noise_node.inputs[3].default_value = 0.0

    bump_node = nodes.new(type="ShaderNodeBump")
    bump_node.location = 0,-300
    bump_node.inputs[0].default_value = strength
    bump_node.inputs[1].default_value = 1.0

    links = mat.node_tree.links
    link = links.new(coordinates_node.outputs[3], mapping_node.inputs[0])
    link = links.new(mapping_node.outputs[0], noise_node.inputs[0])
    link = links.new(noise_node.outputs[0], bump_node.inputs['Height'])
    link = links.new(bump_node.outputs[0], node_principled.inputs['Normal'])
  #
  # Link the nodes together
  #
  links = mat.node_tree.links
  if node_texture:
    link = links.new(node_texture.outputs[0], node_principled.inputs['Base Color'])
  if node_normalmap:
    link = links.new(node_normalmap.outputs[0], node_normalvector.inputs[1])
    link = links.new(node_normalvector.outputs[0], node_principled.inputs['Normal']) #needs to find the link by name, doesn't connect otherwise??
  link = links.new(node_principled.outputs[0], node_output.inputs[0])
  if node_noise and node_math:
    link = links.new(node_noise.outputs[1], node_math.inputs[0])
    link = links.new(node_math.outputs[0], node_output.inputs[2])
  return mat


def setup_transparent_shader(mat, col, transparency=0.5):
  # col is already gamma-corrected by the caller (setupMaterial line ~88).
  # Do NOT gamma-correct again here - that was the old double-gamma bug that
  # pushed colours into x**4.84 territory and made transparent parts look black.
  # Use BLEND blend_method (not HASHED) to avoid grain/noise on low-sample renders.
  mat.blend_method = 'BLEND'
  nodes = mat.node_tree.nodes
  for node in nodes:
    nodes.remove(node)
  # Mix between a coloured principled shader and a pure transparent shader
  # based on the VC opacity. This keeps the object's tint visible instead of
  # washing everything out to near-white (old x*0.2+0.8 behaviour).
  node_principled = nodes.new(type="ShaderNodeBsdfPrincipled")
  node_principled.location = 0,100
  node_principled.inputs['Roughness'].default_value = 0.05
  # Keep Transmission Weight low here - the Transparent BSDF mix node handles
  # the see-through effect. High Transmission + Alpha mix = grain/noise.
  node_principled.inputs['Transmission Weight'].default_value = 0.0
  # Principled Alpha feeds the BLEND pipeline so we get proper depth sorting.
  node_principled.inputs['Alpha'].default_value = max(transparency, 0.01)
  if len(col) == 3:
    ccolor = [0,0,0,1]
    ccolor[:3] = col
    col = tuple(ccolor)
  node_principled.inputs['Base Color'].default_value = col

  node_transparent = nodes.new(type="ShaderNodeBsdfTransparent")
  node_transparent.location = 0,-150

  node_mix = nodes.new(type="ShaderNodeMixShader")
  node_mix.location = 300,0
  # transparency=1 -> fully opaque principled, transparency=0 -> fully transparent
  node_mix.inputs[0].default_value = 1.0 - max(transparency, 0.0)

  node_output = nodes.new(type='ShaderNodeOutputMaterial')
  node_output.location = 600,0
  links = mat.node_tree.links
  links.new(node_principled.outputs[0], node_mix.inputs[1])
  links.new(node_transparent.outputs[0], node_mix.inputs[2])
  links.new(node_mix.outputs[0], node_output.inputs[0])
  return mat

def setupShadowCatcher(mat_name, color):
  node_noise,node_math = None, None
  mat = bpy.data.materials.new(name=mat_name)
  mat.use_nodes = True
  nodes = mat.node_tree.nodes
  for node in nodes:
    nodes.remove(node)

  node_principled = nodes.new(type="ShaderNodeBsdfPrincipled")
  node_principled.location = 200,0
  if len(color) == 3:
    ccolor = [0,0,0,1]
    ccolor[:3] = color
    color = tuple(ccolor)
  color = [x**2.2 for x in color] # gamma correction
  node_principled.inputs['Base Color'].default_value = color

  node_output = nodes.new(type='ShaderNodeOutputMaterial')   
  node_output.location = 600,0
  
  node_diffuse = nodes.new(type='ShaderNodeBsdfDiffuse')
  node_diffuse.location = -600,-200
  
  node_shader2rgb = nodes.new(type='ShaderNodeShaderToRGB')
  node_shader2rgb.location = -400,-200

  node_colorramp = nodes.new(type='ShaderNodeValToRGB')
  node_colorramp.location = -200,-200

  node_colorramp.color_ramp.elements[0].position = 0.0
  node_colorramp.color_ramp.elements[0].color = (1,1,1,1)
  node_colorramp.color_ramp.elements[1].position = 0.3
  node_colorramp.color_ramp.elements[1].color = (0,0,0,1)

  links = mat.node_tree.links
  link = links.new(node_diffuse.outputs[0], node_shader2rgb.inputs[0])
  link = links.new(node_shader2rgb.outputs[0], node_colorramp.inputs[0])
  link = links.new(node_colorramp.outputs[0], node_principled.inputs['Alpha'])
  link = links.new(node_principled.outputs[0], node_output.inputs[0])

  mat.blend_method = 'BLEND'

  return mat
