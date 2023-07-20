# 3DE4.script.name:    Import object track
# 3DE4.script.gui:    Main Window::mpc_matchmove
# 3DE4.script.comment:    Imports object animation from maya as *.mov file
# import sdv's python vector lib...

 

from vl_sdv import *
import math

 

window_title = "ImportObjTrack"

 

def convertToAngles(r3d):
        rot    = rot3d(mat3d(r3d)).angles(VL_APPLY_ZXY)
        rx    = (rot[0]*180.0)/3.141592654
        ry    = (rot[1]*180.0)/3.141592654
        rz    = (rot[2]*180.0)/3.141592654
        return(rx,ry,rz)


def ImportObjPose():
    pg    = tde4.getCurrentPGroup()
    cam     = tde4.getCurrentCamera()
    frame   = tde4.getCurrentFrame(cam)
    if pg!=None and cam !=None:
        if tde4.getPGroupType(pg)=="OBJECT":
            path    = tde4.getWidgetValue(req,"file_browser")
            if path!=None:
                f    = open(path,"r")
                frame    = 1
                if not f.closed:
                    while True:
                        string    = f.readline()
                        if string=="": break
                        a    = string.split()
                        if len(a) == 6:

                            pos_x    = float(a[0])
                            pos_y    = float(a[1])
                            pos_z    = float(a[2])
                            rot_x    = float(a[3])
                            rot_y    = float(a[4])
                            rot_z    = float(a[5])

                            rot_x    = (rot_x*3.141592654)/180.0
                            rot_y    = (rot_y*3.141592654)/180.0
                            rot_z    = (rot_z*3.141592654)/180.0
                            r3d    = mat3d(rot3d(rot_x,rot_y,rot_z,VL_APPLY_ZXY))
                            r3d0    = [[r3d[0][0],r3d[0][1],r3d[0][2]],[r3d[1][0],r3d[1][1],r3d[1][2]],[r3d[2][0],r3d[2][1],r3d[2][2]]]

                            newvalues = tde4.convertObjectPGroupTransformationWorldTo3DE(cam, frame, r3d0, [pos_x,pos_y,pos_z], 1.0, 0)
                            tde4.setPGroupPosition3D(pg,cam,frame,newvalues[1])
                            tde4.setPGroupRotation3D(pg,cam,frame,newvalues[0])
                            tde4.setPGroupPostfilterMode(pg,"POSTFILTER_OFF")
                            tde4.filterPGroup(pg,cam)
                            tde4.setPGroupScale3D(pg,1.0)
                            tde4.updateGUI()
                            frame    = frame+1
        else:
            tde4.postQuestionRequester(window_title,"ObjectPGroup must be selected.", "ok")
    else:
        tde4.postQuestionRequester(window_title, "there must be a Camera and PointGroup.", "ok")    

def doIt():

 

    ImportObjPose()

 


try:
    req    = _pose_requester
except (ValueError,NameError,TypeError):
    req    = tde4.createCustomRequester()
    _pose_requester    = req

    tde4.addFileWidget(req,"file_browser","Browse...","*.mov")    

ret = tde4.postCustomRequester(req,window_title,600,70,"Ok","Cancel")    

 

doIt()
