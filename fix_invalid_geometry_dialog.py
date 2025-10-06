from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QFileDialog, QLineEdit, QHBoxLayout, QMessageBox
)
from qgis.core import QgsProject, QgsVectorLayer
from qgis.utils import iface

class FixInvalidGeometryDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fix Invalid Geometry – Simpan ke File Baru")
        self.resize(550, 180)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Layer selection
        layout.addWidget(QLabel("Pilih layer vektor:"))
        self.layer_combo = QComboBox()
        layout.addWidget(self.layer_combo)

        # Output file
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File output:"))
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Contoh: C:/data/hasil_fixed.gpkg")
        file_layout.addWidget(self.output_edit)

        self.btn_browse = QPushButton("Pilih File...")
        self.btn_browse.clicked.connect(self.browse_output)
        file_layout.addWidget(self.btn_browse)
        layout.addLayout(file_layout)

        # Tombol
        self.btn_ok = QPushButton("Perbaiki dan Simpan")
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)

        self.setLayout(layout)

    def showEvent(self, event):
        """Dipanggil setiap kali dialog ditampilkan → selalu refresh daftar layer"""
        super().showEvent(event)
        self.load_layers()

    def load_layers(self):
        self.layer_combo.clear()
        vector_layers = []

        for layer_id, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsVectorLayer) and layer.isValid():
                vector_layers.append((layer.name(), layer_id))

        if vector_layers:
            # Urutkan berdasarkan nama
            vector_layers.sort(key=lambda x: x[0])
            for name, lid in vector_layers:
                self.layer_combo.addItem(name, lid)
        else:
            self.layer_combo.addItem("Tidak ada layer vektor", None)
            self.layer_combo.setEnabled(False)
            self.btn_ok.setEnabled(False)
            return

        self.layer_combo.setEnabled(True)
        self.btn_ok.setEnabled(True)

    def selected_layer_id(self):
        return self.layer_combo.currentData()

    def output_path(self):
        return self.output_edit.text().strip()

    def browse_output(self):
        filters = (
            "GeoPackage (*.gpkg);;"
            "ESRI Shapefile (*.shp);;"
            "GeoJSON (*.geojson);;"
            "All files (*.*)"
        )
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Simpan Hasil Perbaikan Geometri",
            "",
            filters
        )
        if filename:
            # Tambahkan ekstensi jika belum ada
            lower = filename.lower()
            if not (lower.endswith('.gpkg') or lower.endswith('.shp') or lower.endswith('.geojson')):
                if 'GeoPackage' in selected_filter:
                    filename += '.gpkg'
                elif 'Shapefile' in selected_filter:
                    filename += '.shp'
                elif 'GeoJSON' in selected_filter:
                    filename += '.geojson'
                else:
                    filename += '.gpkg'
            self.output_edit.setText(filename)