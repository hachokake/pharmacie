from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.dateparse import parse_date
from datetime import timedelta, date
from decimal import Decimal
from .models import Medicament, Vente, ItemVente, Client, Categorie, ActivityLog, CarteEmploye
from .forms import MedicamentForm, CategorieForm, ClientForm, VenteForm, ItemVenteForm


# Fonction utilitaire pour enregistrer les activités
def log_activity(user, action, description, model_name='', object_id=None, ip_address=None):
    """Enregistre une activité utilisateur"""
    ActivityLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
        ip_address=ip_address
    )


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def home(request):
    """Page d'accueil publique"""
    if request.user.is_authenticated:
        return redirect('pharmacy:dashboard')
    return render(request, 'pharmacy/home.html')


def admin_home(request):
    """Page d'accueil pour les administrateurs"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('pharmacy:admin_dashboard')
        else:
            return redirect('pharmacy:dashboard')
    
    # Vérifier s'il existe au moins un administrateur
    try:
        admin_exists = User.objects.filter(is_staff=True).exists()
    except Exception as e:
        # Si la table n'existe pas encore (première migration en cours)
        admin_exists = False
    
    context = {
        'admin_exists': admin_exists,
    }
    
    return render(request, 'pharmacy/admin_home.html', context)


def create_first_admin(request):
    """Créer le premier compte administrateur"""
    # Vérifier si un admin existe déjà
    if User.objects.filter(is_staff=True).exists():
        messages.warning(request, 'Un compte administrateur existe déjà.')
        return redirect('pharmacy:admin_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
        elif password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif len(password1) < 8:
            messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
        else:
            # Créer le super administrateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            # Enregistrer l'activité
            log_activity(
                user,
                'CREATE',
                f'Création du premier compte administrateur: {username}',
                model_name='User',
                object_id=user.id,
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, f'Compte administrateur créé avec succès pour {username}! Vous pouvez maintenant vous connecter.')
            return redirect('pharmacy:login')
    
    return render(request, 'pharmacy/create_first_admin.html')


def register(request):
    """Page d'inscription pour les nouveaux utilisateurs"""
    if request.user.is_authenticated:
        return redirect('pharmacy:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
        elif password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif len(password1) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
        else:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, f'Compte créé avec succès pour {username}! Vous pouvez maintenant vous connecter.')
            return redirect('pharmacy:login')
    
    return render(request, 'pharmacy/register.html')


