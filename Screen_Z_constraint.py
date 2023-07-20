Python 3.11.3 (tags/v3.11.3:f3909b8, Apr  4 2023, 23:49:59) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
# 3DE4.script.name: ObjectPGroup Screen Z Constraint...
# 3DE4.script.version: v1.2
# 3DE4.script.gui: Lineup Controls::Edit
# 3DE4.script.gui.config_menus: true
# 3DE4.script.gui.button: Lineup Controls::ScreenZ, align-bottom-left,80,20
# 3DE4.script.gui.button: Orientation Controls::ScreenZ, align-bottom-left,70,20

 

# Start Python 3 Migration
from builtins import str
# End Python 3 Migration
from vl_sdv import*

 

def Bake_Buffer_Curves():
    pg = tde4.getCurrentPGroup()
    cam = tde4.getCurrentCamera()
    frames = tde4.getCameraNoFrames(cam)
    pg_type = tde4.getPGroupType(pg)
    currentFrame = tde4.getCurrentFrame(cam)
    if pg_type == "CAMERA":
        for i in range(1,frames+1):
            tde4.setCurrentFrame(cam,i)
            frame = tde4.getCurrentFrame(cam)    
            pos = vec3d(tde4.getPGroupPosition3D(pg,cam,frame))
            rot = mat3d(tde4.getPGroupRotation3D(pg,cam,frame))
            scale = tde4.getPGroupScale3D(pg)
            focal = tde4.getCameraFocalLength(cam,frame)
            tde4.setPGroupPosition3D(pg,cam,frame,pos.list())
            tde4.setPGroupRotation3D(pg,cam,frame,rot.list())
            tde4.setPGroupScale3D(pg,scale)
            tde4.setCameraFocalLength(cam,frame,focal)
        pf_mode  = tde4.getPGroupPostfilterMode(pg)
        tde4.setPGroupPostfilterMode(pg,"POSTFILTER_OFF")
        tde4.filterPGroup(pg,cam)
        tde4.setPGroupPostfilterMode(pg,pf_mode)
    if pg_type == "OBJECT":
        pg = tde4.getCurrentPGroup()
        for i_pg in tde4.getPGroupList():
            if tde4.getPGroupType(i_pg) == "CAMERA":
                id_cpg = i_pg
                break
        id_opg = pg        
        for i in range(1,frames+1):
            tde4.setCurrentFrame(cam,i)
            frame = tde4.getCurrentFrame(cam)
            rot_cpg = mat3d(tde4.getPGroupRotation3D(id_cpg,cam,frame))
            pos_cpg = vec3d(tde4.getPGroupPosition3D(id_cpg,cam,frame))
            rot_pos_base = igl3d(rot_cpg,pos_cpg)

 

            rot_opg_global = mat3d(tde4.getPGroupRotation3D(id_opg,cam,frame))
            pos_opg_global = vec3d(tde4.getPGroupPosition3D(id_opg,cam,frame))
            scale = tde4.getPGroupScale3D(pg)

 

            rot_pos_opg_new = igl3d(rot_opg_global,pos_opg_global).invert() * rot_pos_base
            tde4.setPGroupRotation3D(id_opg,cam,frame,rot_pos_opg_new.m.list())
            tde4.setPGroupPosition3D(id_opg,cam,frame,rot_pos_opg_new.v.list())
            tde4.setPGroupScale3D(pg,scale)
        pf_mode  = tde4.getPGroupPostfilterMode(pg)
        tde4.setPGroupPostfilterMode(pg,"POSTFILTER_OFF")
        tde4.filterPGroup(pg,cam)
        tde4.setPGroupPostfilterMode(pg,pf_mode)
    #only change from public, returns to parked frame
    tde4.setCurrentFrame(cam,currentFrame)

 


