from django.urls import path
from . import views, views_auth, views_pagos, views_gamificacion, views_chatbot, views_export

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

    # Invitaciones a familias
    path('familia/invitar/', views_auth.generar_invitacion_familia, name='generar_invitacion_familia'),
    path('familia/invitaciones/', views_auth.gestionar_invitaciones, name='gestionar_invitaciones'),
    path('familia/invitaciones/cancelar/<int:invitacion_id>/', views_auth.cancelar_invitacion, name='cancelar_invitacion'),
    path('familia/unirse/', views_auth.unirse_familia, name='unirse_familia'),
    path('familia/unirse/<str:codigo>/', views_auth.unirse_familia, name='unirse_familia_codigo'),

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

    # Página de inicio - redirige al login
    path('', views_auth.inicio, name='inicio'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/exportar-pdf/', views_export.exportar_dashboard_pdf, name='exportar_dashboard_pdf'),
    path('dashboard/exportar-excel/', views_export.exportar_dashboard_excel, name='exportar_dashboard_excel'),

    # Chatbot IA
    path('chatbot/', views_chatbot.chatbot_dashboard, name='chatbot_dashboard'),
    path('chatbot/conversacion/', views_chatbot.chatbot_conversacion, name='chatbot_nueva_conversacion'),
    path('chatbot/conversacion/<int:conversacion_id>/', views_chatbot.chatbot_conversacion, name='chatbot_conversacion'),
    path('chatbot/enviar/', views_chatbot.chatbot_enviar_mensaje, name='chatbot_enviar_mensaje'),
    path('chatbot/generar-analisis/', views_chatbot.chatbot_generar_analisis, name='chatbot_generar_analisis'),
    path('chatbot/generar-prediccion/', views_chatbot.chatbot_generar_prediccion, name='chatbot_generar_prediccion'),
    path('chatbot/cerrar/<int:conversacion_id>/', views_chatbot.chatbot_cerrar_conversacion, name='chatbot_cerrar_conversacion'),
    path('chatbot/historial/', views_chatbot.chatbot_historial, name='chatbot_historial'),

    # Gamificación
    path('gamificacion/', views_gamificacion.dashboard_gamificacion, name='gamificacion_dashboard'),
    path('gamificacion/logros/', views_gamificacion.logros_lista, name='logros_lista'),
    path('gamificacion/ranking/', views_gamificacion.ranking_general, name='ranking_general'),
    path('gamificacion/notificaciones/', views_gamificacion.notificaciones_logros, name='notificaciones_logros'),
    path('gamificacion/estadisticas/', views_gamificacion.estadisticas_usuario, name='estadisticas_usuario'),
    path('gamificacion/verificar-logros/', views_gamificacion.verificar_logros_ajax, name='verificar_logros_ajax'),

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

    # Metas de Ahorro
    path('metas/', views.lista_metas, name='lista_metas'),
    path('metas/crear/', views.crear_meta, name='crear_meta'),
    path('metas/<int:pk>/', views.detalle_meta, name='detalle_meta'),
    path('metas/<int:pk>/editar/', views.editar_meta, name='editar_meta'),
    path('metas/<int:pk>/agregar-ahorro/', views.agregar_ahorro, name='agregar_ahorro'),
    path('metas/<int:pk>/cambiar-estado/', views.cambiar_estado_meta, name='cambiar_estado_meta'),
    path('metas/<int:pk>/eliminar/', views.eliminar_meta, name='eliminar_meta'),

    # Onboarding
    path('marcar-onboarding-completado/', views.marcar_onboarding_completado, name='marcar_onboarding_completado'),
]
