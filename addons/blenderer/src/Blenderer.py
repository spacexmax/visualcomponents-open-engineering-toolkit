# -*- coding: utf-8 -*-
# Blenderer Addon version 2026-08 v2.6.0 (Blender 5.2)
# with VisualComponents
# ################Thanks for Tang ###########################
from vcCommand import *
import vcHelpers.Selection as selection
from collections import defaultdict
import vcMatrix, vcVector
import os, sys, os.path, csv
import math
import subprocess
import time
import sys
import xml.etree.cElementTree as ET
import export_from_vc
import tempfile, shutil
from pprint import pprint
import ctypes
import msvcrt
reload(export_from_vc)


DEG2RAD = math.radians(1)
RAD2DEG = math.degrees(1)
LINECHANGE = '\n'
cmd = getCommand()
app = getApplication()
app2 = getApplication() #two app objects for two separate OnRender events
camera = app.findCamera()
if not camera:
    print 'Blenderer Error: No camera found in the scene. Please add a camera before rendering.'


sim = getSimulation()
SCALE = 0.001
rec_file = False
animation_recorded = False
animation_timing = None


def OnStart():
  global blender_exe_uri_prop, prop_defaults_dict, user_settings_uri, user_settings, persistent_props
  reload( export_from_vc )
  thefolder, commandfilename = os.path.split(getCommandPath()[8:])
  thefolder = thefolder.decode('utf8')
  # Register Chinese localization as fallback for XAML-based localization
  # (XAML files: Blenderer_2_6_0__2026_0801.PyResource.*.xaml)
  try:
    import BlenderAddOn_Language
    localize = app.findCommand('netCommand')
    BlenderAddOn_Language.register_localization(cmd.Name, localize)
  except Exception:
    pass
  # clear possible render limit frame
  geocont = sim.World.UserGeometry
  geocont.clear()
  app.render()
  #
  # read default settings
  #
  prop_defaults_dict = read_settings(os.path.join(thefolder, 'defaults.xml'))
  user_settings_uri = os.path.join(as_unicode(os.environ['LOCALAPPDATA']),
                                   'Visual Components', 'Blenderer', 'settings.xml')
  user_settings = read_settings(user_settings_uri)
  persistent_props = {}
  #
  # # DEFAULT TAB
  #
  global outputFolderProp, imageNameProp, tempuriProp, samplesProp, resProp, resXProp, resYProp, portraitProp, reRender_prop, renderstill_prop, presetProp, preset_tree, temproot_uri
  pictures = os.path.join(as_unicode(os.environ.get('USERPROFILE', thefolder)), 'Pictures')
  renderuri = os.path.join(pictures, 'Blenderer', 'Picture.png')
  _, legacy_output = getDefaultValue('Output file', VC_URI, [])
  folder, name = split_output(legacy_output or renderuri, os.path.dirname(renderuri),
                              'Picture', ('.png',))
  outputFolderProp = getProp(VC_STRING, 'Output folder', folder)
  global chooseFolderProp, openOutputFolderProp
  chooseFolderProp = getProp(VC_BUTTON, 'Choose output folder', True)
  chooseFolderProp.OnChanged = folder_picker_for(outputFolderProp)
  openOutputFolderProp = getProp(VC_BUTTON, 'Open output folder', True)
  openOutputFolderProp.OnChanged = folder_opener_for(outputFolderProp)
  imageNameProp = getProp(VC_STRING, 'Image name', name)
  thefolder, commandfilename = os.path.split(getCommandPath()[8:])
  temp_dir = tempfile.gettempdir()
  temproot_uri = os.path.join(temp_dir,'blenderer_temp')
  if not os.path.exists(temproot_uri):
    os.makedirs(temproot_uri)
  tempdata_uri = os.path.join(temproot_uri, 'TEMPDATA')
  if not os.path.exists(tempdata_uri):
    os.makedirs(tempdata_uri)
  #tempdata_uri = 'file///:' + tempdata_uri
  tempdata_uri = tempdata_uri.decode('utf8')
  tempuriProp = getProp(VC_URI, 'TEMPDATA_URI', str(tempdata_uri), visible = False, overwrite = False)
  samplesProp = getProp(VC_INTEGER, 'Samples', 16, visible = True, overwrite = False)
  #
  res_list = ['<Custom>', '300x300', '384x216', '640x360', '640x640' ,'1280x720', '1920x1080', '3840x2160']
  resProp = getProp(VC_STRING, 'Resolution', '1920x1080', steps = res_list, limits = [], visible = True, overwrite = False)
  resXProp = getProp(VC_INTEGER, 'ResX', 1920, visible = True, overwrite = False)
  resYProp = getProp(VC_INTEGER, 'ResY', 1080, visible = True, overwrite = False)
  resXProp.WritableWhenConnected = False
  resXProp.WritableWhenDisconnected = False
  resYProp.WritableWhenConnected = False
  resYProp.WritableWhenDisconnected = False
  portraitProp = getProp(VC_STRING, 'Page', 'Landscape', steps = ['Landscape', 'Portrait'], visible = True, overwrite = False)
  tree = getPresetTree()
  preset_tree = tree.getroot()
  preset_names = [x.get('name') for x in preset_tree]
  stepvals = preset_names
  #stepvals.sort()
  presetProp = getProp(VC_STRING, 'Lighting Preset', stepvals[0], steps = stepvals, visible = True, overwrite = False)
  if stepvals != presetProp.StepValues:
    presetProp.StepValues = stepvals

  renderstill_prop = getProp(VC_BUTTON, 'Render', True, visible = True, overwrite = False)
  reRender_prop = getProp(VC_BOOLEAN, 'Reuse Previous Scene', False, visible = True, overwrite = False)
  renderstill_prop.OnChanged = CallStill
  #   
  # LIGHTS TAB
  global addPointLightProp, addAreaLightProp, addSpotLightProp, addSunLightProp, lightStrengthProp, addSparksProp
  addPointLightProp = getProp(VC_BUTTON, 'Lights::Add Point Light', False, visible = True, overwrite = False)
  addPointLightProp.OnChanged = addLamp
  addAreaLightProp = getProp(VC_BUTTON, 'Lights::Add Area Light', False, visible = True, overwrite = False)
  addAreaLightProp.OnChanged = addLamp
  addSpotLightProp = getProp(VC_BUTTON, 'Lights::Add Spot Light', False, visible = True, overwrite = False)
  addSpotLightProp.OnChanged = addLamp
  addSunLightProp = getProp(VC_BUTTON, 'Lights::Add Sun Light', False, visible = True, overwrite = False)
  addSunLightProp.OnChanged = addLamp
  lightStrengthProp = getProp(VC_REAL, 'Lights::Default Strength', 500, visible = True, overwrite = False)
  addSparksProp = getProp(VC_BUTTON, 'Lights::Add Sparks Emitter', False, visible = True, overwrite = False)
  addSparksProp.OnChanged = addSparks
  #
  # ADVANCED TAB
  global indirectLightProp, renderedgesProp, engeThicknessProp, fovProp, showBorderProp, exposureProp, bloomProp, bloomIntensityProp
  global openinblenderProp, deviceProp, saveExposureProp, resetExposureProp
  global depthOFnodeProp, depthOfFstopProp, cameraProp, viewProp, reset_props_prop
  global renderEngineProp, cyclesBackendProp, cyclesSamplesProp
  fovProp = getProp(VC_REAL, 'Advanced::CameraFov', 33.0, visible = True, overwrite = False, unit = 'Angle', magnitude = 1.0)
  showBorderProp = getProp(VC_BOOLEAN, 'Advanced::Show Border', False, visible = True, overwrite = False)
  showBorderProp.OnChanged = showBorderChangedEvent
  exposureProp = getProp(VC_REAL, 'Advanced::Exposure', 0.0, visible = True, overwrite = False)
  saveExposureProp = getProp(VC_BUTTON, 'Advanced::Save preset exposure', True)
  saveExposureProp.OnChanged = save_preset_exposure
  resetExposureProp = getProp(VC_BUTTON, 'Advanced::Reset preset exposure', True)
  resetExposureProp.OnChanged = reset_preset_exposure
  apply_preset_exposure()
  bloomProp = getProp(VC_BOOLEAN, 'Advanced::Bloom', False, visible = True, overwrite = False)
  bloomIntensityProp = getProp(VC_REAL, 'Advanced::Bloom Intensity', 0.1, visible = True, overwrite = False)
  openinblenderProp = getProp(VC_BOOLEAN, 'Advanced::Open in Blender', False, visible = True, overwrite = False)
  # Render engine selector: EEVEE (default, all existing settings apply) or Cycles.
  # When Cycles is selected, the Cycles-specific options below become visible.
  renderEngineProp = getProp(VC_STRING, 'Advanced::Render Engine', 'EEVEE', steps = ['EEVEE', 'Cycles'], visible = True, overwrite = False)
  # Cycles device: CPU or GPU (visible only when engine == Cycles)
  deviceProp = getProp(VC_STRING, 'Advanced::RenderDevice', 'GPU', steps = ['GPU'], visible = False, overwrite = False)
  # Cycles GPU compute backend (visible only when engine == Cycles and device == GPU)
  cyclesBackendProp = getProp(VC_STRING, 'Advanced::OnlyCyclesBackend', 'CUDA', steps = ['CUDA', 'OptiX', 'HIP', 'oneAPI'], visible = False, overwrite = False)
  # Cycles render samples (visible only when engine == Cycles and device == GPU)
  cyclesSamplesProp = getProp(VC_INTEGER, 'Advanced::OnlyCyclesSamples', 64, steps = [64, 128, 256], visible = False, overwrite = False)
  renderEngine_changed(None)
  renderedgesProp = getProp(VC_BOOLEAN, 'Advanced::Render Edges', False, visible = True, overwrite = False)
  engeThicknessProp = getProp(VC_INTEGER, 'Advanced::Edge Thickness', 3, visible = True, overwrite = False)
  depthOFnodeProp = getProp('Ref<Node>', 'Advanced::DepthOfFieldNode', None, visible = True, overwrite = False)
  depthOfFstopProp = getProp(VC_REAL, 'Advanced::Depth F-Stop', 2.8, visible = True, overwrite = False) 
  indirectLightProp = getProp(VC_STRING, 'Advanced::Indirect Lighting', 'Off', steps = ['Off', 'Fast', 'Normal', 'HQ'], visible = True, overwrite = False)
  blender_exe_uri_prop = getProp(VC_URI, 'Advanced::Blender Executable', '', visible = True, overwrite = False)
  reset_props_prop = getProp(VC_BUTTON, 'Advanced::Reset All Properties', True, visible = True, overwrite = False)
  reset_props_prop.OnChanged = reset_all_props
  #
  # MATERIALS TAB
  global materialTableProp, tableSeparatorProp, robotMaterials, monochromeProp, simpleTransparentProp, materialVersionProp
  materialTableProp = getProp(VC_STRING, 'Materials::Mode', 'Default', steps = ['Default','Read From Table', 'Write To Table'], visible = True, overwrite = False)
  tableSeparatorProp = getProp(VC_STRING, 'Materials::Table Delimiter', ';', steps = [';', ','], visible = True, overwrite = False)
  robotMaterials = getProp(VC_STRING, 'Materials::Robot Materials', 'Smart Materials', steps = ['Default', 'Smart Materials'], visible = True, overwrite = False)
  monochromeProp = getProp('Ref<Material>', 'Materials::Monochrome Override', None, visible = True, overwrite = False)
  simpleTransparentProp = getProp(VC_BOOLEAN, 'Materials::UseSimpleTransparent', False, visible = True, overwrite = False)
  # Material version: OLD keeps legacy pipeline; NEW maps VC<->Blender more
  # accurately (standard sRGB->Linear, glass transmission, physical lights).
  materialVersionProp = getProp(VC_STRING, 'Materials::MaterialVersion', 'OLD', steps = ['OLD', 'NEW'], visible = True, overwrite = False)
  # 
  # ANIMATION TAB
  global recanim_prop, startanim_prop, endanim_prop, stepanim_prop, fpsanim_prop, videocontainer_prop, renderanim_prop
  global renderVideoModeProp, videoQualityProp
  global animationFolderProp, animationNameProp, chooseAnimationFolderProp, openAnimationFolderProp
  _, legacy_animation = getDefaultValue('Animation::Output file', VC_URI, [])
  folder, name = animation_output_defaults(legacy_animation, legacy_output, os.path.dirname(renderuri))
  animationFolderProp = getProp(VC_STRING, 'Animation::Output folder', folder)
  chooseAnimationFolderProp = getProp(VC_BUTTON, 'Animation::Choose output folder', True)
  chooseAnimationFolderProp.OnChanged = folder_picker_for(animationFolderProp)
  openAnimationFolderProp = getProp(VC_BUTTON, 'Animation::Open output folder', True)
  openAnimationFolderProp.OnChanged = folder_opener_for(animationFolderProp)
  animationNameProp = getProp(VC_STRING, 'Animation::Video name', name)
  recanim_prop = getProp(VC_BOOLEAN, 'Animation::RecAnimation', False, visible = True, overwrite = True)
  recanim_prop.OnChanged = InitAnim
  startanim_prop = getProp(VC_REAL, 'Animation::Start', 5.0, visible = True, overwrite = False, unit = 'Time', magnitude = 1.0)
  endanim_prop = getProp(VC_REAL, 'Animation::End', 10.0, visible = True, overwrite = False, unit = 'Time', magnitude = 1.0)
  stepanim_prop = getProp(VC_REAL, 'Animation::Rec step', 1.0/25.0, visible = True, overwrite = False, unit = 'Time', magnitude = 1.0)
  fpsanim_prop = getProp(VC_INTEGER, 'Animation::FPS', 25, visible = True, overwrite = False)
  update_animation_fps(None)
  fpsanim_prop.WritableWhenConnected = False
  fpsanim_prop.WritableWhenDisconnected = False
  videocontainer_prop = getProp(VC_STRING, 'Animation::Container', 'MP4', steps = ['MP4'], visible = True, overwrite = False)
  # Video rendering strategy (applies ONLY to animation/video, never to still images):
  #   'PNG Sequence' : render each frame to PNG, then merge via VSE + FFMPEG.
  #                    Keeps the intermediate PNG frames on disk.
  #   'Direct Video'  : render straight to MP4 with no PNG intermediates.
  #                    Faster + smaller disk footprint; not re-editable frame-by-frame.
  renderVideoModeProp = getProp(VC_STRING, 'Animation::RenderVideoMode', 'PNG Sequence', steps = ['PNG Sequence', 'Direct Video'], visible = True, overwrite = False)
  # Video quality (applies ONLY to animation/video, never to still images):
  #   'Lossless' : perceptually lossless (visually indistinguishable from source)
  #   'High'     : high quality, balanced size  [default]
  #   'Low'      : low quality, smallest file
  videoQualityProp = getProp(VC_STRING, 'Animation::VideoQuality', 'High', steps = ['Lossless', 'High', 'Low'], visible = True, overwrite = False)
  renderanim_prop = getProp(VC_BUTTON, 'Animation::RenderAnimation', True, visible = True, overwrite = False)
  renderanim_prop.OnChanged = CallAnim
  #
  # ENV TAB
  global envtypeProp, envimageProp, envcolorProp, envstrengthProp, envRotationProp, envvisibleProp
  global backdropTypeProp, backdropImageProp, backdropRgbProp
  thefolder, commandfilename = os.path.split(getCommandPath()[8:])
  envmapuri = ''
  hdri_strength = 0
  current_preset = [x for x in preset_tree if x.get("name") == presetProp.Value]
  if current_preset:
    current_preset = current_preset[0]
    hdri_element = current_preset.find('hdri')
    if hdri_element!=None: # must compare to none
      hdri_uri = hdri_element.get('file')
      hdri_uri = hdri_uri.decode('utf8')
      hdri_strength = hdri_element.get('strength')
      envmapuri = os.path.join('file:///', thefolder , 'Lights\\Presets' , hdri_uri)
  envtypeProp = getProp(VC_STRING, 'Env::Background', 'Image', steps = ['Image', 'ColorRGB'], visible = True, overwrite = False)
  envimageProp = getProp(VC_URI, 'Env::Image', envmapuri, visible = True, overwrite = False)
  envcolorProp = getProp(VC_VECTOR, 'Env::ColorRGB', vcVector.new(1,1,1), visible = False, overwrite = False)
  envstrengthProp = getProp(VC_REAL, 'Env::Strength', float(hdri_strength), visible = True, overwrite = False)
  if envstrengthProp.Name not in user_settings:
    envstrengthProp.Value = float(hdri_strength)
  envtypeChanged(envtypeProp)
  envRotationProp = getProp(VC_REAL, 'Env::Rotation', 0.0, visible = True, overwrite = False)
  envvisibleProp = getProp(VC_BOOLEAN, 'Env::Visible', True, visible = True, overwrite = False)
  backdropTypeProp = getProp(VC_STRING, 'Env::BackdropType', 'None', steps = ['None', 'Image', 'ColorRGB'], visible = True, overwrite = False)
  backdropImageProp = getProp(VC_URI, 'Env::BackdropImage', envmapuri, visible = True, overwrite = False)
  backdropRgbProp = getProp(VC_VECTOR, 'Env::BackdropColorRGB', vcVector.new(1,1,1), visible = True, overwrite = False)
  backdrop_props_visibility('void')

  #
  # FLOOR TAB
  global floorvisibleProp, floorsizeProp, floortypeProp, floorcolorimageProp, floorbumpimageProp, floortexturesizeProp, floorcolorProp, floorbumpstrengthProp
  floorvisibleProp = getProp(VC_BOOLEAN, 'Floor::Visible', True, visible = True, overwrite = False)
  floorsizeProp = getProp(VC_REAL, 'Floor::BorderSize', 6000, visible = True, overwrite = False, unit = 'Distance', magnitude = 1.0)
  floortypes_list = sorted(floortextures.keys())
  floortypeProp = getProp(VC_STRING, 'Floor::Style', 'SlateBrown', steps = floortypes_list, visible = True, overwrite = False)
  floor_defaults = floortextures[floortypeProp.Value]
  floorcolorimageProp = getProp(VC_URI, 'Floor::ColorTexture', floor_defaults[0], visible = True, overwrite = False)
  floorbumpimageProp = getProp(VC_URI, 'Floor::BumpTexture', floor_defaults[1], visible = True, overwrite = False)
  floorbumpstrengthProp = getProp(VC_REAL, 'Floor::BumpStrength', floor_defaults[2], visible = True, overwrite = False)
  floortexturesizeProp = getProp(VC_REAL, 'Floor::TextureSize', floor_defaults[3], visible = True, overwrite = False)
  floorcolorProp = getProp(VC_VECTOR, 'Floor::ColorRGB', vcVector.new(.8,.8,.8), visible = True, overwrite = False)
  if floortexturesizeProp.Name not in user_settings:
    floortexturesizeProp.Value = floor_defaults[3]
  resChanged(None)
  callbacks = {
    'Resolution': resChanged, 'ResX': showBorderChangedEvent, 'ResY': showBorderChangedEvent,
    'Page': fovChangedEvent, 'Lighting Preset': setEnvHDRI,
    'Advanced::CameraFov': fovChangedEvent, 'Advanced::Render Engine': renderEngine_changed,
    'Advanced::RenderDevice': cyclesDevice_changed, 'Animation::Rec step': update_animation_fps,
    'Env::Background': envtypeChanged, 'Env::Visible': backdrop_props_visibility,
    'Env::BackdropType': backdrop_props_visibility, 'Floor::Style': floortypeChanged,
  }
  for name, (prop, ptype) in persistent_props.items():
    prop.OnChanged = settings_changed(name, callbacks.get(name))
  executeInActionPanel()
  #


def backdrop_props_visibility(arg):
  if envvisibleProp.Value == True:
    backdropTypeProp.IsVisible = False
    backdropRgbProp.IsVisible = False
    backdropImageProp.IsVisible = False
  else:
    backdropTypeProp.IsVisible = True
    backdropRgbProp.IsVisible = False
    backdropImageProp.IsVisible = False
    if backdropTypeProp.Value == 'Image':
      backdropImageProp.IsVisible = True
    if backdropTypeProp.Value == 'ColorRGB':
      backdropRgbProp.IsVisible = True


def renderEngine_changed(arg):
  # Toggle visibility of Cycles-specific properties based on engine selection.
  # EEVEE: all Cycles options hidden (existing EEVEE settings remain unchanged).
  # Cycles: device selector visible; backend + samples visible only when GPU.
  is_cycles = renderEngineProp.Value == 'Cycles'
  deviceProp.IsVisible = is_cycles
  if is_cycles and deviceProp.Value == 'GPU':
    cyclesBackendProp.IsVisible = True
    cyclesSamplesProp.IsVisible = True
  else:
    cyclesBackendProp.IsVisible = False
    cyclesSamplesProp.IsVisible = False


def cyclesDevice_changed(arg):
  # When the Cycles device changes, update backend/samples visibility.
  if renderEngineProp.Value == 'Cycles' and deviceProp.Value == 'GPU':
    cyclesBackendProp.IsVisible = True
    cyclesSamplesProp.IsVisible = True
  else:
    cyclesBackendProp.IsVisible = False
    cyclesSamplesProp.IsVisible = False




def reset_all_props(arg=None):
  global animation_recorded
  try:
    update_user_settings(None)
  except Exception as error:
    print 'Blenderer: could not reset user settings:', error
    return
  animation_recorded = False
  for prop in cmd.Properties:
    cmd.deleteProperty(prop)
  cmd.execute()


def etree_to_dict(t):
  d = {t.tag: {} if t.attrib else None}
  children = list(t)
  if children:
    dd = defaultdict(list)
    for dc in map(etree_to_dict, children):
      for k, v in dc.items():
        dd[k].append(v)
    d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
  if t.attrib:
    d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
  if t.text:
    text = t.text.strip()
    if children or t.attrib:
      if text:
        d[t.tag]['#text'] = text
    else:
      d[t.tag] = text
  return d

def as_unicode(value):
  if isinstance(value, bytes):
    try:
      return value.decode('utf-8')
    except UnicodeDecodeError:
      return value.decode('mbcs')
  return unicode(value)


def read_settings(path):
  if not os.path.isfile(path):
    return {}
  try:
    root = ET.parse(path).getroot()
    if root.tag != 'defaults':
      raise ValueError('expected a defaults element')
    return dict((item.get('name'), item.get('value')) for item in root.findall('property')
                if item.get('name') is not None and item.get('value') is not None)
  except Exception as error:
    print 'Blenderer: could not read settings:', error
    return {}


def update_user_settings(changes):
  folder = os.path.dirname(user_settings_uri)
  if not os.path.isdir(folder):
    try:
      os.makedirs(folder)
    except OSError:
      if not os.path.isdir(folder):
        raise
  # Windows releases the lock if VC exits while saving.
  with open(os.path.join(folder, 'settings.lock'), 'a+b') as lock:
    lock.seek(0)
    msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
    if changes is None:
      if os.path.isfile(user_settings_uri):
        os.remove(user_settings_uri)
      user_settings.clear()
      return
    values = read_settings(user_settings_uri)
    for name, value in changes.items():
      if value is None:
        values.pop(name, None)
      else:
        values[name] = value
    root = ET.Element('defaults')
    for name, value in sorted(values.items()):
      ET.SubElement(root, 'property', name=name, value=value)
    fd, temporary = tempfile.mkstemp(dir=folder, suffix='.xml')
    os.close(fd)
    try:
      ET.ElementTree(root).write(temporary, encoding='utf-8', xml_declaration=True)
      # MOVEFILE_REPLACE_EXISTING. The temporary file is on the same volume.
      if not ctypes.windll.kernel32.MoveFileExW(temporary, user_settings_uri, 1):
        raise ctypes.WinError()
      user_settings.clear()
      user_settings.update(values)
    finally:
      if os.path.exists(temporary):
        os.remove(temporary)


TEXTURE_SETTINGS = ('Env::Image', 'Env::BackdropImage',
                    'Floor::ColorTexture', 'Floor::BumpTexture')
BUNDLED_TEXTURE_PREFIX = u'blenderer-resource:'


def bundled_texture_path(path):
  parts = path.replace(u'\\', u'/').split(u'/')
  if parts[-1] in (u'', u'.', u'..') or u':' in parts[-1]:
    return None
  if len(parts) >= 3 and [part.lower() for part in parts[-3:-1]] == [u'lights', u'presets']:
    return os.path.join(u'Lights', u'Presets', parts[-1])
  if len(parts) >= 2 and parts[-2].lower() == u'textures':
    return os.path.join(u'Textures', parts[-1])
  return None


def texture_setting_value(value, folder, default, saving=False):
  path = os.path.normpath(output_path(value))
  if saving:
    relative = bundled_texture_path(path)
    if relative and os.path.normcase(path) == os.path.normcase(os.path.join(folder, relative)) and os.path.isfile(path):
      return BUNDLED_TEXTURE_PREFIX + relative.replace(u'\\', u'/')
    return value

  if value.startswith(BUNDLED_TEXTURE_PREFIX):
    stored = value[len(BUNDLED_TEXTURE_PREFIX):].replace(u'\\', u'/')
    relative = bundled_texture_path(stored)
    if not relative or relative.replace(u'\\', u'/').lower() != stored.lower():
      return default
  else:
    # Legacy builds stored absolute paths. Rebase only missing assets from a
    # recognizable Blenderer install, leaving custom files and external paths alone.
    relative = bundled_texture_path(path)
    if not relative or not os.path.isabs(path) or os.path.isfile(path):
      return value
    old_folder = path[:-len(relative)].rstrip(u'\\/')
    parent, addon = os.path.split(old_folder)
    command_parent, python_dir = os.path.split(parent)
    if not (addon.lower().startswith(u'blenderer') and python_dir.lower() == u'python 2'
            and os.path.basename(command_parent).lower() == u'my commands'):
      return value
  current = os.path.join(folder, relative)
  return u'file:///' + current if os.path.isfile(current) else default


def settings_changed(name, callback):
  def on_changed(arg):
    if callback:
      callback(arg)
    prop, ptype = persistent_props[name]
    value = prop.Value
    if ptype == VC_VECTOR:
      value = u'|'.join(as_unicode(part) for part in (value.X, value.Y, value.Z))
    else:
      value = as_unicode(value)
    if name in TEXTURE_SETTINGS:
      folder = os.path.dirname(output_path(getCommandPath()))
      value = texture_setting_value(value, folder, None, saving=True)
    try:
      update_user_settings({name: value})
    except Exception as error:
      print 'Blenderer: could not save user settings:', error
  return on_changed


def getDefaultValue(pname, ptype, steps):
  for settings in (user_settings, prop_defaults_dict):
    if pname not in settings:
      continue
    ok, value = parse_setting(settings[pname], ptype)
    if ok and (not steps or value in steps):
      return True, value
  return False, None


def parse_setting(raw_value, ptype):
  value = None
  ok = False
  if ptype == VC_BOOLEAN:
    raw_value = raw_value.strip().lower()
    ok = raw_value in ('true', 'false', '1', '0')
    value = raw_value in ('true', '1')
  elif ptype == VC_INTEGER:
    try:
      value = int(raw_value)
      ok = True
    except Exception, e:
      pass
  elif ptype == VC_REAL:
    try:
      value = float(raw_value)
      ok = True
    except Exception, e:
      pass
  elif ptype == VC_VECTOR:
    try:
      vals = [float(x) for x in raw_value.split('|')]
      value = vcVector.new(*vals)
      ok = True
    except Exception, e:
      pass
  elif ptype in (VC_STRING, VC_URI):
    value = raw_value
    ok = True
  else:
    print 'Blenderer: non supported value type in defaults.xml:',ptype,'|', raw_value
  return ok, value