def _mainCallback(req,widget,action):

 

    cam = tde4.getCurrentCamera()
    frames = tde4.getCameraNoFrames(cam)

 

    #getting camera pgroup...
    pg_list = tde4.getPGroupList()
    for cpg in pg_list:
        pg_type = tde4.getPGroupType(cpg)
        if pg_type == "CAMERA":
            break    

 

    #getting parent and child objPG...
    if widget == "parent_get_wdgt" or widget == "child_get_wdgt":
        if widget == "parent_get_wdgt":
            v = 1
        else:
            v = 0        
        current_pg = tde4.getCurrentPGroup()
        pg_type = tde4.getPGroupType(current_pg)    
        if pg_type == "OBJECT":
            if v == 1:
                calc_status = 0
                pl = tde4.getPointList(current_pg,0)
                if len(pl) > 0:
                    n = 0
                    for p in pl:
                        if tde4.getPointCalculated3DStatus(current_pg,p) == "CALCULATED":
                            calc_status = 1
                if calc_status == 1:
                    com = vec3d()
                    pl = tde4.getPointList(current_pg,0)
                    if len(pl) > 0:
                        n = 0
                        for p in pl:
                            if tde4.getPointCalculated3DStatus(current_pg,p) == "CALCULATED":
                                v = tde4.getPointCalcPosition3D(current_pg,p)
                                com = com + vec3d(v)
                                n = n +1
                        com = com / float(n)
                    #creating pivot locator...
                    model_list = tde4.get3DModelList(current_pg,0)
                    for model in model_list:
                        if tde4.get3DModelName(current_pg,model) == "screenZ_pivot_locator":
                            tde4.delete3DModel(current_pg,model)
                    m = tde4.create3DModel(current_pg,7)
                    tde4.set3DModelName(current_pg,m,"screenZ_pivot_locator")
                    vertex = 3.0
                    tde4.add3DModelVertex(current_pg,m,[0.0,0.0,0.0])
                    tde4.add3DModelVertex(current_pg,m,[vertex,0.0,0.0])
                    tde4.add3DModelVertex(current_pg,m,[-vertex,0.0,0.0])
                    tde4.add3DModelVertex(current_pg,m,[0.0,vertex,0.0])
                    tde4.add3DModelVertex(current_pg,m,[0.0,-vertex,0.0])
                    tde4.add3DModelVertex(current_pg,m,[0.0,0.0,vertex])
                    tde4.add3DModelVertex(current_pg,m,[0.0,0.0,-vertex])
                    for i in range(7):
                        tde4.add3DModelLine(current_pg,m,[0,i])
                    tde4.set3DModelSurveyFlag(current_pg,m,0)
                    tde4.set3DModelPosition3D(current_pg,m,com.list())
                    tde4.set3DModelColor(current_pg,m,1.0,0.0,0.0,1.0)
                    tde4.setWidgetValue(req,"parent_wdgt",str(tde4.getPGroupName(current_pg)))
                else:
                    tde4.postQuestionRequester(window_title,"Error, current objPG has no 3dpoints.","ok")
                    tde4.setWidgetValue(req,"parent_wdgt","")
            else:
                calc_status = 0
                pl = tde4.getPointList(current_pg,0)
                if len(pl) > 0:
                    n = 0
                    for p in pl:
                        if tde4.getPointCalculated3DStatus(current_pg,p) == "CALCULATED":
                            calc_status = 1
                if calc_status == 1:                
                    tde4.setWidgetValue(req,"child_wdgt",str(tde4.getPGroupName(current_pg)))
                else:
                    tde4.postQuestionRequester(window_title,"Error, current objPG has no 3dpoints.","ok")
                    tde4.setWidgetValue(req,"child_wdgt","")
        else:
            tde4.postQuestionRequester(window_title,"Error, please select objectPGroup.","ok")

 

 


    parent_v = tde4.getWidgetValue(req,"parent_wdgt")
    child_v = tde4.getWidgetValue(req,"child_wdgt")
    for pg in pg_list:
        pg_name = tde4.getPGroupName(pg)
        if pg_name == parent_v:
            parent_opg = pg
        if pg_name == child_v:
            child_opg = pg

 

    #delete pivot locator...
    if widget == "delete_pivot_locator_btn":
        pg_list = tde4.getPGroupList(0)
        for temp_pg in pg_list:
            model_list = tde4.get3DModelList(temp_pg,0)
            for model in model_list:
                if tde4.get3DModelName(temp_pg,model) == "screenZ_pivot_locator":
                    tde4.delete3DModel(temp_pg,model)

 

    #main...
    if widget == "main_button":
        if parent_v != None and child_v != None:
            Bake_Buffer_Curves()
            """com = vec3d()
            pl = tde4.getPointList(parent_opg,0)
            n = 0
            for p in pl:
                if tde4.getPointCalculated3DStatus(parent_opg,p) == "CALCULATED":
                    v = tde4.getPointCalcPosition3D(parent_opg,p)
                    com = com + vec3d(v)
                    n = n +1
            com = com / float(n)"""
            model_list = tde4.get3DModelList(parent_opg,0)
            for model in model_list:
                if tde4.get3DModelName(parent_opg,model) == "screenZ_pivot_locator":
                    com = vec3d(tde4.get3DModelPosition3D(parent_opg,model,cam,int(tde4.getCurrentFrame(cam))))

 

            #getting parent screen Z distance list...
            parent_distance_list = []
            for frame in range(1,frames+1):
                v0 = vec3d(tde4.getPGroupPosition3D(cpg,cam,frame))
                v = vec3d(tde4.getPGroupPosition3D(parent_opg,cam,frame))
                mtx = mat3d(tde4.getPGroupRotation3D(parent_opg,cam,frame))
                v = ((mtx*com)+v).list()
                d = (vec3d(v)-vec3d(v0)).norm2()
                parent_distance_list.append(d)

 

            #getting parent screen Z distance on current frame...
            frame = tde4.getCurrentFrame(cam)
            parent_distance_current_frame = parent_distance_list[frame-1]

 

            #getting child screen Z distance on current frame...
            com = vec3d()
            pl = tde4.getPointList(child_opg,0)
            n = 0
            for p in pl:
                if tde4.getPointCalculated3DStatus(child_opg,p) == "CALCULATED":
                    v = tde4.getPointCalcPosition3D(child_opg,p)
                    com = com + vec3d(v)
                    n = n +1
            com = com / float(n)
            v0 = vec3d(tde4.getPGroupPosition3D(cpg,cam,frame))
            v = vec3d(tde4.getPGroupPosition3D(child_opg,cam,frame))
            mtx = mat3d(tde4.getPGroupRotation3D(child_opg,cam,frame))
            v = ((mtx*com)+v).list()
            d = (vec3d(v)-vec3d(v0)).norm2()
            child_distance_current_frame = d

 

            #getting delta...
            delta = child_distance_current_frame - parent_distance_current_frame

 

            #subtract delta from parent distance list to get child opg new screen z value...
            null = 1
            for i in parent_distance_list:
                frame = null
                d = i + delta
                v0 = tde4.getPGroupPosition3D(cpg,cam,frame)
                v = tde4.getPGroupPosition3D(child_opg,cam,frame)
                mtx = tde4.getPGroupRotation3D(child_opg,cam,frame)
                vcom = (mat3d(mtx)*com)+vec3d(v)
                vd = (vec3d(v0)+((vcom-vec3d(v0)).unit()*d))-vcom
                mtx,v = tde4.convertObjectPGroupTransformationWorldTo3DE(cam,frame,mtx,(vec3d(v)+vd).list(),1.0,1)
                opg_scale = tde4.getPGroupScale3D(child_opg)
                pf_mode = tde4.getPGroupPostfilterMode(child_opg)
                tde4.setPGroupPosition3D(child_opg,cam,frame,v)
                tde4.setPGroupScale3D(child_opg,opg_scale)
                null = null + 1
            tde4.setPGroupPostfilterMode(child_opg,"POSTFILTER_OFF")
            tde4.filterPGroup(child_opg,cam)
            tde4.setPGroupPostfilterMode(child_opg,pf_mode)

 

        else:
            tde4.postQuestionRequester(window_title,"Error, please get parent and child objPGroups.","ok")

 

    if widget == "freeze":
        if child_v != None:
            Bake_Buffer_Curves()
            frame = tde4.getCurrentFrame(cam)
            com = vec3d()
            pl = tde4.getPointList(child_opg,0)
            n = 0
            for p in pl:
                if tde4.getPointCalculated3DStatus(child_opg,p) == "CALCULATED":
                    v = tde4.getPointCalcPosition3D(child_opg,p)
                    com = com + vec3d(v)
                    n = n +1
            com = com / float(n)
            v = vec3d(tde4.getPGroupPosition3D(child_opg,cam,frame))
            mtx = mat3d(tde4.getPGroupRotation3D(child_opg,cam,frame))
            v = ((mtx*com)+v).list()
            child_freeze_distance_list = []
            for frame in range(1,frames+1):
                v0 = tde4.getPGroupPosition3D(cpg,cam,frame)
                d = (vec3d(v)-vec3d(v0)).norm2()
                child_freeze_distance_list.append(d)
            for frame in range(1,frames+1):
                d = child_freeze_distance_list[frame-1]
                v0 = tde4.getPGroupPosition3D(cpg,cam,frame)
                v = tde4.getPGroupPosition3D(child_opg,cam,frame)
                mtx = tde4.getPGroupRotation3D(child_opg,cam,frame)
                vcom = (mat3d(mtx)*com)+vec3d(v)
                vd = (vec3d(v0)+((vcom-vec3d(v0)).unit()*d))-vcom
                mtx,v = tde4.convertObjectPGroupTransformationWorldTo3DE(cam,frame,mtx,(vec3d(v)+vd).list(),1.0,1)
                opg_scale = tde4.getPGroupScale3D(child_opg)
                pf_mode = tde4.getPGroupPostfilterMode(child_opg)
                tde4.setPGroupPosition3D(child_opg,cam,frame,v)
                tde4.setPGroupScale3D(child_opg,opg_scale)
            tde4.setPGroupPostfilterMode(child_opg,"POSTFILTER_OFF")
            tde4.filterPGroup(child_opg,cam)
            tde4.setPGroupPostfilterMode(child_opg,pf_mode)    

 

        else:
            tde4.postQuestionRequester(window_title,"Error, please get child objPGroup.","ok")

 

    #screen x,y,z translation nudge...
    power = tde4.getWidgetValue(req,"slider_wdgt")
    if widget == "screenx+" or widget == "screenx-" or widget == "screeny+" or widget == "screeny-" or widget == "screenz+" or widget == "screenz-":
        if widget == "screenx-" or widget == "screeny-" or widget == "screenz-": power = -float(power)
        if child_v != None:
            pl = tde4.getPointList(child_opg,0)
            calc_status = 0
            for p in pl:
                if tde4.getPointCalculated3DStatus(child_opg,p) == "CALCULATED":
                     calc_status = 1
            if calc_status == 1:
                Bake_Buffer_Curves()
                if widget == "screenx+" or widget == "screenx-" or widget == "screeny+" or widget == "screeny-":
                    for frame in range(1,frames+1):
                        cam_pos = vec3d(tde4.getPGroupPosition3D(cpg,cam,frame))
                        cam_rot = mat3d(tde4.getPGroupRotation3D(cpg,cam,frame))
                        obj_pos = vec3d(tde4.getPGroupPosition3D(child_opg,cam,frame))
                        obj_rot = mat3d(tde4.getPGroupRotation3D(child_opg,cam,frame))
                        cam_rot = mat3d(cam_rot).trans()
                        d = vec3d(obj_pos) - vec3d(cam_pos)
                        x_axis = vec3d(cam_rot[0]).unit()
                        y_axis = vec3d(cam_rot[1]).unit()
                        z_axis = vec3d(cam_rot[2]).unit()
                        if widget == "screenx+" or widget == "screenx-":
                            x_axis = x_axis * float(power)
                            x_axis = x_axis + cam_pos + d
                            local_values = tde4.convertObjectPGroupTransformationWorldTo3DE(cam,frame,obj_rot.list(),x_axis.list(),1.0,0)
                        if widget == "screeny+" or widget == "screeny-":
                            y_axis = y_axis * float(power)
                            y_axis = y_axis + cam_pos + d
                            local_values = tde4.convertObjectPGroupTransformationWorldTo3DE(cam,frame,obj_rot.list(),y_axis.list(),1.0,0)
                        opg_scale = tde4.getPGroupScale3D(child_opg)
                        pf_mode = tde4.getPGroupPostfilterMode(child_opg)
                        tde4.setPGroupPosition3D(child_opg,cam,frame,local_values[1])
                        tde4.setPGroupScale3D(child_opg,opg_scale)
                        tde4.setPGroupPostfilterMode(child_opg,"POSTFILTER_OFF")
                        tde4.filterPGroup(child_opg,cam)
                        tde4.setPGroupPostfilterMode(child_opg,pf_mode)
                if widget == "screenz+" or widget == "screenz-":
                    com = vec3d()
                    pl = tde4.getPointList(child_opg,0)
                    n = 0
                    for p in pl:
                        if tde4.getPointCalculated3DStatus(child_opg,p) == "CALCULATED":
                            v = tde4.getPointCalcPosition3D(child_opg,p)
                            com = com + vec3d(v)
                            n = n +1
                    com = com / float(n)
                    for frame in range(1,frames+1):
                        v0 = vec3d(tde4.getPGroupPosition3D(cpg,cam,frame))
                        v = vec3d(tde4.getPGroupPosition3D(child_opg,cam,frame))
                        mtx = mat3d(tde4.getPGroupRotation3D(child_opg,cam,frame))
                        com_global = ((mtx*com)+v).list()
                        cam_pos = vec3d(tde4.getPGroupPosition3D(cpg,cam,frame))
                        cam_rot = mat3d(tde4.getPGroupRotation3D(cpg,cam,frame))
                        obj_pos = vec3d(tde4.getPGroupPosition3D(child_opg,cam,frame))
                        obj_rot = mat3d(tde4.getPGroupRotation3D(child_opg,cam,frame))
                        p1 = cam_pos + ((vec3d(com_global) - cam_pos)*(1.0+float(power)))
                        p1 = p1 + (obj_pos - vec3d(com_global))
                        local_values = tde4.convertObjectPGroupTransformationWorldTo3DE(cam,frame,obj_rot.list(),p1.list(),1.0,1)
                        opg_scale = tde4.getPGroupScale3D(child_opg)
                        pf_mode = tde4.getPGroupPostfilterMode(child_opg)
                        tde4.setPGroupPosition3D(child_opg,cam,frame,local_values[1])
                        tde4.setPGroupScale3D(child_opg,opg_scale)
                        tde4.setPGroupPostfilterMode(child_opg,"POSTFILTER_OFF")
                        tde4.filterPGroup(child_opg,cam)
                        tde4.setPGroupPostfilterMode(child_opg,pf_mode)
            else:
                tde4.postQuestionRequester(window_title,"Error, child objPG has no 3dpoints.","ok")
        else:
            tde4.postQuestionRequester(window_title,"Error, please get child objPGroup.","ok")

 


