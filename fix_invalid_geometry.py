from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import QgsProject, QgsVectorLayer
from qgis.utils import iface
import os.path

from .fix_invalid_geometry_dialog import FixInvalidGeometryDialog

class FixInvalidGeometryPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dlg = FixInvalidGeometryDialog()
        self.actions = []
        self.menu = 'Fix Invalid Geometry'

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.action = QAction(
            QIcon(icon_path) if os.path.exists(icon_path) else QIcon(),
            'Fix Invalid Geometry (Save to File)',
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu(self.menu, self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginVectorMenu(self.menu, self.action)
        del self.action

    def run(self):
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            layer_id = self.dlg.selected_layer_id()
            output_path = self.dlg.output_path()

            if not layer_id:
                iface.messageBar().pushWarning("Error", "Pilih layer vektor terlebih dahulu.")
                return
            if not output_path:
                iface.messageBar().pushWarning("Error", "Tentukan lokasi file output.")
                return

            layer = QgsProject.instance().mapLayer(layer_id)
            if not isinstance(layer, QgsVectorLayer):
                iface.messageBar().pushWarning("Error", "Layer bukan vektor.")
                return

            self.fix_geometry(layer, output_path)

    def fix_geometry(self, layer, output_path):
        from qgis import processing
        from qgis.core import QgsProcessingFeedback, QgsProcessingContext

        feedback = QgsProcessingFeedback()
        context = QgsProcessingContext()

        try:
            # Langkah 1: Fix geometri dasar
            alg_params = {
                'INPUT': layer,
                'OUTPUT': 'memory:'
            }
            fixed = processing.run("native:fixgeometries", alg_params, context=context, feedback=feedback)['OUTPUT']

            # Langkah 2: Hapus vertex duplikat
            alg_params = {
                'INPUT': fixed,
                'TOLERANCE': 1e-8,
                'USE_Z_VALUE': False,
                'OUTPUT': 'memory:'
            }
            no_dup = processing.run("native:removeduplicatevertices", alg_params, context=context, feedback=feedback)['OUTPUT']

            # Langkah 3: Gunakan buffer(0) untuk perbaiki self-intersection & ring issues
            alg_params = {
                'INPUT': no_dup,
                'DISTANCE': 0,
                'SEGMENTS': 5,
                'END_CAP_STYLE': 0,  # Round
                'JOIN_STYLE': 0,     # Round
                'MITER_LIMIT': 2,
                'DISSOLVE': False,
                'OUTPUT': 'memory:'
            }
            clean = processing.run("native:buffer", alg_params, context=context, feedback=feedback)['OUTPUT']

            # Langkah 4: Simpan ke file
            alg_params = {
                'INPUT': clean,
                'OUTPUT': output_path
            }
            processing.run("native:savefeatures", alg_params, context=context, feedback=feedback)

            iface.messageBar().pushSuccess("Sukses", f"Geometri diperbaiki dan disimpan ke:\n{output_path}")
            # Opsional: tambahkan layer hasil ke peta
            iface.addVectorLayer(output_path, os.path.splitext(os.path.basename(output_path))[0], "ogr")

        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), "Error", f"Gagal memperbaiki geometri:\n{str(e)}")