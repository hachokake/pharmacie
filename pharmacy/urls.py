from django.urls import path
from . import views
from .migrate_view import run_migrations

app_name = 'pharmacy'

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-home/', views.admin_home, name='admin_home'),
    path('setup-database-migrations-2026/', run_migrations, name='run_migrations'),  # Route temporaire pour migrations
    path('create-first-admin/', views.create_first_admin, name='create_first_admin'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Médicaments
    path('medicaments/', views.liste_medicaments, name='liste_medicaments'),
    path('medicaments/ajouter/', views.ajouter_medicament, name='ajouter_medicament'),
    path('medicaments/verifier-code/', views.verifier_code_medicament, name='verifier_code_medicament'),
    path('medicaments/ajuster-stock/', views.ajuster_stock_medicament, name='ajuster_stock_medicament'),
    path('medicaments/<int:medicament_id>/', views.detail_medicament, name='detail_medicament'),
    path('medicaments/<int:medicament_id>/modifier/', views.modifier_medicament, name='modifier_medicament'),
    path('medicaments/<int:medicament_id>/supprimer/', views.supprimer_medicament, name='supprimer_medicament'),
    
    # Catégories
    path('categories/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
    
    # Clients
    path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),
    
    # Stock et ventes
    path('stock-alerte/', views.stock_alerte, name='stock_alerte'),
    path('ventes/', views.liste_ventes, name='liste_ventes'),
    path('ventes/creer/', views.creer_vente, name='creer_vente'),
    path('ventes/<int:vente_id>/', views.detail_vente, name='detail_vente'),
    path('ventes/<int:vente_id>/supprimer/', views.supprimer_vente, name='supprimer_vente'),
    
    # Administration personnalisée
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.admin_users_list, name='admin_users_list'),
    path('admin-users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin-users/<int:user_id>/toggle-status/', views.admin_user_toggle_status, name='admin_user_toggle_status'),
    path('admin-users/<int:user_id>/toggle-staff/', views.admin_user_toggle_staff, name='admin_user_toggle_staff'),
    path('admin-users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin-activities/', views.admin_activities, name='admin_activities'),
    path('admin-stock-by-user/', views.admin_stock_by_user, name='admin_stock_by_user'),
    path('admin-chiffres-affaires/', views.admin_chiffres_affaires, name='admin_chiffres_affaires'),
    path('creer-investissement/', views.creer_investissement, name='creer_investissement'),
    
    # Cartes d'employés (Admin)
    path('admin-cartes/', views.admin_cartes_liste, name='admin_cartes_liste'),
    path('admin-cartes/rechercher/', views.admin_carte_rechercher, name='admin_carte_rechercher'),
    path('admin-cartes/creer/', views.admin_carte_creer, name='admin_carte_creer'),
    path('admin-cartes/<int:carte_id>/', views.admin_carte_detail, name='admin_carte_detail'),
    path('admin-cartes/<int:carte_id>/modifier/', views.admin_carte_modifier, name='admin_carte_modifier'),
    path('admin-cartes/<int:carte_id>/supprimer/', views.admin_carte_supprimer, name='admin_carte_supprimer'),
    path('admin-cartes/<int:carte_id>/imprimer/', views.admin_carte_imprimer, name='admin_carte_imprimer'),
    path('admin-cartes/<int:carte_id>/regenerer-qr/', views.admin_carte_regenerer_qr, name='admin_carte_regenerer_qr'),
    
    # Ma Carte de Service (Utilisateur)
    path('ma-carte/', views.ma_carte_detail, name='ma_carte_detail'),
    path('ma-carte/imprimer/', views.ma_carte_imprimer, name='ma_carte_imprimer'),
    
    # Téléchargement de l'application
    path('telecharger/', views.telecharger_app, name='telecharger_app'),
]
