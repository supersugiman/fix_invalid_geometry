def classFactory(iface):
    from .fix_invalid_geometry import FixInvalidGeometryPlugin
    return FixInvalidGeometryPlugin(iface)