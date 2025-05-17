# Use a imagem base Python
FROM python:3.9-slim

# Defina o diretório de trabalho na imagem
WORKDIR /app

# Copie o código da sua aplicação para o diretório de trabalho
COPY . /app/

# Instale as dependências necessárias
RUN pip install --upgrade pip \
    --no-cache-dir \
    six==1.16.0 \
    is-wire==1.2.1 \
    is-msgs==1.1.18 \
    numpy \
    opencv-python-headless \
    protobuf==3.20.3 \
    opencensus==0.5.0 \
    opencensus-ext-zipkin==0.2.1 \
    vine==5.1.0

# Defina a variável de ambiente para o Zipkin
ENV ZIPKIN_HOST "10.244.6.3:9411"

# Comando para executar a aplicação
CMD ["python", "rgb2gray.py"]
