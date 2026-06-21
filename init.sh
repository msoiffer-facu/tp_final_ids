#!/bin/bash

# init.sh - Inicializa el entorno virtual e instala dependencias
# Uso: ./init.sh

set -e  # Salir si hay algún error

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

echo -e "${YELLOW}=== Inicializando entorno del proyecto ===${NC}"

# 1. Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 no está instalado. Por favor instalá Python 3.${NC}"
    exit 1
fi

echo -e "${GREEN}✔ Python3 encontrado: $(python3 --version)${NC}"

# 2. Crear el entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creando entorno virtual en ./$VENV_DIR ...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✔ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✔ Entorno virtual ya existe en ./$VENV_DIR${NC}"
fi

# 3. Activar el entorno virtual
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✔ Entorno virtual activado${NC}"

# 4. Actualizar pip
echo -e "${YELLOW}Actualizando pip ...${NC}"
pip install --upgrade pip

# 5. Instalar dependencias desde requirements.txt
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${YELLOW}Instalando dependencias desde $REQUIREMENTS_FILE ...${NC}"
    pip install -r "$REQUIREMENTS_FILE"
    echo -e "${GREEN}✔ Dependencias instaladas correctamente${NC}"
else
    echo -e "${RED}Error: no se encontró el archivo $REQUIREMENTS_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}=== Iniciando Aplicaciones ===${NC}"

# 6. Iniciar Backend en segundo plano
echo -e "${YELLOW}Iniciando Backend...${NC}"
cd backend
python app_back.py &
BACKEND_PID=$! # Guarda el ID del proceso del backend
cd ..

# 7. Iniciar Frontend en segundo plano
echo -e "${YELLOW}Iniciando Frontend...${NC}"
cd frontend
python app_front.py &
FRONTEND_PID=$! # Guarda el ID del proceso del frontend
cd ..

echo ""
echo -e "${GREEN}=== Todo en marcha ===${NC}"
echo -e "Backend corriendo con PID: ${YELLOW}$BACKEND_PID${NC}"
echo -e "Frontend corriendo con PID: ${YELLOW}$FRONTEND_PID${NC}"
echo ""
echo -e "${RED}Presioná Ctrl+C para apagar ambos servidores y salir.${NC}"

# Función para apagar los servidores cuando aprietes Ctrl+C
trap "echo -e '${YELLOW}\nApagando servidores...${NC}'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Se queda esperando para que la terminal no se cierre
wait
