"""
blender_loader.py - Utilities for loading Blender objects and animations with MTL support
"""
import os
import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *

class BlenderModel:
    """Class for loading and rendering Blender 3D models (OBJ format)"""
    
    def __init__(self, obj_file_path=None):
        """
        Initialize a BlenderModel
        
        Args:
            obj_file_path (str, optional): Path to OBJ file
        """
        self.vertices = []
        self.vertex_normals = []
        self.faces = []
        self.textures = []
        self.materials = {}
        
        if obj_file_path and os.path.exists(obj_file_path):
            self.load_obj(obj_file_path)
    
    def load_obj(self, file_path):
        """
        Load a Wavefront OBJ file
        
        Args:
            file_path (str): Path to OBJ file
            
        Returns:
            bool: Success or failure
        """
        try:
            vertices = []
            normals = []
            texcoords = []
            faces = []
            mtl_file = None
            current_material = None
            materials = {}
            
            with open(file_path, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue  # Skip comments
                    
                    values = line.split()
                    if not values:
                        continue
                    
                    if values[0] == 'v':
                        # Vertex position
                        vertices.append([float(x) for x in values[1:4]])
                    elif values[0] == 'vn':
                        # Vertex normal
                        normals.append([float(x) for x in values[1:4]])
                    elif values[0] == 'vt':
                        # Texture coordinate
                        texcoords.append([float(x) for x in values[1:3]])
                    elif values[0] == 'f':
                        # Face
                        face = []
                        for v in values[1:]:
                            w = v.split('/')
                            # OBJ indexing starts at 1, so subtract 1
                            face.append(int(w[0]) - 1)
                        faces.append((face, current_material))
                    elif values[0] == 'mtllib':
                        # MTL file reference
                        mtl_file = os.path.join(os.path.dirname(file_path), values[1])
                    elif values[0] == 'usemtl':
                        # Set current material
                        current_material = values[1]
            
            # Load materials if MTL file exists
            if mtl_file and os.path.exists(mtl_file):
                self.load_mtl(mtl_file, materials)
                print(f"Loaded material file: {mtl_file}")
            
            self.vertices = vertices
            self.vertex_normals = normals
            self.faces = faces
            self.materials = materials
            
            print(f"Loaded OBJ file: {file_path} ({len(vertices)} vertices, {len(faces)} faces)")
            return True
            
        except Exception as e:
            print(f"Error loading OBJ file {file_path}: {e}")
            return False
    
    def load_mtl(self, mtl_file, materials):
        """
        Load MTL material file
        
        Args:
            mtl_file (str): Path to MTL file
            materials (dict): Dictionary to store material properties
        """
        try:
            current_material = None
            
            with open(mtl_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue  # Skip comments
                    
                    values = line.split()
                    if not values:
                        continue
                    
                    if values[0] == 'newmtl':
                        # New material
                        current_material = values[1]
                        materials[current_material] = {
                            'ambient': [0.2, 0.2, 0.2],
                            'diffuse': [0.8, 0.8, 0.8],
                            'specular': [1.0, 1.0, 1.0],
                            'shininess': 0.0,
                            'opacity': 1.0
                        }
                    elif current_material is not None:
                        if values[0] == 'Ka':
                            # Ambient color
                            materials[current_material]['ambient'] = [float(x) for x in values[1:4]]
                        elif values[0] == 'Kd':
                            # Diffuse color
                            materials[current_material]['diffuse'] = [float(x) for x in values[1:4]]
                        elif values[0] == 'Ks':
                            # Specular color
                            materials[current_material]['specular'] = [float(x) for x in values[1:4]]
                        elif values[0] == 'Ns':
                            # Shininess
                            materials[current_material]['shininess'] = float(values[1])
                        elif values[0] == 'd' or values[0] == 'Tr':
                            # Opacity/transparency
                            materials[current_material]['opacity'] = float(values[1])
            
            print(f"Loaded {len(materials)} materials from {mtl_file}")
            return True
            
        except Exception as e:
            print(f"Error loading MTL file {mtl_file}: {e}")
            return False
    
    def create_display_list(self):
        """
        Create an OpenGL display list for faster rendering
        
        Returns:
            int: Display list ID
        """
        display_list = glGenLists(1)
        glNewList(display_list, GL_COMPILE)
        
        # Render the model
        glBegin(GL_TRIANGLES)
        for face, material_name in self.faces:
            # Apply material if available
            if hasattr(self, 'materials') and material_name in self.materials:
                material = self.materials[material_name]
                # Apply diffuse color
                glColor3f(
                    material['diffuse'][0],
                    material['diffuse'][1],
                    material['diffuse'][2]
                )
            
            if len(face) >= 3:  # Make sure it's at least a triangle
                # Convert polygons to triangles
                for i in range(1, len(face) - 1):
                    # Define a triangle from vertices 0, i, i+1
                    for idx in [0, i, i+1]:
                        vertex_idx = face[idx]
                        if vertex_idx < len(self.vertices):
                            glVertex3fv(self.vertices[vertex_idx])
        glEnd()
        
        glEndList()
        return display_list
    
    def render(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=1.0, color=(1.0, 1.0, 1.0)):
        """
        Render the model
        
        Args:
            position (tuple): (x, y, z) position
            rotation (tuple): (x, y, z) rotation in degrees
            scale (float): Scale factor
            color (tuple): (r, g, b) color
        """
        glPushMatrix()
        
        # Apply transformations
        glTranslatef(position[0], position[1], position[2])
        glRotatef(rotation[0], 1, 0, 0)
        glRotatef(rotation[1], 0, 1, 0)
        glRotatef(rotation[2], 0, 0, 1)
        glScalef(scale, scale, scale)
        
        # Draw each face with its material
        glBegin(GL_TRIANGLES)
        for face_info in self.faces:
            if isinstance(face_info, tuple) and len(face_info) == 2:
                face, material_name = face_info
            else:
                # Handle older format where faces were stored directly
                face = face_info
                material_name = None
            
            # Apply material if available
            if hasattr(self, 'materials') and material_name in self.materials:
                material = self.materials[material_name]
                # Apply diffuse color
                glColor3f(
                    material['diffuse'][0] * color[0],
                    material['diffuse'][1] * color[1],
                    material['diffuse'][2] * color[2]
                )
            else:
                # Use default color
                glColor3f(color[0], color[1], color[2])
            
            if len(face) >= 3:  # Make sure it's at least a triangle
                # Convert polygons to triangles
                for i in range(1, len(face) - 1):
                    # Define a triangle from vertices 0, i, i+1
                    for idx in [0, i, i+1]:
                        vertex_idx = face[idx]
                        if vertex_idx < len(self.vertices):
                            glVertex3fv(self.vertices[vertex_idx])
        glEnd()
        
        # Draw wireframe outline
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_TRIANGLES)
        for face_info in self.faces:
            if isinstance(face_info, tuple) and len(face_info) == 2:
                face, _ = face_info
            else:
                # Handle older format where faces were stored directly
                face = face_info
            
            if len(face) >= 3:
                for i in range(1, len(face) - 1):
                    for idx in [0, i, i+1]:
                        vertex_idx = face[idx]
                        if vertex_idx < len(self.vertices):
                            glVertex3fv(self.vertices[vertex_idx])
        glEnd()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        glPopMatrix()

    def render_with_lighting(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=1.0, color=(1.0, 1.0, 1.0)):
        """
        Render the model with lighting for glossy appearance
        
        Args:
            position (tuple): (x, y, z) position
            rotation (tuple): (x, y, z) rotation in degrees
            scale (float): Scale factor
            color (tuple): (r, g, b) color
        """
        try:
            # Save state
            glPushMatrix()
            
            # Force color material to be enabled
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
            
            # Apply transformations
            glTranslatef(position[0], position[1], position[2])
            glRotatef(rotation[0], 1, 0, 0)
            glRotatef(rotation[1], 0, 1, 0)
            glRotatef(rotation[2], 0, 0, 1)
            glScalef(scale, scale, scale)
            
            # Ensure color is valid
            color = (
                max(0.0, min(1.0, color[0])),
                max(0.0, min(1.0, color[1])),
                max(0.0, min(1.0, color[2]))
            )
            
            # Skip rendering if model has no data
            if not self.faces or not self.vertices:
                glPopMatrix()
                return
            
            # Draw each face with the applied color
            for face_info in self.faces:
                # Extract face and material
                if isinstance(face_info, tuple) and len(face_info) == 2:
                    face, material_name = face_info
                else:
                    # Handle older format where faces were stored directly
                    face = face_info
                    material_name = None
                
                # Skip invalid faces
                if not isinstance(face, list) or len(face) < 3:
                    continue
                
                # If we have material information, use it to modify our color
                if hasattr(self, 'materials') and material_name in self.materials:
                    material = self.materials[material_name]
                    # Just use the specular from the material, clamp shininess to valid range
                    specular = material.get('specular', [1.0, 1.0, 1.0])
                    shininess = material.get('shininess', 50.0)
                    
                    # Limit shininess to valid range (0-128)
                    shininess = max(0.0, min(128.0, shininess))
                    
                    try:
                        # Apply material properties
                        glMaterialfv(GL_FRONT, GL_SPECULAR, specular + [1.0])
                        glMaterialf(GL_FRONT, GL_SHININESS, shininess)
                    except Exception as e:
                        print(f"Material property error (non-fatal): {e}")
                        # Default material properties as fallback
                        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
                        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
                else:
                    # Default material properties
                    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
                    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
                
                # This is the key change - explicitly set the color for each face
                # This ensures our color is applied regardless of material settings
                glColor3f(color[0], color[1], color[2])
                
                # Draw the face as a triangle fan with the color applied
                glBegin(GL_TRIANGLE_FAN)
                for idx in face:
                    if isinstance(idx, int) and 0 <= idx < len(self.vertices):
                        # Set normal if available
                        if hasattr(self, 'vertex_normals') and len(self.vertex_normals) > idx:
                            try:
                                normal = self.vertex_normals[idx]
                                if len(normal) >= 3:
                                    glNormal3fv(normal)
                            except Exception:
                                # If there's an error with normals, use generic normal
                                glNormal3f(0.0, 1.0, 0.0)
                        else:
                            # Default normal pointing up
                            glNormal3f(0.0, 1.0, 0.0)
                        
                        # Set vertex
                        vertex = self.vertices[idx]
                        if len(vertex) >= 3:
                            glVertex3fv(vertex)
                glEnd()
            
            # Restore state
            glPopMatrix()
            
        except Exception as e:
            print(f"Error in render_with_lighting: {e}")
            # Restore state if there was an error
            try:
                glPopMatrix()
            except:
                pass  # Matrix wasn't pushed, or already popped

class AnimationLoader:
    """Class for loading Blender animation frames"""
    
    def __init__(self, frames_dir=None, frame_prefix="frame_", frame_extension=".png"):
        """
        Initialize an AnimationLoader
        
        Args:
            frames_dir (str, optional): Directory containing animation frames
            frame_prefix (str): Prefix for frame filenames
            frame_extension (str): Extension for frame files
        """
        self.frames = []
        self.current_frame = 0
        
        if frames_dir and os.path.exists(frames_dir):
            self.load_frames(frames_dir, frame_prefix, frame_extension)
    
    def load_frames(self, frames_dir, frame_prefix="frame_", frame_extension=".png"):
        """
        Load animation frames from a directory
        
        Args:
            frames_dir (str): Directory containing animation frames
            frame_prefix (str): Prefix for frame filenames
            frame_extension (str): Extension for frame files
            
        Returns:
            int: Number of frames loaded
        """
        self.frames = []
        
        try:
            # Get all files in the directory that match the pattern
            files = [f for f in os.listdir(frames_dir) 
                    if f.startswith(frame_prefix) and f.endswith(frame_extension)]
            
            # Sort files by frame number
            files.sort(key=lambda f: int(''.join(filter(str.isdigit, f.replace(frame_prefix, "").replace(frame_extension, "")))))
            
            # Load each frame
            for filename in files:
                file_path = os.path.join(frames_dir, filename)
                try:
                    surface = pygame.image.load(file_path)
                    self.frames.append(surface)
                except Exception as e:
                    print(f"Error loading frame {file_path}: {e}")
            
            print(f"Loaded {len(self.frames)} animation frames from {frames_dir}")
            return len(self.frames)
            
        except Exception as e:
            print(f"Error loading animation frames from {frames_dir}: {e}")
            return 0
    
    def get_frame(self, frame_index):
        """
        Get a specific frame
        
        Args:
            frame_index (int): Index of the frame
            
        Returns:
            pygame.Surface: The frame surface or None if invalid index
        """
        if 0 <= frame_index < len(self.frames):
            return self.frames[frame_index]
        return None
    
    def get_current_frame(self):
        """
        Get the current frame
        
        Returns:
            pygame.Surface: The current frame surface
        """
        return self.get_frame(self.current_frame)
    
    def advance(self, amount=1):
        """
        Advance the animation by the specified number of frames
        
        Args:
            amount (int): Number of frames to advance (can be negative)
            
        Returns:
            int: New current frame index
        """
        if self.frames:
            self.current_frame = (self.current_frame + amount) % len(self.frames)
        return self.current_frame
    
    def set_frame(self, frame_index):
        """
        Set the current frame
        
        Args:
            frame_index (int): Index of the frame to set as current
            
        Returns:
            bool: Success or failure
        """
        if 0 <= frame_index < len(self.frames):
            self.current_frame = frame_index
            return True
        return False

def create_default_cube():
    """
    Create a default cube model when no OBJ file is available
    
    Returns:
        BlenderModel: A model with cube vertices and faces
    """
    model = BlenderModel()
    
    # Define cube vertices
    model.vertices = [
        [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
        [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
    ]
    
    # Define cube faces (as quads, will be converted to triangles during rendering)
    model.faces = [
        ([0, 1, 3, 2], None),  # Right face
        ([4, 6, 7, 5], None),  # Left face
        ([0, 4, 5, 1], None),  # Top face
        ([2, 3, 7, 6], None),  # Bottom face
        ([0, 2, 6, 4], None),  # Front face
        ([1, 5, 7, 3], None)   # Back face
    ]
    
    return model

def create_default_sphere(radius=1.0, segments=12):
    """
    Create a default sphere model when no OBJ file is available
    
    Args:
        radius (float): Sphere radius
        segments (int): Number of segments (higher = smoother)
        
    Returns:
        BlenderModel: A model with sphere vertices and faces
    """
    model = BlenderModel()
    vertices = []
    faces = []
    
    # Create vertices
    for i in range(segments + 1):
        phi = math.pi * i / segments
        for j in range(segments * 2):
            theta = 2.0 * math.pi * j / (segments * 2)
            
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            
            vertices.append([x, y, z])
    
    # Create faces
    for i in range(segments):
        for j in range(segments * 2):
            next_j = (j + 1) % (segments * 2)
            
            # Current row, current column
            p1 = i * (segments * 2) + j
            # Current row, next column
            p2 = i * (segments * 2) + next_j
            # Next row, next column
            p3 = (i + 1) * (segments * 2) + next_j
            # Next row, current column
            p4 = (i + 1) * (segments * 2) + j
            
            # Add two triangular faces (a quad split into two triangles)
            if i > 0:
                faces.append(([p1, p2, p3], None))
            if i < segments - 1:
                faces.append(([p1, p3, p4], None))
    
    model.vertices = vertices
    model.faces = faces
    
    return model

