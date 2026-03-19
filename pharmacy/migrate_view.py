"""
Vue spéciale pour exécuter les migrations depuis le navigateur
ATTENTION: À supprimer après utilisation pour des raisons de sécurité!
"""
from django.http import HttpResponse
from django.core.management import call_command
from django.db import connection
import io

def run_migrations(request):
    """Exécute les migrations et affiche le résultat"""
    
    # Créer un buffer pour capturer la sortie
    out = io.StringIO()
    
    html = "<html><head><meta charset='utf-8'><title>Migrations Django</title></head><body>"
    html += "<h1>🔧 Exécution des Migrations Django</h1>"
    html += "<pre style='background: #f4f4f4; padding: 20px; border: 1px solid #ddd;'>"
    
    try:
        # Vérifier la connexion
        html += "="*70 + "\n"
        html += "ÉTAPE 1: Vérification de la connexion PostgreSQL\n"
        html += "="*70 + "\n\n"
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            html += f"✅ Connecté à PostgreSQL\n"
            html += f"   Version: {version[0][:80]}\n\n"
            
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            html += f"✅ Base de données: {db_name[0]}\n\n"
            
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
            table_count = cursor.fetchone()
            html += f"📊 Tables existantes avant migration: {table_count[0]}\n\n"
        
        # Exécuter les migrations
        html += "="*70 + "\n"
        html += "ÉTAPE 2: Exécution des migrations\n"
        html += "="*70 + "\n\n"
        
        call_command('migrate', verbosity=2, interactive=False, stdout=out)
        html += out.getvalue()
        html += "\n✅ MIGRATIONS TERMINÉES!\n\n"
        
        # Vérifier les tables créées
        html += "="*70 + "\n"
        html += "ÉTAPE 3: Vérification des tables créées\n"
        html += "="*70 + "\n\n"
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            html += f"📋 Tables dans la base ({len(tables)} tables):\n"
            for table in tables:
                html += f"   ✓ {table[0]}\n"
        
        html += "\n" + "="*70 + "\n"
        html += "🎉 SUCCÈS TOTAL!\n"
        html += "="*70 + "\n"
        html += "\nVotre site devrait maintenant fonctionner correctement.\n"
        html += "Vous pouvez fermer cette page et essayer de vous connecter.\n"
        
    except Exception as e:
        html += f"\n❌ ERREUR:\n{str(e)}\n"
        import traceback
        html += f"\n{traceback.format_exc()}\n"
    
    html += "</pre>"
    html += "<p><a href='/'>← Retour à l'accueil</a></p>"
    html += "</body></html>"
    
    return HttpResponse(html)
