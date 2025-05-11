"""
main_menu.py - Main menu with flying Blender objects - Fixed implementation
"""
import os
import random
import math
import pygame
import json
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from utils.blender_loader import BlenderModel, create_default_cube, create_default_sphere
from utils.decay_bar import DecayBar
from utils.color_utils import load_jetbrains_mono_font

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Load the decay grids JSON
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go to the project root
json_path = os.path.join(current_dir, 'assets', 'decay_grids.json')
try:
    with open(json_path, 'r') as f:
        DECAY_GRIDS = json.load(f)
except Exception as e:
    print(f"Error loading decay_grids.json: {e}")
    DECAY_GRIDS = None

class BlenderObject:
    """Represents a 3D object loaded from Blender"""
    
    def __init__(self, obj_file, initial_position, initial_rotation, scale=1.0, row_index=None, preloaded_model=None):
        """
        Initialize a Blender object
        
        Args:
            obj_file (str): Path to the .obj file
            initial_position (tuple): (x, y, z) initial position
            initial_rotation (tuple): (x, y, z) initial rotation in degrees
            scale (float): Scaling factor
            row_index (int, optional): The row index for color selection
            preloaded_model (BlenderModel, optional): Preloaded model to use instead of loading from file
        """
        self.model = preloaded_model  # Use preloaded model if provided
        
        # Store label data
        self.label_id = random.randint(100, 999)
        self.label_offset = [0, 0]  # Will be used to position label
        
        # Extract the row index from filename if provided
        self.row_index = row_index
        if row_index is None and "row" in obj_file.lower():
            try:
                # Try to extract row number from filename (e.g., row1.obj -> 1)
                filename = os.path.basename(obj_file)
                if filename.startswith("row") and ".obj" in filename:
                    row_num = int(filename[3:filename.find(".")])
                    if 1 <= row_num <= 7:
                        self.row_index = row_num - 1  # Convert to 0-based index
            except:
                pass
        
        # Assign a random column from the grid
        self.grid_col = random.randint(0, 12)  # 0-12 for 13 columns
        
        # Try to load the model from file if not preloaded
        if self.model is None:
            if os.path.exists(obj_file):
                self.model = BlenderModel(obj_file)
                self.object_name = os.path.basename(obj_file)
            else:
                # Create default shapes if file doesn't exist
                if "cube" in obj_file.lower():
                    self.model = create_default_cube()
                    self.object_name = "Default Cube"
                elif "sphere" in obj_file.lower():
                    self.model = create_default_sphere()
                    self.object_name = "Default Sphere"
                else:
                    self.model = create_default_cube()
                    self.object_name = "Default Object"
        else:
            # If we have a preloaded model, just use its name
            self.object_name = os.path.basename(obj_file)
            
        self.position = list(initial_position)
        self.rotation = list(initial_rotation)
        self.scale = scale
        
        # Movement parameters - always move from right to left
        self.velocity = [-random.uniform(0.1, 0.2), 0, 0]  # Only horizontal movement
        self.rotation_speed = [random.uniform(-1, 1) for _ in range(3)]
        
        # Base color assignment from decay grids
        if self.row_index is not None and DECAY_GRIDS is not None:
            # Get a color from decay grids
            try:
                # Use stage 1 (initial state) colors by default
                stage_colors = DECAY_GRIDS["stages"][0]["grid"]
                if self.row_index < len(stage_colors):
                    # Use the stored grid column 
                    col_index = self.grid_col
                    hex_color = stage_colors[self.row_index][col_index]
                    
                    # Convert hex to RGB
                    r = int(hex_color[1:3], 16) / 255.0
                    g = int(hex_color[3:5], 16) / 255.0
                    b = int(hex_color[5:7], 16) / 255.0
                    
                    # Make colors more saturated to stand out better with lighting
                    # This uses a simple enhancement algorithm
                    avg = (r + g + b) / 3
                    r = min(1.0, r + (r - avg) * 0.5)
                    g = min(1.0, g + (g - avg) * 0.5)
                    b = min(1.0, b + (b - avg) * 0.5)
                    
                    self.base_color = [r, g, b]
                    print(f"Assigned color {hex_color} -> {self.base_color} to {self.object_name}")
                else:
                    self.base_color = [
                        random.uniform(0.5, 1.0), 
                        random.uniform(0.5, 1.0), 
                        random.uniform(0.5, 1.0)
                    ]
            except Exception as e:
                print(f"Error assigning color: {e}")
                self.base_color = [
                    random.uniform(0.5, 1.0), 
                    random.uniform(0.5, 1.0), 
                    random.uniform(0.5, 1.0)
                ]
        else:
            # If no specific color assignment, use brighter random colors
            self.base_color = [
                random.uniform(0.5, 1.0), 
                random.uniform(0.5, 1.0), 
                random.uniform(0.5, 1.0)
            ]
        
        # Information about the object
        self.info_text = f"Object: {self.object_name}\nPosition: {self.position}\nRotation: {self.rotation}\nColor: RGB{tuple(int(c*255) for c in self.base_color)}"
        
        # Flag to mark if object has gone off screen
        self.off_screen = False
        
        # Store screen position for label rendering
        self.screen_pos = None
    
    def update(self, delta_time):
        """
        Update the object position and rotation
        
        Args:
            delta_time (float): Time in seconds since last update
            
        Returns:
            bool: False if object has gone off screen, True otherwise
        """
        # Update position based on velocity
        for i in range(3):
            self.position[i] += self.velocity[i] * delta_time * 60  # Scale by frame rate
            
        # Update rotation based on rotation speed
        for i in range(3):
            self.rotation[i] += self.rotation_speed[i] * delta_time * 60  # Scale by frame rate
            
        # Check if object has gone off screen (left side)
        if self.position[0] < -8.0:  # Just off the left edge of the screen
            self.off_screen = True
            return False
            
        return True
    
    def render(self, decay_engine):
        """
        Render the object
        
        Args:
            decay_engine (DecayEngine): Reference to the decay engine for color effects
        """
        if not self.model:
            return
            
        # Apply decay effect to color
        base_color_rgb = tuple(int(c*255) for c in self.base_color)
        r, g, b = decay_engine.get_decay_color(base_color_rgb)
        color = (r/255.0, g/255.0, b/255.0)
        
        # Force GL_COLOR_MATERIAL to ensure colors are properly applied
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set object material for better color fidelity
        ambient = [color[0] * 0.4, color[1] * 0.4, color[2] * 0.4, 1.0]
        diffuse = [color[0], color[1], color[2], 1.0]
        specular = [0.8, 0.8, 0.8, 1.0]
        
        glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
        
        # Add explicit color setting (redundant but ensures color is applied)
        glColor3f(color[0], color[1], color[2])
        
        # Render the model with proper transformations and lighting
        self.model.render_with_lighting(
            position=self.position,
            rotation=self.rotation,
            scale=self.scale,
            color=color
        )


