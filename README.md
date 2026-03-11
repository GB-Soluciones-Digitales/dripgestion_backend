# 💧 DripGestión API - SaaS

![Estado](https://img.shields.io/badge/Estado-En_Producción-success)
![Versión](https://img.shields.io/badge/Versión-1.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql)

Motor de gestión multi-tenant de alto rendimiento diseñado para distribuidoras de agua, soda y logística de última milla. Construido con una arquitectura de aislamiento de datos que permite servir a múltiples empresas desde una única instancia.

## 🚀 Tecnologías Core
* **Framework:** FastAPI
* **ORM:** SQLAlchemy con PostgreSQL
* **Seguridad:** OAuth2 con JWT (JSON Web Tokens) & Bcrypt
* **Validación:** Pydantic v2
* **Aislamiento:** Filtro por `tenant_id` en capa de acceso a datos.

## 🏗️ Arquitectura Técnica
* **Aislamiento de Datos:** Implementación de filtrado estricto en la capa de acceso a datos (Repository Pattern).
* **Seguridad:** Autenticación JWT con hashing de contraseñas mediante Bcrypt.
* **Escalabilidad:** Diseñado para soportar múltiples empresas con una sola instancia de API.

## 🏗️ Arquitectura Multi-tenant
El sistema utiliza una estrategia de **Shared Database, Shared Schema**. 
Cada registro en las tablas críticas (`clientes`, `pedidos`, `movimientos`) posee una clave foránea `tenant_id`. El middleware de autenticación extrae el ID de la empresa del token del usuario, garantizando que ninguna empresa pueda acceder a los datos de otra.

## 🛠️ Instalación y Uso
1. Clonar el repositorio.
2. Crear entorno virtual: `python -m venv venv`
3. Instalar dependencias: `pip install -r requirements.txt`
4. Configurar `.env` con tus credenciales de Postgres y `SECRET_KEY`.
5. Iniciar: `uvicorn app.main:app --reload`

## 📡 Módulos Principales
- **Auth:** Gestión de sesiones y roles (ADMIN, CHOFER, CLIENTE).
- **Tenants:** Configuración de branding dinámico (Colores, Logos, WhatsApp).
- **Clientes:** Gestión de cuentas corrientes, envases prestados y geolocalización.
- **Logística:** Registro de recorridos, ventas y cierres de caja diarios.

## 🚀 Roadmap / Próximas Actualizaciones
- [ ] **Facturación Electrónica:** Integración con AFIP.
- [ ] **Optimización de Rutas:** Algoritmo de despacho inteligente basado en Google Maps.
- [ ] **Notificaciones Push:** Alertas de stock y recordatorios de pago automáticos.
- [ ] **Reportes en PDF:** Generación de resúmenes de cuenta descargables.

## 👨‍💻 Autores
Un producto desarrollado por **GB Soluciones Digitales**.

**Desarrollador Principal**: Brian Battauz ([@Brian13b](https://github.com/Brian13b))

---
> 💡 *Este backend es el corazón del ecosistema DripGestión, garantizando integridad y privacidad para cada distribuidora.*