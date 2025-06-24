# Usa a imagem correta para Azure Functions em Python com Docker
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# Define variáveis de ambiente obrigatórias
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Define diretório de trabalho
WORKDIR /home/site/wwwroot

# Copia todos os ficheiros da função para o container
COPY . .

# Instala dependências Python
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt
