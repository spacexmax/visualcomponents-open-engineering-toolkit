# -*- coding: utf-8 -*-
# Blenderer Addon version 2026-08 v2.6.0 (Blender 5.2)
# with VisualComponents
# ################Thanks for Tang ###########################
from vcApplication import *

cmdName = 'cmdBlenderer520'
title = 'Blenderer5.2.0'
pyNetCommand = findCommand('netCommand')
pyNetCommand.execute('SetLocalizationCommand', 'English', 'Python', cmdName, 'Text', title)

def OnStart():
  cmduri = getApplicationPath() + 'Blenderer.py'
  # Register ALL localization labels (both English and Chinese) so they are
  # available. The actual language is applied in Blenderer.py's OnStart
  # based on the saved preference.
  try:
    import BlenderAddOn_Language
    BlenderAddOn_Language.register_localization(cmdName, pyNetCommand)
  except Exception as e:
    print 'Blender5.2.0: init failed: %s' % e
  cmd = loadCommand(cmdName, cmduri)
  iconuri = getCommandPath() + 'rBlendererIcon.svg'
  addMenuItem('VcTabHome/Render', title, -1, cmdName, iconuri)
  addMenuItem('VcTabAuthor/Render', title, -1, cmdName, iconuri)