def getProp(ptype, pname, pval, steps = [], limits = [], visible = True, overwrite = False, unit = '', magnitude = 1.0):
  owner = cmd
  p = owner.getProperty(pname)
  if p and overwrite:
    owner.deleteProperty(p)
  elif p:
    register_setting(p, ptype, pname, overwrite)
    if pname in persistent_props:
      p.OnChanged = None
    if pname in TEXTURE_SETTINGS:
      folder = os.path.dirname(output_path(getCommandPath()))
      current = as_unicode(p.Value)
      restored = texture_setting_value(current, folder, pval)
      if restored != current:
        p.Value = as_unicode(restored).encode('utf-8')
    return p
  default_available, default_value = getDefaultValue(pname, ptype, steps)
  if steps:
    p = owner.createProperty(ptype,pname,VC_PROPERTY_STEP)
    p.StepValues = steps
  elif limits:
    p = owner.createProperty(ptype,pname,VC_PROPERTY_LIMIT)
    p.MinLimits = limits[0]
    p.MaxLimits = limits[1]
  else:
    p = owner.createProperty(ptype,pname)
  if ptype != VC_BUTTON:
    if default_available:
      if pname in TEXTURE_SETTINGS:
        folder = os.path.dirname(output_path(getCommandPath()))
        default_value = texture_setting_value(default_value, folder, pval)
      pval = default_value
    if isinstance(pval, unicode):
      pval = pval.encode('utf-8')
    p.Value = pval
  p.IsVisible = visible
  if unit:
    p.Quantity = unit
    p.Magnitude = magnitude
  register_setting(p, ptype, pname, overwrite)
  return p


def register_setting(prop, ptype, name, overwrite):
  transient = ('TEMPDATA_URI', 'Reuse Previous Scene', 'Advanced::Show Border', 'Advanced::Exposure')
  if not overwrite and name not in transient and ptype in (
      VC_BOOLEAN, VC_INTEGER, VC_REAL, VC_STRING, VC_URI, VC_VECTOR):
    persistent_props[name] = (prop, ptype)


def sanitizefilename(fname):
  suspiciouscharacters = [r'/', '\\' ,'#',':',';','!','¤','%','&','?','^','*',' ','\t']
  for c in suspiciouscharacters:
    fname = fname.replace(c,'_')
  return fname


def resChanged(arg):
  if resProp.Value == '<Custom>':
    resXProp.WritableWhenConnected = True
    resXProp.WritableWhenDisconnected = True
    resYProp.WritableWhenConnected = True
    resYProp.WritableWhenDisconnected = True
  else:
    resXProp.WritableWhenConnected = False
    resXProp.WritableWhenDisconnected = False
    resYProp.WritableWhenConnected = False
    resYProp.WritableWhenDisconnected = False
    vals = [int(x) for x in resProp.Value.split('x')]
    resXProp.Value = vals[0]
    resYProp.Value = vals[1]


def output_path(value):
  path = as_unicode(value)
  return path[8:] if path.startswith('file:///') else path


def split_output(value, default_folder, default_name, extensions):
  path = output_path(value)
  if path.endswith(('\\', '/')) or os.path.isdir(path):
    return path, default_name
  folder, name = os.path.split(path)
  stem, ext = os.path.splitext(name)
  if extensions is None or ext.lower() in extensions:
    name = stem
  return folder or default_folder, name or default_name


def animation_output_defaults(legacy_animation, legacy_image, folder):
  if legacy_animation:
    # The old animation importer discarded the last extension before adding .mp4.
    return split_output(legacy_animation, folder, 'Animation', None)
  if legacy_image:
    folder, _ = split_output(legacy_image, folder, 'Picture', ('.png',))
  return folder, 'Animation'


def render_output_path(folder, name, default_name, extension):
  folder = output_path(folder).strip()
  drive = os.path.splitdrive(folder)[0]
  if not drive or not os.path.isabs(folder):
    raise ValueError('AbsoluteFolder')
  name = as_unicode(name).strip() or default_name
  if any(char in u'<>:"/\\|?*' or ord(char) < 32 for char in name) or name.endswith('.'):
    raise ValueError('InvalidName')
  if name.split('.')[0].upper().rstrip() in ('CON', 'PRN', 'AUX', 'NUL') + tuple(
      prefix + str(number) for prefix in ('COM', 'LPT') for number in range(1, 10)):
    raise ValueError('ReservedName')
  if name.lower().endswith(extension):
    stem = name[:-len(extension)]
    if stem and stem == stem.rstrip(' .'):
      return os.path.join(folder, name)
    if stem:
      raise ValueError('TrailingName')
    name = default_name
  return os.path.join(folder, name + extension)


def folder_opener_for(folder_prop):
  def open_folder(arg):
    folder = output_path(folder_prop.Value).strip()
    try:
      if os.path.isabs(folder) and os.path.isdir(folder):
        os.startfile(os.path.normpath(folder))
        return
    except (OSError, ValueError):
      preflight_error('OpenFolderFailed', 'Could not open the output folder.', folder)
      return
    preflight_error('OpenFolderMissing', 'The output folder does not exist. Choose an existing folder.', folder)
  return open_folder


def folder_picker_for(folder_prop):
  def choose_folder(arg):
    print 'Blenderer: opening output folder picker'
    try:
      folder = browse_output_folder(folder_prop.Value)
      if folder is not None:
        folder_prop.Value = folder.encode('utf-8')
    except Exception as error:
      print 'Blenderer: folder picker failed:', error
      app.messageBox('Could not open the folder picker. Enter the output folder manually.',
                     'Blenderer', VC_MESSAGE_TYPE_ERROR, VC_MESSAGE_BUTTONS_OK)
  return choose_folder


def browse_output_folder(initial_folder):
  # Run the modal Windows Forms picker in its own STA process. Calling the
  # shell picker directly from the VC command callback can block without UI.
  script = r"""
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
$owner = New-Object System.Windows.Forms.Form
$owner.ShowInTaskbar = $false
$owner.TopMost = $true
$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = 'Select the output folder'
$dialog.ShowNewFolderButton = $true
try {
  $initial = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String([string]$env:BLENDERER_PICKER_INITIAL))
  if ($initial -and [IO.Directory]::Exists($initial)) {
    $dialog.SelectedPath = $initial
  }
  if ($dialog.ShowDialog($owner) -eq [System.Windows.Forms.DialogResult]::OK) {
    [Console]::Write([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($dialog.SelectedPath)))
  }
} finally {
  $dialog.Dispose()
  $owner.Dispose()
}
"""
  import base64
  executable = os.path.join(os.environ['SystemRoot'], 'System32',
                            'WindowsPowerShell', 'v1.0', 'powershell.exe')
  encoded_script = base64.b64encode(script.decode('ascii').encode('utf-16-le'))
  env = os.environ.copy()
  # Base64 keeps the environment and subprocess output ASCII on Python 2.
  initial = output_path(initial_folder)
  env['BLENDERER_PICKER_INITIAL'] = base64.b64encode(initial.encode('utf-8'))
  process = subprocess.Popen([executable, '-NoProfile', '-NonInteractive', '-STA',
                              '-EncodedCommand', encoded_script],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env, creationflags=0x08000000)
  selected, errors = process.communicate()
  if process.returncode:
    raise IOError('Windows folder picker exited with code %s: %s' %
                  (process.returncode, errors.strip()))
  if selected.strip():
    return base64.b64decode(selected.strip()).decode('utf-8')
  return None


def create_config_XML(uri, filepath, video_frames=0, video_fps=25):
  uri = uri.decode('utf8')
  settings_dict = {}
  # Engine: BLENDER_EEVEE (default) or CYCLES
  if renderEngineProp.Value == 'Cycles':
    settings_dict['engine'] = 'CYCLES'
  else:
    settings_dict['engine'] = 'BLENDER_EEVEE'
  settings_dict['re_render'] = str(reRender_prop.Value)
  res = [resXProp.Value, resYProp.Value]
  portrait = portraitProp.Value == 'Portrait'
  res = res[::-1] if portrait else res
  settings_dict['resolution_x'] = res[0]
  settings_dict['resolution_y'] = res[1]
  settings_dict['samples'] = samplesProp.Value
  settings_dict['filepath'] = filepath
  #
  settings_dict['resolution_percentage'] = 100
  settings_dict['openinblender'] = openinblenderProp.Value
  settings_dict['frame_start'] = 0
  settings_dict['frame_end'] = max(0, video_frames - 1)
  settings_dict['anim_fps'] = video_fps
  settings_dict['is_animation'] = int(video_frames > 0)
  settings_dict['video_container'] = videocontainer_prop.Value
  # Video rendering strategy + quality — passed through to import_to_blender.py.
  # Maps UI string → internal enum understood by the Blender side.
  # Still images ignore these video settings.
  video_mode_map = {'PNG Sequence': 'PNG_SEQUENCE', 'Direct Video': 'DIRECT_VIDEO'}
  settings_dict['video_mode'] = video_mode_map.get(renderVideoModeProp.Value, 'PNG_SEQUENCE')
  settings_dict['video_quality'] = videoQualityProp.Value
  portrait = portraitProp.Value == 'Portrait'
  xRes = resYProp.Value if portrait else resXProp.Value
  yRes = resXProp.Value if portrait else resYProp.Value
  dist = (yRes/2.0)/(math.tan(fovProp.Value/2.0*DEG2RAD))
  fov = fovProp.Value if portrait else math.atan(xRes/2.0/dist)*2*RAD2DEG # convert vertical res to horizontal in non portrait
  settings_dict['CameraFOV'] = fov
  settings_dict['device'] = deviceProp.Value
  # Cycles-specific settings (passed through to import_to_blender.py)
  settings_dict['cycles_device'] = deviceProp.Value
  settings_dict['cycles_backend'] = cyclesBackendProp.Value
  settings_dict['cycles_samples'] = cyclesSamplesProp.Value
  settings_dict['use_renderedges'] = renderedgesProp.Value
  if monochromeProp.Value:
    monochrome_material = monochromeProp.Value
    mono_r = monochrome_material.Diffuse.X
    mono_g = monochrome_material.Diffuse.Y
    mono_b = monochrome_material.Diffuse.Z
    settings_dict['monochrome'] = '|'.join([str(mono_r), str(mono_g), str(mono_b)])
  else:
    settings_dict['monochrome'] = ''

  settings_dict['use_simple_transparent'] = simpleTransparentProp.Value
  settings_dict['material_version'] = materialVersionProp.Value
  settings_dict['edge_line_thickness'] = engeThicknessProp.Value
  settings_dict['depth_fstop'] = depthOfFstopProp.Value
  settings_dict['indirect_lighting'] = indirectLightProp.Value
  if depthOFnodeProp.Value:
    node = depthOFnodeProp.Value
    node_name = get_node_name(node)
  else:
    node_name = ''
  settings_dict['depthOFnode'] = node_name
  settings_dict['exposure'] = exposureProp.Value
  settings_dict['bloom'] = bloomProp.Value
  settings_dict['bloomintensity'] = bloomIntensityProp.Value
  #
  settings_dict['envimage'] = envimageProp.Value.replace('file:///','')
  settings_dict['envstrength'] = envstrengthProp.Value
  settings_dict['envrotation'] = envRotationProp.Value
  settings_dict['envtype'] = envtypeProp.Value
  rgb_vec = envcolorProp.Value
  settings_dict['envcolor'] = '%s;%s;%s' % (rgb_vec.X, rgb_vec.Y, rgb_vec.Z)
  settings_dict['envvisible'] = envvisibleProp.Value

  settings_dict['backdroptype'] = backdropTypeProp.Value
  backdrop_rgb_vec = backdropRgbProp.Value
  settings_dict['backdropcolor'] = '%s;%s;%s' % (backdrop_rgb_vec.X, backdrop_rgb_vec.Y, backdrop_rgb_vec.Z)
  settings_dict['backdropimage'] = backdropImageProp.Value.replace('file:///','')
  #
  settings_dict['floorvisible'] = floorvisibleProp.Value
  settings_dict['floorsize'] = floorsizeProp.Value
  settings_dict['floortype'] = floortypeProp.Value
  settings_dict['floorcolorimage'] = floorcolorimageProp.Value.replace(r'file:///','')
  settings_dict['floorbumpimage'] = floorbumpimageProp.Value.replace(r'file:///','')
  settings_dict['floorbumpstrength'] = str(floorbumpstrengthProp.Value)
  rgb_vec = floorcolorProp.Value
  settings_dict['floorcolor'] = '%s;%s;%s' % (rgb_vec.X, rgb_vec.Y, rgb_vec.Z)
  settings_dict['floortexturesize'] = floortexturesizeProp.Value*SCALE
  settings_dict['scene_bound'] = str([x*SCALE for x in threeD_bound])
  settings_dict['floor_overshoot'] = str(floorsizeProp.Value*SCALE)

  root = ET.Element("RenderSettings")
  # v2.6.1-fix (R5): ElementTree .write(uri, 'UTF-8') emits the XML header as
  # UTF-8 and will internally encode Element.text to UTF-8 bytes *only* if
  # Element.text is a unicode string. Using str(item) on an IronPython 2
  # unicode string triggers the default ASCII codec, raising UnicodeEncodeError
  # as soon as any value contains Chinese/Japanese/Cyrillic/accents — which is
  # common for:
  #   - filepath         (user output PNG in a Chinese folder)
  #   - depthOFnode      (node/component/product with a Chinese name, via get_node_name)
  #   - envimage / backdropimage / floorcolorimage / floorbumpimage
  #                      (user picked a texture whose path contains Chinese)
  # Fix: keep unicode strings as unicode and convert anything else through
  # unicode() so ElementTree gets a consistently unicode Element.text.
  def _xml_text(v):
    if isinstance(v, unicode):
      return v
    if isinstance(v, bytes):
      try:
        return v.decode('utf-8')
      except UnicodeDecodeError:
        return v.decode('latin-1', errors='replace')
    return unicode(v)
  for key, item in settings_dict.iteritems():
    ET.SubElement(root, key).text = _xml_text(item)
  settings_tree = ET.ElementTree(root)
  settings_tree.write(uri, 'UTF-8')


def parentVisible(n):
  if not n.Visible:
    return False
  if n.Parent and not parentVisible(n.Parent):
    return False
  return True


