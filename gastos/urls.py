from django.urls import path
from . import views, views_auth, views_pagos

urlpatterns = [
    # Autenticación
    path('login/', views_auth.login_view, name='login'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('registro/', views_auth.registro_view, name='registro'),

    # Planes y comercialización (público)
    path('planes/', views_auth.planes_precios, name='planes_precios'),

    # Gestión de familias
    path('familia/crear/', views_auth.crear_familia, name='crear_familia'),
    path('familia/seleccionar/', views_auth.seleccionar_familia, name='seleccionar_familia'),
    path('suscripcion/', views_auth.estado_suscripcion, name='estado_suscripcion'),

    # Pagos con QR
    path('suscripcion/pagar/', views_pagos.pagar_suscripcion, name='pagar_suscripcion'),
    path('suscripcion/generar-qr/<int:plan_id>/<str:metodo>/', views_pagos.generar_qr_pago, name='generar_qr_pago'),
    path('suscripcion/subir-comprobante/<int:pago_id>/', views_pagos.subir_comprobante, name='subir_comprobante'),
    path('suscripcion/estado/<int:pago_id>/', views_pagos.estado_pago, name='estado_pago'),
    path('suscripcion/mis-pagos/', views_pagos.mis_pagos, name='mis_pagos'),

    # Administración de pagos (staff)
    path('admin/verificar-pagos/', views_pagos.verificar_pagos, name='verificar_pagos'),
    path('admin/aprobar-pago/<int:pago_id>/', views_pagos.aprobar_pago_ajax, name='aprobar_pago_ajax'),
    path('admin/rechazar-pago/<int:pago_id>/', views_pagos.rechazar_pago_ajax, name='rechazar_pago_ajax'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Aportantes
    path('aportantes/', views.lista_aportantes, name='lista_aportantes'),
    path('aportantes/nuevo/', views.crear_aportante, name='crear_aportante'),
    path('aportantes/<int:pk>/editar/', views.editar_aportante, name='editar_aportante'),

    # Categorías
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nueva/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),

    # Subcategorías
    path('subcategorias/', views.lista_subcategorias, name='lista_subcategorias'),
    path('subcategorias/nueva/', views.crear_subcategoria, name='crear_subcategoria'),
    path('subcategorias/<int:pk>/editar/', views.editar_subcategoria, name='editar_subcategoria'),

    # Gastos
    path('gastos/', views.lista_gastos, name='lista_gastos'),
    path('gastos/nuevo/', views.crear_gasto, name='crear_gasto'),
    path('gastos/<int:pk>/', views.detalle_gasto, name='detalle_gasto'),
    path('gastos/<int:pk>/editar/', views.editar_gasto, name='editar_gasto'),

    # Reportes
    path('reportes/', views.reportes, name='reportes'),

    # Conciliación
    path('conciliacion/', views.conciliacion, name='conciliacion'),
    path('conciliacion/cerrar/', views.cerrar_conciliacion, name='cerrar_conciliacion'),
    path('conciliacion/confirmar/', views.confirmar_conciliacion, name='confirmar_conciliacion'),
    path('conciliacion/historial/', views.historial_conciliaciones, name='historial_conciliaciones'),
]

