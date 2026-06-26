# Plano de Desenvolvimento do Projeto

## Etapa 0 — Concepção da pesquisa e do experimento

### 0.1 Definição do problema de pesquisa

* [x] Realizar a análise do estado da arte
* [x] Identificar a lacuna de pesquisa
* [x] Formular a pergunta de pesquisa
* [x] Definir os objetivos
* [x] Formular as hipóteses
* [x] Definir as contribuições esperadas

### 0.2 Definição da metodologia

* [x] Definir o tipo de pesquisa
* [x] Definir o delineamento experimental
* [x] Definir as variáveis do estudo
* [x] Definir as métricas de avaliação
* [x] Definir os métodos de análise dos resultados
* [x] Definir os critérios de validade da pesquisa

### 0.3 Especificação do experimento

* [x] Definir o protocolo experimental
* [x] Definir os participantes e/ou conjuntos de dados
* [x] Definir os materiais e instrumentos
* [x] Definir o procedimento de coleta de dados
* [x] Definir o plano de análise dos dados

### 0.4 Planejamento da execução

* [x] Definir os requisitos do artefato
* [x] Elaborar o plano de desenvolvimento
* [x] Identificar os recursos necessários

## Etapa 1 — Configuração inicial do ambiente e estrutura do projeto

### 1.1 Configuração do ambiente

* [x] Configurar Docker
* [x] Definir versão do Python
* [x] Criar `requirements.txt`
* [x] Configurar Git e GitHub
* [x] Definir padrão de versionamento
* [x] Configurar estrutura de diretórios

### 1.2 Estrutura do projeto

* [x] Criar estrutura de módulos (`src`)
    - [x] Pré Processamento
    - [x] Transformações
    - [x] Métricas
    - [x] Experimento
* [x] Criar diretório de documentação
* [x] Criar diretório de dados
    - [x] Dados brutos
    - [x] Dados processados
    - [x] Dados resultados
* [x] Criar diretório de notebooks
* [x] Criar `.gitignore`
* [x] Criar diretório de configurações
    - [x] Criar `default.yaml`
* [x] Criar script principal de execução

### 1.3 Reprodutibilidade

* [ ] Documentar ambiente
* [ ] Registrar versões das bibliotecas
* [ ] Definir política de seeds
* [ ] Documentar processo de execução

---

# Etapa 2 — Pré-processamento dos dados

## 2.1 Carregamento do dataset

* [ ] Baixar POP909
* [ ] Organizar estrutura dos dados
* [ ] Implementar carregamento dos arquivos MIDI
* [ ] Validar integridade dos arquivos

## 2.2 Limpeza dos dados

* [ ] Identificar arquivos inválidos
* [ ] Padronizar tempos (tempo map)
* [ ] Padronizar resolução temporal
* [ ] Remover inconsistências

## 2.3 Preparação dos dados

* [ ] Selecionar subconjunto do dataset
* [ ] Extrair trechos de 8/16 compassos
* [ ] Salvar segmentos processados
* [ ] Registrar metadados dos segmentos

## 2.4 Extração das representações musicais

* [ ] Extrair melodia
* [ ] Extrair harmonia
* [ ] Extrair ritmo
* [ ] Validar representações extraídas

---

# Etapa 3 — Transformações musicais controladas

## 3.1 Transformações melódicas

* [ ] Transposição
* [ ] Alteração de intervalos
* [ ] Ornamentação
* [ ] Simplificação melódica

## 3.2 Transformações harmônicas

* [ ] Substituição de acordes
* [ ] Reharmonização
* [ ] Simplificação harmônica

## 3.3 Transformações rítmicas

* [ ] Alteração de andamento
* [ ] Escalonamento de durações
* [ ] Alteração parcial do ritmo

## 3.4 Transformações combinadas

* [ ] Melodia + Harmonia
* [ ] Melodia + Ritmo
* [ ] Harmonia + Ritmo
* [ ] Melodia + Harmonia + Ritmo

## 3.5 Validação

* [ ] Verificar preservação dos componentes esperados
* [ ] Registrar parâmetros utilizados

---

# Etapa 4 — Implementação das métricas de similaridade

## 4.1 Métricas melódicas

* [ ] Interval N-Gram Similarity
* [ ] Longest Common Subsequence (LCS)
* [ ] Edit Distance

## 4.2 Métricas harmônicas

* [ ] Chord N-Gram Similarity
* [ ] Edit Distance Harmônica
* [ ] Pitch Class Similarity

## 4.3 Métricas rítmicas

* [ ] Rhythm N-Gram Similarity
* [ ] IOI Similarity
* [ ] Edit Distance Rítmica

## 4.4 Métrica global

* [ ] Média simples
* [ ] Média ponderada
* [ ] Configuração de pesos

## 4.5 Testes

* [ ] Testes unitários
* [ ] Testes de consistência
* [ ] Validação contra casos conhecidos

---

# Etapa 5 — Execução do experimento

## 5.1 Formação dos pares

* [ ] Gerar pares positivos
* [ ] Gerar pares negativos
* [ ] Balancear o conjunto experimental

## 5.2 Execução das métricas

* [ ] Calcular similaridade melódica
* [ ] Calcular similaridade harmônica
* [ ] Calcular similaridade rítmica
* [ ] Calcular similaridade global

## 5.3 Avaliação da robustez

* [ ] Precision
* [ ] Recall
* [ ] F1-score
* [ ] False Negative Rate
* [ ] Queda de similaridade

## 5.4 Avaliação da interpretabilidade

* [ ] Comparação entre componente transformado e escores
* [ ] Comparação entre métricas individuais e global
* [ ] Registro das evidências interpretativas

---

# Etapa 6 — Análise e apresentação dos resultados

## 6.1 Consolidação dos resultados

* [ ] Gerar tabelas 
* [ ] Organizar resultados por experimento
* [ ] Consolidar estatísticas

## 6.2 Visualização

* [ ] Gráficos de distribuição
* [ ] Comparação entre métricas
* [ ] Heatmaps
* [ ] Boxplots

## 6.3 Análise estatística

* [ ] Testes de significância
* [ ] Comparação entre abordagens
* [ ] Discussão dos resultados

## 6.4 Reprodutibilidade

* [ ] Validar execução completa
* [ ] Atualizar documentação
* [ ] Registrar configurações finais
* [ ] Preparar artefatos para publicação

## 6.5 Artigo científico

* [ ] Gerar tabelas do artigo
* [ ] Gerar figuras do artigo
* [ ] Revisar metodologia
* [ ] Revisar seção experimental
* [ ] Revisar ameaças à validade
* [ ] Preparar material suplementar