def user_login(request):
    """Page de connexion pour les utilisateurs"""
    if request.user.is_authenticated:
        return redirect('pharmacy:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            log_activity(user, 'LOGIN', f'Connexion de {username}', ip_address=get_client_ip(request))
            messages.success(request, 'Connexion réussie!')
            
            # Rediriger les administrateurs vers l'admin personnalisé
            if user.is_staff:
                return redirect('pharmacy:admin_dashboard')
            else:
                return redirect('pharmacy:dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'pharmacy/login.html')


def user_logout(request):
    """Déconnexion de l'utilisateur"""
    if request.user.is_authenticated:
        log_activity(request.user, 'LOGOUT', f'Déconnexion de {request.user.username}', ip_address=get_client_ip(request))
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('pharmacy:home')


@login_required
def dashboard(request):
    """Page d'accueil avec statistiques"""
    # Statistiques générales (filtrées par utilisateur si non-admin)
    if request.user.is_staff:
        medicaments_queryset = Medicament.objects.all()
    else:
        medicaments_queryset = Medicament.objects.filter(created_by=request.user)
    
    total_medicaments = medicaments_queryset.count()
    medicaments_en_rupture = medicaments_queryset.filter(quantite_stock=0).count()
    medicaments_alerte = medicaments_queryset.filter(
        quantite_stock__gt=0,
        quantite_stock__lte=F('seuil_alerte')
    ).count()
    
    # Médicaments expirés ou proche expiration (30 jours)
    date_limite = timezone.now().date() + timedelta(days=30)
    medicaments_expires = medicaments_queryset.filter(date_expiration__lte=timezone.now().date()).count()
    medicaments_proche_expiration = medicaments_queryset.filter(
        date_expiration__gt=timezone.now().date(),
        date_expiration__lte=date_limite
    ).count()
    
    # Ventes du jour (filtrées par utilisateur si non-admin)
    aujourd_hui = timezone.now().date()
    if request.user.is_staff:
        ventes_jour = Vente.objects.filter(date_vente__date=aujourd_hui)
    else:
        ventes_jour = Vente.objects.filter(date_vente__date=aujourd_hui, vendeur=request.user)
    
    total_ventes_jour = ventes_jour.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    nombre_ventes_jour = ventes_jour.count()
    
    # Ventes du mois (filtrées par utilisateur si non-admin)
    debut_mois = aujourd_hui.replace(day=1)
    if request.user.is_staff:
        ventes_mois = Vente.objects.filter(date_vente__date__gte=debut_mois)
    else:
        ventes_mois = Vente.objects.filter(date_vente__date__gte=debut_mois, vendeur=request.user)
    
    total_ventes_mois = ventes_mois.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    # Top 5 médicaments les plus vendus (filtrés par utilisateur si non-admin)
    if request.user.is_staff:
        top_medicaments = ItemVente.objects.values('medicament__nom').annotate(
            total_vendu=Sum('quantite')
        ).order_by('-total_vendu')[:5]
    else:
        top_medicaments = ItemVente.objects.filter(vente__vendeur=request.user).values('medicament__nom').annotate(
            total_vendu=Sum('quantite')
        ).order_by('-total_vendu')[:5]
    
    # Statistiques par utilisateur (tous les vendeurs) - Visible uniquement pour admin
    if request.user.is_staff:
        users_stats = User.objects.filter(is_active=True).annotate(
            nb_ventes=Count('ventes'),
            montant_total=Sum('ventes__montant_total'),
            nb_medicaments_vendus=Sum('ventes__items__quantite'),
            derniere_vente=Count('ventes', filter=Q(ventes__date_vente__date=aujourd_hui))
        ).order_by('-montant_total')
    else:
        users_stats = None
    
    # Activités récentes (filtrées par utilisateur si non-admin)
    if request.user.is_staff:
        activites_recentes = ActivityLog.objects.select_related('user').all().order_by('-timestamp')[:10]
    else:
        activites_recentes = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:10]
    
    # Mes statistiques personnelles (pour les utilisateurs non-admin)
    if not request.user.is_staff:
        mes_ventes_jour = nombre_ventes_jour
        mon_montant_jour = total_ventes_jour
        mes_ventes_mois = ventes_mois.count()
        mon_montant_mois = total_ventes_mois
    else:
        mes_ventes_jour = ventes_jour.filter(vendeur=request.user).count()
        mon_montant_jour = ventes_jour.filter(vendeur=request.user).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        mes_ventes_mois = ventes_mois.filter(vendeur=request.user).count()
        mon_montant_mois = ventes_mois.filter(vendeur=request.user).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    # Ma carte de service
    try:
        ma_carte = CarteEmploye.objects.get(utilisateur=request.user)
    except CarteEmploye.DoesNotExist:
        ma_carte = None
    
    context = {
        'total_medicaments': total_medicaments,
        'medicaments_en_rupture': medicaments_en_rupture,
        'medicaments_alerte': medicaments_alerte,
        'medicaments_expires': medicaments_expires,
        'medicaments_proche_expiration': medicaments_proche_expiration,
        'total_ventes_jour': total_ventes_jour,
        'nombre_ventes_jour': nombre_ventes_jour,
        'total_ventes_mois': total_ventes_mois,
        'top_medicaments': top_medicaments,
        'users_stats': users_stats,
        'activites_recentes': activites_recentes,
        'mes_ventes_jour': mes_ventes_jour,
        'mon_montant_jour': mon_montant_jour,
        'mes_ventes_mois': mes_ventes_mois,
        'mon_montant_mois': mon_montant_mois,
        'ma_carte': ma_carte,
    }
    
    return render(request, 'pharmacy/dashboard.html', context)


@login_required
def liste_medicaments(request):
    """Liste tous les médicaments avec recherche"""
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie', '')
    user_filter = request.GET.get('user', '')
    
    medicaments = Medicament.objects.select_related('created_by', 'categorie').all()
    
    # Filtrer par utilisateur : chaque utilisateur ne voit que ses médicaments (sauf admin)
    if not request.user.is_staff:
        medicaments = medicaments.filter(created_by=request.user)
    
    if query:
        medicaments = medicaments.filter(
            Q(nom__icontains=query) |
            Q(fabricant__icontains=query) |
            Q(code_barre__icontains=query)
        )
    
    if categorie_id:
        medicaments = medicaments.filter(categorie_id=categorie_id)
    
    if user_filter:
        medicaments = medicaments.filter(created_by_id=user_filter)
    
    categories = Categorie.objects.all()
    
    # Statistiques par utilisateur pour les admins
    users_medicaments_stats = None
    all_users = None
    if request.user.is_staff:
        users_medicaments_stats = User.objects.annotate(
            nb_medicaments=Count('medicaments_crees'),
            valeur_stock=Sum(F('medicaments_crees__quantite_stock') * F('medicaments_crees__prix_unitaire'))
        ).filter(nb_medicaments__gt=0).order_by('-nb_medicaments')
        all_users = User.objects.filter(is_active=True).order_by('username')
    
    context = {
        'medicaments': medicaments,
        'categories': categories,
        'query': query,
        'categorie_id': categorie_id,
        'user_filter': user_filter,
        'users_medicaments_stats': users_medicaments_stats,
        'all_users': all_users,
    }
    
    return render(request, 'pharmacy/liste_medicaments.html', context)


@login_required
def stock_alerte(request):
    """Liste des médicaments en rupture ou avec stock faible"""
    # Filtrer par utilisateur (sauf admin)
    if request.user.is_staff:
        medicaments_queryset = Medicament.objects.all()
    else:
        medicaments_queryset = Medicament.objects.filter(created_by=request.user)
    
    medicaments_rupture = medicaments_queryset.filter(quantite_stock=0)
    medicaments_alerte = medicaments_queryset.filter(
        quantite_stock__gt=0,
        quantite_stock__lte=F('seuil_alerte')
    )
    
    context = {
        'medicaments_rupture': medicaments_rupture,
        'medicaments_alerte': medicaments_alerte,
    }
    
    return render(request, 'pharmacy/stock_alerte.html', context)


@login_required
def liste_ventes(request):
    """Liste toutes les ventes"""
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    
    # Filtrer les ventes par utilisateur (sauf admin)
    if request.user.is_staff:
        ventes = Vente.objects.all()
    else:
        ventes = Vente.objects.filter(vendeur=request.user)
    
    if date_debut:
        ventes = ventes.filter(date_vente__date__gte=date_debut)
    
    if date_fin:
        ventes = ventes.filter(date_vente__date__lte=date_fin)
    
    context = {
        'ventes': ventes,
        'date_debut': date_debut,
        'date_fin': date_fin,
    }
    
    return render(request, 'pharmacy/liste_ventes.html', context)


@login_required
def detail_vente(request, vente_id):
    """Détail d'une vente"""
    # Vérifier que la vente appartient à l'utilisateur (sauf admin)
    if request.user.is_staff:
        vente = get_object_or_404(Vente, id=vente_id)
    else:
        vente = get_object_or_404(Vente, id=vente_id, vendeur=request.user)
    
    items = vente.items.all()
    
    context = {
        'vente': vente,
        'items': items,
    }
    
    return render(request, 'pharmacy/detail_vente.html', context)


@login_required
def ajouter_medicament(request):
    """Ajouter un nouveau médicament"""
    if request.method == 'POST':
        form = MedicamentForm(request.POST)
        if form.is_valid():
            medicament = form.save(commit=False)
            medicament.created_by = request.user
            medicament.save()
            log_activity(
                request.user,
                'CREATE',
                f'Médicament "{medicament.nom}" ajouté',
                model_name='Medicament',
                object_id=medicament.id,
                ip_address=get_client_ip(request)
            )
            messages.success(request, f'Le médicament "{medicament.nom}" a été ajouté avec succès!')
            return redirect('pharmacy:liste_medicaments')
        else:
            messages.error(request, 'Erreur lors de l\'ajout du médicament. Veuillez vérifier les informations.')
    else:
        form = MedicamentForm()
    
    context = {
        'form': form,
        'titre': 'Ajouter un médicament',
        'action': 'Ajouter',
    }
    
    return render(request, 'pharmacy/medicament_form.html', context)


@login_required
def verifier_code_medicament(request):
    """Vérifier si un code-barres/QR existe déjà (AJAX)"""
    from django.http import JsonResponse
    
    code = request.GET.get('code', '').strip()
    
    if not code:
        return JsonResponse({'existe': False})
    
    try:
        medicament = Medicament.objects.get(code_barre=code)
        return JsonResponse({
            'existe': True,
            'medicament': {
                'id': medicament.id,
                'nom': medicament.nom,
                'quantite_stock': medicament.quantite_stock,
                'prix_unitaire': str(medicament.prix_unitaire),
                'categorie': medicament.categorie.nom if medicament.categorie else 'Non définie',
            }
        })
    except Medicament.DoesNotExist:
        return JsonResponse({'existe': False})


@login_required
def ajuster_stock_medicament(request):
    """Ajuster le stock d'un médicament (ajouter ou retirer) via AJAX"""
    from django.http import JsonResponse
    import json
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})
    
    try:
        data = json.loads(request.body)
        medicament_id = data.get('medicament_id')
        action_type = data.get('action_type')
        quantite = int(data.get('quantite', 0))
        motif = data.get('motif', '')
        
        if not medicament_id or not action_type or quantite <= 0:
            return JsonResponse({'success': False, 'message': 'Données invalides'})
        
        medicament = Medicament.objects.get(id=medicament_id)
        ancien_stock = medicament.quantite_stock
        
        if action_type == 'ajouter':
            medicament.quantite_stock += quantite
            action_desc = f'Ajout de {quantite} unités'
        elif action_type == 'retirer':
            if medicament.quantite_stock < quantite:
                return JsonResponse({
                    'success': False, 
                    'message': f'Stock insuffisant. Stock actuel: {medicament.quantite_stock} unités'
                })
            medicament.quantite_stock -= quantite
            action_desc = f'Retrait de {quantite} unités'
        else:
            return JsonResponse({'success': False, 'message': 'Action non reconnue'})
        
        medicament.save()
        
        # Log de l'activité
        log_activity(
            request.user,
            'UPDATE',
            f'{action_desc} pour "{medicament.nom}" (Stock: {ancien_stock} → {medicament.quantite_stock}). Motif: {motif or "Non spécifié"}',
            model_name='Medicament',
            object_id=medicament.id,
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Stock mis à jour avec succès! Nouveau stock: {medicament.quantite_stock} unités',
            'nouveau_stock': medicament.quantite_stock
        })
        
    except Medicament.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Médicament non trouvé'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'})


