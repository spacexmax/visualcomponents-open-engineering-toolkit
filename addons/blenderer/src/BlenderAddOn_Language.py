# -*- coding: utf-8 -*-
# BlenderAddOn_Language.py
# Localization module for Blenderer add-on in Visual Components.
# Provides Chinese/English labels for the command, its properties and step
# values via XAML resource dictionaries (primary) and SetLocalizationCommand
# (fallback for manual language switching).
#
# XAML files:
#   Blenderer_2_6_0__2026_0801.PyResource.English.xaml
#   Blenderer_2_6_0__2026_0801.PyResource.Chinese.xaml
#
# Usage:
#   import BlenderAddOn_Language
#   BlenderAddOn_Language.register_localization('cmdBlenderer520', pyNetCommand)
#
# Reference: VC Premium 4.10 Help
#   Python_API/Creating_a_Python_Add-on.htm  (SetLocalizationCommand usage)
#   Python_API/Template_for_Python_Add-on.htm (key format & step values)

SCOPE = 'Python'
LANG_ZH = 'Chinese'
LANG_EN = 'English'

# ---------------------------------------------------------------------------
# Property display-name mapping (Chinese only; English defaults to the
# property name itself when no localization is found)
# ---------------------------------------------------------------------------
# Note: Property name prefixes are English (Lights/Advanced/Materials/Animation/
# Env/Floor). Tab/group headers and all property names are localized via XAML
# resource dictionaries and SetLocalizationCommand fallback below.

PROP_LABELS_ZH = {
    'Output file':                    u'输出文件',
    'Samples':                        u'EEVEE采样数',
    'Resolution':                     u'分辨率',
    'ResX':                           u'横向分辨率',
    'ResY':                           u'纵向分辨率',
    'Page':                           u'页面方向',
    'Lighting Preset':                u'光照预设',
    'Render':                         u'渲染图片',
    'Reuse Previous Scene':           u'复用上次场景',
    'Lights::Add Point Light':        u'添加点光源',
    'Lights::Add Area Light':         u'添加面光源',
    'Lights::Add Spot Light':         u'添加聚光灯',
    'Lights::Add Sun Light':          u'添加阳光光源',
    'Lights::Default Strength':       u'默认强度',
    'Lights::Add Sparks Emitter':     u'添加火花发射器',
    'Advanced::CameraFov':            u'相机视角场角',
    'Advanced::Show Border':          u'显示边框',
    'Advanced::Exposure':             u'曝光',
    'Advanced::Bloom':                u'泛光',
    'Advanced::Bloom Intensity':      u'泛光强度',
    'Advanced::Open in Blender':      u'在 Blender 中打开',
    'Advanced::Render Engine':        u'渲染引擎',
    'Advanced::RenderDevice':         u'渲染设备',
    'Advanced::OnlyCyclesBackend':    u'Cycles后端',
    'Advanced::OnlyCyclesSamples':   u'Cycles采样数',
    'Advanced::Render Edges':         u'渲染边缘',
    'Advanced::Edge Thickness':      u'边缘粗细',
    'Advanced::DepthOfFieldNode':    u'景深节点',
    'Advanced::Depth F-Stop':         u'景深光圈',
    'Advanced::Indirect Lighting':    u'间接光照',
    'Advanced::Blender Executable':   u'Blender 可执行文件',
    'Advanced::Reset All Properties': u'重置所有属性',
    'Materials::Mode':                u'模式',
    'Materials::Table Delimiter':     u'表格分隔符',
    'Materials::Robot Materials':     u'机器人材质',
    'Materials::Monochrome Override': u'单色覆盖',
    'Materials::UseSimpleTransparent':u'使用简单透明',
    'Materials::MaterialVersion':     u'材质版本',
    'Animation::RecAnimation':        u'录制动画',
    'Animation::Start':               u'开始',
    'Animation::End':                 u'结束',
    'Animation::Rec step':            u'录制步长',
    'Animation::FPS':                 u'帧率',
    'Animation::Container':           u'视频格式',
    'Animation::RenderVideoMode':     u'输出方式',
    'Animation::VideoQuality':        u'视频质量',
    'Animation::RenderAnimation':     u'渲染动画',
    'Env::Background':                u'背景',
    'Env::Image':                     u'图片',
    'Env::ColorRGB':                  u'颜色',
    'Env::Strength':                  u'强度',
    'Env::Rotation':                  u'旋转',
    'Env::Visible':                   u'可见',
    'Env::BackdropType':              u'背景类型',
    'Env::BackdropImage':             u'背景图片',
    'Env::BackdropColorRGB':          u'背景颜色',
    'Floor::Visible':                u'地板可见',
    'Floor::BorderSize':             u'边框尺寸',
    'Floor::Style':                   u'地板样式',
    'Floor::ColorTexture':            u'颜色纹理',
    'Floor::BumpTexture':             u'凹凸纹理',
    'Floor::BumpStrength':            u'凹凸强度',
    'Floor::TextureSize':            u'纹理尺寸',
    'Floor::ColorRGB':                u'颜色',
}