def hasgeometry(n, rebuild_flag = False):
  hasgeometry = False
  if rebuild_flag:
    n.rebuild()
  if n.Component.getProperty('ShowWhenSimulating') and not n.Component.getProperty('ShowWhenSimulating').Value:
    return False
  if not parentVisible(n):
    return False
  for gs in n.Geometry.GeometrySets:
    if gs.Type == VC_TRIANGLESET:
      if gs.PointCount > 0:
        hasgeometry = True
        return True
  return False


def exportType(x):
  if x.Type in [VC_NODE]: # comp fails this test
    if x.Parent.Type == VC_COMPONENT and x.Parent.getProperty('BLENDER_OBJECT_TYPE') and x.Parent.getProperty('BLENDER_OBJECT_TYPE').Value == 'SPARKS':
      return 'SPARKS_VISUAL'
    return 'NODE'
  type_prop = x.getProperty('BLENDER_OBJECT_TYPE')
  if type_prop:
    return type_prop.Value
  else:
    return 'NODE'


def findAllNodes():
  nodes = []
  for c in app.Components:
    nodes.append(c)
    kids = [x for x in c.Children if x.Type == VC_NODE]
    while kids:
      k = kids.pop(0)
      nodes.append(k)
      kids.extend([x for x in k.Children if x.Type == VC_NODE])
  return nodes


def setCustomDataProps(material_name, custom_data_val):
  m = app.findMaterial(material_name)
  if m:
    p = m.createProperty(VC_STRING, 'CustomData')
    p.Value = custom_data_val
  return m


def setBound(node,threeD_bound):
  bd = node.BoundDiagonal
  bc = node.BoundCenter
  V = vcVector.new
  wp = node.WorldPositionMatrix
  corners = [V(bd.X,bd.Y,bd.Z), 
             V(bd.X,-bd.Y,bd.Z), 
             V(-bd.X,-bd.Y,bd.Z), 
             V(-bd.X,bd.Y,bd.Z),
             V(bd.X,bd.Y,-bd.Z), 
             V(bd.X,-bd.Y,-bd.Z), 
             V(-bd.X,-bd.Y,-bd.Z), 
             V(-bd.X,bd.Y,-bd.Z)]
  corners = [wp * (bc+x) for x in corners]
  minX = min([x.X for x in corners])
  maxX = max([x.X for x in corners])
  minY = min([x.Y for x in corners])
  maxY = max([x.Y for x in corners])
  minZ = min([x.Z for x in corners])
  maxZ = max([x.Z for x in corners])
  if minX < threeD_bound[0]:
    threeD_bound[0] = minX
  if maxX > threeD_bound[1]:
    threeD_bound[1] = maxX
  if minY < threeD_bound[2]:
    threeD_bound[2] = minY
  if maxY > threeD_bound[3]:
    threeD_bound[3] = maxY
  if minZ < threeD_bound[4]:
    threeD_bound[4] = minZ
  if maxZ > threeD_bound[5]:
    threeD_bound[5] = maxZ


def get_render_items():
  nodes = findAllNodes()
  all_them_items = [[x, exportType(x)] for x in nodes if hasgeometry(x)]
  current_camera = app.findCamera()
  if current_camera is None:
    app.messageBox('Error: No camera found in the scene. Please add a camera before rendering.', 'Blenderer Error', 16, 1)
    return []
  all_them_items.insert(0,[current_camera, 'CAMERA'])
  return all_them_items


def getMaterialFiles():
  global threeD_bound
  materials = {}
  mtl_file = None
  uri_root = cmd.TEMPDATA_URI
  uri_root = uri_root.decode('utf8')
  for root, folders, files in os.walk(uri_root):
    for f in files:
      thisuri = os.path.join( root, f )
      thisuri = thisuri.decode('utf8')
      body, extension = os.path.splitext( f )
      if reRender_prop.Value and extension == '.blend':
        # do not delete the blend file as it is used for re-rendering same scene
        continue
      os.remove(thisuri)
  threeD_bound = [9999999,-9999999,9999999,-9999999,9999999,-999999]
  material_table_csv = None
  material_data_dict = {}
  if materialTableProp.Value == 'Write To Table':
    thefolder, commandfilename = os.path.split(getCommandPath()[8:])
    material_table_csv_uri = os.path.join(thefolder, 'materials.csv')
    material_table_csv_uri = material_table_csv_uri.decode('utf8')
    # v2.6.1-fix (R6): open CSV in binary mode and write UTF-8 bytes so that
    # Chinese / non-ASCII material names and texture file paths are stored
    # byte-exactly as UTF-8, matching what export_from_vc.py writes via _c()
    # helper and matching the Read From Table decoder below (so the material
    # name dict key `mat.Name` (unicode) hits `material_data_dict[csvline[0]]`
    # also unicode, instead of never matching due to bytes/unicode type gap
    # or due to locale encoding such as cp1252/cp936 producing a different
    # byte sequence for the same logical Chinese material name).
    def _csv_utf8(v):
      if isinstance(v, unicode):
        return v.encode('utf-8')
      if isinstance(v, bytes):
        return v
      return unicode(v).encode('utf-8')
    try:
      material_table_csv = open(material_table_csv_uri, 'wb')
      SEP = tableSeparatorProp.Value
      header_bytes = SEP.join([_csv_utf8(c) for c in material_columns])
      material_table_csv.write(header_bytes + _csv_utf8(LINECHANGE))
    except:
      material_table_csv = None
      print 'Unable to open table file for writing "%s"' % material_table_csv_uri
      print 'Make sure it is not open in another software.'
  elif materialTableProp.Value == 'Read From Table':
    thefolder, commandfilename = os.path.split(getCommandPath()[8:])
    material_table_csv_uri = os.path.join(thefolder, 'materials.csv')
    material_table_csv_uri = material_table_csv_uri.decode('utf8')
    # v2.6.1-fix (R6): open CSV in binary mode, read UTF-8 bytes, decode
    # each cell to unicode before storing into material_data_dict. This
    # guarantees that when export_from_vc.py does `mat.Name in mat_dict`
    # (where mat.Name is a unicode string from the VC API), the dictionary
    # lookup succeeds for Chinese / non-ASCII material names instead of
    # silently falling through to default material properties.
    def _cell_unicode(v):
      if isinstance(v, unicode):
        return v
      if isinstance(v, bytes):
        try:
          return v.decode('utf-8')
        except UnicodeDecodeError:
          # tolerate legacy files saved by older Blenderer versions under
          # the system locale (cp936 on Chinese Windows, cp1252 elsewhere)
          try:
            return v.decode('mbcs')
          except Exception:
            return v.decode('latin-1', errors='replace')
      return unicode(v)
    with open(material_table_csv_uri, 'rb') as material_table_csv:
      SEP = tableSeparatorProp.Value
      SEP_bytes = _cell_unicode(SEP).encode('utf-8') if isinstance(SEP, unicode) else str(SEP)
      tablereader = csv.reader(material_table_csv, delimiter=SEP_bytes)
      tablereader.next() #skip header
      for csvline in tablereader:
        csvline = [_cell_unicode(c) for c in list(csvline)]
        if not csvline or not csvline[0]:
          continue
        material_data_dict[csvline[0]] = {}
        for title, csv_value in zip(material_columns, csvline)[1:]:
          material_data_dict[csvline[0]][title] = csv_value
  return materials, mtl_file, material_table_csv, material_data_dict


def getAllMaterials():
  materials = set()
  nodes = sim.World.Children
  i=0
  while nodes:
    i+=1
    node = nodes.pop(0)
    nodes.extend(node.Children)
    materials.update([x.Material.Name for x in node.Geometry.GeometrySets if x.Type == VC_TRIANGLESET and x.Material])
  return list(materials)


def exportGeo(items,
              materials, 
              mtl_file, 
              material_table_csv, 
              material_data_dict):
  global threeD_bound
  # loop layout content
  uri_root = cmd.TEMPDATA_URI
  uri_root = uri_root.decode('utf8')
  for node, object_type in items:
    try:
      node.Name
      dead = False
    except:
      dead = True
    if dead:
      continue
    if object_type in ['CAMERA', 'RECORDER', 'POINT_LIGHT', 'AREA_LIGHT', 'SUN_LIGHT', 'SPOT_LIGHT', 'SPARKS_VISUAL']:
      # skip abstract components. Geometry not exported
      continue
    if camera is not None and isinstance(node, type(camera)):
      # item is of type camera. Skip as there's no geometry to export
      continue
    if node.Type in [VC_COMPONENT, VC_NODE]:
      setBound(node,threeD_bound)
    node_name = get_node_name(node)
    fileuri = os.path.join(uri_root, node_name+'.obj')
    # v2.6.1-fix: do NOT .decode('utf8') here. After get_node_name fix,
    # both uri_root and node_name are already unicode strings, so the
    # os.path.join result is pure unicode. Calling .decode() on a Python 2
    # unicode object implicitly re-encodes via ASCII first → UnicodeEncodeError
    # for any non-ASCII character (e.g. Chinese component names).
    if isinstance(fileuri, bytes):
        fileuri = fileuri.decode('utf8')
    SEP = tableSeparatorProp.Value
    ok, materials, mtl_file = export_from_vc.export_obj( app, 
                                                              node, 
                                                              materials, 
                                                              mtl_file, 
                                                              SCALE, 
                                                              fileuri, 
                                                              materialTableProp.Value, 
                                                              material_table_csv, 
                                                              material_data_dict, 
                                                              SEP,
                                                              reRender_prop.Value,
                                                              robotMaterials.Value == 'Smart Materials' )
  return materials, mtl_file, material_table_csv, material_data_dict


def get_node_name(node):
  if node.Type == VC_COMPONENT:
    #comp name
    node_name = node.Name
    item_component = node
  else:
    #comp name + node name
    node_name = '%s__%s'  % (node.Component.Name, node.Name)
    item_component = node.Component
  if item_component.Product:
    node_name += '_PRD_' + item_component.Product.ProductType.Name
  node_name = sanitizefilename(node_name)
  # v2.6.1-fix: remove harmful .encode('utf-8') here. It converted the
  # unicode node_name (containing e.g. Chinese chars "信号升降机") into
  # raw UTF-8 bytes. When later concatenated with the unicode uri_root
  # in os.path.join(... node_name+'.obj'), Python 2 would auto-decode the
  # bytes using ASCII → UnicodeDecodeError for any non-ASCII filename.
  # Keeping the name as unicode throughout ensures correct path joining
  # (both for filesystem writes and for the JSON recording file).
  # The JSON serializer _normalize_for_json already handles bytes just in
  # case, so the old comment "not helping.. assigning to a list screws
  # things up" refers to a stale list/bytes mixing that no longer applies.
  return node_name

prev_cam_id = ''

def recKeyFrame(items, rec_data, frame=0):
  global preset_tree, prev_cam_id
  sim.update()
  for i, token in enumerate(items):
    item, item_type = token
    item_component = None #set for node types later
    deadComponent = False
    try:
      item.Name #this fails if a component has disappeared from the layout (dynamic comps during animation)
    except:
      deadComponent = True
    if item_type == 'CAMERA':
      # element is camera
      object_name = 'VC_TO_BLENDER_CAMERA_OBJECT'
      cam = item if item is not None else camera
      if cam is None:
        continue
      mtx = cam.Matrix
      rot = mtx.WPR
      eye = cam.Eye
      coi = cam.Coi
      position_data = frame, eye.X*SCALE, eye.Y*SCALE, eye.Z*SCALE, coi.X*SCALE, coi.Y*SCALE, coi.Z*SCALE
      title_line = 'addon: t%.2f; ' % (sim.SimTime)
      cam_id = 'x=%.2f; y=%.2f; z=%.2f; mtx.Y=%.2f' % (eye.X*SCALE, eye.Y*SCALE, eye.Z*SCALE, mtx.P.Y)
      if cam_id == prev_cam_id:
        pass
        #print title_line + cam_id, ' <= same'
      else:
        pass
        #print title_line + cam_id
      prev_cam_id = cam_id
      if keyframe_index == 0:
        object_data = []
    elif item_type == 'SPARKS':
      object_name = item.Name
      object_name = sanitizefilename(object_name)
      if keyframe_index == 0:
        rgb = (item.R/255.0, item.G/255.0, item.B/255.0, 1.0)
        object_data = [rgb, item.DimGlobalLighting]
      mtx = item.WorldPositionMatrix
      rot = mtx.WPR
      sx = mtx.N.length()
      sy = mtx.O.length()
      sz = mtx.A.length()
      spark_on = 2.0 if item.findBehaviour('SparksSignal').Value else 0.0
      position_data = frame, mtx.P.X*SCALE, mtx.P.Y*SCALE, mtx.P.Z*SCALE, rot.X*DEG2RAD, rot.Y*DEG2RAD, rot.Z*DEG2RAD, sx,sy,sz, spark_on
    elif item_type in ['AREA_LIGHT', 'POINT_LIGHT', 'SUN_LIGHT', 'SPOT_LIGHT']:
      object_name = item.Name
      object_name = sanitizefilename(object_name)
      rgb = [item.R, item.G, item.B]
      strength = item.Strength
      if keyframe_index == 0 and item_type in ['AREA_LIGHT']:
        sizeX = item.SizeX*SCALE
        sizeY = item.SizeY*SCALE
        falloff = item.Falloff
        object_data = [rgb, strength, sizeX, sizeY, falloff]
      elif keyframe_index == 0 and item_type in ['POINT_LIGHT']:
        size = item.Size*SCALE
        falloff = item.Falloff
        object_data = [rgb, strength, size, falloff]
      elif keyframe_index == 0 and item_type in ['SUN_LIGHT']:
        size = 0.1
        object_data = [rgb, strength, size]
      elif keyframe_index == 0 and item_type in ['SPOT_LIGHT']:
        size = item.Size*SCALE
        angle = item.Angle
        falloff = item.Falloff
        object_data = [rgb, strength, size, angle, falloff]
      p = item.WorldPositionMatrix.P
      coi = vcMatrix.new(item.WorldPositionMatrix)
      coi.translateRel(0,0,-1000)
      coi = coi.P
      position_data = frame, p.X*SCALE, p.Y*SCALE, p.Z*SCALE, coi.X*SCALE, coi.Y*SCALE, coi.Z*SCALE, strength
    elif item_type == 'NODE':
      if deadComponent:
        position_data = rec_data[i][3][-1] #last keyframe
        position_data = list(position_data)
        # SCALE to zero so that the node disappears
        position_data[-1] = 0
        position_data[-2] = 0
        position_data[-3] = 0
        position_data[0] = frame
        position_data = tuple(position_data)
      else:
        object_name = get_node_name(item)
        mtx = item.WorldPositionMatrix
        rot = mtx.WPR
        sx = mtx.N.length()
        sy = mtx.O.length()
        sz = mtx.A.length()
        position_data = frame, mtx.P.X*SCALE, mtx.P.Y*SCALE, mtx.P.Z*SCALE, rot.X*DEG2RAD, rot.Y*DEG2RAD, rot.Z*DEG2RAD, sx,sy,sz
        if keyframe_index == 0:
          object_data = []
    if keyframe_index == 0:
      if item_type == 'NODE':
        object_name = get_node_name(item)
      rec_data.append( [object_name, item_type, object_data, [position_data]] )
    else:
      last_pd = rec_data[i][3][-1]
      # In RealTimeMode, multiple OnRender calls fire per simulation step.
      # If frame hasn't changed (same sim step), replace the last
      # entry instead of appending a duplicate at the same frame index.
      # This applies to ALL types including sparks — one keyframe per step.
      if frame == last_pd[0]:
        rec_data[i][3][-1] = position_data
      elif len(rec_data[i][3]) >= 2 and position_data[1:] == last_pd[1:] == rec_data[i][3][-2][1:] and item_type != 'SPARKS':
        # node is stationary.. only keyframe index changes.. replace prev positiondata
        # NOTE: check len >= 2, not keyframe_index > 1, because the same-frame
        # dedup above can keep rec_data[i][3] at 1 element even when
        # keyframe_index > 1 (multiple OnRender in the same sim step replaced
        # instead of appending). Accessing [-2] on a 1-element list raises
        # IndexError.
        rec_data[i][3][-1] = position_data
      else:
        # sparks must be keyframed even if stationary
        # When OnRender skips steps during long recordings, frame
        # has gaps. We do NOT insert bridge frames holding the old pose — that
        # caused "freeze-then-jump" stuttering (object frozen for N frames then
        # snapping to the new pose). Instead, let Blender interpolate naturally
        # between the two real keyframes (smooth constant-speed motion across
        # the gap). Combined with LINEAR interpolation in import_to_blender.py,
        # this gives smooth motion even with sparse keyframes.
        rec_data[i][3].append(position_data)
  return rec_data