@login_required
def modifier_medicament(request, medicament_id):
    """Modifier un médicament existant"""
    # Vérifier que le médicament appartient à l'utilisateur (sauf admin)
    if request.user.is_staff:
        medicament = get_object_or_404(Medicament, id=medicament_id)
    else:
        medicament = get_object_or_404(Medicament, id=medicament_id, created_by=request.user)
    
    if request.method == 'POST':
        form = MedicamentForm(request.POST, instance=medicament)
        if form.is_valid():
            medicament = form.save()
            log_activity(
                request.user,
                'UPDATE',
                f'Médicament "{medicament.nom}" modifié',
                model_name='Medicament',
                object_id=medicament.id,
                ip_address=get_client_ip(request)
            )
            messages.success(request, f'Le médicament "{medicament.nom}" a été modifié avec succès!')
            return redirect('pharmacy:liste_medicaments')
        else:
            messages.error(request, 'Erreur lors de la modification du médicament.')
    else:
        form = MedicamentForm(instance=medicament)
    
    context = {
        'form': form,
        'medicament': medicament,
        'titre': 'Modifier le médicament',
        'action': 'Modifier',
    }
    
    return render(request, 'pharmacy/medicament_form.html', context)


@login_required
def supprimer_medicament(request, medicament_id):
    """Supprimer un médicament"""
    # Vérifier que le médicament appartient à l'utilisateur (sauf admin)
    if request.user.is_staff:
        medicament = get_object_or_404(Medicament, id=medicament_id)
    else:
        medicament = get_object_or_404(Medicament, id=medicament_id, created_by=request.user)
    
    if request.method == 'POST':
        nom = medicament.nom
        medicament.delete()
        log_activity(
            request.user,
            'DELETE',
            f'Médicament "{nom}" supprimé',
            model_name='Medicament',
            object_id=medicament_id,
            ip_address=get_client_ip(request)
        )
        messages.success(request, f'Le médicament "{nom}" a été supprimé avec succès!')
        return redirect('pharmacy:liste_medicaments')
    
    context = {
        'medicament': medicament,
    }
    
    return render(request, 'pharmacy/medicament_confirm_delete.html', context)


@login_required
def detail_medicament(request, medicament_id):
    """Afficher les détails d'un médicament"""
    # Vérifier que le médicament appartient à l'utilisateur (sauf admin)
    if request.user.is_staff:
        medicament = get_object_or_404(Medicament, id=medicament_id)
    else:
        medicament = get_object_or_404(Medicament, id=medicament_id, created_by=request.user)
    
    context = {
        'medicament': medicament,
    }
    
    return render(request, 'pharmacy/detail_medicament.html', context)


@login_required
def ajouter_categorie(request):
    """Ajouter une nouvelle catégorie"""
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            categorie = form.save()
            messages.success(request, f'La catégorie "{categorie.nom}" a été ajoutée avec succès!')
            return redirect('pharmacy:liste_medicaments')
        else:
            messages.error(request, 'Erreur lors de l\'ajout de la catégorie.')
    else:
        form = CategorieForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'pharmacy/categorie_form.html', context)


