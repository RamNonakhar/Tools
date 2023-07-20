# 3DE4.script.name:    Export Nuke LD_3DE4 Lens Distortion Node
# 3DE4.script.version:    v1.2
# 3DE4.script.gui:    Main Window::3DE4::File::Export
# 3DE4.script.comment:    Creates an LD_3DE4 Lens Distortion Node for each selected camera (exports .nk script)
# 3DE4.script.comment:    The five LD_3DE4 Nodes were introduced in Lens Distortion Plugin Kit version 1.7 (2013-12-11).
# 3DE4.script.comment:  With the release of Nuke8.0 we will update and promote these plugins on linux, osx and windows,
# 3DE4.script.comment:    also for Nuke6.2 (osx and linux), Nuke6.3 and Nuke7.0.
# 3DE4.script.comment:    This script should not be mistaken for "Export Weta Nuke Distortion"
# Date: 2013-11-18
# Original script: Wolgang Niedermeier (Weta)
# Author: Uwe Sassenberg (SDV)
# For 3DE4 releases r1 or higher
# Versions:
# 1.2 - Minor Changes for first official release
# 1.1 - Make sure it runs on R1
# 1.0 - Start

 


# Start Python 3 Migration
from __future__ import print_function
from builtins import str
# End Python 3 Migration
import tde4
import string
import re

 

# We translate our API model and parameter names into Nuke identifiers.
# The rules are:
# - The empty string maps to an underscore
# - When the names starts with 0-9 it gets an underscore
# - All non-alphanumeric characters are mapped to underscores, but sequences
#   of underscores shrink to a single underscore, looks better.
def nukify_name(s):
    if s == "":
        return "_"
    if s[0] in "0123456789":
        t = "_"
    else:
        t = ""
    t += string.join(re.sub("[+,:; _-]+","_",s.strip()).split())
    return t

 