def setPresetLights(rec_data):
  current_preset = [x for x in preset_tree if x.get("name") == presetProp.Value]
  if current_preset:
    current_preset = current_preset[0]
    sun_lights = current_preset.findall('sun_light')
    for light in sun_lights:
      object_name = 'preset_light'
      item_type = 'SUN_LIGHT'
      rgb = tuple( [float(light.get(x)) for x in ['r','g','b']])
      strength = float(light.get('energy'))
      size = float(light.get('size'))
      object_data = [rgb, strength, size]
      if light.get('angle') is not None:
        object_data.append(float(light.get('angle')))
      mtx = vcMatrix.new()
      mtx.rotateRelZ( float(light.get('orientation')) + envRotationProp.Value )
      mtx.rotateRelY( 90 - float(light.get('elevation')) )
      if 'auto' in light.get('distance').lower():
        mtx.translateRel(0,0,10000)
      else:
        mtx.translateRel(0,0,eval(light.get('distance')))
      p = mtx.P
      coi = vcMatrix.new(mtx)
      coi.translateRel(0,0,-1000)
      coi = coi.P
      position_data1 = 0,p.X*SCALE, p.Y*SCALE, p.Z*SCALE, coi.X*SCALE, coi.Y*SCALE, coi.Z*SCALE
      position_data2 = keyframe_index,p.X*SCALE, p.Y*SCALE, p.Z*SCALE, coi.X*SCALE, coi.Y*SCALE, coi.Z*SCALE
      # v2.6.1-fix: keep object_name as unicode, not bytes. Other fixes
      # (get_node_name, _normalize_for_json, _xml_text) all keep Chinese
      # names as unicode. Encoding here would be inconsistent and rely on
      # _normalize_for_json to decode it back. 'preset_light' is ASCII so
      # it was harmless, but removing it keeps the codebase consistent.
      rec_data.append( [object_name, item_type, object_data, [position_data1,position_data2]] )
  return rec_data


def getPresetTree():
  import xml.etree.ElementTree as ET
  thefolder, commandfilename = os.path.split(getCommandPath()[8:])
  thefolder = thefolder.decode('utf8')
  preset_xml_uri = os.path.join(thefolder , 'Lights\\Presets' , 'presets.xml')
  preset_xml_uri = preset_xml_uri.decode('utf8')
  preset_tree = ET.parse(preset_xml_uri)
  return preset_tree


def preflight_text(key, fallback):
  resource_key = 'ComboKey::Python.cmdBlenderer520.Preflight.' + key + '.Text'
  label = app.getLocalizedString(resource_key)
  return as_unicode(label) if label and label != resource_key else fallback


def preflight_error(key, fallback, path=None):
  message = preflight_text(key, fallback)
  if path:
    message += u'\n\n' + path
  app.messageBox(message.encode('utf-8'), 'Blenderer', VC_MESSAGE_TYPE_ERROR, VC_MESSAGE_BUTTONS_OK)


def check_output_folder(filepath):
  folder = os.path.dirname(filepath)
  if os.path.isdir(filepath):
    preflight_error('NameIsFolder', 'A folder already uses this output name. Choose another file name.', filepath)
    return False
  try:
    if not os.path.isdir(folder):
      try:
        os.makedirs(folder)
      except OSError:
        if not os.path.isdir(folder):
          raise
    # Opening a temporary file checks actual Windows permissions, including network drives.
    fd, probe = tempfile.mkstemp(prefix='.blenderer-', dir=folder)
    try:
      os.close(fd)
    finally:
      os.remove(probe)
  except (IOError, OSError, ValueError):
    preflight_error('UnwritableFolder', 'Cannot write to this folder. Choose another output folder.', folder)
    return False
  return True


def prepare_render(folder, name, default_name, extension):
  try:
    filepath = render_output_path(folder, name, default_name, extension)
  except ValueError as error:
    messages = {
      'AbsoluteFolder': 'Select an output folder with an absolute path.',
      'InvalidName': 'Enter a valid file name without a folder path.',
      'ReservedName': 'This name is reserved by Windows. Enter another file name.',
      'TrailingName': 'The file name cannot end with a dot or space.',
    }
    key = str(error)
    preflight_error(key, messages[key])
    return None, None
  if not openinblenderProp.Value and not check_output_folder(filepath):
    return None, None
  return filepath, get_blender_exe_uri()


def CallStill(arg):
  global keyframe_index
  filepath, blender_exe = prepare_render(outputFolderProp.Value, imageNameProp.Value, 'Picture', '.png')
  if not blender_exe:
    return
  showBorderProp.Value = False
  rec_data = []
  new_dynamic_nodes = []
  all_items = get_render_items()
  keyframe_index=0
  recKeyFrame(all_items, rec_data)
  setPresetLights(rec_data)
  materials, mtl_file, material_table_csv, material_data_dict = getMaterialFiles()
  exportGeo(all_items,
            materials, 
            mtl_file, 
            material_table_csv, 
            material_data_dict)

  if material_table_csv:
    material_table_csv.close()
  '''
  overshoot = floorsizeProp.Value
  threeD_bound[0] -= overshoot
  threeD_bound[1] += overshoot
  threeD_bound[2] -= overshoot
  threeD_bound[3] += overshoot'''
  CallBlender(rec_data, filepath, blender_exe)



def CallAnim(arg):
  global rec_data, threeD_bound
  if recanim_prop.Value or not animation_recorded:
    preflight_error('RecordingIncomplete',
                    'Record the animation and let the simulation run past the end time before rendering.')
    return
  video_path, blender_exe = prepare_render(animationFolderProp.Value, animationNameProp.Value, 'Animation', '.mp4')
  if not blender_exe:
    return
  # Blender's importer uses this stem for MP4 and the extension for PNG frames.
  frame_path = os.path.splitext(video_path)[0] + '.png'
  showBorderProp.Value = False
  overshoot = floorsizeProp.Value
  try:
    threeD_bound[0] -= overshoot
    threeD_bound[1] += overshoot
    threeD_bound[2] -= overshoot
    threeD_bound[3] += overshoot
  except Exception as error:
    print 'Blenderer: animation scene preparation failed:', error
    print preflight_text('ScenePreparationFailed', 'Failed to prepare the scene for export.')
    return
  CallBlender(rec_data, frame_path, blender_exe, animation = True)


def OnSimRender(local_sim):
  global rec_data, new_dynamic_nodes, keyframe_index, cache_material_files, animation_recorded
  start, end, fps, frame_count = animation_timing
  t = sim.SimTime
  if showBorderProp.Value:
    showBorderProp.Value = False
  if start <= t < end:
    frame = min(frame_count - 1, int(round((t - start) * fps)))
    app.OnDynamicComponent = MyOnDynamicComponent
    #if keyframe_index==0:
    if keyframe_index == 0:
      all_items = get_render_items()
      materials, mtl_file, material_table_csv, material_data_dict = getMaterialFiles()
      materials, mtl_file, material_table_csv, material_data_dict = exportGeo(all_items,
                                                                              materials, 
                                                                              mtl_file, 
                                                                              material_table_csv, 
                                                                              material_data_dict)
    else:
      all_items, materials, mtl_file, material_table_csv, material_data_dict = cache_material_files
      if new_dynamic_nodes:
        added_dynamic_nodes = add_new_dynamic_component(new_dynamic_nodes)
        materials, mtl_file, material_table_csv, material_data_dict = exportGeo(added_dynamic_nodes,
                                                                                materials, 
                                                                                mtl_file, 
                                                                                material_table_csv, 
                                                                                material_data_dict)
        all_items.extend( added_dynamic_nodes )

        for i, token in enumerate(added_dynamic_nodes):
          item, item_type = token
          object_name = get_node_name(item)
          mtx = item.WorldPositionMatrix
          rot = mtx.WPR
          sx = 0.0 # force scale to zero. Item will be invisible until this keyframe.
          sy = 0.0
          sz = 0.0
          position_data1 = min(0, frame - 1), mtx.P.X*SCALE, mtx.P.Y*SCALE, mtx.P.Z*SCALE, rot.X*DEG2RAD, rot.Y*DEG2RAD, rot.Z*DEG2RAD, sx,sy,sz
          position_data2 = frame - 1, mtx.P.X*SCALE, mtx.P.Y*SCALE, mtx.P.Z*SCALE, rot.X*DEG2RAD, rot.Y*DEG2RAD, rot.Z*DEG2RAD, sx,sy,sz
          object_data = []
          hidden_frames = [position_data1, position_data2] if frame > 1 else [position_data1]
          rec_data.append([object_name, item_type, object_data, hidden_frames])
        new_dynamic_nodes = []
    cache_material_files = all_items, materials, mtl_file, material_table_csv, material_data_dict
    rec_data = recKeyFrame(all_items, rec_data, frame)
    keyframe_index += 1
  elif t >= end:
    if rec_data and keyframe_index > 0:
      setPresetLights(rec_data)
      animation_recorded = True
    recanim_prop.Value = False
    if not animation_recorded:
      print preflight_text('NoRecordedFrames', 'No animation frames were captured. Reset the simulation and record again.').encode('utf-8')


def MyOnDynamicComponent(component, container, added):
  global new_dynamic_nodes
  #rint component.Name, '|',container.Parent.Component.Name, '|', container.Name
  if added:
    new_dynamic_nodes.append(component)



def add_new_dynamic_component(new_components):
  added_dynamic_nodes = []
  added = []
  while new_components:
    new_component = new_components.pop(0)
    new_components.extend(new_component.Children)
    if hasgeometry(new_component) and new_component not in added:
      added.append(new_component)
      added_dynamic_nodes.append( [new_component, exportType(new_component)] )
  return added_dynamic_nodes


def stop_animation_capture():
  app.OnRender = None
  app.OnDynamicComponent = None
  sim.OnReset = None


def MyOnReset(local_sim):
  stop_animation_capture()
  if recanim_prop.Value:
    recanim_prop.Value = False


def fps_from_step(step):
  if not step > 0 or math.isinf(step):
    raise ValueError('InvalidRecordingStep')
  fps = 1.0 / step
  if fps < 1 or fps > 32767:
    raise ValueError('InvalidRecordingStep')
  return int(round(fps))


def animation_time_range(start, end, step):
  if not (0 <= start < end) or math.isinf(end):
    raise ValueError('InvalidRecordingRange')
  fps = fps_from_step(step)
  frames = (end - start) * fps
  if frames >= 1048575.5:  # Blender's last valid index is 1048574.
    raise ValueError('RecordingTooLong')
  return start, end, fps, max(1, int(round(frames)))


def update_animation_fps(arg):
  if recanim_prop.Value:
    return
  try:
    fpsanim_prop.Value = fps_from_step(stepanim_prop.Value)
  except ValueError:
    pass


def InitAnim(arg):
  global rec_data, new_dynamic_nodes, keyframe_index, animation_recorded, animation_timing
  if not recanim_prop.Value:
    stop_animation_capture()
    update_animation_fps(None)
    return
  messages = {
    'InvalidRecordingRange': 'Use a nonnegative start time and an end time after it.',
    'InvalidRecordingStep': 'Use a recording step that yields a frame rate between 1 and 32767 FPS.',
    'RecordingTooLong': 'The recording range exceeds Blender\'s frame limit.',
  }
  try:
    timing = animation_time_range(startanim_prop.Value, endanim_prop.Value, stepanim_prop.Value)
  except ValueError as error:
    key = str(error)
    recanim_prop.Value = False
    preflight_error(key, messages[key])
    return

  animation_timing = timing
  animation_recorded = False
  rec_data = []
  new_dynamic_nodes = []
  keyframe_index = 0
  start, end, fps, frames = timing
  fpsanim_prop.Value = fps
  label = preflight_text('ExpectedAnimationFrames', 'Expected output: %d frames / %.3f s at %d FPS')
  print (label % (frames, frames / float(fps), fps)).encode('utf-8')
  # Real time gives the render callback a chance to sample the moving scene.
  app.RealTimeMode = True
  app.Simulation.SimSpeed = 1
  sim.OnReset = MyOnReset
  app.OnRender = OnSimRender


