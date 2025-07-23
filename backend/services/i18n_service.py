"""
Internationalization & Localization Service
Business logic for multi-language support
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

from core.database import get_database

class I18nService:
    
    # Supported languages with comprehensive metadata
    SUPPORTED_LANGUAGES = {
        "en": {
            "name": "English",
            "native": "English",
            "flag": "🇺🇸",
            "rtl": False,
            "coverage": 100,
            "region": "US",
            "currency": "USD",
            "date_format": "MM/DD/YYYY"
        },
        "es": {
            "name": "Spanish",
            "native": "Español",
            "flag": "🇪🇸",
            "rtl": False,
            "coverage": 95,
            "region": "ES",
            "currency": "EUR",
            "date_format": "DD/MM/YYYY"
        },
        "fr": {
            "name": "French",
            "native": "Français",
            "flag": "🇫🇷",
            "rtl": False,
            "coverage": 92,
            "region": "FR",
            "currency": "EUR",
            "date_format": "DD/MM/YYYY"
        },
        "de": {
            "name": "German",
            "native": "Deutsch",
            "flag": "🇩🇪",
            "rtl": False,
            "coverage": 88,
            "region": "DE",
            "currency": "EUR",
            "date_format": "DD.MM.YYYY"
        },
        "it": {
            "name": "Italian",
            "native": "Italiano",
            "flag": "🇮🇹",
            "rtl": False,
            "coverage": 85,
            "region": "IT",
            "currency": "EUR",
            "date_format": "DD/MM/YYYY"
        },
        "pt": {
            "name": "Portuguese",
            "native": "Português",
            "flag": "🇵🇹",
            "rtl": False,
            "coverage": 85,
            "region": "BR",
            "currency": "BRL",
            "date_format": "DD/MM/YYYY"
        },
        "ru": {
            "name": "Russian",
            "native": "Русский",
            "flag": "🇷🇺",
            "rtl": False,
            "coverage": 80,
            "region": "RU",
            "currency": "RUB",
            "date_format": "DD.MM.YYYY"
        },
        "zh": {
            "name": "Chinese",
            "native": "中文",
            "flag": "🇨🇳",
            "rtl": False,
            "coverage": 75,
            "region": "CN",
            "currency": "CNY",
            "date_format": "YYYY/MM/DD"
        },
        "ja": {
            "name": "Japanese",
            "native": "日本語",
            "flag": "🇯🇵",
            "rtl": False,
            "coverage": 70,
            "region": "JP",
            "currency": "JPY",
            "date_format": "YYYY/MM/DD"
        },
        "ko": {
            "name": "Korean",
            "native": "한국어",
            "flag": "🇰🇷",
            "rtl": False,
            "coverage": 65,
            "region": "KR",
            "currency": "KRW",
            "date_format": "YYYY/MM/DD"
        },
        "ar": {
            "name": "Arabic",
            "native": "العربية",
            "flag": "🇸🇦",
            "rtl": True,
            "coverage": 60,
            "region": "SA",
            "currency": "SAR",
            "date_format": "DD/MM/YYYY"
        },
        "hi": {
            "name": "Hindi",
            "native": "हिन्दी",
            "flag": "🇮🇳",
            "rtl": False,
            "coverage": 55,
            "region": "IN",
            "currency": "INR",
            "date_format": "DD/MM/YYYY"
        }
    }
    
    # Translation database
    TRANSLATIONS = {
        "en": {
            "common": {
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "create": "Create",
                "loading": "Loading...",
                "error": "Error",
                "success": "Success",
                "warning": "Warning",
                "info": "Information",
                "yes": "Yes",
                "no": "No",
                "ok": "OK",
                "close": "Close",
                "back": "Back",
                "next": "Next",
                "previous": "Previous",
                "search": "Search",
                "filter": "Filter",
                "sort": "Sort",
                "export": "Export",
                "import": "Import",
                "upload": "Upload",
                "download": "Download"
            },
            "navigation": {
                "dashboard": "Dashboard",
                "analytics": "Analytics",
                "settings": "Settings",
                "profile": "Profile",
                "workspaces": "Workspaces",
                "bio_sites": "Bio Sites",
                "courses": "Courses",
                "ecommerce": "E-commerce",
                "marketing": "Marketing",
                "support": "Support",
                "billing": "Billing",
                "team": "Team"
            },
            "forms": {
                "first_name": "First Name",
                "last_name": "Last Name",
                "full_name": "Full Name",
                "email": "Email Address",
                "password": "Password",
                "confirm_password": "Confirm Password",
                "phone": "Phone Number",
                "address": "Address",
                "city": "City",
                "country": "Country",
                "postal_code": "Postal Code",
                "company": "Company",
                "website": "Website",
                "description": "Description",
                "title": "Title",
                "name": "Name"
            },
            "business": {
                "revenue": "Revenue",
                "customers": "Customers",
                "orders": "Orders",
                "products": "Products",
                "services": "Services",
                "sales": "Sales",
                "profit": "Profit",
                "growth": "Growth",
                "conversion": "Conversion",
                "traffic": "Traffic",
                "leads": "Leads",
                "campaigns": "Campaigns"
            },
            "messages": {
                "welcome": "Welcome to Mewayz Platform",
                "login_success": "Login successful",
                "logout_success": "Logout successful",
                "save_success": "Saved successfully",
                "delete_success": "Deleted successfully",
                "update_success": "Updated successfully",
                "create_success": "Created successfully",
                "error_occurred": "An error occurred",
                "invalid_credentials": "Invalid credentials",
                "access_denied": "Access denied",
                "not_found": "Not found",
                "validation_error": "Validation error"
            }
        },
        "es": {
            "common": {
                "save": "Guardar",
                "cancel": "Cancelar",
                "delete": "Eliminar",
                "edit": "Editar",
                "create": "Crear",
                "loading": "Cargando...",
                "error": "Error",
                "success": "Éxito",
                "warning": "Advertencia",
                "info": "Información",
                "yes": "Sí",
                "no": "No",
                "ok": "Vale",
                "close": "Cerrar",
                "back": "Atrás",
                "next": "Siguiente",
                "previous": "Anterior",
                "search": "Buscar",
                "filter": "Filtrar",
                "sort": "Ordenar",
                "export": "Exportar",
                "import": "Importar",
                "upload": "Subir",
                "download": "Descargar"
            },
            "navigation": {
                "dashboard": "Panel",
                "analytics": "Analíticas",
                "settings": "Configuración",
                "profile": "Perfil",
                "workspaces": "Espacios de Trabajo",
                "bio_sites": "Bio Sitios",
                "courses": "Cursos",
                "ecommerce": "Comercio Electrónico",
                "marketing": "Marketing",
                "support": "Soporte",
                "billing": "Facturación",
                "team": "Equipo"
            },
            "forms": {
                "first_name": "Nombre",
                "last_name": "Apellido",
                "full_name": "Nombre Completo",
                "email": "Correo Electrónico",
                "password": "Contraseña",
                "confirm_password": "Confirmar Contraseña",
                "phone": "Teléfono",
                "address": "Dirección",
                "city": "Ciudad",
                "country": "País",
                "postal_code": "Código Postal",
                "company": "Empresa",
                "website": "Sitio Web",
                "description": "Descripción",
                "title": "Título",
                "name": "Nombre"
            },
            "business": {
                "revenue": "Ingresos",
                "customers": "Clientes",
                "orders": "Pedidos",
                "products": "Productos",
                "services": "Servicios",
                "sales": "Ventas",
                "profit": "Beneficio",
                "growth": "Crecimiento",
                "conversion": "Conversión",
                "traffic": "Tráfico",
                "leads": "Leads",
                "campaigns": "Campañas"
            },
            "messages": {
                "welcome": "Bienvenido a Mewayz Platform",
                "login_success": "Inicio de sesión exitoso",
                "logout_success": "Cierre de sesión exitoso",
                "save_success": "Guardado exitosamente",
                "delete_success": "Eliminado exitosamente",
                "update_success": "Actualizado exitosamente",
                "create_success": "Creado exitosamente",
                "error_occurred": "Ocurrió un error",
                "invalid_credentials": "Credenciales inválidas",
                "access_denied": "Acceso denegado",
                "not_found": "No encontrado",
                "validation_error": "Error de validación"
            }
        },
        "fr": {
            "common": {
                "save": "Sauvegarder",
                "cancel": "Annuler",
                "delete": "Supprimer",
                "edit": "Modifier",
                "create": "Créer",
                "loading": "Chargement...",
                "error": "Erreur",
                "success": "Succès",
                "warning": "Avertissement",
                "info": "Information",
                "yes": "Oui",
                "no": "Non",
                "ok": "D'accord",
                "close": "Fermer",
                "back": "Retour",
                "next": "Suivant",
                "previous": "Précédent",
                "search": "Rechercher",
                "filter": "Filtrer",
                "sort": "Trier",
                "export": "Exporter",
                "import": "Importer",
                "upload": "Télécharger",
                "download": "Télécharger"
            },
            "navigation": {
                "dashboard": "Tableau de bord",
                "analytics": "Analyses",
                "settings": "Paramètres",
                "profile": "Profil",
                "workspaces": "Espaces de travail",
                "bio_sites": "Bio Sites",
                "courses": "Cours",
                "ecommerce": "E-commerce",
                "marketing": "Marketing",
                "support": "Support",
                "billing": "Facturation",
                "team": "Équipe"
            }
        }
    }
    
    @staticmethod
    async def get_supported_languages() -> Dict[str, Any]:
        """Get all supported languages"""
        languages_list = []
        for code, info in I18nService.SUPPORTED_LANGUAGES.items():
            languages_list.append({
                "code": code,
                **info
            })
        
        return {
            "languages": languages_list,
            "default_language": "en",
            "total_languages": len(languages_list),
            "detection_methods": ["browser", "user_preference", "ip_location"],
            "fallback_strategy": "en"
        }
    
    @staticmethod
    async def get_translations(language: str) -> Optional[Dict[str, Any]]:
        """Get translations for specific language"""
        if language not in I18nService.SUPPORTED_LANGUAGES:
            return None
        
        # Get translations, fallback to English if not available
        translations = I18nService.TRANSLATIONS.get(language, I18nService.TRANSLATIONS["en"])
        
        # Fill in missing translations with English
        english_translations = I18nService.TRANSLATIONS["en"]
        complete_translations = {}
        
        for category, items in english_translations.items():
            complete_translations[category] = {}
            for key, english_value in items.items():
                if category in translations and key in translations[category]:
                    complete_translations[category][key] = translations[category][key]
                else:
                    complete_translations[category][key] = english_value
        
        total_keys = sum(len(section) for section in complete_translations.values())
        language_info = I18nService.SUPPORTED_LANGUAGES[language]
        
        return {
            "language": language,
            "language_info": language_info,
            "translations": complete_translations,
            "metadata": {
                "total_keys": total_keys,
                "coverage": language_info["coverage"],
                "last_updated": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "rtl": language_info["rtl"]
            }
        }
    
    @staticmethod
    
    ) -> Dict[str, Any]:
        """Detect user's preferred language"""
        detected_languages = []
        
        # 1. User preference (highest priority)
        if user_preference and user_preference in I18nService.SUPPORTED_LANGUAGES:
            detected_languages.append({
                "code": user_preference,
                "source": "user_preference",
                "confidence": 1.0
            })
        
        # 2. Browser Accept-Language header
        if accept_language:
            browser_langs = accept_language.replace(" ", "").split(',')
            confidence = 0.9
            for lang_entry in browser_langs[:3]:  # Top 3 preferences
                if ';' in lang_entry:
                    lang_code, weight = lang_entry.split(';')
                    try:
                        confidence = float(weight.split('=')[1])
                    except:
                        pass
                else:
                    lang_code = lang_entry
                
                # Extract language code
                lang_code = lang_code.split('-')[0].lower()
                if lang_code in I18nService.SUPPORTED_LANGUAGES:
                    detected_languages.append({
                        "code": lang_code,
                        "source": "browser_preference",
                        "confidence": confidence
                    })
                confidence = max(0.1, confidence - 0.1)
        
        # 3. IP-based geolocation (mock implementation)
        if ip_address:
            country_lang_map = {
                "US": "en", "GB": "en", "CA": "en", "AU": "en",
                "ES": "es", "MX": "es", "AR": "es", "CO": "es",
                "FR": "fr", "BE": "fr", "CH": "fr",
                "DE": "de", "AT": "de",
                "IT": "it", "PT": "pt", "BR": "pt",
                "RU": "ru", "CN": "zh", "JP": "ja", "KR": "ko",
                "SA": "ar", "AE": "ar", "IN": "hi"
            }
            # In real implementation, use IP geolocation service
            # For mock, assume US
            ip_language = country_lang_map.get("US", "en")
            detected_languages.append({
                "code": ip_language,
                "source": "ip_geolocation",
                "confidence": 0.7
            })
        
        # 4. Timezone-based detection
        if timezone:
            timezone_lang_map = {
                "America/New_York": "en", "America/Los_Angeles": "en",
                "Europe/Madrid": "es", "Europe/Paris": "fr",
                "Europe/Berlin": "de", "Europe/Rome": "it",
                "Asia/Shanghai": "zh", "Asia/Tokyo": "ja",
                "Asia/Seoul": "ko", "Asia/Kolkata": "hi"
            }
            tz_language = timezone_lang_map.get(timezone, "en")
            detected_languages.append({
                "code": tz_language,
                "source": "timezone",
                "confidence": 0.6
            })
        
        # Default fallback
        if not detected_languages:
            detected_languages.append({
                "code": "en",
                "source": "default_fallback",
                "confidence": 0.5
            })
        
        # Get highest confidence language
        recommended_language = max(detected_languages, key=lambda x: x["confidence"])["code"]
        
        return {
            "recommended_language": recommended_language,
            "detected_languages": detected_languages,
            "fallback_language": "en",
            "detection_methods_used": list(set([d["source"] for d in detected_languages])),
            "language_info": I18nService.SUPPORTED_LANGUAGES.get(recommended_language, I18nService.SUPPORTED_LANGUAGES["en"])
        }
    
    @staticmethod
    async def set_user_language(user_id: str, language: str) -> Dict[str, Any]:
        """Set user's language preference"""
        if language not in I18nService.SUPPORTED_LANGUAGES:
            raise Exception("Language not supported")
        
        database = get_database()
        users_collection = database.users
        
        # Update user's language preference
        result = await users_collection.update_one(
            {"_id": user_id},
            {"$set": {
                "language": language,
                "language_updated_at": datetime.utcnow()
            }}
        if result.matched_count == 0:
            raise Exception("User not found")
        
        return {
            "user_id": user_id,
            "language": language,
            "language_info": I18nService.SUPPORTED_LANGUAGES[language],
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def get_user_language(user_id: str) -> str:
        """Get user's language preference"""
        database = get_database()
        users_collection = database.users
        
        user = await users_collection.find_one({"_id": user_id})
        if user and "language" in user:
            return user["language"]
        
        return "en"  # Default fallback
    
    @staticmethod
    
    ) -> Dict[str, Any]:
        """Translate text (mock implementation)"""
        
        # Mock translation logic
        translations = {
            ("Hello", "es"): "Hola",
            ("Welcome", "es"): "Bienvenido",
            ("Dashboard", "es"): "Panel",
            ("Settings", "es"): "Configuración",
            ("Hello", "fr"): "Bonjour",
            ("Welcome", "fr"): "Bienvenue",
            ("Dashboard", "fr"): "Tableau de bord",
            ("Settings", "fr"): "Paramètres"
        }
        
        translation_key = (text, target_language)
        translated_text = translations.get(translation_key, f"[{target_language}] {text}")
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "confidence_score": 0.95,
            "translation_method": "neural_machine_translation",
            "context_used": context,
            "alternatives": [
                {"text": f"Alt1: {translated_text}", "confidence": 0.92},
                {"text": f"Alt2: {translated_text}", "confidence": 0.89}
            ]
        }
    
    @staticmethod
    async def get_localization_data(language: str, category: str = "all") -> Dict[str, Any]:
        """Get localization data for specific language and category"""
        if language not in I18nService.SUPPORTED_LANGUAGES:
            language = "en"
        
        language_info = I18nService.SUPPORTED_LANGUAGES[language]
        translations = await I18nService.get_translations(language)
        
        localization_data = {
            "language": language,
            "language_info": language_info,
            "number_format": {
                "decimal_separator": "." if language in ["en", "zh", "ja", "ko"] else ",",
                "thousands_separator": "," if language in ["en", "zh", "ja", "ko"] else ".",
                "currency_symbol_position": "before" if language in ["en", "zh", "ja", "ko"] else "after"
            },
            "date_format": {
                "short": language_info["date_format"],
                "long": "dddd, MMMM Do YYYY" if language == "en" else "dddd, D MMMM YYYY",
                "time": "h:mm A" if language == "en" else "HH:mm"
            },
            "currency": {
                "code": language_info["currency"],
                "symbol": I18nService._get_currency_symbol(language_info["currency"]),
                "position": "before" if language in ["en", "zh", "ja", "ko"] else "after"
            }
        }
        
        if category == "all" or not category:
            localization_data["translations"] = translations["translations"]
        elif category in translations["translations"]:
            localization_data["translations"] = {category: translations["translations"][category]}
        
        return localization_data
    
    @staticmethod
    async def get_currency_info(country: str) -> Dict[str, Any]:
        """Get currency information for a country"""
        country_currency_map = {
            "US": {"code": "USD", "symbol": "$", "name": "US Dollar"},
            "GB": {"code": "GBP", "symbol": "£", "name": "British Pound"},
            "EU": {"code": "EUR", "symbol": "€", "name": "Euro"},
            "DE": {"code": "EUR", "symbol": "€", "name": "Euro"},
            "FR": {"code": "EUR", "symbol": "€", "name": "Euro"},
            "ES": {"code": "EUR", "symbol": "€", "name": "Euro"},
            "IT": {"code": "EUR", "symbol": "€", "name": "Euro"},
            "JP": {"code": "JPY", "symbol": "¥", "name": "Japanese Yen"},
            "CN": {"code": "CNY", "symbol": "¥", "name": "Chinese Yuan"},
            "IN": {"code": "INR", "symbol": "₹", "name": "Indian Rupee"},
            "BR": {"code": "BRL", "symbol": "R$", "name": "Brazilian Real"},
            "MX": {"code": "MXN", "symbol": "$", "name": "Mexican Peso"},
            "CA": {"code": "CAD", "symbol": "$", "name": "Canadian Dollar"}
        }
        
        currency_info = country_currency_map.get(country.upper(), country_currency_map["US"])
        
        return {
            "country": country.upper(),
            "currency": currency_info,
            "exchange_rate": 1.0,  # Mock rate
            "last_updated": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def get_timezone_info(location: str) -> Dict[str, Any]:
        """Get timezone information for a location"""
        timezone_map = {
            "new_york": {"timezone": "America/New_York", "offset": "-05:00", "name": "Eastern Time"},
            "los_angeles": {"timezone": "America/Los_Angeles", "offset": "-08:00", "name": "Pacific Time"},
            "london": {"timezone": "Europe/London", "offset": "+00:00", "name": "Greenwich Mean Time"},
            "paris": {"timezone": "Europe/Paris", "offset": "+01:00", "name": "Central European Time"},
            "tokyo": {"timezone": "Asia/Tokyo", "offset": "+09:00", "name": "Japan Standard Time"},
            "sydney": {"timezone": "Australia/Sydney", "offset": "+11:00", "name": "Australian Eastern Time"}
        }
        
        location_key = location.lower().replace(" ", "_")
        timezone_info = timezone_map.get(location_key, timezone_map["london"])
        
        return {
            "location": location,
            "timezone": timezone_info["timezone"],
            "utc_offset": timezone_info["offset"],
            "name": timezone_info["name"],
            "current_time": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def get_format_patterns(language: str) -> Dict[str, Any]:
        """Get formatting patterns for a language"""
        if language not in I18nService.SUPPORTED_LANGUAGES:
            language = "en"
        
        language_info = I18nService.SUPPORTED_LANGUAGES[language]
        
        patterns = {
            "date": {
                "short": language_info["date_format"],
                "medium": "MMM D, YYYY" if language == "en" else "D MMM YYYY",
                "long": "MMMM D, YYYY" if language == "en" else "D MMMM YYYY",
                "full": "dddd, MMMM D, YYYY" if language == "en" else "dddd, D MMMM YYYY"
            },
            "time": {
                "short": "h:mm A" if language == "en" else "HH:mm",
                "medium": "h:mm:ss A" if language == "en" else "HH:mm:ss",
                "long": "h:mm:ss A z" if language == "en" else "HH:mm:ss z"
            },
            "number": {
                "decimal_places": 2,
                "decimal_separator": "." if language in ["en", "zh", "ja", "ko"] else ",",
                "thousands_separator": "," if language in ["en", "zh", "ja", "ko"] else ".",
                "currency_format": "${amount}" if language == "en" else "{amount} {symbol}"
            }
        }
        
        return {
            "language": language,
            "patterns": patterns
        }
    
    @staticmethod
    
    ) -> Dict[str, Any]:
        """Set workspace localization settings"""
        database = get_database()
        workspaces_collection = database.workspaces
        
        # Update workspace settings
        result = await workspaces_collection.update_one(
            {"owner_id": user_id},
            {"$set": {
                "localization": {
                    "language": language,
                    "timezone": timezone,
                    "currency": currency,
                    "date_format": date_format,
                    "updated_at": datetime.utcnow()
                }
            }}
        if result.matched_count == 0:
            raise Exception("Workspace not found")
        
        return {
            "workspace_id": user_id,
            "localization": {
                "language": language,
                "timezone": timezone,
                "currency": currency,
                "date_format": date_format
            },
            "language_info": I18nService.SUPPORTED_LANGUAGES.get(language, I18nService.SUPPORTED_LANGUAGES["en"]),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def get_workspace_language(user_id: str) -> Dict[str, Any]:
        """Get workspace localization settings"""
        database = get_database()
        workspaces_collection = database.workspaces
        
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if workspace and "localization" in workspace:
            localization = workspace["localization"]
        else:
            # Default settings
            localization = {
                "language": "en",
                "timezone": "UTC",
                "currency": "USD",
                "date_format": "YYYY-MM-DD"
            }
        
        return {
            "workspace_id": user_id,
            "localization": localization,
            "language_info": I18nService.SUPPORTED_LANGUAGES.get(
                localization["language"], 
                I18nService.SUPPORTED_LANGUAGES["en"]
        }
    
    @staticmethod
    def _get_currency_symbol(currency_code: str) -> str:
        """Get currency symbol for currency code"""
        currency_symbols = {
            "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
            "CNY": "¥", "INR": "₹", "BRL": "R$", "CAD": "$",
            "AUD": "$", "CHF": "Fr", "SEK": "kr", "NOK": "kr",
            "DKK": "kr", "RUB": "₽", "KRW": "₩", "MXN": "$"
        }
        return currency_symbols.get(currency_code, currency_code)

# Global service instance

    async def create_item(self, user_id: str, item_data: dict):
        """Create new item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            new_item = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                **item_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active"
            }
            
            await collections['items'].insert_one(new_item)
            
            return {
                "success": True,
                "data": new_item,
                "message": "Item created successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def get_item(self, user_id: str, item_id: str):
        """Get specific item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if not item:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "data": item,
                "message": "Item retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def update_item(self, user_id: str, item_id: str, update_data: dict):
        """Update existing item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collections['items'].update_one(
                {"_id": item_id, "user_id": user_id},
                {"$set": update_data}
            if result.modified_count == 0:
                return {"success": False, "message": "Item not found or no changes made"}
            
            # Get updated item
            updated_item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            return {
                "success": True,
                "data": updated_item,
                "message": "Item updated successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def delete_item(self, user_id: str, item_id: str):
        """Delete item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            result = await collections['items'].delete_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "message": "Item deleted successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def list_items(self, user_id: str, filters: dict = None, page: int = 1, limit: int = 50):
        """List user's items"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            query = {"user_id": user_id}
            if filters:
                query.update(filters)
            
            skip = (page - 1) * limit
            
            cursor = collections['items'].find(query).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)
            
            total_count = await collections['items'].count_documents(query)
            
            return {
                "success": True,
                "data": {
                    "items": items,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Items retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}