@login_required
def ajouter_client(request):
    """Ajouter un nouveau client"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Le client "{client.nom} {client.prenom}" a été ajouté avec succès!')
            return redirect('pharmacy:creer_vente')
        else:
            messages.error(request, 'Erreur lors de l\'ajout du client.')
    else:
        form = ClientForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'pharmacy/client_form.html', context)


@login_required
def creer_vente(request):
    """Créer une nouvelle vente avec plusieurs médicaments"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        client_id = request.POST.get('client')
        methode_paiement = request.POST.get('methode_paiement')
        remarques = request.POST.get('remarques', '')
        
        # Récupérer les médicaments et quantités
        medicaments_ids = request.POST.getlist('medicament[]')
        quantites = request.POST.getlist('quantite[]')
        
        if not medicaments_ids or not any(quantites):
            messages.error(request, 'Veuillez ajouter au moins un médicament à la vente.')
            return redirect('pharmacy:creer_vente')
        
        # Créer la vente
        vente = Vente.objects.create(
            client_id=client_id if client_id else None,
            methode_paiement=methode_paiement,
            remarques=remarques,
            vendeur=request.user,
            montant_total=0
        )
        
        montant_total = Decimal('0.00')
        
        # Ajouter les items à la vente
        for i, med_id in enumerate(medicaments_ids):
            if med_id and quantites[i]:
                try:
                    # Vérifier que le médicament appartient à l'utilisateur (sauf admin)
                    if request.user.is_staff:
                        medicament = Medicament.objects.get(id=med_id)
                    else:
                        medicament = Medicament.objects.get(id=med_id, created_by=request.user)
                    
                    quantite = int(quantites[i])
                    
                    # Vérifier le stock
                    if quantite > medicament.quantite_stock:
                        messages.warning(request, f'Stock insuffisant pour {medicament.nom}. Stock disponible: {medicament.quantite_stock}')
                        continue
                    
                    # Créer l'item de vente
                    prix_unitaire = medicament.prix_unitaire
                    sous_total = prix_unitaire * quantite
                    
                    ItemVente.objects.create(
                        vente=vente,
                        medicament=medicament,
                        quantite=quantite,
                        prix_unitaire=prix_unitaire,
                        sous_total=sous_total
                    )
                    
                    # Mettre à jour le stock
                    medicament.quantite_stock -= quantite
                    medicament.save()
                    
                    montant_total += sous_total
                    
                except Medicament.DoesNotExist:
                    continue
        
        # Mettre à jour le montant total de la vente
        vente.montant_total = montant_total
        vente.save()
        
        # Enregistrer l'activité
        log_activity(
            request.user,
            'VENTE',
            f'Vente #{vente.id} créée - Montant: {montant_total} FCFA',
            model_name='Vente',
            object_id=vente.id,
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, f'Vente créée avec succès! Montant total: {montant_total} FCFA')
        return redirect('pharmacy:detail_vente', vente_id=vente.id)
    
    # GET request
    # Filtrer les médicaments par utilisateur (sauf admin)
    if request.user.is_staff:
        medicaments = Medicament.objects.filter(quantite_stock__gt=0).order_by('nom')
    else:
        medicaments = Medicament.objects.filter(created_by=request.user, quantite_stock__gt=0).order_by('nom')
    
    clients = Client.objects.all().order_by('nom')
    
    context = {
        'medicaments': medicaments,
        'clients': clients,
        'methodes_paiement': Vente.METHODE_PAIEMENT_CHOICES,
    }
    
    return render(request, 'pharmacy/creer_vente.html', context)


@login_required
def supprimer_vente(request, vente_id):
    """Supprimer une vente et restaurer le stock"""
    # Vérifier que la vente appartient à l'utilisateur (sauf admin)
    if request.user.is_staff:
        vente = get_object_or_404(Vente, id=vente_id)
    else:
        vente = get_object_or_404(Vente, id=vente_id, vendeur=request.user)
    
    if request.method == 'POST':
        # Restaurer le stock des médicaments
        for item in vente.items.all():
            medicament = item.medicament
            medicament.quantite_stock += item.quantite
            medicament.save()
        
        vente_ref = f"Vente #{vente.id}"
        vente.delete()
        messages.success(request, f'{vente_ref} a été supprimée et le stock a été restauré.')
        return redirect('pharmacy:liste_ventes')
    
    context = {
        'vente': vente,
    }
    
    return render(request, 'pharmacy/vente_confirm_delete.html', context)


# ==================== ADMINISTRATION PERSONNALISÉE ====================

@login_required
def admin_dashboard(request):
    """Tableau de bord de l'administration personnalisée"""
    # Vérifier que l'utilisateur est un administrateur
    if not request.user.is_staff:
        messages.error(request, 'Vous n\'avez pas accès à cette page.')
        return redirect('pharmacy:dashboard')
    
    # Statistiques générales
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = User.objects.filter(is_staff=True).count()
    
    # Statistiques d'activité
    today = timezone.now().date()
    activities_today = ActivityLog.objects.filter(timestamp__date=today).count()
    logins_today = ActivityLog.objects.filter(timestamp__date=today, action='LOGIN').count()
    
    # Statistiques de ventes par utilisateur
    ventes_stats = Vente.objects.values('vendeur__id', 'vendeur__username', 'vendeur__first_name', 'vendeur__last_name').annotate(
        total_ventes=Count('id'),
        montant_total=Sum('montant_total')
    ).order_by('-montant_total')[:10]
    
    # Statistiques globales
    total_medicaments = Medicament.objects.count()
    total_ventes = Vente.objects.count()
    total_clients = Client.objects.count()
    
    # Activités récentes
    recent_activities = ActivityLog.objects.select_related('user').all()[:20]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'activities_today': activities_today,
        'logins_today': logins_today,
        'ventes_stats': ventes_stats,
        'total_medicaments': total_medicaments,
        'total_ventes': total_ventes,
        'total_clients': total_clients,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'pharmacy/admin_dashboard.html', context)


@login_required
def admin_users_list(request):
    """Liste de tous les utilisateurs pour l'administration"""
    if not request.user.is_staff:
        messages.error(request, 'Vous n\'avez pas accès à cette page.')
        return redirect('pharmacy:dashboard')
    
    # Filtres de recherche
    search = request.GET.get('search', '')
    is_active = request.GET.get('is_active', '')
    is_staff = request.GET.get('is_staff', '')
    
    users = User.objects.all()
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    if is_active:
        users = users.filter(is_active=(is_active == 'true'))
    
    if is_staff:
        users = users.filter(is_staff=(is_staff == 'true'))
    
    # Annoter avec statistiques
    users = users.annotate(
        total_ventes=Count('ventes'),
        montant_ventes=Sum('ventes__montant_total'),
        total_activities=Count('activities')
    ).order_by('-date_joined')
    
    context = {
        'users': users,
        'search': search,
        'is_active': is_active,
        'is_staff': is_staff,
    }
    
    return render(request, 'pharmacy/admin_users_list.html', context)


