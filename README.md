# 🖤 RGB2Gray

A aplicação **RGB2Gray** é responsável por **converter imagens em escala de cinza** recebidas de múltiplos gateways de câmera e **publicar novamente os frames processados** via RabbitMQ. Além disso, fornece **observabilidade** por meio de integração com o Zipkin, permitindo análise de desempenho da aplicação em tempo real, como **tempo de processamento** e **taxa de frames por segundo (FPS)**.

---

## 📌 Objetivo

Este serviço foi desenvolvido para:

- **Consumir imagens RGB** enviadas por quatro gateways de câmera, nos tópicos:
  ```
  CameraGateway.{camera_id}.Frame  (onde camera_id ∈ [1, 4])
  ```

- **Converter essas imagens para escala de cinza** usando OpenCV.

- **Publicar os frames convertidos** nos tópicos:
  ```
  GrayCam.{camera_id}
  ```

- **Exportar métricas de desempenho** como atributos de tracing para o **Zipkin**, incluindo:
  - Tempo de processamento por imagem
  - Quantidade de frames processados por segundo (FPS)

---

## ⚙️ Arquitetura

- **Linguagem:** Python
- **Mensageria:** RabbitMQ (via is-wire)
- **Tracing:** OpenCensus + Zipkin
- **Execução:** Kubernetes (1 pod)
- **Publicação por tópico:** Um canal para cada câmera (4 câmeras suportadas)

---

## 📁 Estrutura dos Arquivos

| Arquivo             | Descrição |
|---------------------|----------|
| `rgb2gray.py`       | Código principal da aplicação: conversão e publicação de imagens em cinza |
| `streamChannel.py`  | Canal especializado para consumir **apenas o último frame** de um tópico |
| `Dockerfile`        | Imagem Docker da aplicação |
| `rgb2gray.yaml`     | Deployment e variáveis de ambiente para execução no Kubernetes |

---

## 🧠 Explicação dos Componentes

### `rgb2gray.py`
- Inicializa conexões com o broker RabbitMQ.
- Cria um `StreamChannel` para cada câmera (1 a 4).
- Consome a **última imagem disponível** por canal (evita backlog).
- Converte a imagem RGB para escala de cinza usando `cv2.cvtColor`.
- Publica o frame em `GrayCam.{camera_id}`.
- Utiliza `OpenCensus` para exportar:
  - Tempo de processamento individual
  - Quantidade de frames processados por segundo (FPS)

### `streamChannel.py`
Extensão da classe `Channel` do `is-wire`, com um método adicional `consume_last()` que:

- Consome todas as mensagens de um tópico.
- Retorna **apenas a última** disponível, descartando as anteriores.
- Ideal para aplicações de vídeo, onde o frame mais recente é o mais relevante.

---

## 📦 Dependências

Listadas no `requirements.txt` (implícito no Dockerfile):

```
six==1.16.0
is-wire==1.2.1
is-msgs==1.1.18
numpy
opencv-python-headless
protobuf==3.20.3
opencensus==0.5.0
opencensus-ext-zipkin==0.2.1
vine==5.1.0
```

---

## ☁️ Execução no Kubernetes

### Pré-requisitos

- Cluster Kubernetes ativo
- RabbitMQ acessível com os tópicos de entrada
- Serviço Zipkin acessível para coleta de traces
- `kubectl` configurado corretamente

### Deploy

A aplicação pode ser executada com:

```bash
kubectl apply -f rgb2gray.yaml
```

O arquivo `yaml` define:

- Um `Deployment` com **1 pod**
- As variáveis de ambiente, como o endereço do Zipkin, por exemplo:

```yaml
env:
  - name: ZIPKIN_URL
    value: http://zipkin:30200
```

---

## 🔍 Observabilidade

A cada frame processado, são exportados os seguintes atributos para o **Zipkin**:

- `Tempo de Processamento (ms)`: tempo necessário para converter a imagem
- `FPS`: quantidade de imagens processadas no último segundo

Essa visibilidade permite **ajustar dinamicamente os recursos** (CPU/memória) e verificar seu impacto no desempenho.

---

## ✅ Características

- Processamento contínuo e em tempo real
- Baixa latência: consome apenas o frame mais recente
- Pronto para escalonamento horizontal (um pod por câmera, se necessário)
- Leve, eficiente e altamente observável

---

## 🧪 Teste Local

Você pode rodar localmente com:

```bash
python3 rgb2gray.py
```

Garanta que as variáveis como `broker_uri` e `zipkin_url` estejam configuradas no código ou via ambiente.

---

## 📬 Contato

Para dúvidas ou contribuições, entre em contato com o time do **LabSEA**.
