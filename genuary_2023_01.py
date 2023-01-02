import bpy
import math
import mathutils


def smoothstep(x):
    if x < 0:
        return 0
    if x > 1:
        return 1
    return x * x * (3 - 2 * x)


def clear_grid():
    cubes = bpy.data.collections["Cubes"].objects
    for cube in cubes:
        if not cube.type == "MESH":
            continue
        mesh = cube.data
        
        bpy.data.objects.remove(cube)
    
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def make_grid():
    for x in range(-1, +2):
        for y in range(-1, +2):
            for z in range(-1, +2):
                bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(x, y, z), scale=(1, 1, 1))
                cube = bpy.context.active_object
                bpy.ops.collection.objects_remove_all()
                bpy.data.collections["Cubes"].objects.link(cube)

MAX_FRAME = 241
AMOUNT_SCALE = 2.18


def frame_arg(frame):
    return 2 * math.pi * (frame - 1) / (MAX_FRAME - 1)


def get_amount(frame):
    t = (frame - 1) / (MAX_FRAME - 1)
    curve = (25 * math.sqrt(5) / 16) * math.sqrt(t) * (1 - t) * (1 - t)
    scaled = AMOUNT_SCALE * curve
    
    return scaled


frames_and_amounts = [ (frame, get_amount(frame)) for frame in range(1, MAX_FRAME + 1, 5) ]
     
                
def move_cubes():
    cubes = bpy.data.collections["Cubes"].objects
    
    for (idx, cube) in enumerate(cubes):
        
        og_location = cube.location.copy()
        modifier = 0.85 + 0.3 * mathutils.noise.random()
        
        for (frame, amount) in frames_and_amounts:
            
            global_rotation_angle = (math.pi / 2) * smoothstep((frame - 1) / (MAX_FRAME - 1))
            og_rotated = og_location.copy()
            og_rotated.rotate(mathutils.Euler((0, 0, global_rotation_angle)))
            
            new_location_clean = og_rotated * (1 + amount * modifier * og_location.magnitude)
            
            arg = frame_arg(frame)
            noise_arg = 1.16 * mathutils.Vector((math.sin(arg), math.cos(arg), idx))
            noise = 1.28 * mathutils.noise.noise_vector(noise_arg)
            
            new_location = new_location_clean + amount * modifier * noise
            
            cube.location = new_location
            cube.keyframe_insert(data_path="location", frame=frame)
            
            base_rotation = arg / 2
            rotation_arg = 0.72 * mathutils.Vector((math.cos(arg), math.sin(arg), idx + math.pi))
            rotation_noise = 1.16 * mathutils.noise.noise_vector(rotation_arg)
            rotation_x = 0.19720 * amount * modifier * rotation_noise.x
            rotation_y = 0.24942 * amount * modifier * rotation_noise.y
            rotation_z = base_rotation + amount * modifier * rotation_noise.z
            
            cube.rotation_euler = [ rotation_x, rotation_y, rotation_z ]
            cube.keyframe_insert(data_path="rotation_euler", frame=frame)
        

clear_grid()
make_grid()
move_cubes()