# ---------------------------------------------------------------------------
# Step value (drop-down option) mapping
# ---------------------------------------------------------------------------
STEP_LABELS_ZH = {
    ('Page', 'Landscape'):            u'横向',
    ('Page', 'Portrait'):             u'纵向',
    ('Advanced::Indirect Lighting', 'Off'):    u'关闭',
    ('Advanced::Indirect Lighting', 'Fast'):   u'快速',
    ('Advanced::Indirect Lighting', 'Normal'): u'标准',
    ('Advanced::Indirect Lighting', 'HQ'):    u'高质量',
    ('Materials::Mode', 'Default'):           u'默认',
    ('Materials::Mode', 'Read From Table'):   u'从表格读取',
    ('Materials::Mode', 'Write To Table'):    u'写入表格',
    ('Materials::Robot Materials', 'Default'):        u'默认',
    ('Materials::Robot Materials', 'Smart Materials'):u'智能材质',
    ('Materials::MaterialVersion', 'OLD'):    u'旧版',
    ('Materials::MaterialVersion', 'NEW'):    u'新版',
    ('Env::Background', 'Image'):    u'图片',
    ('Env::Background', 'ColorRGB'): u'颜色',
    ('Env::BackdropType', 'None'):    u'无',
    ('Env::BackdropType', 'Image'):   u'图片',
    ('Env::BackdropType', 'ColorRGB'):u'颜色',
    ('Animation::RenderVideoMode', 'PNG Sequence'): u'PNG 序列转 MP4',
    ('Animation::RenderVideoMode', 'Direct Video'): u'直接输出 MP4',
    ('Animation::VideoQuality', 'Lossless'): u'感知无损',
    ('Animation::VideoQuality', 'High'):    u'高质量',
    ('Animation::VideoQuality', 'Low'):     u'低质量',
    ('Floor::Style', 'ConcreteLight'):       u'浅色混凝土',
    ('Floor::Style', 'ConcreteWhite'):       u'白色混凝土',
    ('Floor::Style', 'ConcreteDark'):        u'深色混凝土',
    ('Floor::Style', 'SlateBrown'):          u'棕色板岩',
    ('Floor::Style', 'SlateGrey'):           u'灰色板岩',
    ('Floor::Style', 'SlateLight'):          u'浅色板岩',
    ('Floor::Style', 'Oak'):                 u'橡木',
    ('Floor::Style', 'Asphalt'):             u'沥青',
    ('Floor::Style', 'Alu'):                 u'铝合金',
    ('Floor::Style', 'GreyPlaster'):         u'灰色石膏',
    ('Floor::Style', 'SquareFloor'):         u'方格地板',
    ('Floor::Style', 'BrushedConcrete'):     u'拉毛混凝土',
    ('Floor::Style', 'Gravel'):              u'砾石',
    ('Floor::Style', 'Pavement Dark'):       u'深色路面',
    ('Floor::Style', 'Pavement Multi Color'):u'多彩路面',
    ('Floor::Style', 'Garage floor'):        u'车库地板',
    ('Floor::Style', '<ShadowCatcher>'):     u'阴影捕获器',
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_net_command():
    """Get netCommand handle via getApplication().findCommand."""
    try:
        try:
            from vcApplication import getApplication
        except ImportError:
            from vcCommand import getApplication
        app = getApplication()
        return app.findCommand('netCommand')
    except Exception:
        return None


def _register_labels(localize, command_name, lang, prop_labels, step_labels):
    """Register property names and step value labels."""
    count = 0
    for prop_name, label in (prop_labels or {}).items():
        key = '%s.%s' % (command_name, prop_name)
        try:
            localize.execute('SetLocalizationCommand', lang, SCOPE, key, 'Name', label)
            count += 1
        except Exception:
            pass
    for (prop_name, step_val), label in (step_labels or {}).items():
        key = '%s.%s.%s' % (command_name, prop_name, step_val)
        try:
            localize.execute('SetLocalizationCommand', lang, SCOPE, key, 'Name', label)
            count += 1
        except Exception:
            pass
    return count


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_registered = False


def _detect_language():
    """Detect VC's active UI language.

    Returns
    -------
    str
        'Chinese' if the current VC UI language is Simplified/Traditional
        Chinese; 'English' for all other cases.
    """
    # Try .NET CurrentUICulture via IronPython clr interop (most reliable in VC)
    try:
        import clr
        clr.AddReference('System')
        from System.Threading import Thread
        ui_name = Thread.CurrentThread.CurrentUICulture.Name
        if ui_name.lower().startswith('zh'):
            return 'Chinese'
    except Exception:
        pass
    # Fallback: try Python locale module
    try:
        import locale
        lang, _ = locale.getdefaultlocale()
        if lang and lang.lower().startswith('zh'):
            return 'Chinese'
    except Exception:
        pass
    # Fallback: inspect environment variables (LANG, LC_ALL, etc.)
    try:
        import os
        for envkey in ['LANG', 'LC_ALL', 'LANGUAGE']:
            val = os.environ.get(envkey, '')
            if val and val.lower().startswith('zh'):
                return 'Chinese'
    except Exception:
        pass
    return 'English'


def register_localization(command_name, net_command=None):
    """Register Chinese localization labels as a fallback for XAML.

    XAML files (Blenderer_2_6_0__2026_0801.PyResource.*.xaml) are the
    primary localization mechanism. This function provides a fallback via
    SetLocalizationCommand when XAML auto-loading is not available.

    Parameters
    ----------
    command_name : str
        The command id, e.g. 'cmdBlenderer520'.
    net_command : object, optional
        Pre-found netCommand handle.
    """
    global _registered
    if _registered:
        return True
    try:
        localize = net_command or _get_net_command()
        if localize is None:
            print 'Blender5.2.0: cannot find netCommand'
            return False
        lang = _detect_language()
        if lang == 'Chinese':
            _register_labels(localize, command_name, LANG_ZH,
                             PROP_LABELS_ZH, STEP_LABELS_ZH)
        _registered = True
        print 'Blender5.2.0,Please!'
        return True
    except Exception as e:
        print 'Blender5.2.0: %s' % e
        return False


def prompt_reopen(language):
    """Print a message telling the user to close and reopen the command.

    Parameters
    ----------
    language : str
        The selected language ('English' or 'Chinese').
    """
    print ''
    print '============================================'
    print 'BlenderAddOn_Language: language changed to "%s"' % language
    print 'Please close and reopen the Blenderer command'
    print 'for the new language to take effect.'
    print '============================================'
    print ''
