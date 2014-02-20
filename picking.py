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

        default_region = context.getDefaultRegion()
        
        # Get the field module for root region, with which we  shall create a 
        # finite element coordinate field.
        field_module = default_region.getFieldmodule()
        
        finite_element_field = field_module.createFieldFiniteElement(3)
        
        node_coordinate_set = [[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [0.0, 4.0, 0.0], [2.0, 2.0, 0.0],
                               [0.0, 0.0, 1.0], [3.0, 0.0, 1.0], [0.0, 4.0, 1.0], [2.0, 2.0, 1.0]]
        
        self.ui._zincWidget.create3DFiniteElement(field_module, finite_element_field, node_coordinate_set)

        #self.createSurfaceGraphic()
        self.ui._zincWidget.graphicsInitialized.connect(self.setUp)
        
    def setUp(self):
        zw = self.ui._zincWidget
        context = zw.getContext()
                 
        sv = zw.getSceneviewer()
        print "sv", sv
        self.createSurfaceGraphic()
        

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
        # createSurfaceGraphic graphic end
        
        #zw = self.ui._zincWidget
        #sv = zw.getSceneviewer()
        
        # Set the scene to our scene viewer. - no longer required
        # sv.setScene(scene) 
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