def is_blender_executable(path):
  return os.path.basename(path).lower() == 'blender.exe' and os.path.isfile(path)


def get_blender_exe_uri():
  blender_exe_uri = output_path(blender_exe_uri_prop.Value).strip()
  if is_blender_executable(blender_exe_uri):
    return blender_exe_uri
  message = preflight_text('LocateBlender',
                           'Blender was not found. Would you like to select blender.exe now?')
  result = app.messageBox(message.encode('utf-8'), 'Blenderer', VC_MESSAGE_BUTTONS_YESNO)
  if result != VC_MESSAGE_RESULT_YES:
    return None
  picker = app.findCommand('dialogOpen')
  title = preflight_text('BlenderPickerTitle', 'Locate Blender executable')
  picker.execute('', True, 'blender.exe|blender.exe', title.encode('utf-8'))
  if not picker.Param_2:
    return None
  blender_exe_uri = output_path(picker.Param_1).strip()
  if not is_blender_executable(blender_exe_uri):
    preflight_error('InvalidBlender', 'Select an existing blender.exe file.')
    return None
  blender_exe_uri_prop.Value = blender_exe_uri.encode('utf-8')
  return blender_exe_uri


import io
import json

# --- recording.vcbx serialization -----------------------------------
# Long animations (>2 min) produce very large recording.vcbx files.
# The old approach `unicode(rec_data)` wrote each float with full 17-digit
# precision and required `eval()` on the Blender side (slow + unsafe).
# We now serialize as JSON with 6-decimal float precision, which cuts file
# size by ~60% and parse time by 3-5x. Tuples become JSON arrays (lists),
# which are index-compatible with the downstream consumer.
_REC_FLOAT_FMT = '%.6f'
_REC_FLOAT_PRECISION = 6

def _round_float(v):
  # Round to 6 decimals to shrink file size. Values smaller than 1e-6
  # are collapsed to 0.0 to avoid scientific-notation strings like "1e-08".
  r = round(float(v), _REC_FLOAT_PRECISION)
  if r == 0:
    r = 0.0  # normalise -0.0 -> 0.0
  return r

def _normalize_for_json(obj):
  # Recursively convert the rec_data structure into pure JSON-serializable
  # types: tuple -> list, bytes -> unicode, floats rounded to 6 decimals.
  if isinstance(obj, (int,)):
    return obj
  if isinstance(obj, float):
    return _round_float(obj)
  if isinstance(obj, bytes):
    try:
      return obj.decode('utf-8')
    except UnicodeDecodeError:
      return obj.decode('latin-1')
  if isinstance(obj, unicode):
    return obj
  if isinstance(obj, (list, tuple)):
    return [_normalize_for_json(x) for x in obj]
  if isinstance(obj, dict):
    return {k: _normalize_for_json(v) for k, v in obj.items()}
  # fallback: stringify anything unexpected
  return unicode(obj)

def serialize_rec_data(rec_data):
  # Returns a unicode JSON string with 6-decimal float precision.
  normalized = _normalize_for_json(rec_data)
  return json.dumps(normalized, ensure_ascii=False, separators=(',', ':'))

def CallBlender(rec_data, filepath, blender_exe_uri, animation = False):
  started = time.time()
  try:
    return export_to_blender(rec_data, filepath, blender_exe_uri, animation, started)
  except Exception as error:
    print 'Blenderer: export setup or startup failed:', error
    print preflight_text('ExportSetupFailed', 'Could not prepare or start Blender. See the details above.')
    return False


def export_to_blender(rec_data, filepath, blender_exe_uri, animation, started):
  uri_root = cmd.TEMPDATA_URI
  uri_root = uri_root.decode('utf8')
  rec_file_name = os.path.join(uri_root, 'recording.vcbx')
  rec_file_name = rec_file_name.decode('utf8')
  with io.open(rec_file_name, 'w', encoding = 'utf-8') as rec_file:
    rec_file.write( serialize_rec_data(rec_data) )
  xml_uri = os.path.join(uri_root, 'render_config.xml')
  xml_uri = xml_uri.decode('utf8')
  if animation:
    _, _, fps, frames = animation_timing
    create_config_XML(xml_uri, filepath, frames, fps)
  else:
    create_config_XML(xml_uri, filepath)
  thefolder, commandfilename = os.path.split(getCommandPath()[8:])
  vcimporteruri = os.path.join(thefolder, 'import_to_blender.py')
  vcimporteruri = vcimporteruri.decode('utf8')
  vcimporteruri_copy = os.path.join(temproot_uri, 'import_to_blender.py')
  vcimporteruri_copy = vcimporteruri_copy.decode('utf8')
  materialhelperuri = os.path.join(thefolder, 'material_helper.py')
  materialhelperuri = materialhelperuri.decode('utf8')
  materialhelperuri_copy = os.path.join(temproot_uri, 'material_helper.py')
  materialhelperuri_copy = materialhelperuri_copy.decode('utf8')
  shutil.copyfile(vcimporteruri, vcimporteruri_copy)
  shutil.copyfile(materialhelperuri, materialhelperuri_copy)
  cli_data = ['%s' % blender_exe_uri]
  if reRender_prop.Value:
    cli_data.append(latest_blender_scene(uri_root))
  if openinblenderProp.Value:
    return launch_interactive_blender(cli_data, uri_root, vcimporteruri, materialhelperuri)
  cli_data.append('--background')
  cli_data.extend(['--python-exit-code', '1', '--python'])
  cli_data.append('%s' % vcimporteruri_copy)
  cli_data.append('--')
  cli_data.append('%s' % uri_root)
  log_path = os.path.join(uri_root, 'blender_log.txt')
  with tempfile.NamedTemporaryFile(prefix='blenderer-result-', suffix='.json',
                                   dir=uri_root, delete=False) as result_file:
    result_path = result_file.name
  try:
    cli_data.append(result_path)
    progress_path = result_path + '.progress'
    exit_code = run_blender_once(cli_data, log_path, progress_path)
    result = settle_render_output(result_path, filepath, exit_code)
    ok = print_export_result(result, exit_code, time.time() - started, log_path)
    if ok and result.get('status') == 'image':
      try:
        os.startfile(result['path'])
      except OSError as error:
        print 'Blenderer: could not open the rendered image:', error
    return ok
  finally:
    for suffix in ('', '.progress', '.progress.tmp', '.progress.cancel', '.frames', '.frames.tmp'):
      remove_export_temporary_file(result_path + suffix)


def latest_blender_scene(uri_root):
  import glob
  shared = os.path.join(uri_root, 'blender_scene.blend')
  candidates = glob.glob(os.path.join(os.path.dirname(uri_root), 'interactive-*', 'blender_scene.blend'))
  if os.path.isfile(shared):
    candidates.append(shared)
  return max(candidates, key=os.path.getmtime) if candidates else shared


def launch_interactive_blender(cli_data, uri_root, importer, material_helper):
  # A later VC export can clear TEMPDATA while this Blender is still importing.
  session = tempfile.mkdtemp(prefix='interactive-', dir=os.path.dirname(uri_root))
  log_path = os.path.join(session, 'blender_log.txt')
  try:
    for name in os.listdir(uri_root):
      source = os.path.join(uri_root, name)
      if os.path.isfile(source) and not name.lower().endswith(('.blend', '.blend1')):
        shutil.copyfile(source, os.path.join(session, name))
    script = os.path.join(session, 'import_to_blender.py')
    shutil.copyfile(importer, script)
    shutil.copyfile(material_helper, os.path.join(session, 'material_helper.py'))
    with io.open(log_path, 'wb') as log:
      subprocess.Popen(cli_data + ['--python-exit-code', '1', '--python', script, '--', session],
                       stdout=log, stderr=subprocess.STDOUT)
  except Exception:
    shutil.rmtree(session, ignore_errors=True)
    raise
  print preflight_text('InteractiveBlenderStarted', 'Blender launched. Scene import runs in Blender.')
  print preflight_text('ExportLog', 'Blender log: %s') % log_path
  return True


def settle_render_output(result_path, filepath, exit_code):
  token = os.path.join(os.path.dirname(filepath), os.path.basename(result_path))
  result = finish_render_output(read_blender_result(result_path), exit_code, token)
  leftovers = [path for path in export_temporary_paths(token) if not remove_export_temporary_file(path)]
  if exit_code is None:
    frames = read_blender_result(result_path + '.frames').get('path')
    if frames and os.path.isdir(frames):
      try:
        os.rmdir(frames)  # Deletes only an empty frame folder.
        frames = None
      except OSError:
        pass
    return {'status': 'cancelled', 'path': frames, 'leftovers': leftovers}
  return result


def export_temporary_paths(token):
  return token + '.partial.png', token + '.partial.mp4'


def finish_render_output(result, exit_code, token):
  temporary = result.get('temporary')
  if exit_code != 0 or not temporary:
    return result
  destination = result['path']
  if temporary not in export_temporary_paths(token) or os.path.dirname(destination) != os.path.dirname(token):
    return {'status': 'failed', 'detail': 'Blender returned an unexpected output path.'}
  try:
    # Windows rename will fail if a different render already used this name.
    os.rename(temporary, destination)
  except OSError as error:
    return {'status': 'failed', 'detail': as_unicode(error)}
  return result


def remove_export_temporary_file(path):
  try:
    os.remove(path)
  except OSError as error:
    if os.path.lexists(path):
      print ('Blenderer: could not remove a temporary export file: %s (%s)' %
             (path, as_unicode(error))).encode('utf-8')
      return False
  return True


def show_render_progress(process_id, progress_path):
  import base64

  labels = {
    'title': preflight_text('ProgressTitle', 'Blenderer render progress'),
    'prepare': preflight_text('ProgressPreparing', 'Preparing scene...'),
    'render': preflight_text('ProgressRendering', 'Rendering'),
    'encode': preflight_text('ProgressEncoding', 'Combining PNG frames into MP4'),
    'frames': preflight_text('ProgressFrames', '{0} / {1} frames'),
    'finishing': preflight_text('ProgressFinishing', 'Finishing export...'),
    'cancel': preflight_text('CancelRender', 'Cancel render'),
    'confirm': preflight_text('ConfirmCancelRender', 'Stop the current render? Completed PNG frames will be kept.'),
    'cancelling': preflight_text('CancellingRender', 'Stopping render...'),
    'requestFailed': preflight_text('CancelRequestFailed', 'Could not request cancellation. Rendering is still running.'),
  }
  env = os.environ.copy()
  payload = json.dumps({'pid': process_id, 'path': progress_path, 'labels': labels})
  env['BLENDERER_PROGRESS'] = base64.b64encode(payload.encode('ascii'))
  executable = os.path.join(os.environ['SystemRoot'], 'System32',
                            'WindowsPowerShell', 'v1.0', 'powershell.exe')
  encoded_script = base64.b64encode(RUN_PROGRESS_WINDOW.decode('ascii').encode('utf-16-le'))
  # The window requests cancellation. Only VC owns the Blender process handle.
  subprocess.Popen([executable, '-NoProfile', '-NonInteractive', '-STA',
                    '-EncodedCommand', encoded_script], env=env, creationflags=0x08000000)


RUN_PROGRESS_WINDOW = r"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$request = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($env:BLENDERER_PROGRESS)) | ConvertFrom-Json
$labels = $request.labels
$target = Get-Process -Id $request.pid -ErrorAction SilentlyContinue
if (-not $target) { return }

