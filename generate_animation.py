"""
generate_animation.py - Generate a simple animation for testing
"""
import os
import math
import pygame

# Create directories if they don't exist
def create_dirs():
    dirs = [
        "assets",
        "assets/blender",
        "assets/blender/animation"
    ]
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")

# Generate frames with rotating shapes
def generate_frames(num_frames=60, width=800, height=600):
    frames_dir = os.path.join("assets", "blender", "animation")
    
    # Initialize pygame
    pygame.init()
    font = pygame.font.Font(None, 36)
    
    # Create surface for drawing
    surface = pygame.Surface((width, height))
    
    # Generate each frame
    for i in range(num_frames):
        # Clear surface
        surface.fill((0, 0, 0))
        
        # Calculate animation progress
        progress = i / num_frames
        angle = progress * 2 * math.pi
        
        # Draw a rotating shape
        center_x, center_y = width // 2, height // 2
        radius = 150
        
        # Draw a polygon
        points = []
        num_points = 5  # Pentagon
        for p in range(num_points):
            point_angle = angle + (p * 2 * math.pi / num_points)
            x = center_x + radius * math.cos(point_angle)
            y = center_y + radius * math.sin(point_angle)
            points.append((x, y))
        
        # Calculate color based on progress - FIX: Ensure values are between 0-255
        r = int(abs(math.sin(progress * math.pi)) * 255)
        g = int(abs(math.sin(progress * math.pi + math.pi/3)) * 255)
        b = int(abs(math.sin(progress * math.pi + 2*math.pi/3)) * 255)
        
        # Draw shape
        pygame.draw.polygon(surface, (r, g, b), points)
        
        # Draw frame number
        text = font.render(f"Frame {i+1}/{num_frames}", True, (255, 255, 255))
        surface.blit(text, (20, 20))
        
        # Save frame
        file_path = os.path.join(frames_dir, f"frame_{i:03d}.png")
        pygame.image.save(surface, file_path)
        print(f"Generated: {file_path}")

if __name__ == "__main__":
    create_dirs()
    generate_frames()
    print("Animation frames generated successfully.")
    print("Place the frames in assets/blender/animation/ to use them in the game.")