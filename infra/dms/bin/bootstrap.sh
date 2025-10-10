#!/usr/bin/env bash
# Mayan-DMS Bootstrap Script
# Idempotent setup via REST-API für VALEO-NeuroERP

set -euo pipefail

# Colors für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Pfade
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
CFG="$ROOT/config/bootstrap.json"

# Load .env
if [ ! -f "$ENV_FILE" ]; then
  echo -e "${RED}❌ .env file not found. Copy env.example to .env first.${NC}"
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

# Config
BASE="${DMS_BASE:-http://localhost:8010}"
TOKEN="${DMS_BOOTSTRAP_TOKEN:?❌ Set DMS_BOOTSTRAP_TOKEN in .env}"

# Headers
AUTH="Authorization: Token ${TOKEN}"
JSON="Content-Type: application/json"

echo -e "${GREEN}🚀 VALEO-NeuroERP Mayan-DMS Bootstrap${NC}"
echo "Base-URL: $BASE"
echo "Config: $CFG"
echo ""

# Helper-Funktionen
get_all() { 
  curl -fsS -H "$AUTH" "$BASE$1"
}

post() { 
  curl -fsS -H "$AUTH" -H "$JSON" -X POST -d "$2" "$BASE$1"
}

# 1) Warten bis Mayan bereit ist
echo -e "${YELLOW}⏳ Waiting for Mayan to be ready...${NC}"
"$(dirname "$0")/wait-for-http.sh" "${BASE}/api/" 120

# IDs cachen
declare -A META_ID DOC_ID

# 2) Document Types anlegen
echo -e "${YELLOW}📄 Creating Document Types...${NC}"
doc_types_created=0

for dt in $(jq -r '.document_types[]' "$CFG"); do
  # Check if exists
  if ! get_all "/api/document_types/document_types/?page_size=1000" | jq -e --arg n "$dt" '.results[]|select(.label==$n)' >/dev/null 2>&1; then
    echo "Creating document type: $dt"
    post "/api/document_types/document_types/" "$(jq -n --arg label "$dt" '{label:$label}')" >/dev/null
    doc_types_created=$((doc_types_created + 1))
  else
    echo "Document type already exists: $dt"
  fi
  
  # Get ID
  id=$(get_all "/api/document_types/document_types/?page_size=1000" | jq -r --arg n "$dt" '.results[]|select(.label==$n)|.id' | head -n1)
  DOC_ID["$dt"]="$id"
done

echo -e "${GREEN}✅ Document Types: ${#DOC_ID[@]} total, $doc_types_created created${NC}"

# 3) Metadata Types anlegen
echo -e "${YELLOW}🏷️  Creating Metadata Types...${NC}"
meta_types_created=0

meta_count=$(jq '.metadata_types|length' "$CFG")
for i in $(seq 0 $((meta_count - 1))); do
  name=$(jq -r ".metadata_types[$i].name" "$CFG")
  label=$(jq -r ".metadata_types[$i].label" "$CFG")
  type=$(jq -r ".metadata_types[$i].type" "$CFG")
  required=$(jq -r ".metadata_types[$i].required // false" "$CFG")
  choices=$(jq -c ".metadata_types[$i].choices // []" "$CFG")
  
  # Check if exists
  if ! get_all "/api/metadata/metadata_types/?page_size=1000" | jq -e --arg n "$name" '.results[]|select(.name==$n)' >/dev/null 2>&1; then
    echo "Creating metadata type: $name"
    body=$(jq -n \
      --arg name "$name" \
      --arg label "$label" \
      --arg type "$type" \
      --argjson choices "$choices" \
      --argjson required "$required" \
      '{name:$name, label:$label, parser:"", default:"", lookup:"", validation:"", type:$type, required:$required, choices:$choices}')
    post "/api/metadata/metadata_types/" "$body" >/dev/null || true
    meta_types_created=$((meta_types_created + 1))
  else
    echo "Metadata type already exists: $name"
  fi
  
  # Get ID
  id=$(get_all "/api/metadata/metadata_types/?page_size=1000" | jq -r --arg n "$name" '.results[]|select(.name==$n)|.id' | head -n1)
  META_ID["$name"]="$id"
done

echo -e "${GREEN}✅ Metadata Types: ${#META_ID[@]} total, $meta_types_created created${NC}"

# 4) Metadata an DocumentTypes binden
echo -e "${YELLOW}🔗 Creating Metadata Bindings...${NC}"
bindings_created=0

for dt in "${!DOC_ID[@]}"; do
  bind_list=$(jq -r --arg dt "$dt" '.metadata_bindings[$dt][]?' "$CFG" 2>/dev/null || true)
  [ -z "$bind_list" ] && continue
  
  for m in $bind_list; do
    mid="${META_ID[$m]}"
    [ -z "$mid" ] && continue
    
    # Prüfe ob Binding bereits existiert
    exists=$(get_all "/api/metadata/document_type_metadata_types/?page_size=1000" | \
      jq -e --argjson dtid "${DOC_ID[$dt]}" --argjson mid "$mid" \
      '.results[]|select(.document_type==$dtid and .metadata_type==$mid)' 2>/dev/null || true)
    
    if [ -z "$exists" ]; then
      echo "Creating binding: $dt → $m"
      post "/api/metadata/document_type_metadata_types/" \
        "$(jq -n --argjson document_type "${DOC_ID[$dt]}" --argjson metadata_type "$mid" \
        '{document_type:$document_type, metadata_type:$metadata_type}')" >/dev/null || true
      bindings_created=$((bindings_created + 1))
    fi
  done
done

echo -e "${GREEN}✅ Metadata Bindings: $bindings_created created${NC}"

# 5) OCR-Konfiguration (Hinweis)
enable_ocr=$(jq -r '.ocr.enable' "$CFG")
if [ "$enable_ocr" = "true" ]; then
  languages=$(jq -r '.ocr.languages[]' "$CFG" | paste -sd "," -)
  echo -e "${YELLOW}ℹ️  OCR is active (languages: $languages)${NC}"
  echo "   Configure OCR backends in Mayan UI: Settings → OCR backends"
fi

# Summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✔ Mayan-DMS Bootstrap Complete${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Summary:"
echo "  Document Types: ${#DOC_ID[@]} ($doc_types_created created)"
echo "  Metadata Types: ${#META_ID[@]} ($meta_types_created created)"
echo "  Bindings: $bindings_created created"
echo ""
echo "Brand: ${VALEO_BRAND:-VALEO NeuroERP}"
echo "DMS URL: $BASE"
echo ""
echo -e "${GREEN}🎉 Mayan is ready for VALEO-NeuroERP integration!${NC}"

