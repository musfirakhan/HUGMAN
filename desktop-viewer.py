# FOR DESKTOP
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import trimesh
import numpy as np
import os

def view_model(model_path):
    # Load your mesh (OBJ, PLY, etc.)
    mesh = trimesh.load(model_path)

    # If it's a Scene, extract the first geometry
    if isinstance(mesh, trimesh.Scene):
        # Combine all geometries into a single mesh (if you want all parts)
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

    # Convert to vertex/face arrays
    verts = mesh.vertices
    faces = mesh.faces

    # Center the mesh at the origin
    center = verts.mean(axis=0)
    verts_centered = verts - center
    size = np.linalg.norm(verts.max(axis=0) - verts.min(axis=0))

    ########## commented part is for showing mesh of 3d object

    # Create Qt app and 3D view widget
    # app = pg.mkQApp("3D Model Viewer")
    # w = gl.GLViewWidget()
    # w.show()
    # w.setWindowTitle('3D Model Viewer')

    # # Set background to dark grey using OpenGL directly
    # try:
    #     w.setBackgroundColor((50, 50, 50, 1))
    # except Exception:
    #     import OpenGL.GL as ogl
    #     w.paintGL = lambda: ogl.glClearColor(50, 50, 50, 1)

    # # Center the view on the origin (where the mesh is now centered)
    # w.opts['center'] = pg.Vector(0, 0, 0)
    # # Set camera distance based on model size
    # w.setCameraPosition(distance=size * 2)

    # Create mesh item
    meshdata = gl.MeshData(vertexes=verts_centered, faces=faces)
    m1 = gl.GLMeshItem(meshdata=meshdata, smooth=True, color=(1, 0, 0, 1), shader='shaded', drawEdges=True)
    # w.addItem(m1)

    mesh.show(background=[0.3, 0.3, 0.3, 1])  # Opens in browser, supports background color

    # app.exec_() 

view_model("/Users/musfiraaslam/Desktop/makehuman-mastercopy42/3d-model/output/yuna.obj")