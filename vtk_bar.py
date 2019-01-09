import numpy as np

class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_vector(self):
        return [self.x, self.y]


class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.w = 1

    def to_vector(self):
        return (self.x, self.y, self.z)
    
    def to_np_array(self):
        return np.array([self.x, self.y, self.z])

    def out_of_camera(self):
        return self.z <= 0

    def update_from_vector(self, vector):
        self.x = vector[0]
        self.y = vector[1]
        self.z = vector[2]
        self.w = vector[3]


class Polygon:
    def __init__(self, vectors, color):
        self.vectors = vectors
        self.color = color
        self.points = self.set_points()

    def set_points(self):
        return [x for x in self.vectors]

    def dist_to_observator(self):
        pt = Point3D(np.sum(map(lambda point: point.x, self.points))/len(self.points),
                   np.sum(map(lambda point: point.y, self.points))/len(self.points),
                   np.sum(map(lambda point: point.z, self.points))/len(self.points))
        distance = np.sqrt(pt.x**2 + pt.y**2 + pt.z**2)
        return distance

    def max_z(self):
        return np.max(map(lambda point: point[2], self.points))

    def min_z(self):
        return np.min(map(lambda point: point[2], self.points))
    
    def to_list(self):
        list_of_points = []
        for v in self.vectors:
            list_of_points += v.to_list()
        return list(np.array(p) for p in set(list_of_points))


class Vector:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
    def to_list(self):
        return (self.a.to_vector(), self.b.to_vector())


class Cuboid:
    def __init__(self, x, y, z, width, height, color):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.color = color
        self.polygons = []
        self.create_walls()

    def create_walls(self):
        self.create_front_wall()
        self.create_back_wall()
        self.create_bottom_wall()
        self.create_top_wall()
        self.create_left_wall()
        self.create_right_wall()

    def create_front_wall(self):
        vectors = []
        vectors.append(Vector(Point3D(self.x, self.y, self.z)
                              , Point3D(self.x + self.width, self.y, self.z)))

        vectors.append(Vector(Point3D(self.x + self.width, self.y, self.z),
                              Point3D(self.x + self.width, self.y + self.height, self.z)))

        vectors.append(Vector(Point3D(self.x + self.width, self.y + self.height, self.z),
                              Point3D(self.x, self.y + self.height, self.z)))

        vectors.append(Vector(Point3D(self.x, self.y + self.height, self.z),
                              Point3D(self.x, self.y, self.z)))

        self.polygons.append(Polygon(vectors, self.color))

    def create_back_wall(self):
        vectors = []
        vectors.append(Vector(Point3D(self.x, self.y, self.z + self.height),
                              Point3D(self.x + self.width, self.y, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x + self.width, self.y, self.z + self.height),
                              Point3D(self.x + self.width, self.y + self.height, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x + self.width, self.y + self.height, self.z + self.height),
                              Point3D(self.x, self.y + self.height, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x, self.y + self.height, self.z + self.height),
                              Point3D(self.x, self.y, self.z + self.height)))
        self.polygons.append(Polygon(vectors, self.color))

    def create_bottom_wall(self):
        vectors = []
        vectors.append(Vector(Point3D(self.x, self.y, self.z),
                              Point3D(self.x, self.y, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x, self.y, self.z + self.height),
                              Point3D(self.x + self.width, self.y, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x + self.width, self.y, self.z + self.height),
                              Point3D(self.x + self.width, self.y, self.z)))
        vectors.append(Vector(Point3D(self.x + self.width, self.y, self.z),
                              Point3D(self.x, self.y, self.z)))
        self.polygons.append(Polygon(vectors, self.color))

    def create_top_wall(self):
        vectors = []
        vectors.append(Vector(Point3D(self.x, self.y + self.height, self.z),
                              Point3D(self.x, self.y + self.height, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x, self.y + self.height, self.z + self.height),
                              Point3D(self.x + self.width, self.y + self.height, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x + self.width, self.y + self.height, self.z + self.height),
                              Point3D(self.x + self.width, self.y + self.height, self.z)))
        vectors.append(Vector(Point3D(self.x + self.width, self.y + self.height, self.z),
                              Point3D(self.x, self.y + self.height, self.z)))
        self.polygons.append(Polygon(vectors, self.color))

    def create_left_wall(self):
        vectors = []
        vectors.append(Vector(Point3D(self.x, self.y, self.z),
                              Point3D(self.x, self.y, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x, self.y, self.z + self.height),
                              Point3D(self.x, self.y + self.height, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x, self.y + self.height, self.z + self.height),
                              Point3D(self.x, self.y + self.height, self.z)))
        vectors.append(Vector(Point3D(self.x, self.y + self.height, self.z),
                              Point3D(self.x, self.y, self.z)))
        self.polygons.append(Polygon(vectors, self.color))

    def create_right_wall(self):
        vectors = []
        vectors.append(Vector(Point3D(self.x + self.width, self.y, self.z),
                              Point3D(self.x + self.width, self.y, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x + self.width, self.y, self.z + self.height),
                              Point3D(self.x + self.width, self.y + self.height, self.z + self.height)))
        vectors.append(Vector(Point3D(self.x + self.width, self.y + self.height, self.z + self.height),
                              Point3D(self.x + self.width, self.y + self.height, self.z)))
        vectors.append(Vector(Point3D(self.x + self.width, self.y + self.height, self.z),
                              Point3D(self.x + self.width, self.y, self.z)))
        self.polygons.append(Polygon(vectors, self.color))
    
    def get_vertices_and_faces(self):
        edges = self.get_edges()
        vertices = list(set(tuple(p.tolist()) for edge in edges for p in edge))
        faces = []
        for polygon in self.polygons:
            _points = [tuple(p.tolist()) for p in polygon.to_list()]
            faces.append([vertices.index(p) for p in _points])
        return vertices, faces
    
    def get_edges(self):
        return [p.to_list() for p in self.polygons]

import vtk

def vtk_bar(center, val):
    def mkVtkIdList(it):
        vil = vtk.vtkIdList()
        for i in it:
            vil.InsertNextId(int(i))
        return vil
    x_center, y_center, z_center = center
    cube_constructor = Cuboid(x_center, y_center, z_center, val, 0.03, "blue")
    x, pts = cube_constructor.get_vertices_and_faces()

    cube    = vtk.vtkPolyData()
    points  = vtk.vtkPoints()
    polys   = vtk.vtkCellArray()
    scalars = vtk.vtkFloatArray()
    for i in range(8):
        points.InsertPoint(i, x[i])
    for i in range(6):
        polys.InsertNextCell( mkVtkIdList(pts[i]) )
    for i in range(8):
        scalars.InsertTuple1(i,i)
    cube.SetPoints(points)
    del points
    cube.SetPolys(polys)
    del polys
    cube.GetPointData().SetScalars(scalars)
    del scalars
    cubeMapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        cubeMapper.SetInput(cube)
    else:
        cubeMapper.SetInputData(cube)
    cubeMapper.SetScalarRange(0,7)
    cubeActor = vtk.vtkActor()
    cubeActor.SetMapper(cubeMapper)
    return cubeActor
