workspace "VALEO NeuroERP" "Architecture OS — Structurizr C4 model (source of truth)" {

    !identifiers hierarchical

    model {
        user = person "Sachbearbeiter" "Annahme, Verkauf, Lager, FiBu"
        admin = person "Admin / IT" "Mandant, Deploy, Integrationen"
        mobileUser = person "Mobile Nutzer" "Waage, Annahme, CRM unterwegs"

        valeo = softwareSystem "VALEO NeuroERP" "Multi-Mandanten ERP Landhandel/Agrar" {
            frontend = container "frontend-web" "React/Vite" "Fachmasken, Flow Spine"
            bff = container "bff-web" "Node BFF" "MCP, Aggregation"
            sse = container "dev-sse" "Node SSE" "Event-Stream Dev"
            backend = container "backend" "FastAPI" "Modularer Monolith /api/v1"
            kiUsability = container "ki-usability" "FastAPI" "Action Registry, Voice"
            inventory = container "inventory-service" "FastAPI" "Lager Microservice"
            crmCluster = container "crm-* Cluster" "FastAPI x8" "CRM bounded context"
            dmsAdapter = container "dms-adapter" "FastAPI" "DMS Brücke"
            rations = container "rations-optimization" "Python" "Futtermittel LP"
            ai = container "ai" "Python" "AI Service optional profile"
            postgres = container "postgres" "PostgreSQL 15" "ERP + Keycloak DB" {
                tags "Database"
            }
            redis = container "redis" "Redis 7" "Cache, Sessions"
            nats = container "nats" "NATS JetStream" "Event Bus"
            keycloak = container "keycloak" "Keycloak 22" "OIDC"
            paperless = container "paperless" "Paperless-ngx" "DMS Slave"
        }

        l3 = softwareSystem "L3 Legacy" "Bestandssystem Waage, Kontrakte, Migration" {
            tags "External"
        }
        datev = softwareSystem "DATEV" "Steuerberater-Export, FiBu-Übergabe" {
            tags "External"
        }
        elster = softwareSystem "ELSTER / ERiC" "UStVA, eBilanz" {
            tags "External"
        }
        fiskaly = softwareSystem "Fiskaly / TSE" "KassenSichV, DSFinV-K" {
            tags "External"
        }
        superglue = softwareSystem "Superglue / Partner" "REST, EDI, MCP" {
            tags "External"
        }
        webshop = softwareSystem "Webshop / B2B" "Bestellimport" {
            tags "External"
        }
        bank = softwareSystem "Bank / FinTS" "Kontoauszug, Zahlungsverkehr" {
            tags "External"
        }
        waage = softwareSystem "Waagen / Hardware" "Wiegescheine, L3-Anbindung" {
            tags "External"
        }

        user -> valeo "Fachmasken, Flow Spine"
        admin -> valeo "Admin, Monitoring"
        mobileUser -> valeo "Mobile App, Waage"
        valeo -> l3 "Migration, Waage, Kontrakte"
        valeo -> datev "Export Buchungsstapel"
        valeo -> elster "UStVA, eBilanz Submit"
        valeo -> fiskaly "TSE Signatur POS"
        valeo -> superglue "Integrationen API/EDI"
        valeo -> webshop "B2B Orders"
        valeo -> bank "FinTS / CAMT"
        valeo -> waage "Wiegeschein-Daten"

        frontend -> bff "API / MCP"
        frontend -> backend "/api/v1 proxy"
        frontend -> sse "SSE"
        frontend -> keycloak "OIDC"
        bff -> backend "Backend API"
        backend -> postgres "SQLAlchemy"
        backend -> redis "Cache"
        backend -> nats "Outbox publish"
        backend -> inventory "HTTP"
        backend -> crmCluster "HTTP CRM_*"
        backend -> kiUsability "HTTP"
        backend -> dmsAdapter "HTTP"
        backend -> rations "HTTP"
        backend -> ai "HTTP optional"
        backend -> keycloak "Token validation"
        dmsAdapter -> paperless "REST API"
    }

    views {
        systemContext valeo "SystemContext" {
            include *
            autolayout lr
        }
        container valeo "ContainersDev" {
            include *
            autolayout lr
        }
    }
}