window_title = "Patcha ObjectPG Screen Z Constraint v1.2"

 

 

req = tde4.createCustomRequester()

 


#parent objpg text fiels widget...
tde4.addTextFieldWidget(req,"parent_wdgt","Parent objPG")
tde4.setWidgetAttachModes(req,"parent_wdgt","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"parent_wdgt",23,83,10,0)
tde4.setWidgetSensitiveFlag(req,"parent_wdgt",0)

 

#parent get button...
tde4.addButtonWidget(req,"parent_get_wdgt","Get",70,10)
tde4.setWidgetAttachModes(req,"parent_get_wdgt","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"parent_get_wdgt",86,98,10,0)

 

#child objpg text fiels widget...
tde4.addTextFieldWidget(req,"child_wdgt","Child objPG")
tde4.setWidgetAttachModes(req,"child_wdgt","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"child_wdgt",23,83,40,0)
tde4.setWidgetSensitiveFlag(req,"child_wdgt",0)

 

#child get button...
tde4.addButtonWidget(req,"child_get_wdgt","Get",70,10)
tde4.setWidgetAttachModes(req,"child_get_wdgt","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"child_get_wdgt",86,98,40,0)

 

#main button widget...
tde4.addButtonWidget(req,"main_button","Make Screen Z Constraint",70,10)
tde4.setWidgetAttachModes(req,"main_button","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"main_button",3,40,70,0)

 

#freeze child screenZ button widget...
tde4.addButtonWidget(req,"freeze","Freeze Child Screen Z",70,10)
tde4.setWidgetAttachModes(req,"freeze","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"freeze",43,73,70,0)

 


#delete pivot locator button widget...
tde4.addButtonWidget(req,"delete_pivot_locator_btn","Delete Locator",70,10)
tde4.setWidgetAttachModes(req,"delete_pivot_locator_btn","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"delete_pivot_locator_btn",76,97,70,0)

 

#slider widget...
tde4.addScaleWidget(req,"slider_wdgt","Screen Nudge","DOUBLE",0.001,0.1,0.05)
tde4.setWidgetAttachModes(req,"slider_wdgt","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"slider_wdgt",24,98,100,0)

 

#screen X+ button widget...
tde4.addButtonWidget(req,"screenx+","Child Screen X +",70,10)
tde4.setWidgetAttachModes(req,"screenx+","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"screenx+",3,30,130,0)

 

#screen X- button widget...
tde4.addButtonWidget(req,"screenx-","Child Screen X -",70,10)
tde4.setWidgetAttachModes(req,"screenx-","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"screenx-",3,30,160,0)

 

#screen Y+ button widget...
tde4.addButtonWidget(req,"screeny+","Child Screen Y +",70,10)
tde4.setWidgetAttachModes(req,"screeny+","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
tde4.setWidgetOffsets(req,"screeny+",35,63,130,0)

 

... #screen Y- button widget...
... tde4.addButtonWidget(req,"screeny-","Child Screen Y -",70,10)
... tde4.setWidgetAttachModes(req,"screeny-","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
... tde4.setWidgetOffsets(req,"screeny-",35,63,160,0)
... 
...  
... 
... #screen Z+ button widget...
... tde4.addButtonWidget(req,"screenz+","Child Screen Z +",70,10)
... tde4.setWidgetAttachModes(req,"screenz+","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
... tde4.setWidgetOffsets(req,"screenz+",68,96,130,0)
... 
...  
... 
... #screen Z- button widget...
... tde4.addButtonWidget(req,"screenz-","Child Screen Z -",70,10)
... tde4.setWidgetAttachModes(req,"screenz-","ATTACH_POSITION","ATTACH_POSITION","ATTACH_WINDOW","ATTACH_AS_IS")
... tde4.setWidgetOffsets(req,"screenz-",68,96,160,0)
... 
...  
... 
... #Callbacks...
... tde4.setWidgetCallbackFunction(req,"parent_get_wdgt","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"child_get_wdgt","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"main_button","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"freeze","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"screenx+","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"screenx-","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"screeny+","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"screeny-","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"screenz+","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"screenz-","_mainCallback")
... tde4.setWidgetCallbackFunction(req,"delete_pivot_locator_btn","_mainCallback")
... 
...  
... 