class MainMenu:
    """Main menu with flying Blender objects"""
    
    def __init__(self, decay_engine, preloaded_objects=None):
        """
        Initialize the main menu
        
        Args:
            decay_engine (DecayEngine): Reference to the decay engine
            preloaded_objects (dict, optional): Dictionary of preloaded BlenderModel objects
        """
        self.decay_engine = decay_engine
        self.preloaded_objects = preloaded_objects or {}
        pygame.init()
        pygame.display.set_caption("Digital Decay")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()
        
        # Setup OpenGL
        glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (SCREEN_WIDTH / SCREEN_HEIGHT), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Position the camera
        gluLookAt(
            0, 0, 15,  # Eye position
            0, 0, 0,    # Look at position
            0, 1, 0     # Up vector
        )

        # Clear color to dark background
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Enable depth test
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enhanced lighting setup for better color representation
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glShadeModel(GL_SMOOTH)
        
        # Key lighting change: use brighter ambient and diffuse light
        # This helps colors remain more vibrant
        ambient_light = [0.4, 0.4, 0.4, 1.0]  # Brighter ambient
        diffuse_light = [0.9, 0.9, 0.9, 1.0]  # Brighter diffuse
        specular_light = [0.6, 0.6, 0.6, 1.0]
        
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
        
        # Position light from an angle where it illuminates objects better
        light_position = [5.0, 7.0, 10.0, 1.0]  # Positioned for better illumination
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        
        # Add a second light from opposite side for better object illumination
        glEnable(GL_LIGHT1)
        ambient_light1 = [0.2, 0.2, 0.2, 1.0]
        diffuse_light1 = [0.4, 0.4, 0.4, 1.0]
        specular_light1 = [0.3, 0.3, 0.3, 1.0]
        
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_light1)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, diffuse_light1)
        glLightfv(GL_LIGHT1, GL_SPECULAR, specular_light1)
        
        # Position second light from opposite side
        light_position1 = [-5.0, -3.0, 10.0, 1.0]  
        glLightfv(GL_LIGHT1, GL_POSITION, light_position1)
        
        # Enable color material - this is critical for proper color display
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Create Blender objects
        self.objects = []
        
        # Setup Pygame surfaces for UI rendering
        self.pygame_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        
        # Create a decay bar at the bottom of the screen
        self.decay_bar = DecayBar(pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 30), decay_engine, full_width=True)
        
        # Font for text
        self.font = load_jetbrains_mono_font(24)
        
        # Selected object for displaying information
        self.selected_object = None
        self.selection_time = 0
        
        # For calculating delta time
        self.last_time = pygame.time.get_ticks()
        
        # Flag to control game transition
        self.should_transition = False
        self.transition_target = None
        
        # Spawn a few initial objects just off-screen to the right
        for _ in range(5):
            self.spawn_new_object()
    
    def spawn_new_object(self, position_override=None):
        """
        Spawn a new object from the right side of the screen
        
        Args:
            position_override (tuple, optional): Override for the initial position
            
        Returns:
            BlenderObject: The newly created object
        """
        # Define path to OBJ files
        obj_dir = os.path.join("assets", "blender", "objects")
        
        # If directory doesn't exist, create it
        if not os.path.exists(obj_dir):
            os.makedirs(obj_dir)
            print(f"Created directory: {obj_dir}")
        
        # Check for custom row objects first
        custom_row_objects = []
        for i in range(1, 8):  # rows 1-7
            row_obj_path = os.path.join(obj_dir, f"row{i}.obj")
            if os.path.exists(row_obj_path):
                custom_row_objects.append((row_obj_path, i-1))  # Store with row index (0-based)
        
        # Use custom row objects if available, otherwise fall back to any OBJ files
        if custom_row_objects:
            obj_files = custom_row_objects
            print(f"Using {len(custom_row_objects)} custom row objects")
        else:
            # Get list of available OBJ files
            obj_files = []
            if os.path.exists(obj_dir):
                obj_files = [(os.path.join(obj_dir, f), None) for f in os.listdir(obj_dir) 
                        if f.endswith('.obj') and os.path.isfile(os.path.join(obj_dir, f))]
        
        # If no OBJ files found, use default shapes
        if not obj_files:
            obj_files = [
                (os.path.join(obj_dir, "cube.obj"), None),
                (os.path.join(obj_dir, "sphere.obj"), None),
                (os.path.join(obj_dir, "torus.obj"), None)
            ]
        
        # Position new object - use override if provided, otherwise far off-screen to the right
        if position_override:
            x_pos, y_pos, z_pos = position_override
        else:
            # Position new object far off-screen to the right
            # Using 20.0 instead of 8.0 or 10.0 to ensure it's completely out of view
            x_pos = 20.0
            
            # Random vertical position - Constrain to be more visible
            # Keep objects within a narrower visible band
            y_pos = random.uniform(-2.5, 2.5)  # Narrower range for better visibility
            
            # Random depth - Keep closer to camera for better visibility
            z_pos = random.uniform(-3, -1)  # Closer to camera
        
        # Random rotation
        rotation = [random.uniform(0, 360) for _ in range(3)]
        
        # Random scale - Less variation for more consistency
        scale = random.uniform(0.8, 1.1)  # Narrower range for more consistent sizing
        
        # Select random OBJ file
        obj_file, row_index = random.choice(obj_files)
        obj_basename = os.path.basename(obj_file)
        
        # Use preloaded object if available
        preloaded_model = None
        if self.preloaded_objects and obj_basename in self.preloaded_objects:
            preloaded_model = self.preloaded_objects[obj_basename]
            print(f"Using preloaded model for {obj_basename}")
        
        # Create object
        new_obj = BlenderObject(obj_file, (x_pos, y_pos, z_pos), rotation, scale, row_index, preloaded_model)
        
        # Fixed velocity for smooth, consistent animation
        new_obj.velocity = [-random.uniform(0.05, 0.1), 0, 0]  # Slower movement for more graceful entry
        
        self.objects.append(new_obj)
        return new_obj
    
    def update_objects(self, delta_time):
        """
        Update all objects and manage object lifecycle
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        # Update existing objects and track which ones went off-screen
        objects_to_remove = []
        for obj in self.objects:
            if not obj.update(delta_time):
                objects_to_remove.append(obj)
        
        # Remove off-screen objects
        for obj in objects_to_remove:
            if obj in self.objects:
                self.objects.remove(obj)
                
                # If the removed object was selected, clear selection
                if obj == self.selected_object:
                    self.selected_object = None
        
        # Spawn new objects with a certain probability
        if random.random() < 0.02:  # 2% chance each frame
            self.spawn_new_object()
        
        # Ensure there's always at least one object
        if not self.objects:
            self.spawn_new_object()
    
    def draw_text_with_background(self, text, position, color=(255, 255, 255), bg_color=(0, 0, 0, 128)):
        """
        Draw text with a background directly to the screen
        
        Args:
            text (str): Text to display
            position (tuple): (x, y) position in screen coordinates
            color (tuple): RGB color tuple for the text
            bg_color (tuple): RGBA color tuple for the background
        """
        # Move cursor to position
        x, y = position
        
        # Create temporary Pygame surface for the text
        text_surface = self.font.render(text, True, color)
        text_width, text_height = text_surface.get_size()
        
        # Save current OpenGL state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Disable depth testing so text is always on top
        glDisable(GL_DEPTH_TEST)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Switch to 2D orthographic projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Convert y-coordinate from top-left to bottom-left origin
        y = SCREEN_HEIGHT - y - text_height
        
        # Draw background rectangle
        glColor4f(bg_color[0]/255, bg_color[1]/255, bg_color[2]/255, bg_color[3]/255)
        glBegin(GL_QUADS)
        glVertex2f(x - 5, y - 5)
        glVertex2f(x + text_width + 5, y - 5)
        glVertex2f(x + text_width + 5, y + text_height + 5)
        glVertex2f(x - 5, y + text_height + 5)
        glEnd()
        
        # Create a texture from the text surface
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        text_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, text_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, text_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        # Draw textured quad
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, text_texture)
        glColor4f(1, 1, 1, 1)  # Reset color for texture
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + text_width, y)
        glTexCoord2f(1, 1); glVertex2f(x + text_width, y + text_height)
        glTexCoord2f(0, 1); glVertex2f(x, y + text_height)
        glEnd()
        
        # Clean up texture
        glDeleteTextures(1, [text_texture])
        
        # Restore previous OpenGL state
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glPopAttrib()
    
    def render_decay_bar(self):
        """Render decay bar at the bottom of the screen using OpenGL directly"""
        # Get the decay percentage from the engine
        percentage = self.decay_engine.decay_percentage
        
        # Get the position from the decay bar
        bar_y = self.decay_bar.rect.y
        bar_height = self.decay_bar.rect.height
        
        # Save the current lighting state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Disable lighting and depth testing for 2D UI
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glDisable(GL_DEPTH_TEST)
        
        # Switch to orthographic projection for 2D drawing
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Convert bar_y from top-left to bottom-left origin
        bar_y = SCREEN_HEIGHT - bar_y - bar_height
        
        # Draw background
        glColor4f(0.0, 0.0, 0.0, 1.0)  # Black
        glBegin(GL_QUADS)
        glVertex2f(0, bar_y)
        glVertex2f(SCREEN_WIDTH, bar_y)
        glVertex2f(SCREEN_WIDTH, bar_y + bar_height)
        glVertex2f(0, bar_y + bar_height)
        glEnd()
        
        # Calculate fill width based on percentage
        fill_width = int(SCREEN_WIDTH * (percentage / 100.0))
        
        # Determine color based on percentage
        if percentage > 66:
            color = (0.0, 1.0, 0.0)  # Green
        elif percentage > 33:
            color = (1.0, 1.0, 0.0)  # Yellow
        else:
            color = (1.0, 0.0, 0.0)  # Red
        
        # Draw filled portion
        glColor4f(color[0], color[1], color[2], 1.0)
        glBegin(GL_QUADS)
        glVertex2f(0, bar_y)
        glVertex2f(fill_width, bar_y)
        glVertex2f(fill_width, bar_y + bar_height)
        glVertex2f(0, bar_y + bar_height)
        glEnd()
        
        # Draw border
        glColor4f(0.2, 0.2, 0.2, 1.0)  # Dark gray
        glBegin(GL_LINE_LOOP)
        glVertex2f(0, bar_y)
        glVertex2f(SCREEN_WIDTH, bar_y)
        glVertex2f(SCREEN_WIDTH, bar_y + bar_height)
        glVertex2f(0, bar_y + bar_height)
        glEnd()
        
        # Draw percentage text
        text = f"{int(percentage)}%"
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()
        
        # Create texture
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        text_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, text_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, text_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        # Position text on the right side of the bar (to match the games)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, text_texture)
        glColor4f(1, 1, 1, 1)
        
        # Position on right side of bar with 10px padding (matching decay_bar.py)
        text_x = SCREEN_WIDTH - text_width - 10
        text_y = bar_y + (bar_height - text_height) // 2
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(text_x, text_y)
        glTexCoord2f(1, 0); glVertex2f(text_x + text_width, text_y)
        glTexCoord2f(1, 1); glVertex2f(text_x + text_width, text_y + text_height)
        glTexCoord2f(0, 1); glVertex2f(text_x, text_y + text_height)
        glEnd()
        
        # Clean up
        glDeleteTextures(1, [text_texture])
        glDisable(GL_TEXTURE_2D)
        
        # Restore OpenGL state
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glPopAttrib()  # This will restore the lighting state

    def render_3d(self):
        """Render the 3D scene with Blender objects"""
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set background color to black
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Render all objects and update their screen positions
        for obj in self.objects:
            obj.render(self.decay_engine)
            
            # Fixed position calculation
            x, y, z = obj.position
            
            # Only update screen position for objects in view
            if z > -15 and abs(x) < 10 and abs(y) < 10:
                # Basic perspective projection
                scale_x = 50
                scale_y = 50
                center_x = SCREEN_WIDTH // 2
                center_y = SCREEN_HEIGHT // 2
                
                # Perspective factor (objects further away appear smaller)
                perspective_factor = 15.0 / max(0.1, 15.0 + z)
                
                # Calculate screen coordinates
                screen_x = center_x + int(x * scale_x * perspective_factor)
                screen_y = center_y - int(y * scale_y * perspective_factor)
                
                # Store the screen position
                obj.screen_pos = (screen_x, screen_y)
            else:
                obj.screen_pos = None

    def draw_object_label_with_line(self, obj):
        """Draw a technical-style label directly attached to object with dashed connecting line"""
        try:
            if not hasattr(obj, 'screen_pos') or obj.screen_pos is None:
                return
            
            screen_x, screen_y = obj.screen_pos
            
            # Determine correct row and column from the object
            # If row_index is available, use it (it's 0-based)
            row_index = obj.row_index if hasattr(obj, 'row_index') and obj.row_index is not None else 0
            
            # Get color from decay grid based on current decay stage
            decay_level = self.decay_engine.decay_percentage / 100.0
            if decay_level < 0.2:
                decay_stage = 5
            elif decay_level < 0.4:
                decay_stage = 4
            elif decay_level < 0.6:
                decay_stage = 3
            elif decay_level < 0.8:
                decay_stage = 2
            else:
                decay_stage = 1
            
            # Choose a random column if not already assigned
            if not hasattr(obj, 'grid_col'):
                obj.grid_col = random.randint(0, 12)  # 13 columns (0-12)
                
            # Ensure DECAY_GRIDS is available
            if DECAY_GRIDS is not None:
                # Get hex color from the grid
                try:
                    hex_color = DECAY_GRIDS["stages"][decay_stage]["grid"][row_index][obj.grid_col]
                except (KeyError, IndexError):
                    hex_color = '#FFFFFF'  # Fallback color if not found
            else:
                hex_color = '#FFFFFF'  # Default if decay grids not available
            
            # Generate label text with correct information
            label_text = [
                f"Row:{row_index+1} Col:{obj.grid_col+1}",
                f"Color:{hex_color}",
                f"DecayStage:{decay_stage+1}"
            ]
            
            # Position the label at a consistent offset from the object
            # Use object's stored offset or initialize new one
            if not hasattr(obj, 'label_offset') or obj.label_offset == [0, 0]:
                # Set initial offset based on object position on screen
                if screen_x < SCREEN_WIDTH // 2:
                    offset_x = 70  # Right of object if on left side
                else:
                    offset_x = -170  # Left of object if on right side
                    
                if screen_y < SCREEN_HEIGHT // 2:
                    offset_y = 40  # Below object if in top half
                else:
                    offset_y = -90  # Above object if in bottom half
                    
                obj.label_offset = [offset_x, offset_y]
            
            # Use stored offset
            label_x = screen_x + obj.label_offset[0]
            label_y = screen_y + obj.label_offset[1]
            
            # OpenGL setup for 2D drawing
            glPushAttrib(GL_ALL_ATTRIB_BITS)
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_LIGHTING)  # Disable lighting for UI elements
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            # Convert from top-left to bottom-left coordinates
            screen_y = SCREEN_HEIGHT - screen_y
            label_y = SCREEN_HEIGHT - label_y
            
            # Draw each line of text
            text_height = 0
            max_text_width = 0
            rendered_lines = []
            
            for line in label_text:
                text_surface = self.font.render(line, True, (255, 255, 255))  # Always white
                text_width, line_height = text_surface.get_size()
                max_text_width = max(max_text_width, text_width)
                text_height += line_height
                rendered_lines.append((text_surface, text_width, line_height))
            
            # Draw text lines directly without background
            for i, (text_surface, text_width, line_height) in enumerate(rendered_lines):
                # Create texture from text
                text_data = pygame.image.tostring(text_surface, "RGBA", True)
                text_texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, text_texture)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, line_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
                
                # Position for this line (accounting for bottom-left origin)
                line_y = label_y - i * line_height
                
                # Draw text
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, text_texture)
                glColor4f(1, 1, 1, 1)  # White text
                
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(label_x, line_y - line_height)
                glTexCoord2f(1, 0); glVertex2f(label_x + text_width, line_y - line_height)
                glTexCoord2f(1, 1); glVertex2f(label_x + text_width, line_y)
                glTexCoord2f(0, 1); glVertex2f(label_x, line_y)
                glEnd()
                
                # Clean up
                glDeleteTextures(1, [text_texture])
            
            # Draw connecting line as a dashed line
            glDisable(GL_TEXTURE_2D)
            
            # Use color from grid for the line
            if DECAY_GRIDS is not None:
                try:
                    hex_color = DECAY_GRIDS["stages"][decay_stage]["grid"][row_index][obj.grid_col]
                    # Convert hex to RGB (0-1 range)
                    r = int(hex_color[1:3], 16) / 255.0
                    g = int(hex_color[3:5], 16) / 255.0
                    b = int(hex_color[5:7], 16) / 255.0
                    glColor3f(r, g, b)
                except (KeyError, IndexError):
                    glColor3f(1.0, 1.0, 1.0)  # White fallback
            else:
                glColor3f(1.0, 1.0, 1.0)  # White fallback
                
            glLineWidth(1.0)
            
            # Calculate line endpoints
            line_start_x, line_start_y = screen_x, screen_y
            
            # Determine which side of the text box to connect to
            if obj.label_offset[0] > 0:  # Label is to the right
                line_end_x = label_x
            else:  # Label is to the left
                line_end_x = label_x + max_text_width
                
            # Calculate vertical position
            line_end_y = label_y - text_height // 2
            
            # Calculate line parameters for dashed line
            dx = line_end_x - line_start_x
            dy = line_end_y - line_start_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Normalize direction
                dx /= distance
                dy /= distance
                
                # Draw dashed line
                dash_length = 5  # Length of each dash
                gap_length = 5   # Length of gaps between dashes
                
                # Start drawing from object
                current_distance = 0
                drawing = True  # Start with a dash
                
                while current_distance < distance:
                    segment_length = dash_length if drawing else gap_length
                    end_distance = min(current_distance + segment_length, distance)
                    
                    if drawing:
                        # Calculate segment endpoints
                        x1 = line_start_x + dx * current_distance
                        y1 = line_start_y + dy * current_distance
                        x2 = line_start_x + dx * end_distance
                        y2 = line_start_y + dy * end_distance
                        
                        # Draw line segment
                        glBegin(GL_LINES)
                        glVertex2f(x1, y1)
                        glVertex2f(x2, y2)
                        glEnd()
                    
                    # Move to next segment
                    current_distance = end_distance
                    drawing = not drawing
            
            # Restore OpenGL state
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glPopAttrib()
        except Exception as e:
            print(f"Error in draw_object_label: {e}")

    def render_2d_overlay(self):
        """Render 2D overlay with text and UI"""
        # Draw object labels
        for obj in self.objects:
            if hasattr(obj, 'screen_pos') and obj.screen_pos is not None:
                # Only label objects that are in front
                if obj.position[2] > -5:
                    self.draw_object_label_with_line(obj)
        
        # Draw instruction text at the bottom of the screen
        instruction_text = "Click anywhere to enter a random game"
        text_surface = self.font.render(instruction_text, True, (255, 255, 255))
        text_width = text_surface.get_size()[0]
        
        self.draw_text_with_background(
            instruction_text, 
            (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT - 80)
        )
        
        # Draw decay bar at the bottom of the screen
        self.render_decay_bar()
    
    def update(self):
        """Update game state and handle events"""
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_time) / 1000.0  # Convert to seconds
        self.last_time = current_time
        
        # Update decay normally with time (not affected by objects)
        self.decay_engine.update(delta_time)
        
        # Update objects
        self.update_objects(delta_time)
        
        # Check if we should transition to a game
        if self.should_transition:
            self.should_transition = False
            return self.transition_target
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Immediately transition to a random game without delay
                # Choose a random game
                random_game = "game" + str(random.randint(1, 3))
                print(f"Main menu clicked, transitioning to {random_game}")
                return random_game
        
        return True
    
    def run(self):
        """Run the main menu loop"""
        running = True
        while running:
            result = self.update()
            
            # *** CRITICAL ADDITION: Directly check decay percentage ***
            # This ensures the main menu can trigger the end screen
            if self.decay_engine.decay_percentage <= 0.0:
                print("DECAY DETECTED AT 0% IN MAIN MENU - Ending main menu")
                return "end_screen"  # Force transition to end screen
            
            if result is False:
                running = False
            elif isinstance(result, str):
                return result
            
            self.render_3d()
            self.render_2d_overlay()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        return None