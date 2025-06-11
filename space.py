from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective
from OpenGL.arrays import vbo
import numpy as np
import math
import time
import sys

# Globals for VAO/VBO
orbit_VAOs = []
orbit_VBOs = []
num_orbit_points = 100

# Window size
width, height = 800, 600

# Camera controls
angle_x, angle_y = 20, 30
zoom = -30  # Zoomed in

last_time = time.time()

# Planets data (same as before)...
planets = [
    (4.0, 0.5, 0.8, (0.5, 0.5, 1.0), "Mercury", []),
    (6.0, 0.7, 0.6, (1.0, 0.7, 0.2), "Venus", []),
    (8.0, 0.9, 0.4, (0.0, 0.5, 1.0), "Earth", [
        (1.2, 0.2, 2.5, (0.9, 0.9, 0.9), "Moon")
    ]),
    (10.0, 0.8, 0.3, (1.0, 0.0, 0.0), "Mars", []),
    (13.0, 1.4, 0.2, (1.0, 0.9, 0.5), "Jupiter", [
        (2.0, 0.3, 1.5, (0.8, 0.7, 0.6), "Io"),
        (2.5, 0.25, 1.2, (0.7, 0.7, 0.7), "Europa"),
        (3.0, 0.4, 0.9, (0.6, 0.6, 0.6), "Ganymede"),
        (3.5, 0.35, 0.7, (0.5, 0.5, 0.5), "Callisto")
    ]),
    (16.0, 1.2, 0.15, (0.8, 0.8, 0.7), "Saturn", [
        (2.0, 0.25, 1.7, (0.7, 0.7, 0.7), "Titan"),
        (2.7, 0.2, 1.3, (0.6, 0.6, 0.6), "Rhea"),
    ]),
    (13.0, 0.6, 0.1, (0.4, 0.8, 1.0), "Uranus", []),
    (10.0, 0.9, 0.05, (0.3, 0.3, 1.0), "Neptune", [])
]

angles = [0.0 for _ in planets]
moon_angles = [0.0 for _ in range(sum(len(p[5]) for p in planets))]

def create_orbit_circle(radius):
    # Create circle points for the orbit
    points = []
    for i in range(num_orbit_points):
        theta = 2 * math.pi * i / num_orbit_points
        x = math.cos(theta) * radius
        z = math.sin(theta) * radius
        points.extend([x, 0.0, z])
    return np.array(points, dtype=np.float32)

def setup_orbit_VAOs():
    global orbit_VAOs, orbit_VBOs
    orbit_VAOs = []
    orbit_VBOs = []
    for distance, _, _, _, _, _ in planets:
        vao = glGenVertexArrays(1)
        vbo_id = glGenBuffers(1)
        glBindVertexArray(vao)

        points = create_orbit_circle(distance)

        glBindBuffer(GL_ARRAY_BUFFER, vbo_id)
        glBufferData(GL_ARRAY_BUFFER, points.nbytes, points, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        orbit_VAOs.append(vao)
        orbit_VBOs.append(vbo_id)

def draw_orbit_VAO(index):
    glDisable(GL_LIGHTING)
    glColor3f(0.7, 0.7, 0.7)  # Slightly brighter orbit color
    glLineWidth(3)  # Thicker line

    glBindVertexArray(orbit_VAOs[index])
    glDrawArrays(GL_LINE_LOOP, 0, num_orbit_points)
    glBindVertexArray(0)

    glEnable(GL_LIGHTING)
    glLineWidth(1)  # Reset line width

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    light_pos = [0.0, 0.0, 0.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])

    setup_orbit_VAOs()

def draw_text(x, y, z, text):
    glRasterPos3f(x, y, z)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def draw_planet(distance, size, angle, color, name, moons=None, moon_index_start=0):
    x = distance * math.cos(math.radians(angle))
    z = distance * math.sin(math.radians(angle))

    glPushMatrix()
    glTranslatef(x, 0.0, z)
    glColor3fv(color)
    glutSolidSphere(size, 30, 30)
    draw_text(0.0, size + 0.2, 0.0, name)

    if moons:
        for i, (mdist, msize, mspeed, mcolor, mname) in enumerate(moons):
            global moon_angles, last_time
            moon_angles[moon_index_start + i] += mspeed * 50 * (time.time() - last_time)
            if moon_angles[moon_index_start + i] > 360:
                moon_angles[moon_index_start + i] -= 360

            mx = mdist * math.cos(math.radians(moon_angles[moon_index_start + i]))
            mz = mdist * math.sin(math.radians(moon_angles[moon_index_start + i]))

            glPushMatrix()
            glTranslatef(mx, 0.0, mz)
            glColor3fv(mcolor)
            glutSolidSphere(msize, 20, 20)
            draw_text(0.0, msize + 0.05, 0.0, mname)
            glPopMatrix()

    glPopMatrix()

def display():
    global last_time, angles, moon_angles

    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(0.0, -1.5, zoom)  # Slightly raised view
    glRotatef(angle_x, 1.0, 0.0, 0.0)
    glRotatef(angle_y, 0.0, 1.0, 0.0)

    # Sun
    glColor3f(1.0, 1.0, 0.0)
    glutSolidSphere(2.5, 50, 50)
    draw_text(0.0, 2.7, 0.0, "Sun")

    moon_index = 0
    for i, (distance, size, speed, color, name, moons) in enumerate(planets):
        draw_orbit_VAO(i)  # Draw orbit with VAO + thick line

        angles[i] += speed * 50 * delta_time
        if angles[i] > 360:
            angles[i] -= 360

        draw_planet(distance, size, angles[i], color, name, moons, moon_index)
        moon_index += len(moons) if moons else 0

    glutSwapBuffers()

def reshape(w, h):
    global width, height
    width, height = w, h
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, width / float(height), 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def keyboard(key, x, y):
    global zoom
    if key == b'+':
        zoom += 1.0
    elif key == b'-':
        zoom -= 1.0
    elif key == b'\x1b':  # ESC
        sys.exit(0)
    glutPostRedisplay()

def special_keys(key, x, y):
    global angle_x, angle_y
    if key == GLUT_KEY_LEFT:
        angle_y -= 5
    elif key == GLUT_KEY_RIGHT:
        angle_y += 5
    elif key == GLUT_KEY_UP:
        angle_x -= 5
    elif key == GLUT_KEY_DOWN:
        angle_x += 5
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Solar System with VAO/VBO orbits and thicker lines")

    init()
    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)

    glutMainLoop()

if __name__ == "__main__":
    main()
