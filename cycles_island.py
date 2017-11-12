import bpy
import bmesh
import random

from time import time

import sys
import os
import imp

directory = os.path.dirname(bpy.data.filepath)
if not directory in sys.path:
    sys.path.append(directory)

import planemaker
imp.reload(planemaker)


# Parameter stuff.
reset_old_stuff = True

UNIQUE_ID = "34587873456"
ISLAND_NAME = "Island" + UNIQUE_ID
tree_name = "Tree" + UNIQUE_ID
top_name = "Top" + UNIQUE_ID
SUN_NAME = "Sun" + UNIQUE_ID
SEA_NAME = "Sea" + UNIQUE_ID


# Utility stuff.

def select_only(thing):
    # Deselect everything and select only the named object.
    get_me_mode('OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    try:
        bpy.data.objects[thing].select = True
    except:
        pass

def activate_object(object):
    # Deselect everything and select only the named object.
    get_me_mode('OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    try:
        bpy.context.scene.objects.active = object
    except:
        pass

def get_me_mode(new_mode):
    try:
        bpy.ops.object.mode_set(mode=new_mode)

    except:
        pass


# Linear stuff.

def generate_scene():
    create_sun(SUN_NAME)
    create_sea()
    
    set_up_camera()
    
    island_plane = create_island(ISLAND_NAME)
    lots_of_trees(island_plane)

def lots_of_trees(island):
    more = True

    while more:
        generate_tree(island)

        if random.random() > 0.5:
            more = False

def set_up_camera():
    # CAMERA STUFF
    get_me_mode('OBJECT')
    bpy.ops.object.empty_add()
    target = bpy.context.active_object
    #                       Y between -3.0 and 3.0         Z between 1.0 and 2.0
    target.location = (0.0, (random.random() - 0.5) * 6.0, 0.5 + random.random() * 2.0)

    create_camera(target)

def generate_tree(island):
    # Make a tree.
    activate_object(island)
    get_me_mode('EDIT')
    bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
    treetop_position, treetop_size = place_tree(bm)
    make_tree_top(treetop_position, treetop_size)

def delete_old_stuff():
    get_me_mode('OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
def t():
    # Grab the "front" of the plane and pull it down with connected falloff.
    bpy.ops.transform.translate(value=(0.0, 0.0, -1.5) , proportional='CONNECTED', proportional_edit_falloff='SMOOTH', proportional_size=2.0)

def r():
    get_me_mode('OBJECT')
    bpy.ops.transform.rotate(
        value=(random.random() * 6.2),
        axis=(0, 0, 1),
        constraint_axis=(False, False, True),
        constraint_orientation='GLOBAL'
        )

def select_outer_loop(bm):
    for vertex in bm.verts:
        if (len(vertex.link_edges) < 4) and vertex.co.z > 0.0:
            vertex.select = True
            vertex.co.z = 0.0

def delete_faces_under(bm, under=0.0):
    get_me_mode('EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    for face in bm.faces:
        is_under = True
        for vertex in face.verts:
            if vertex.co.z > under:
                is_under = False
        if is_under:
            face.select = True

    bpy.ops.mesh.delete(type='FACE')


# Generate stuff.

def create_camera(target):
    get_me_mode('OBJECT')
    bpy.ops.object.camera_add(location=(13.0, 0.0, 0.2))
    camera = bpy.context.active_object
    
    # Set the new camera as the active rendering camera.
    bpy.context.scene.camera = camera
    
    track = camera.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

def random_spike(island_plane, num_spikes):
    for i in range(num_spikes):
        get_me_mode('EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        
        get_me_mode('OBJECT')
        random.choice(island_plane.data.vertices).select = True
        
        get_me_mode('EDIT')
        bpy.ops.transform.translate(value=(0.0, 0.0, (random.random() * 1.9)) , proportional='CONNECTED', proportional_edit_falloff='SMOOTH', proportional_size=(random.random() * 1) + 0.7)

def create_sea():
    get_me_mode('OBJECT')
    bpy.ops.mesh.primitive_plane_add(radius=200.0, location=(0.0, 0.0, 0.15), enter_editmode=False)
    #bpy.ops.transform.resize(value=(2.0, 2.0, 2.0))
    
    # Apply island material.
    sea = bpy.context.active_object
    sea.data.materials.append(bpy.data.materials.get('Blue'))

def create_island(name):
    get_me_mode('OBJECT')
    
    plane = planemaker.generate_plane(name, True)
    select_only(name)
    plane.location.z
    
    get_me_mode('EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(0.2, 0.2, 0.2))
    
    select_only(name)
    
    random_spike(plane, 8)
    
    # Select edge loop.
    get_me_mode('EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    select_outer_loop(bm)
    
    # Pull down edge of island plane.
    t()
    
    # Rotate island object.
    r()
    
    # Smooth
    get_me_mode('EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.vertices_smooth(factor=0.9)
    bpy.ops.mesh.vertices_smooth(factor=0.9)
    
    # Clean up unneded vertices.
    get_me_mode('EDIT')
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    delete_faces_under(bm)
    
    # Move the island to a spot.
    plane.location = ((random.random() * 5.0) - 1.0, 0.0, 0.0)
    
    # Apply island material.
    plane.data.materials.append(bpy.data.materials.get('Sand'))
    
    return plane

def place_tree(bm):
    bm.verts.ensure_lookup_table()
    
    verts_above_ground = [vertex for vertex in bm.verts if vertex.co.z > 0.1]
    
    if len(verts_above_ground) < 1:
        vert = bm.verts.new((random.random(), random.random(), 0.0))
        coordinates = vert.co
    else:
        coordinates = random.choice(verts_above_ground).co
    
    get_me_mode('OBJECT')
    world_coordinates = (bpy.context.active_object.matrix_world * coordinates)
    
    trunk_thickness = (random.random() * 0.04) + 0.03
    
    bpy.ops.mesh.primitive_plane_add(radius=trunk_thickness, location=world_coordinates, enter_editmode=True)
    bpy.context.active_object.name = tree_name
    bpy.ops.transform.translate(value=(0.0, 0.0, -0.2))
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, (random.random() * 0.7) + 0.7)})
    
    ob = bpy.context.active_object
    ob.update_from_editmode()
    
    bpy.context.active_object.data.materials.append(bpy.data.materials.get('Brown'))
    
    top_of_tree = ob.matrix_world * [v.co for v in ob.data.vertices if v.select][0]
    
    get_me_mode('EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(fractal=0.67)
    
    get_me_mode('OBJECT')
    bpy.ops.object.modifier_add(type='DECIMATE')
    bpy.context.object.modifiers["Decimate"].decimate_type = 'UNSUBDIV'
    bpy.context.object.modifiers["Decimate"].iterations = 1
    bpy.ops.object.modifier_apply(modifier="Decimate")
    
    return top_of_tree, trunk_thickness

def make_tree_top(position=(0.0, 0.0, 0.0), top_size=0.0):
    position[1] += 0.05
    get_me_mode('OBJECT')
    bpy.ops.mesh.primitive_ico_sphere_add(size=0.3 * (1 + (top_size * 3)), subdivisions=1, enter_editmode=True, location=(position))
    bpy.ops.transform.rotate(value=(random.random() * 6.4))
    bpy.context.active_object.name = top_name
    bpy.ops.mesh.subdivide(fractal=9.56, fractal_along_normal=0.15)
    bpy.ops.mesh.vertices_smooth(factor=0.9)
    bpy.ops.obj
    bpy.context.active_object.data.materials.append(bpy.data.materials.get('Green'))

def create_sun(sun_name):
    get_me_mode('OBJECT')
    bpy.ops.object.lamp_add(type='SUN', location=(3.0, 7.0, 2.0))
    sun = bpy.context.active_object
    sun.name = sun_name
    sun.rotation_euler = (random.random() * 1.4, 0.0, random.random() * 6.3)    


# Do stuff.
if reset_old_stuff:
    delete_old_stuff()

generate_scene()

get_me_mode('OBJECT')

# RENDERING PARAMETERS
def set_scene_options():
    # Make the sky point at the sun.
    bpy.data.worlds['World'].node_tree.nodes['Sky Texture'].sun_direction = bpy.data.objects['Sun34587873456'].rotation_euler
    
    # Random amount of haziness.
    bpy.data.worlds['World'].node_tree.nodes['Sky Texture'].turbidity = (random.random() * 9.0) + 1.0
    
    # Random reflected ground color.
    bpy.data.worlds['World'].node_tree.nodes['Sky Texture'].ground_albedo = random.random()
    
def set_render_options():
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.sampling_pattern = 'SOBOL'
    bpy.context.scene.cycles.film_exposure = 1.9
    bpy.context.scene.cycles.samples = 4
    bpy.context.scene.render.threads_mode = 'FIXED'
    bpy.context.scene.render.threads = 1
    bpy.context.scene.render.filepath = '//../automation/cycles/' + str(time()) + ".png"
    bpy.context.scene.render.use_overwrite = False
    
# RENDER
set_scene_options()
set_render_options()
#bpy.ops.render.render()
