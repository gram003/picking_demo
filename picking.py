#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
try:
    from PySide import QtGui
except ImportError:
    from PyQt4 import QtGui
from picking_ui import Ui_PickingDlg
from opencmiss.zinc.context import Context
from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.element import Element, Elementbasis

class PickingDlg(QtGui.QWidget):
    '''
    Create a subclass of QWidget for our application.  We could also have derived this 
    application from QMainApplication to give us a menu bar among other things, but a
    QWidget is sufficient for our purposes.
    '''
    
    def __init__(self, parent=None):
        '''
        Initialise the FiniteElementCreationDlg first calling the QWidget __init__ function.
        '''
        QtGui.QWidget.__init__(self, parent)
        
        # Using composition to include the visual element of the GUI.
        self.ui = Ui_PickingDlg()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("cmiss_icon.ico"))

        context = Context("foo")
        self._context = context
        self.ui._zincWidget.setContext(context)
        
        self.ui._zincWidget.graphicsInitialized.connect(self.setUp)
                
    def setUp(self):
        
        node_coordinate_set = [[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [0.0, 4.0, 0.0], [3.0, 2.0, 0.0],
                               [0.0, 0.0, 2.0], [3.0, 0.0, 2.0], [0.0, 4.0, 2.0], [3.0, 2.0, 2.0]]
        self.create3DFiniteElement(node_coordinate_set)

#         node_coordinate_set = [[0, 0.0], [3.0, 0.0], [0.0, 4.0], [2.0, 2.0]]
#         self.create2DFiniteElement(node_coordinate_set)

        self.createSurfaceGraphic()
        
        self.ui._zincWidget.viewAll()
        
        self.ui._zincWidget.setSelectModeAll()
       
#         # must set _initialized before calling  createSurfaceGraphic()
#         self._initialized = True
#         self.createSurfaceGraphic()
 
    # create2DFiniteElement start
    def create2DFiniteElement(self, node_coordinate_set):
        # Get a the root region, which is the default region of the context.
        default_region = self._context.getDefaultRegion()
        
        # Get the field module for root region, with which we  shall create a 
        # finite element coordinate field.
        field_module = default_region.getFieldmodule()
        
        field_module.beginChange()
        
        # Create a finite element field with 2 components to represent 2 dimensions
        finite_element_field = field_module.createFieldFiniteElement(2)
        # Set the name of the field, we give it label to help us understand it's purpose
        finite_element_field.setName('coordinates')
        self._finite_element_field = finite_element_field
        # Find a special node set named 'cmiss_nodes'
        nodeset = field_module.findNodesetByName('nodes')
        node_template = nodeset.createNodetemplate()
        # Set the finite element coordinate field for the nodes to use
        node_template.defineField(finite_element_field)
        
        field_cache = field_module.createFieldcache()
        
        # Create four nodes to define a square finite element over
        for i, node_coordinate in enumerate(node_coordinate_set):
            # Node indexes start from 1
            node = nodeset.createNode(i+1, node_template)
            # Set the node coordinates, first set the field cache to use the current node
            field_cache.setNode(node)
            # Pass in floats as an array
            finite_element_field.assignReal(field_cache, node_coordinate)

        # We want to create a 2D element so we grab the predefined 2D mesh.  Currently there
        # is only one mesh for each dimension 1D, 2D, and 3D the user is not able to name
        # their own mesh.  This is due to change in an upcoming release of PyZinc.
        mesh = field_module.findMeshByDimension(2)
        element_template = mesh.createElementtemplate()
        element_template.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
        element_node_count = 4
        element_template.setNumberOfNodes(element_node_count)
        # Specify the dimension and the interpolation function for the element basis function. 
        linear_basis = field_module.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
        # The indexes of the nodes in the node template we want to use
        node_indexes = [1, 2, 3, 4]
        # Define a nodally interpolated element field or field component in the
        # element_template. Only Lagrange, simplex and constant basis function types
        # may be used with this function, i.e. where only a simple node value is
        # mapped. Shape must be set before calling this function.  The -1 for the component number
        # defines all components with identical basis and nodal mappings.
        element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)
                    
        for i in range(element_node_count):
            node = nodeset.findNodeByIdentifier(i+1)
            element_template.setNode(i+1, node)

        mesh.defineElement(-1, element_template)
        
        field_module.endChange()

    def create3DFiniteElement(self, node_coordinate_set):
        '''
        Create finite element from a template
        '''
        
        default_region = self._context.getDefaultRegion()
        
        # Get the field module for root region, with which we  shall create a 
        # finite element coordinate field.
        field_module = default_region.getFieldmodule()
        
        field_module.beginChange()

        finite_element_field = field_module.createFieldFiniteElement(3)
        finite_element_field.setName('coordinates')
        
        # Find a special node set named 'nodes'
        nodeset = field_module.findNodesetByName('nodes')
        node_template = nodeset.createNodetemplate()

        # Set the finite element coordinate field for the nodes to use
        node_template.defineField(finite_element_field)
        field_cache = field_module.createFieldcache()

        node_identifiers = []
        # Create eight nodes to define a cube finite element
        for node_coordinate in node_coordinate_set:
            node = nodeset.createNode(-1, node_template)
            node_identifiers.append(node.getIdentifier())
            # Set the node coordinates, first set the field cache to use the current node
            field_cache.setNode(node)
            # Pass in floats as an array
            finite_element_field.assignReal(field_cache, node_coordinate)

        # Use a 3D mesh to to create the 3D finite element.
        mesh = field_module.findMeshByDimension(3)
        element_template = mesh.createElementtemplate()
        element_template.setElementShapeType(Element.SHAPE_TYPE_CUBE)
        element_node_count = 8
        element_template.setNumberOfNodes(element_node_count)
        # Specify the dimension and the interpolation function for the element basis function
        linear_basis = field_module.createElementbasis(3, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
        # the indicies of the nodes in the node template we want to use.
        node_indexes = [1, 2, 3, 4, 5, 6, 7, 8]

        # Define a nodally interpolated element field or field component in the
        # element_template
        element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

        for i, node_identifier in enumerate(node_identifiers):
            node = nodeset.findNodeByIdentifier(node_identifier)
            element_template.setNode(i + 1, node)

        mesh.defineElement(-1, element_template)

        finite_element_field.setTypeCoordinate(True) 
        field_module.defineAllFaces() 
        field_module.endChange()
 
    # createSurfaceGraphic start
    def createSurfaceGraphic(self):
        
        # Get a the root region to create the point in.  Every context has a default region called the root region.
        default_region = self._context.getDefaultRegion()
        
        # Get the scene for the default region to create the visualisation in.
        scene = default_region.getScene()
        
        # We use the beginChange and endChange to wrap any immediate changes and will
        # streamline the rendering of the scene.
        scene.beginChange()
                
        # createSurfaceGraphic graphic start
        field_module = default_region.getFieldmodule()
        finite_element_field = field_module.findFieldByName('coordinates')
        # Create a surface graphic and set it's coordinate field to the finite element coordinate field
        # named coordinates
        surface = scene.createGraphicsSurfaces()
        surface.setCoordinateField(finite_element_field)
        
        # Create point graphics and set the coordinate field to the finite element coordinate field
        # named coordinates
        sphere = scene.createGraphicsPoints()
        sphere.setCoordinateField(finite_element_field)
        sphere.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        att = sphere.getGraphicspointattributes()
        att.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        att.setBaseSize([1])

          
#         zw = self.ui._zincWidget
#         sv = zw.getSceneviewer()
#          
#         # Set the scene to our scene viewer. - no longer required
#         sv.setScene(scene) 
        # Let the scene render the scene.
        scene.endChange()
        # createSurfaceGraphic end


# main start
def main():
    '''
    The entry point for the application, handle application arguments and initialise the 
    GUI.
    '''
    
    app = QtGui.QApplication(sys.argv)

    w = PickingDlg()
    w.show()

    sys.exit(app.exec_())
# main end

if __name__ == '__main__':
    main()