$form = New-Object Windows.Forms.Form
$form.Text = $labels.title
$form.ClientSize = New-Object Drawing.Size(440, 129)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.TopMost = $true
$status = New-Object Windows.Forms.Label
$status.SetBounds(14, 16, 412, 25)
$status.Text = $labels.prepare
$bar = New-Object Windows.Forms.ProgressBar
$bar.SetBounds(14, 55, 412, 19)
$bar.Style = 'Marquee'
$form.Controls.Add($status)
$form.Controls.Add($bar)
$cancel = New-Object Windows.Forms.Button
$cancel.SetBounds(304, 86, 122, 28)
$cancel.Text = $labels.cancel
$form.Controls.Add($cancel)
$cancel.Add_Click({
    $answer = [Windows.Forms.MessageBox]::Show($form, $labels.confirm, $labels.title,
        [Windows.Forms.MessageBoxButtons]::YesNo, [Windows.Forms.MessageBoxIcon]::Question,
        [Windows.Forms.MessageBoxDefaultButton]::Button2)
    if ($answer -ne [Windows.Forms.DialogResult]::Yes -or $target.HasExited) { return }
    try {
        [IO.File]::WriteAllText($request.path + '.cancel', '')
        $cancel.Enabled = $false
        $status.Text = $labels.cancelling
    } catch {
        [void][Windows.Forms.MessageBox]::Show($form, $labels.requestFailed, $labels.title)
    }
})
$timer = New-Object Windows.Forms.Timer
$timer.Interval = 250
$timer.Add_Tick({
    if ($target.HasExited) { $form.Close(); return }
    if (-not $cancel.Enabled) { return }
    try {
        $line = [IO.File]::ReadAllText($request.path)
        if ($line -match '^(prepare|render|encode|finishing) (\d+) (\d+)$') {
            $stage = $Matches[1]
            $done = [int]$Matches[2]
            $total = [int]$Matches[3]
            $status.Text = $labels.$stage
            if ($total -gt 0) {
                $status.Text += '  ' + ($labels.frames -f $done, $total)
                $bar.Style = 'Continuous'
                $bar.Value = [int](100.0 * $done / $total)
            } else {
                $bar.Style = 'Marquee'
            }
        }
    } catch [IO.IOException] {}
})
try {
    $timer.Start()
    [void]$form.ShowDialog()
} finally {
    $timer.Dispose()
    $form.Dispose()
    $target.Dispose()
}
"""


def run_blender_once(cli_data, log_path, progress_path=None):
  log = None
  try:
    log = io.open(log_path, 'wb')
  except IOError as error:
    print 'Blenderer: could not open the render log:', error
  try:
    options = {'stdout': log, 'stderr': subprocess.STDOUT} if log else {}
    process = subprocess.Popen(cli_data, **options)
    if progress_path:
      try:
        show_render_progress(process.pid, progress_path)
      except Exception as error:
        print 'Blenderer: could not open the progress window:', error
    exit_code = wait_for_blender(process, progress_path)
  finally:
    if log:
      log.close()

  if log:
    try:
      with io.open(log_path, 'r', encoding='utf-8', errors='replace') as stream:
        print('=' * 60)
        print('Blender log:')
        for line in stream:
          print line.rstrip(u'\r\n').encode('utf-8')
        print('=' * 60)
    except Exception as error:
      print 'Blenderer: could not read the render log:', error
  return exit_code


def wait_for_blender(process, progress_path):
  if not progress_path:
    return process.wait()
  cancel_path = progress_path + '.cancel'
  while process.poll() is None:
    if os.path.isfile(cancel_path):
      try:
        process.terminate()
      except WindowsError as error:
        if process.poll() is None:
          print 'Blenderer: could not stop the render process:', error
        break
      process.wait()
      return None
    time.sleep(0.1)
  return process.wait()


def read_blender_result(path):
  try:
    with io.open(path, 'r', encoding='utf-8') as stream:
      result = json.load(stream)
    if isinstance(result, dict):
      return result
  except (IOError, ValueError):
    pass
  return {}


def print_export_result(result, exit_code, elapsed, log_path):
  labels = {
    'image': ('ImageExported', 'Image exported.'),
    'video': ('VideoExported', 'Video exported.'),
    'scene': ('SceneSaved', 'Blender scene saved.'),
  }
  status = result.get('status')
  path = result.get('path')
  if status == 'cancelled':
    lines = [preflight_text('RenderCancelled', 'Render cancelled.')]
    if path:
      lines.append(preflight_text('CancelledFrames', 'Completed PNG frames: %s') % path)
    if result.get('leftovers'):
      lines.append(preflight_text('PartialFilesLeft', 'Could not remove these temporary files:'))
      lines.extend(result['leftovers'])
    ok = False
  elif exit_code == 0 and status in labels and path and os.path.isfile(path) and os.path.getsize(path) > 0:
    key, fallback = labels[status]
    lines = [preflight_text(key, fallback),
             preflight_text('SavedTo', 'Saved to: %s') % path]
    frames = result.get('frames')
    fps = result.get('fps')
    if status == 'video' and frames and fps:
      label = preflight_text('ExportedAnimationFrames', 'Video output: %d frames / %.3f s at %d FPS')
      lines.append(label % (frames, frames / float(fps), fps))
    ok = True
  elif status == 'frames_only' and path and os.path.isdir(path):
    lines = [preflight_text('FramesOnly', 'MP4 encoding failed. PNG frames were saved.'),
             preflight_text('SavedTo', 'Saved to: %s') % path]
    ok = False
  else:
    lines = [preflight_text('ExportFailed', 'Export failed. No finished output could be verified.')]
    ok = False
  lines.append(preflight_text('ExportElapsed', 'Export time: %.1f s') % elapsed)
  if not ok:
    if result.get('detail'):
      lines.append(u'%s' % result['detail'])
    if os.path.isfile(log_path):
      lines.append(preflight_text('ExportLog', 'Blender log: %s') % log_path)
  print u'\n'.join(lines).encode('utf-8')
  return ok


import locale
def addLamp(arg):
  thefolder, commandfilename = os.path.split(getCommandPath()[8:])
  thefolder = thefolder.decode('utf8')
  lamp = None
  if 'Sun' in arg.Name:
    lampuri = os.path.join('file///:',thefolder, 'Lights', 'BlenderSunLight.vcmx')
    lamp_strength = lightStrengthProp.Value/20.0
  if 'Spot' in arg.Name:
    lampuri = os.path.join('file///:',thefolder, 'Lights', 'BlenderSpotLight.vcmx')
    lamp_strength = lightStrengthProp.Value
  if 'Area' in arg.Name:
    lampuri = os.path.join('file///:',thefolder, 'Lights', 'BlenderAreaLight.vcmx')
    lamp_strength = lightStrengthProp.Value
  elif 'Point' in arg.Name:
    lampuri = os.path.join('file///:',thefolder, 'Lights', 'BlenderPointLight.vcmx')
    lamp_strength = lightStrengthProp.Value
  lamp = app.load(lampuri)
  c = camera.Coi
  e = camera.Eye
  m = vcMatrix.new()
  m.P = e
  v = e-c
  v.normalize()
  m.setIJK(v.X, v.Y, v.Z)
  m.translateRel(0,0,-1500)
  lamp.PositionMatrix = m
  lamp.Strength = lamp_strength
  lamp.update()
  app.render()


def addSparks(arg):
  selected_comps = app.SelectionManager.getSelection(VC_COMPONENT)
  robot_controller = None
  for selected_comp in selected_comps:
    robot_controllers = selected_comp.findBehavioursByType(VC_ROBOTCONTROLLER)
    robot_executors = selected_comp.findBehavioursByType(VC_ROBOTEXECUTOR)
    if robot_controllers and robot_executors:
      robot = robot_controllers[0]
  #if robot_controller:
  #  target = robot_controller.createTarget()
  thefolder, commandfilename = os.path.split(getCommandPath()[8:])
  thefolder = thefolder.decode('utf8')
  emitter = None
  emitter_uri = os.path.join('file///:',thefolder, 'Lights', 'SparksEmitter.vcmx')
  emitter = app.load(emitter_uri)
  c = camera.Coi
  e = camera.Eye
  m = vcMatrix.new()
  m.P = e
  v = e-c
  v.normalize()
  m.setIJK(v.X, v.Y, v.Z)
  m.translateRel(0,0,-500)
  emitter.PositionMatrix = m
  emitter.update()
  app.render()


def preset_exposure_key():
  return u'Preset exposure::' + as_unicode(presetProp.Value)


def apply_preset_exposure():
  name = as_unicode(presetProp.Value)
  preset = next((item for item in preset_tree if item.get('name') == name), None)
  values = (user_settings.get(preset_exposure_key()),
            preset.get('exposure') if preset is not None else None,
            prop_defaults_dict.get('Advanced::Exposure'), 0.0)
  for raw in values:
    ok, value = parse_setting(raw, VC_REAL)
    if ok and not (math.isnan(value) or math.isinf(value)):
      exposureProp.Value = value
      return


def save_preset_exposure(arg):
  update_preset_exposure(as_unicode(exposureProp.Value),
                         'PresetExposureSaved', 'Saved personal exposure for this lighting preset.')


def reset_preset_exposure(arg):
  if update_preset_exposure(None, 'PresetExposureReset', 'Restored this lighting preset\'s default exposure.'):
    apply_preset_exposure()


def update_preset_exposure(value, message, fallback):
  try:
    update_user_settings({preset_exposure_key(): value})
  except Exception as error:
    print 'Blenderer: could not save preset exposure:', error
    preflight_error('PresetExposureSaveFailed', 'Could not save the preset exposure.')
    return False
  print preflight_text(message, fallback)
  return True


def setEnvHDRI(arg):
  thefolder, commandfilename = os.path.split(getCommandPath()[8:])
  thefolder = thefolder.decode('utf8')
  envmapuri = ''
  hdri_strength = 1
  current_preset = [x for x in preset_tree if x.get("name") == presetProp.Value]
  if current_preset:
    current_preset = current_preset[0]
    hdri_element = current_preset.find('hdri')
    if hdri_element!=None: # must compare to none
      hdri_uri = hdri_element.get('file')
      hdri_uri = hdri_uri.decode('utf8')
      hdri_strength = hdri_element.get('strength')
      envmapuri = os.path.join('file:///', thefolder , 'Lights\\Presets' , hdri_uri)
      envtypeProp.Value = 'Image'
    else:
      envtypeProp.Value = 'ColorRGB'
      hdri_strength = 0
  envimageProp.Value = str(envmapuri)
  envstrengthProp.Value = float(hdri_strength)
  apply_preset_exposure()


def fovChangedEvent(arg):
  portrait = portraitProp.Value == 'Portrait'
  xRes = resYProp.Value if portrait else resXProp.Value
  yRes = resXProp.Value if portrait else resYProp.Value
  overshoot = 2
  temp_view = app.createView('TemporaryBlenderer__VIEW')
  cam = app.findCamera()
  mtx = cam.Matrix
  temp_view.CameraMatrix = mtx
  temp_view.CameraFovy = fovProp.Value + overshoot
  app.useView('TemporaryBlenderer__VIEW')
  app.render()
  app.deleteView('TemporaryBlenderer__VIEW')
  renderBorder('foo')
  app.render()


def showBorderChangedEvent(arg):
  if showBorderProp.Value:
    app2.OnRender = renderBorder
    renderBorder('foo')
  else:
    app2.OnRender = None
    renderBorder('foo')
  app.render()


def renderBorder(foo):
  portrait = portraitProp.Value == 'Portrait'
  xRes = resYProp.Value if portrait else resXProp.Value
  yRes = resXProp.Value if portrait else resYProp.Value
  red = app.findMaterial('red')
  if showBorderProp.Value:
    cam = app.findCamera()
    cont = sim.World.UserGeometry
    cont.clear()
    lset = cont.createGeometrySet(VC_COMPACTLINESET)
    dist_offset = 10.0
    for i in range(5):
      vertical = math.tan(fovProp.Value*DEG2RAD/2)*dist_offset
      horizontal = float(xRes)/float(yRes)*vertical
      v1 = vcVector.new(horizontal,-vertical,0)
      v2 = vcVector.new(horizontal,vertical,0)
      v3 = vcVector.new(-horizontal,vertical,0)
      v4 = vcVector.new(-horizontal,-vertical,0)
      mtx = cam.Matrix
      mtx.invert()
      mtx.translateRel(0,0,-dist_offset)
      line1 = [v1,v2,v3,v4,v1]
      line2 = [v2,v2 + (v4-v2)*0.2]
      line3 = [v4,v4 + (v2-v4)*0.2]
      line4 = [v3,v3 + (v1-v3)*0.2]
      line5 = [v1,v1 + (v3-v1)*0.2]
      for line in [line1, line2, line3, line4, line5]:
        line = [mtx*x for x in line]
        lset.addLine(line)
      dist_offset *= 10.0
    lset.LineWidth = 2
    lset.Material = red
  else:
    cont = sim.World.UserGeometry
    cont.clear()


def envtypeChanged(arg):
  if arg.Value == 'Image':
    envimageProp.IsVisible = True
    envcolorProp.IsVisible = False
  else:
    envimageProp.IsVisible = False
    envcolorProp.IsVisible = True


def floortypeChanged(arg):
  floorcolorimageProp.Value = str(floortextures[arg.Value][0])
  floorbumpimageProp.Value = str(floortextures[arg.Value][1])
  floorbumpstrengthProp.Value = floortextures[arg.Value][2]
  floortexturesizeProp.Value = floortextures[arg.Value][3]


thefolder, commandfilename = os.path.split(getCommandPath()[8:])
thefolder = thefolder.decode('utf8')
asphalt_uri = os.path.join('file:///'+thefolder, 'Textures', 'AsphaltOld.jpg')
asphaltnormal_uri = os.path.join('file:///'+thefolder, 'Textures', 'AsphaltNormal.jpg')
alu_uri = os.path.join('file:///'+thefolder, 'Textures', 'BrushedAlu.jpg')
alunormal_uri = os.path.join('file:///'+thefolder, 'Textures', 'BrushedAluNormal.jpg')
concretelight_uri = os.path.join('file:///'+thefolder, 'Textures', 'ConcreteLight.jpg')
concretewhite_uri = os.path.join('file:///'+thefolder, 'Textures', 'ConcreteWhite.jpg')
concretedark_uri = os.path.join('file:///'+thefolder, 'Textures', 'ConcreteDark.jpg')
metallic_uri = os.path.join('file:///'+thefolder, 'Textures', 'Metallic.jpg')
concretenormal_uri = os.path.join('file:///'+thefolder, 'Textures', 'ConcreteNormal.jpg')
brownslate_uri = os.path.join('file:///'+thefolder, 'Textures', 'FlooringSlateBrown.jpg')
greyslate_uri = os.path.join('file:///'+thefolder, 'Textures', 'FlooringSlateGrey.jpg')
lightslate_uri = os.path.join('file:///'+thefolder, 'Textures', 'FlooringSlateLight.jpg')
slatenormal_uri = os.path.join('file:///'+thefolder, 'Textures', 'FlooringSlateNormal.jpg')
oak_uri = os.path.join('file:///'+thefolder, 'Textures', 'WoodOakTexture.jpg')
metallicnormal_uri = os.path.join('file:///'+thefolder, 'Textures', 'MetallicNormal.jpg')
oaknormal_uri = os.path.join('file:///'+thefolder, 'Textures', 'WoodOakNormal.jpg')
grey_plaster_uri = os.path.join('file:///'+thefolder, 'Textures', 'grey_plaster_diff_2k.jpg')
grey_plaster_normal_uri = os.path.join('file:///'+thefolder, 'Textures', 'grey_plaster_nor_dx_2k.jpg')
brushed_concrete_uri = os.path.join('file:///'+thefolder, 'Textures', 'brushed_concrete_03_diff_2k.jpg')
brushed_concrete_normal_uri = os.path.join('file:///'+thefolder, 'Textures', 'brushed_concrete_03_nor_dx_2k.jpg')
square_floor_uri = os.path.join('file:///'+thefolder, 'Textures', 'square_floor_diff_2k.jpg')
square_floor_normal_uri = os.path.join('file:///'+thefolder, 'Textures', 'square_floor_nor_dx_2k.jpg')
gravel_uri = os.path.join('file:///'+thefolder, 'Textures', 'gravel_embedded_concrete_diff_2k.jpg')
gravel_normal_uri = os.path.join('file:///'+thefolder, 'Textures', 'gravel_embedded_concrete_nor_dx_2k.jpg')
garage_floor_uri = os.path.join('file:///'+thefolder, 'Textures', 'garage_floor_diff_2k.jpg')
garage_floor_normal_uri = os.path.join('file:///'+thefolder, 'Textures', 'garage_floor_nor_dx_2k.jpg')
pavement_uri = os.path.join('file:///'+thefolder, 'Textures', 'pavement_04_diff_2k.jpg')
pavement_normal_uri = os.path.join('file:///'+thefolder, 'Textures', 'pavement_04_nor_dx_2k.jpg')
pavement_multicolor_uri = os.path.join('file:///'+thefolder, 'Textures', 'pavement_03_diff_2k.jpg')
pavement_multicolor_normal_uri = os.path.join('file:///'+thefolder, 'Textures', 'pavement_03_nor_dx_2k.jpg')

# floorcolorimageProp : 0
# floorbumpimageProp : 1
# floorbumpstrengthProp : 2
# floortexturesizeProp : 3

factory_texture_dir = os.path.join(u'file:///' + thefolder, 'Textures')
floortextures = {
'Factory Green Rubber':(os.path.join(factory_texture_dir, 'xg_factory_green_rubber_color.png'),
      os.path.join(factory_texture_dir, 'xg_factory_green_rubber_normal.png'), 0.38, 1000),
'Blue Grey Epoxy':(os.path.join(factory_texture_dir, 'xg_blue_grey_epoxy_color.png'),
      os.path.join(factory_texture_dir, 'xg_blue_grey_epoxy_normal.png'), 0.18, 2000),
'Charcoal Studded Rubber':(os.path.join(factory_texture_dir, 'xg_charcoal_studded_rubber_color.png'),
      os.path.join(factory_texture_dir, 'xg_charcoal_studded_rubber_normal.png'), 0.72, 750),
'ConcreteLight':(concretelight_uri,concretenormal_uri, 1.0, 500),
'ConcreteWhite':(concretewhite_uri,concretenormal_uri, 1.0, 500),
'ConcreteDark':(concretedark_uri,concretenormal_uri, 1.0, 500),
'SlateBrown':(brownslate_uri,slatenormal_uri, 1.0, 1000),
'SlateGrey':(greyslate_uri,slatenormal_uri, 1.0, 1000),
'SlateLight':(lightslate_uri,slatenormal_uri, 1.0, 1000),
'Oak':(oak_uri,oaknormal_uri, 0.3, 1000),
'Asphalt':(asphalt_uri,asphaltnormal_uri, 1.0, 1000),
'Alu':(alu_uri,alunormal_uri, 1.0, 1000),
'GreyPlaster':(grey_plaster_uri,grey_plaster_normal_uri, 1.0, 2000),
'SquareFloor':(square_floor_uri,square_floor_normal_uri, 1.0, 2000),
'BrushedConcrete':(brushed_concrete_uri,brushed_concrete_normal_uri, 1.0, 2000),
'Gravel':(gravel_uri,gravel_normal_uri, 1.0, 2000),
'Pavement Dark':(pavement_uri,pavement_normal_uri, 1.0, 2000),
'Pavement Multi Color':(pavement_multicolor_uri,pavement_multicolor_normal_uri, 1.0, 2000),
'Garage floor':(garage_floor_uri,garage_floor_normal_uri, 1.0, 2000),
#'Metallic':(metallic_uri,metallicnormal_uri, 1.0, 1000),
'<ShadowCatcher>':('','', 1.0, 1000)
}


material_columns = ['Name',
'R', 'G', 'B',
'metallic',
'roughness',
'bumpiness',
'clearcoat',
'clearcoat_rouhness',
'opacity',
'style',
'color_map',
'normal_map']


#
# tooltips
#
net_command = app.findCommand('netCommand')
# Guard against re-registration on module reload (avoids startup lag from
# redundant SetLocalizationCommand IPC calls).
if not globals().get('_blenderer_l10n_registered'):
  # Tab / group names (Chinese + English) - multiple key formats because
  # ::-prefixed auto-tabs may localize differently from the Default tab.
  TAB_NAMES = [('Default', u'默认'), ('Lights', u'灯光'), ('Advanced', u'高级'),
               ('Materials', u'材质'), ('Animation', u'动画'), ('Env', u'环境'), ('Floor', u'地板')]
  for tab_en, tab_zh in TAB_NAMES:
    for lang, label in [('Chinese', tab_zh), ('English', tab_en)]:
      # Format A: cmdBlenderer520.TabName.Text   (works for Default tab)
      net_command.execute('SetLocalizationCommand', lang, 'Python', 'cmdBlenderer520.%s' % tab_en, 'Text', label)
      # Format B: cmdBlenderer520.TabName.Name   (property-like)
      net_command.execute('SetLocalizationCommand', lang, 'Python', 'cmdBlenderer520.%s' % tab_en, 'Name', label)
      # Format C: cmdBlenderer520.TabHeader.Text (explicit tab header)
      net_command.execute('SetLocalizationCommand', lang, 'Python', 'cmdBlenderer520.%s.TabHeader' % tab_en, 'Text', label)
      # Format D: :: separator (matches property name style)
      net_command.execute('SetLocalizationCommand', lang, 'Python', 'cmdBlenderer520.%s::' % tab_en, 'Text', label)
      net_command.execute('SetLocalizationCommand', lang, 'Python', 'cmdBlenderer520.%s::' % tab_en, 'Name', label)
      # Format E: .Properties.Text (property container)
      net_command.execute('SetLocalizationCommand', lang, 'Python', 'cmdBlenderer520.%s.Properties' % tab_en, 'Text', label)
      net_command.execute('SetLocalizationCommand', lang, 'Python', 'cmdBlenderer520.%s.Properties' % tab_en, 'Name', label)
# Floor style step values (Chinese)
if not globals().get('_blenderer_l10n_registered'):
  FLOOR_STYLE_ZH = [
    ('ConcreteLight', u'浅色混凝土'), ('ConcreteWhite', u'白色混凝土'), ('ConcreteDark', u'深色混凝土'),
    ('SlateBrown', u'棕色板岩'), ('SlateGrey', u'灰色板岩'), ('SlateLight', u'浅色板岩'),
    ('Oak', u'橡木'), ('Asphalt', u'沥青'), ('Alu', u'铝合金'),
    ('GreyPlaster', u'灰色石膏'), ('SquareFloor', u'方格地板'), ('BrushedConcrete', u'拉毛混凝土'),
    ('Gravel', u'砾石'), ('Pavement Dark', u'深色路面'), ('Pavement Multi Color', u'多彩路面'),
    ('Garage floor', u'车库地板'),
    ('Factory Green Rubber', u'工厂绿色橡胶'),
    ('Blue Grey Epoxy', u'蓝灰环氧地坪'),
    ('Charcoal Studded Rubber', u'深灰防滑圆点橡胶'),
    ('<ShadowCatcher>', u'阴影捕获器')
  ]
  for style_en, style_zh in FLOOR_STYLE_ZH:
    net_command.execute('SetLocalizationCommand', 'Chinese', 'Python', 'cmdBlenderer520.Floor::Style.%s' % style_en, 'Name', style_zh)
  # Default tab
  for name, label in [('Output folder', u'输出文件夹'),
                      ('Choose output folder', u'选择文件夹…'),
                      ('Image name', u'图片名称'),
                      ('Animation::Output folder', u'输出文件夹'),
                      ('Animation::Choose output folder', u'选择文件夹…'),
                      ('Animation::Video name', u'视频名称')]:
    net_command.execute('SetLocalizationCommand', 'Chinese', 'Python', 'cmdBlenderer520.' + name, 'Name', label)
  samples_tip = '''More samples improve the rendering quality with less noise and smoother lighting, but requires longer rendering time.'''
  presets_tip = '''Predefined lighting presets. Preset includes an environment map which can be edited on Env-tab and may also include actual light sources.'''
  reuse_scene_tip = '''Use this option to render the same scene again. Saves a lot of time as the scene is not exported/imported again. Simulation scene must include all the same components and nodes for this to work. Disable this if rendering is not working properly.'''
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Samples', 'Description', samples_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Lighting Preset', 'Description', presets_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Reuse Previous Scene', 'Description', reuse_scene_tip)
  # Lights tab
  addpoint_tip = '''Add a point light to the scene. Light is located to the current location of the camera. Select the light component in the scene to edit its properties.'''
  addarea_tip = '''Add an area light to the scene. Light is located to the current location of the camera. Select the light component in the scene to edit its properties.'''
  addspot_tip = '''Add a spot light to the scene. Light is located to the current location of the camera. Select the light component in the scene to edit its properties.'''
  addsun_tip = '''Add a sun light to the scene. Light is located to the current location of the camera. Select the light component in the scene to edit its properties.'''
  defaultstrength_tip = '''Default strength given to a newly created light. Strength can be later edited in the properties of the light component.'''
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Lights::Add Point Light', 'Description', addpoint_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Lights::Add Area Light', 'Description', addarea_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Lights::Add Spot Light', 'Description', addspot_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Lights::Add Sun Light', 'Description', addsun_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Lights::Default Strength', 'Description', defaultstrength_tip)
  # Advanced tab
  camerafov_tip = '''Vertical field of view of the camera.'''
  showborder_tip = '''Visualize the camera framing in 3d. Change CameraFov for desired result. Resize panels to fit the frame in 3d window horizontally.'''
  exposure_tip = '''Camera exposure. Smaller values result darker image. Does not change the depth of field.'''
  bloom_tip = '''Enable light bloom effect. Brighter areas in the image bloom creating a glowing effect.'''
  bloomintesity_tip = '''Strength of the bloom effect when Bloom is enabled.'''
  openinblender_tip = '''When enabled "Render" and "Render Animation" buttons will not render the scene. Instead the scene is converted and opened in Blender for further editing.'''
  renderedges_tip = '''Enable to add black edges to the render. Also flattens the materials a little for toon shading style.'''
  edgethickness_tip = '''Defines the edge thickness for edge rendering. Enable also the "Render Edges" property.'''
  renderdevice_tip = '''Choose GPU or CPU device for rendering. GPU is required for Cycles rendering. Selecting CPU will stop the render and display: You need GPU!你需要一张独立显卡渲染更合适！'''
  depthoffieldnode_tip = '''Choose a node in the 3d scene to adjust camera lense focus to that specific object.'''
  depthFstop_tip = '''F Stop value of the lense. Smaller value result blurrier image outside the focus area.'''
  indirect_tip = '''Enabling indirect lighting results more realistic lighting but requires longer rendering and prep time.'''
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::CameraFov', 'Description', camerafov_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::Show Border', 'Description', showborder_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::Exposure', 'Description', exposure_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::Bloom', 'Description', bloom_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::Bloom Intensity', 'Description', bloomintesity_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::Open in Blender', 'Description', openinblender_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::Render Edges', 'Description', renderedges_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::Edge Thickness', 'Description', edgethickness_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::RenderDevice', 'Description', renderdevice_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::DepthOfFieldNode', 'Description', depthoffieldnode_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::Depth F-Stop', 'Description', depthFstop_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Advanced::Indirect Lighting', 'Description', indirect_tip)

  # Materials tab
  materialmode_tip = '''Default:
  Use scene materials as they are in the VC model.

  Read From Table:
  Read material definitions from the materials.csv file inside the command folder.

  Write To Table:
  Write scene material definitions to the materials.csv file inside the command folder.

  Hint: Use first Write To Table mode and render. Then edit the csv and then render again using the Read From Table mode.'''
  delimiter_tip = '''Choose the delimiter that MS Excel is using in your region.'''
  robotmaterials_tip = '''Default:
  Use materials of the robots as they are in the VC model.

  Smart Materials:
  Some shading effects are automatically applied to the materials in the components including robot controller behavior.'''
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Materials::Mode', 'Description', materialmode_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Materials::Table Delimiter', 'Description', delimiter_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Materials::Robot Materials', 'Description', robotmaterials_tip)
  # Animation tab
  rec_animation_tip = '''To record the animation for rendering enable this property. Then run the simulation until this property is automatically disabled and then call RenderAnimation.'''
  start_animation_tip = '''Animation recording start time in seconds.'''
  end_animation_tip = '''Animation recording end time in seconds.'''
  recstep_animation_tip = '''Animation recording step in seconds. Example: 0.04s would result in 25 key frames per second.'''
  fps_animation_tip = '''Frames per second of the result video. This value can be different than what the Rec step property defines to speed up or slow down the resulting video.'''
  container_animation_tip = '''Video file container format. Only MP4 is supported (H.264 codec, best compression and compatibility).'''
  render_animation_tip = '''Make sure to record the animation first before calling rendering. Use RecAnimation preperty for recording the animation.'''
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Animation::RecAnimation', 'Description', rec_animation_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Animation::Start', 'Description', start_animation_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Animation::End', 'Description', end_animation_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Animation::Rec step', 'Description', recstep_animation_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Animation::FPS', 'Description', fps_animation_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Animation::Container', 'Description', container_animation_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Animation::RenderAnimation', 'Description', render_animation_tip)
  # Env tab
  background_tip = '''Background can be an hdr environment image or a plain solid color.'''
  image_tip = '''Background image file. Use spherical projection *.hdr files.'''
  colorrgb_tip = '''Background color defined as RGB values between 0...1'''
  strength_tip = '''Strength of the light that the background adds to the scene.'''
  roration_tip = '''Rotates the background image around the Z axis.'''
  visible_tip = '''Show or hide the background. Even if the background is hidden, it can add light to the scene and will show up in reflections.'''
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Env::Background', 'Description', background_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Env::Image', 'Description', image_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Env::ColorRGB', 'Description', colorrgb_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Env::Strength', 'Description', strength_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Env::Rotation', 'Description', roration_tip)
  net_command.execute('SetLocalizationCommand', 'English', 'Python', 'cmdBlenderer520.Env::Visible', 'Description', visible_tip)
  _blenderer_l10n_registered = True


addState(None)