@login_required
def admin_user_detail(request, user_id):
    """Détails d'un utilisateur pour l'administration"""
    if not request.user.is_staff:
        messages.error(request, 'Vous n\'avez pas accès à cette page.')
        return redirect('pharmacy:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    # Statistiques de l'utilisateur
    total_ventes = user.ventes.count()
    montant_total_ventes = user.ventes.aggregate(total=Sum('montant_total'))['total'] or 0
    
    # Ventes de l'utilisateur
    ventes = user.ventes.all().order_by('-date_vente')[:10]
    
    # Médicaments ajoutés par cet utilisateur
    medicaments = user.medicaments_crees.select_related('categorie').all()
    
    # Ajouter la valeur du stock pour chaque médicament
    for med in medicaments:
        med.valeur_stock = med.prix_unitaire * med.quantite_stock
    
    # Statistiques des médicaments
    total_medicaments = medicaments.count()
    valeur_stock_total = medicaments.aggregate(
        valeur=Sum(F('quantite_stock') * F('prix_unitaire'))
    )['valeur'] or 0
    medicaments_rupture = medicaments.filter(quantite_stock=0).count()
    medicaments_alerte = medicaments.filter(
        quantite_stock__gt=0,
        quantite_stock__lte=F('seuil_alerte')
    ).count()
    
    # Activités récentes
    activities = user.activities.all().order_by('-timestamp')[:50]
    
    # Statistiques d'activité par type
    activity_stats = user.activities.values('action').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'user_detail': user,
        'total_ventes': total_ventes,
        'montant_total_ventes': montant_total_ventes,
        'ventes': ventes,
        'medicaments': medicaments,
        'total_medicaments': total_medicaments,
        'valeur_stock_total': valeur_stock_total,
        'medicaments_rupture': medicaments_rupture,
        'medicaments_alerte': medicaments_alerte,
        'activities': activities,
        'activity_stats': activity_stats,
        'today': date.today(),
    }
    
    return render(request, 'pharmacy/admin_user_detail.html', context)


