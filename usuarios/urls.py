from django.urls import path
from .views import (
    RegistroView,
    LoginView,
    UsuarioCRUDView,
    ClienteView,
    ProveedorView,
    FacturaView,
    ExportarPDF,
    ImportarCSV,
    FacturasPorProveedorView,
    ImportarFacturasProveedoresCSV,
    NotificacionesView,
    ObtenerRolUsuarioView,
    EstadisticasDashboardView,
    FacturasVencidasCountView
)

urlpatterns = [
    # Registro y autenticación
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),

    # Gestión de usuarios
    path('', UsuarioCRUDView.as_view(), name='usuarios_crud'),
    path('<int:pk>/', UsuarioCRUDView.as_view(), name='usuario_crud_detail'),

    # Clientes y Proveedores
    path('clientes/', ClienteView.as_view(), name='clientes'),
    path('proveedores/', ProveedorView.as_view(), name='proveedores'),

    # Facturas
    path('facturas/', FacturaView.as_view(), name='facturas'),
    path('facturas/<int:pk>/', FacturaView.as_view(), name='factura_detail'),
    path('facturas/<int:pk>/pdf/', ExportarPDF.as_view(), name='exportar_pdf'),
    path('facturas/proveedores/', FacturasPorProveedorView.as_view(), name='facturas_proveedores'),
    path('facturas/proveedores/importar/', ImportarFacturasProveedoresCSV.as_view(), name='importar_facturas_proveedores'),

    # Importación y Notificaciones
    path('proveedores/importar/', ImportarCSV.as_view(), name='importar_csv'),
    path('notificaciones/', NotificacionesView.as_view(), name='notificaciones'),

    # Rol de usuario
    path('rol/', ObtenerRolUsuarioView.as_view(), name='obtener_rol_usuario'),
    path('dashboard/estadisticas/', EstadisticasDashboardView.as_view(), name='dashboard_estadisticas'),

    path('facturas/vencidas/count/', FacturasVencidasCountView.as_view(), name='facturas_vencidas_count'),

    
    
    

]
