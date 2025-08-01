#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion à l'API Veolia
Utilisez ce script pour diagnostiquer les problèmes de connexion
"""

import asyncio
import sys
from datetime import datetime
import logging

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    from veolia_api import VeoliaAPI
    from veolia_api.exceptions import VeoliaAPIError, VeoliaAPIAuthError, VeoliaAPIInvalidCredentialsError
except ImportError:
    print("❌ Erreur: Le module veolia_api n'est pas installé")
    print("Installez-le avec: pip install veolia_api==1.2.4")
    sys.exit(1)


async def test_veolia_connection():
    """Test de connexion à l'API Veolia"""
    
    # Demande sécurisée des identifiants
    print("🔐 Test de connexion à l'API Veolia")
    print("=" * 50)
    
    username = input("Nom d'utilisateur Veolia: ").strip()
    if not username:
        print("❌ Nom d'utilisateur requis")
        return False
    
    import getpass
    password = getpass.getpass("Mot de passe Veolia: ")
    if not password:
        print("❌ Mot de passe requis")
        return False
    
    try:
        print("\n🔄 Initialisation de l'API...")
        api = VeoliaAPI(username=username, password=password)
        
        print("🔄 Test de connexion...")
        login_result = await api.login()
        
        if login_result:
            print("✅ Connexion réussie!")
            
            # Test de récupération des données
            print("🔄 Test de récupération des données...")
            now = datetime.now()
            
            try:
                await api.fetch_all_data(now.year, now.month)
                print("✅ Récupération des données réussie!")
                
                if hasattr(api, 'account_data') and api.account_data:
                    print(f"📊 Données récupérées: {api.account_data}")
                else:
                    print("⚠️ Aucune donnée récupérée")
                    
            except Exception as e:
                print(f"❌ Erreur lors de la récupération des données: {e}")
                
        else:
            print("❌ Échec de la connexion")
            return False
            
    except VeoliaAPIInvalidCredentialsError:
        print("❌ Identifiants invalides - Vérifiez votre nom d'utilisateur et mot de passe")
        return False
        
    except VeoliaAPIAuthError as e:
        print(f"❌ Erreur d'authentification: {e}")
        return False
        
    except VeoliaAPIError as e:
        print(f"❌ Erreur de l'API Veolia: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        logger.exception("Erreur détaillée:")
        return False
    
    return True


async def main():
    """Fonction principale"""
    print("🧪 Script de diagnostic Veolia API")
    print("Ce script teste la connexion à l'API Veolia de manière sécurisée\n")
    
    success = await test_veolia_connection()
    
    if success:
        print("\n✅ Test terminé avec succès!")
        print("Votre intégration Home Assistant devrait fonctionner.")
    else:
        print("\n❌ Test échoué!")
        print("Vérifiez:")
        print("- Vos identifiants Veolia")
        print("- Votre connexion internet")
        print("- Que votre compte Veolia est actif")


if __name__ == "__main__":
    asyncio.run(main())