@login_required
def admin_user_toggle_status(request, user_id):
    """Activer/Désactiver un utilisateur"""
    if not request.user.is_staff:
        messages.error(request, 'Vous n\'avez pas accès à cette action.')
        return redirect('pharmacy:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    # Empêcher la désactivation du propre compte admin
    if user.id == request.user.id:
        messages.error(request, 'Vous ne pouvez pas désactiver votre propre compte.')
        return redirect('pharmacy:admin_user_detail', user_id=user_id)
    
    user.is_active = not user.is_active
    user.save()
    
    status = "activé" if user.is_active else "désactivé"
    log_activity(
        request.user,
        'UPDATE',
        f'Compte de {user.username} {status}',
        model_name='User',
        object_id=user.id,
        ip_address=get_client_ip(request)
    )
    
    messages.success(request, f'Le compte de {user.username} a été {status}.')
    return redirect('pharmacy:admin_user_detail', user_id=user_id)


@login_required
def admin_user_toggle_staff(request, user_id):
    """Promouvoir/Rétrograder un utilisateur en tant qu'admin"""
    if not request.user.is_staff or not request.user.is_superuser:
        messages.error(request, 'Seul un super administrateur peut effectuer cette action.')
        return redirect('pharmacy:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    # Empêcher la modification du propre statut
    if user.id == request.user.id:
        messages.error(request, 'Vous ne pouvez pas modifier votre propre statut d\'administrateur.')
        return redirect('pharmacy:admin_user_detail', user_id=user_id)
    
    user.is_staff = not user.is_staff
    user.save()
    
    status = "administrateur" if user.is_staff else "utilisateur normal"
    log_activity(
        request.user,
        'UPDATE',
        f'{user.username} est maintenant {status}',
        model_name='User',
        object_id=user.id,
        ip_address=get_client_ip(request)
    )
    
    messages.success(request, f'{user.username} est maintenant {status}.')
    return redirect('pharmacy:admin_user_detail', user_id=user_id)


@login_required
def admin_user_delete(request, user_id):
    """Supprimer un utilisateur"""
    if not request.user.is_staff or not request.user.is_superuser:
        messages.error(request, 'Seul un super administrateur peut supprimer des utilisateurs.')
        return redirect('pharmacy:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    # Empêcher la suppression du propre compte
    if user.id == request.user.id:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('pharmacy:admin_user_detail', user_id=user_id)
    
    if request.method == 'POST':
        username = user.username
        log_activity(
            request.user,
            'DELETE',
            f'Suppression du compte de {username}',
            model_name='User',
            object_id=user.id,
            ip_address=get_client_ip(request)
        )
        user.delete()
        messages.success(request, f'Le compte de {username} a été supprimé.')
        return redirect('pharmacy:admin_users_list')
    
    context = {
        'user_to_delete': user,
    }
    
    return render(request, 'pharmacy/admin_user_delete.html', context)


@login_required
def admin_activities(request):
    """Journal d'activités de tous les utilisateurs"""
    if not request.user.is_staff:
        messages.error(request, 'Vous n\'avez pas accès à cette page.')
        return redirect('pharmacy:dashboard')
    
    # Filtres
    user_id = request.GET.get('user', '')
    action = request.GET.get('action', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    activities = ActivityLog.objects.select_related('user').all()
    
    if user_id:
        activities = activities.filter(user_id=user_id)
    
    if action:
        activities = activities.filter(action=action)
    
    if date_from:
        activities = activities.filter(timestamp__date__gte=date_from)
    
    if date_to:
        activities = activities.filter(timestamp__date__lte=date_to)
    
    activities = activities.order_by('-timestamp')[:200]
    
    # Liste des utilisateurs pour le filtre
    users = User.objects.all().order_by('username')
    
    context = {
        'activities': activities,
        'users': users,
        'action_choices': ActivityLog.ACTION_CHOICES,
        'selected_user': user_id,
        'selected_action': action,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'pharmacy/admin_activities.html', context)


@login_required
def admin_stock_by_user(request):
    """Voir les stocks gérés par chaque utilisateur"""
    if not request.user.is_staff:
        messages.error(request, 'Vous n\'avez pas accès à cette page.')
        return redirect('pharmacy:dashboard')
    
    # Note: Cette fonctionnalité nécessiterait d'ajouter un champ 'created_by' au modèle Medicament
    # Pour l'instant, on affiche les ventes par utilisateur
    
    users = User.objects.annotate(
        nb_ventes=Count('ventes'),
        montant_ventes=Sum('ventes__montant_total'),
        nb_medicaments_vendus=Sum('ventes__items__quantite')
    ).order_by('-montant_ventes')
    
    context = {
        'users': users,
    }
    
    return render(request, 'pharmacy/admin_stock_by_user.html', context)


@login_required
def admin_chiffres_affaires(request):
    """Tableau de bord des chiffres d'affaires et investissements par utilisateur"""
    if not request.user.is_staff:
        messages.error(request, 'Vous n\'avez pas accès à cette page.')
        return redirect('pharmacy:dashboard')
    
    # Récupérer la période sélectionnée (en jours)
    periode = request.GET.get('periode', '30')
    try:
        periode_jours = int(periode)
    except ValueError:
        periode_jours = 30
    
    # Calculer la date de début
    date_fin = timezone.now().date()
    date_debut = date_fin - timedelta(days=periode_jours)
    
    # Statistiques par utilisateur
    users_stats = []
    users = User.objects.filter(is_active=True).exclude(is_staff=True)
    
    for user in users:
        # Investissement actuel (valeur du stock)
        medicaments = user.medicaments_crees.all()
        investissement_actuel = medicaments.aggregate(
            total=Sum(F('quantite_stock') * F('prix_unitaire'))
        )['total'] or 0
        
        # Médicaments en rupture de stock
        medicaments_rupture = medicaments.filter(quantite_stock=0).count()
        medicaments_alerte = medicaments.filter(
            quantite_stock__gt=0,
            quantite_stock__lte=F('seuil_alerte')
        ).count()
        
        # Ventes dans la période
        ventes = user.ventes.filter(
            date_vente__date__gte=date_debut,
            date_vente__date__lte=date_fin
        )
        
        revenus_periode = ventes.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        nb_ventes_periode = ventes.count()
        
        # Calculer le coût des médicaments vendus dans la période
        items_vendus = ItemVente.objects.filter(
            vente__vendeur=user,
            vente__date_vente__date__gte=date_debut,
            vente__date_vente__date__lte=date_fin
        )
        
        cout_medicaments_vendus = items_vendus.aggregate(
            total=Sum(F('quantite') * F('prix_unitaire'))
        )['total'] or 0
        
        # Calculer le bénéfice
        benefice = revenus_periode - cout_medicaments_vendus
        
        # Calculer la marge bénéficiaire
        if cout_medicaments_vendus > 0:
            marge_beneficiaire = (benefice / cout_medicaments_vendus) * 100
        else:
            marge_beneficiaire = 0
        
        # Retour sur investissement (ROI)
        if investissement_actuel > 0:
            roi = (benefice / investissement_actuel) * 100
        else:
            roi = 0
        
        users_stats.append({
            'user': user,
            'investissement_actuel': investissement_actuel,
            'medicaments_rupture': medicaments_rupture,
            'medicaments_alerte': medicaments_alerte,
            'nb_ventes_periode': nb_ventes_periode,
            'revenus_periode': revenus_periode,
            'cout_medicaments_vendus': cout_medicaments_vendus,
            'benefice': benefice,
            'marge_beneficiaire': marge_beneficiaire,
            'roi': roi,
        })
    
    # Trier par bénéfice décroissant
    users_stats.sort(key=lambda x: x['benefice'], reverse=True)
    
    # Statistiques globales
    total_investissement = sum(u['investissement_actuel'] for u in users_stats)
    total_revenus = sum(u['revenus_periode'] for u in users_stats)
    total_benefice = sum(u['benefice'] for u in users_stats)
    
    context = {
        'users_stats': users_stats,
        'periode': periode_jours,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'total_investissement': total_investissement,
        'total_revenus': total_revenus,
        'total_benefice': total_benefice,
        'periodes': [7, 15, 20, 30, 60, 90, 180],
    }
    
    return render(request, 'pharmacy/admin_chiffres_affaires.html', context)


@login_required
def creer_investissement(request):
    """Créer un investissement pour un utilisateur"""
    if not request.user.is_staff:
        messages.error(request, 'Vous n\'avez pas accès à cette fonctionnalité.')
        return redirect('pharmacy:dashboard')
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            user_id = request.POST.get('user_id')
            montant = request.POST.get('montant')
            duree = request.POST.get('duree')
            taux_interet = request.POST.get('taux_interet', 10)
            description = request.POST.get('description', '')
            
            # Validation
            if not all([user_id, montant, duree]):
                messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
                return redirect('pharmacy:admin_chiffres_affaires')
            
            utilisateur = User.objects.get(id=user_id)
            montant = float(montant)
            duree = int(duree)
            taux_interet = float(taux_interet)
            
            if montant < 1000:
                messages.error(request, 'Le montant minimum est de 1,000 FCFA.')
                return redirect('pharmacy:admin_chiffres_affaires')
            
            # Importer le modèle Investissement
            from .models import Investissement
            
            # Créer l'investissement
            investissement = Investissement.objects.create(
                administrateur=request.user,
                utilisateur=utilisateur,
                montant=montant,
                taux_interet=taux_interet,
                duree_jours=duree,
                description=description
            )
            
            # Enregistrer l'activité
            ActivityLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Investissement',
                object_id=investissement.id,
                description=f"Investissement de {montant} FCFA pour {utilisateur.username} (durée: {duree} jours)",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(
                request, 
                f'Investissement de {montant:,.0f} FCFA créé avec succès pour {utilisateur.username}. '
                f'Intérêts estimés: {investissement.interets_calcules:,.0f} FCFA. '
                f'Total attendu: {investissement.montant_total_attendu:,.0f} FCFA.'
            )
            
            return redirect('pharmacy:admin_chiffres_affaires')
            
        except User.DoesNotExist:
            messages.error(request, 'Utilisateur non trouvé.')
            return redirect('pharmacy:admin_chiffres_affaires')
        except ValueError as e:
            messages.error(request, f'Erreur dans les données: {str(e)}')
            return redirect('pharmacy:admin_chiffres_affaires')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création de l\'investissement: {str(e)}')
            return redirect('pharmacy:admin_chiffres_affaires')
    
    return redirect('pharmacy:admin_chiffres_affaires')


def telecharger_app(request):
    """Page de téléchargement de l'application"""
    return render(request, 'pharmacy/telecharger_app.html')


# ============================================
# VUES POUR LES CARTES D'EMPLOYÉS
# ============================================

@login_required
def admin_cartes_liste(request):
    """Liste toutes les cartes d'employés (admin uniquement)"""
    if not request.user.is_staff:
        messages.error(request, "Accès refusé. Vous devez être administrateur.")
        return redirect('pharmacy:dashboard')
    
    cartes = CarteEmploye.objects.select_related('utilisateur').all()
    
    # Filtres
    recherche = request.GET.get('recherche', '')
    if recherche:
        cartes = cartes.filter(
            Q(utilisateur__username__icontains=recherche) |
            Q(utilisateur__first_name__icontains=recherche) |
            Q(utilisateur__last_name__icontains=recherche) |
            Q(matricule__icontains=recherche) |
            Q(poste__icontains=recherche)
        )
    
    filtre_poste = request.GET.get('poste', '')
    if filtre_poste:
        cartes = cartes.filter(poste=filtre_poste)
    
    filtre_statut = request.GET.get('statut', '')
    if filtre_statut == 'actif':
        cartes = cartes.filter(actif=True)
    elif filtre_statut == 'inactif':
        cartes = cartes.filter(actif=False)
    elif filtre_statut == 'expire':
        cartes = cartes.filter(date_expiration_carte__lt=timezone.now().date())
    
    context = {
        'cartes': cartes,
        'recherche': recherche,
        'filtre_poste': filtre_poste,
        'filtre_statut': filtre_statut,
        'postes_choices': CarteEmploye.POSTES_CHOICES,
    }
    
    return render(request, 'pharmacy/admin_cartes_liste.html', context)


@login_required
def admin_carte_creer(request):
    """Créer une nouvelle carte d'employé"""
    if not request.user.is_staff:
        messages.error(request, "Accès refusé.")
        return redirect('pharmacy:dashboard')
    
    if request.method == 'POST':
        utilisateur_id = request.POST.get('utilisateur')
        poste = request.POST.get('poste')
        matricule = request.POST.get('matricule', '')
        telephone = request.POST.get('telephone', '')
        email_professionnel = request.POST.get('email_professionnel', '')
        adresse = request.POST.get('adresse', '')
        date_embauche = request.POST.get('date_embauche')
        date_expiration_carte = request.POST.get('date_expiration_carte', '')
        notes = request.POST.get('notes', '')
        
        try:
            utilisateur = User.objects.get(id=utilisateur_id)
            
            # Vérifier si l'utilisateur a déjà une carte
            if hasattr(utilisateur, 'carte_employe'):
                messages.warning(request, f"{utilisateur.username} a déjà une carte.")
                return redirect('pharmacy:admin_carte_detail', carte_id=utilisateur.carte_employe.id)
            
            # Créer la carte
            carte = CarteEmploye(
                utilisateur=utilisateur,
                poste=poste,
                telephone=telephone,
                email_professionnel=email_professionnel,
                adresse=adresse,
            )
            
            if matricule:
                carte.matricule = matricule
            
            if date_embauche:
                # Convertir la chaîne en objet date
                carte.date_embauche = parse_date(date_embauche) if isinstance(date_embauche, str) else date_embauche
            
            if date_expiration_carte:
                # Convertir la chaîne en objet date
                carte.date_expiration_carte = parse_date(date_expiration_carte) if isinstance(date_expiration_carte, str) else date_expiration_carte
            
            if notes:
                carte.notes = notes
            
            # Gérer la photo
            if 'photo' in request.FILES:
                carte.photo = request.FILES['photo']
            
            carte.save()
            
            log_activity(
                request.user,
                'CREATE',
                f'Carte créée pour {utilisateur.username} - {carte.matricule}',
                'CarteEmploye',
                carte.id,
                get_client_ip(request)
            )
            
            messages.success(request, f"✅ Carte créée avec succès pour {utilisateur.get_full_name() or utilisateur.username}!")
            return redirect('pharmacy:admin_carte_detail', carte_id=carte.id)
            
        except User.DoesNotExist:
            messages.error(request, "Utilisateur introuvable.")
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    # Liste des utilisateurs sans carte
    users_sans_carte = User.objects.filter(carte_employe__isnull=True)
    
    context = {
        'users_sans_carte': users_sans_carte,
        'postes_choices': CarteEmploye.POSTES_CHOICES,
    }
    
    return render(request, 'pharmacy/admin_carte_form.html', context)


@login_required
def admin_carte_detail(request, carte_id):
    """Afficher les détails d'une carte"""
    if not request.user.is_staff:
        messages.error(request, "Accès refusé.")
        return redirect('pharmacy:dashboard')
    
    carte = get_object_or_404(CarteEmploye, id=carte_id)
    
    context = {
        'carte': carte,
    }
    
    return render(request, 'pharmacy/admin_carte_detail.html', context)


@login_required
def admin_carte_modifier(request, carte_id):
    """Modifier une carte d'employé"""
    if not request.user.is_staff:
        messages.error(request, "Accès refusé.")
        return redirect('pharmacy:dashboard')
    
    carte = get_object_or_404(CarteEmploye, id=carte_id)
    
    if request.method == 'POST':
        carte.poste = request.POST.get('poste', carte.poste)
        carte.matricule = request.POST.get('matricule', carte.matricule)
        carte.telephone = request.POST.get('telephone', '')
        carte.email_professionnel = request.POST.get('email_professionnel', '')
        carte.adresse = request.POST.get('adresse', '')
        carte.notes = request.POST.get('notes', '')
        carte.actif = request.POST.get('actif') == 'on'
        
        date_embauche = request.POST.get('date_embauche')
        if date_embauche:
            # Convertir la chaîne en objet date
            carte.date_embauche = parse_date(date_embauche) if isinstance(date_embauche, str) else date_embauche
        
        date_expiration = request.POST.get('date_expiration_carte')
        if date_expiration:
            # Convertir la chaîne en objet date
            carte.date_expiration_carte = parse_date(date_expiration) if isinstance(date_expiration, str) else date_expiration
        
        # Gérer la photo
        if 'photo' in request.FILES:
            carte.photo = request.FILES['photo']
        
        try:
            carte.save()
            
            log_activity(
                request.user,
                'UPDATE',
                f'Carte modifiée pour {carte.utilisateur.username}',
                'CarteEmploye',
                carte.id,
                get_client_ip(request)
            )
            
            messages.success(request, "✅ Carte mise à jour avec succès!")
            return redirect('pharmacy:admin_carte_detail', carte_id=carte.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    context = {
        'carte': carte,
        'postes_choices': CarteEmploye.POSTES_CHOICES,
    }
    
    return render(request, 'pharmacy/admin_carte_form.html', context)


@login_required
def admin_carte_supprimer(request, carte_id):
    """Supprimer une carte d'employé"""
    if not request.user.is_staff:
        messages.error(request, "Accès refusé.")
        return redirect('pharmacy:dashboard')
    
    carte = get_object_or_404(CarteEmploye, id=carte_id)
    
    if request.method == 'POST':
        nom_employe = carte.utilisateur.get_full_name() or carte.utilisateur.username
        matricule = carte.matricule
        
        log_activity(
            request.user,
            'DELETE',
            f'Carte supprimée pour {nom_employe} - {matricule}',
            'CarteEmploye',
            carte.id,
            get_client_ip(request)
        )
        
        carte.delete()
        messages.success(request, f"✅ Carte de {nom_employe} supprimée.")
        return redirect('pharmacy:admin_cartes_liste')
    
    return render(request, 'pharmacy/admin_carte_confirm_delete.html', {'carte': carte})


@login_required
def admin_carte_imprimer(request, carte_id):
    """Afficher la carte pour impression"""
    if not request.user.is_staff and not request.user.id == CarteEmploye.objects.get(id=carte_id).utilisateur.id:
        messages.error(request, "Accès refusé.")
        return redirect('pharmacy:dashboard')
    
    carte = get_object_or_404(CarteEmploye, id=carte_id)
    
    context = {
        'carte': carte,
    }
    
    return render(request, 'pharmacy/admin_carte_imprimer.html', context)


@login_required
def admin_carte_regenerer_qr(request, carte_id):
    """Régénérer le QR code d'une carte"""
    if not request.user.is_staff:
        messages.error(request, "Accès refusé.")
        return redirect('pharmacy:dashboard')
    
    carte = get_object_or_404(CarteEmploye, id=carte_id)
    
    try:
        carte.generer_qr_code()
        carte.save(update_fields=['qr_code'])
        
        log_activity(
            request.user,
            'UPDATE',
            f'QR code régénéré pour {carte.utilisateur.username}',
            'CarteEmploye',
            carte.id,
            get_client_ip(request)
        )
        
        messages.success(request, "✅ QR code régénéré avec succès!")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
    
    return redirect('pharmacy:admin_carte_detail', carte_id=carte.id)


@login_required
def admin_carte_rechercher(request):
    """Rechercher une carte par matricule (pour le scanner QR)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Accès refusé'})
    
    matricule = request.GET.get('matricule', '').strip()
    
    if not matricule:
        return JsonResponse({'success': False, 'error': 'Matricule manquant'})
    
    try:
        carte = CarteEmploye.objects.select_related('utilisateur').get(matricule=matricule)
        
        # Préparer les données de réponse
        data = {
            'success': True,
            'carte': {
                'id': carte.id,
                'nom': carte.utilisateur.get_full_name() or carte.utilisateur.username,
                'matricule': carte.matricule,
                'poste': carte.get_poste_display(),
                'telephone': carte.telephone or 'N/A',
                'email': carte.email_professionnel or carte.utilisateur.email,
                'date_embauche': carte.date_embauche.strftime('%d/%m/%Y') if carte.date_embauche else 'N/A',
                'date_expiration': carte.date_expiration_carte.strftime('%d/%m/%Y') if carte.date_expiration_carte else 'N/A',
                'photo_url': carte.photo.url if carte.photo else None,
                'actif': carte.actif,
            }
        }
        
        # Logger l'activité
        log_activity(
            request.user,
            'READ',
            f'Carte scannée: {carte.utilisateur.username} ({matricule})',
            'CarteEmploye',
            carte.id,
            get_client_ip(request)
        )
        
        return JsonResponse(data)
        
    except CarteEmploye.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Carte non trouvée'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def ma_carte_detail(request):
    """Vue détaillée de ma carte de service (utilisateur)"""
    try:
        carte = CarteEmploye.objects.select_related('utilisateur').get(utilisateur=request.user)
    except CarteEmploye.DoesNotExist:
        messages.warning(request, "Vous n'avez pas encore de carte de service. Contactez l'administrateur.")
        return redirect('pharmacy:dashboard')
    
    # Logger l'activité
    log_activity(
        request.user,
        'READ',
        f'Consultation de ma carte de service',
        'CarteEmploye',
        carte.id,
        get_client_ip(request)
    )
    
    context = {
        'carte': carte,
        'is_owner': True,
    }
    
    return render(request, 'pharmacy/ma_carte_detail.html', context)


@login_required
def ma_carte_imprimer(request):
    """Imprimer ma carte de service (utilisateur)"""
    try:
        carte = CarteEmploye.objects.select_related('utilisateur').get(utilisateur=request.user)
    except CarteEmploye.DoesNotExist:
        messages.warning(request, "Vous n'avez pas encore de carte de service.")
        return redirect('pharmacy:dashboard')
    
    # Logger l'activité
    log_activity(
        request.user,
        'READ',
        f'Impression de ma carte de service',
        'CarteEmploye',
        carte.id,
        get_client_ip(request)
    )
    
    context = {
        'carte': carte,
    }
    
    return render(request, 'pharmacy/admin_carte_imprimer.html', context)