# Nuke interprets entities like "<" and ">".
def decode_entities(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

 

class CancelException(Exception):    
    pass

 

def getLDmodelParameterList(model):
    l = []
    for p in range(tde4.getLDModelNoParameters(model)):
        l.append(tde4.getLDModelParameterName(model, p))
    return l

 

def exportNukeDewarpNode(cam, offset, nuke_path):
    lens     = tde4.getCameraLens(cam)
    model     = tde4.getLensLDModel(lens)
    num_frames     = tde4.getCameraNoFrames(cam)
    w_fb_cm = tde4.getLensFBackWidth(lens)
    h_fb_cm = tde4.getLensFBackHeight(lens)
    lco_x_cm = tde4.getLensLensCenterX(lens)
    lco_y_cm = tde4.getLensLensCenterY(lens)
    pxa = tde4.getLensPixelAspect(lens)
# xa,xb,ya,yb in unit coordinates, in this order.
    fov = tde4.getCameraFOV(cam)

    print('camera: ', tde4.getCameraName(cam))
    print('offset:', offset)
    print('lens:', tde4.getLensName(lens))
    print('model: ', model)

    f = open(nuke_path,"w")
    try:
        f.write('# Created by 3DEqualizer4 using Export Nuke Distortion Nodes export script\n')
        f.write("LD" + nukify_name(model) + ' {\n')
        f.write(' direction undistort\n')

 

# write focal length curve if dynamic
        if tde4.getCameraZoomingFlag(cam):
            print('dynamic focal length')
            f.write(' tde4_focal_length_cm {{curve ')    
            for frame in range(1,num_frames + 1):
                f.write ('x%i' % (frame+offset))
                f.write(' %.7f ' % tde4.getCameraFocalLength(cam,frame))
            f.write('}}\n')
# write static focal length else
        else:
            print('static focal length')
            f.write(' tde4_focal_length_cm %.7f \n' % tde4.getCameraFocalLength(cam,1))
# write focus distance curve if dynamic
        try:
            if tde4.getCameraFocusMode(cam) == "FOCUS_DYNAMIC":
                print('dynamic focus distance')
                f.write(' tde4_custom_focus_distance_cm {{curve ')    
                for frame in range(1,num_frames + 1):
                    f.write ('x%i' % (frame+offset))
                    f.write(' %.7f ' % tde4.getCameraFocus(cam,frame))
                f.write('}}\n')
        except:
# For 3DE4 Release 1:
            pass
# write static focus distance else
        else:
            print('static focus distance')
            try:
                f.write(' tde4_custom_focus_distance_cm %.7f \n' % tde4.getCameraFocus(cam,1))
            except:
# For 3DE4 Release 1:
                f.write(' tde4_custom_focus_distance_cm 100.0 \n')
# write camera
        f.write(' tde4_filmback_width_cm %.7f \n' % w_fb_cm)
        f.write(' tde4_filmback_height_cm %.7f \n' % h_fb_cm)
        f.write(' tde4_lens_center_offset_x_cm %.7f \n' % lco_x_cm)
        f.write(' tde4_lens_center_offset_y_cm %.7f \n' % lco_y_cm)
        f.write(' tde4_pixel_aspect %.7f \n' % pxa)
        f.write(' field_of_view_xa_unit %.7f \n' % fov[0])
        f.write(' field_of_view_ya_unit %.7f \n' % fov[2])
        f.write(' field_of_view_xb_unit %.7f \n' % fov[1])
        f.write(' field_of_view_yb_unit %.7f \n' % fov[3])


# write distortion parameters
#
# dynamic distortion
        try:
            dyndistmode    = tde4.getLensDynamicDistortionMode(lens)
        except:
# For 3DE4 Release 1:
            if tde4.getLensDynamicDistortionFlag(lens) == 1:
                dyndistmode = "DISTORTION_DYNAMIC_FOCAL_LENGTH"
            else:
                dyndistmode = "DISTORTION_STATIC"

        if dyndistmode=="DISTORTION_DYNAMIC_FOCAL_LENGTH":
            print('dynamic lens distortion, focal length')
# dynamic focal length (zoom)
            for para in (getLDmodelParameterList(model)):
                f.write(' ' + nukify_name(para) + ' {{curve ')    
                for frame in range(1,num_frames + 1):
                    focal = tde4.getCameraFocalLength(cam,frame)
                    f.write ('x%i' % (frame+offset))
                    f.write(' %.7f '%tde4.getLensLDAdjustableParameter(lens, para, focal))    
                f.write('}}\n')

 

        if dyndistmode=="DISTORTION_DYNAMIC_FOCUS_DISTANCE":
            print('dynamic lens distortion, focus distance')
# dynamic focus distance
            for para in (getLDmodelParameterList(model)):
                f.write(' ' + nukify_name(para) + ' {{curve ')    
                for frame in range(1,num_frames + 1):
# Older Releases do not have Focus-methods.
                    try:
                        focus = tde4.getCameraFocus(cam,frame)
                    except:
                        focus = 100.0
                    f.write ('x%i' % (frame+offset))
                    f.write(' %.7f '%tde4.getLensLDAdjustableParameter(lens, para, focus))    
                f.write('}}\n')

 

# static distortion
        if dyndistmode=="DISTORTION_STATIC":
            print('static lens distortion')
            for para in (getLDmodelParameterList(model)):
                f.write(' ' + nukify_name(para) + ' %.7f \n'%tde4.getLensLDAdjustableParameter(lens, para, 1))

        f.write(' name LD_3DE4_' + decode_entities(tde4.getCameraName(cam)) + '\n')
        f.write('}\n')

 

    finally:    
        f.close()    

 


# main
try:
    camlist = tde4.getCameraList(1)
    if not camlist:
        raise Exception('     Only selected cameras will be exported     ')

    for cam in camlist:
        offset     = (tde4.getCameraSequenceAttr(cam)[0])-1
        lens     = tde4.getCameraLens(cam)

 

# check if variable 'nuke_path' exists already or is of type None
        try: 
            nuke_path
        except:
            nuke_path = ''

 

        if nuke_path is None:
            nuke_path = ''

 


# open requester
        nuke_node_req    = tde4.createCustomRequester()
        tde4.addFileWidget(nuke_node_req, 'userInput', 'Filename: ', '*.nk', nuke_path)

 

        if tde4.getCameraZoomingFlag(cam) and offset != 0:
            tde4.addToggleWidget(nuke_node_req, "stfr_menu", ("Offset curves to frame " + str(offset+1)+": "), 1)

 

        ret    = tde4.postCustomRequester(nuke_node_req,'  Export nuke distortion node for camera  '+tde4.getCameraName(cam)+' ',700,110,'  Ok  ',' Cancel ')
        if ret != 1:
            raise CancelException('Cancelled')
        nuke_path = tde4.getWidgetValue(nuke_node_req, 'userInput')

 

# check path and suffix
        if not nuke_path:
            raise Exception('     No path entered     ')

        if not nuke_path.endswith('.nk'):
            nuke_path    = nuke_path+'.nk'

 

# check if offset should be applied or not if there is one
        if tde4.getCameraZoomingFlag(cam) and offset != 0:
            n    = tde4.getWidgetValue(nuke_node_req,"stfr_menu")
            if n != 1:
                offset = 0

 

# export
        if ret == 1:
            print('------------------ Export tde4 Nuke Distortion Node ------------------')
            exportNukeDewarpNode(cam, offset, nuke_path)
            print('file:',nuke_path, '\n')

 


except CancelException as e:
    print(e)

 

except Exception as e:
    print(e)
    tde4.postQuestionRequester('Error ', str(e), '  OK  ')
