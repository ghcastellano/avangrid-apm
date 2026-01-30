# 📋 PLANO DE IMPLEMENTAÇÃO - AVANGRID APM WEB APPLICATION

## 🎯 VISÃO GERAL

Transformar o gerador de Excel atual em uma aplicação web moderna e interativa com capacidades de IA para análise de aplicações, apresentação de insights e suporte à consultoria.

---

## 🏗️ ARQUITETURA TÉCNICA PROPOSTA

### Stack Tecnológica

**Opção A - Manter Python Ecosystem (RECOMENDADA)**
- **Frontend**: Streamlit + Custom Components (ou migrar para Dash/Reflex)
- **Backend**: FastAPI + Python 3.14
- **IA/ML**: OpenAI API + LangChain para análise inteligente
- **Banco de Dados**: SQLite (desenvolvimento) → PostgreSQL (produção)
- **Visualizações**: Plotly + Altair (interativos)
- **Processamento**: Pandas + openpyxl (já existente)

**Opção B - Stack Moderna Full JavaScript**
- **Frontend**: Next.js 14 + React + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: Node.js + Express/Fastify
- **IA/ML**: OpenAI API + Vercel AI SDK
- **Banco de Dados**: PostgreSQL + Prisma ORM
- **Visualizações**: Recharts + D3.js
- **Processamento Excel**: ExcelJS ou SheetJS

**SUPOSIÇÃO**: Recomendo **Opção A** pois:
1. Aproveita todo o código existente (app.py, generate_apm_strategic.py)
2. Lógica de scoring e análise já está madura em Python
3. Integração com openpyxl é robusta
4. Mais rápido para implementar (menos reescrita)
5. Time provavelmente tem mais familiaridade com Python

**PERGUNTA**: Qual stack prefere? Python (mais rápido, aproveita código) ou JavaScript (mais moderno para web)?

---

## 📊 ESTRUTURA DE DADOS E BANCO DE DADOS

### Modelo de Dados

```sql
-- Tabela de Aplicações
applications (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  safe_name VARCHAR(255),
  is_green BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Tabela de Respostas do Questionário Original
questionnaire_answers (
  id UUID PRIMARY KEY,
  application_id UUID REFERENCES applications(id),
  question_text TEXT,
  answer_text TEXT,
  score INTEGER CHECK (score BETWEEN 1 AND 5),
  synergy_block VARCHAR(50),
  created_at TIMESTAMP
)

-- Tabela de Transcripts de Reuniões
meeting_transcripts (
  id UUID PRIMARY KEY,
  application_id UUID REFERENCES applications(id),
  file_name VARCHAR(255),
  transcript_text TEXT,
  upload_date TIMESTAMP,
  processed BOOLEAN DEFAULT FALSE
)

-- Tabela de Respostas Extraídas de Transcripts (NOVO)
transcript_answers (
  id UUID PRIMARY KEY,
  application_id UUID REFERENCES applications(id),
  transcript_id UUID REFERENCES meeting_transcripts(id),
  question_text TEXT,
  answer_text TEXT,
  confidence_score DECIMAL(3,2), -- 0.00 a 1.00
  extraction_method VARCHAR(50), -- 'ai_extraction', 'keyword_match', etc.
  synergy_block VARCHAR(50),
  created_at TIMESTAMP
)

-- Tabela de Scores dos Blocos de Sinergia
synergy_scores (
  id UUID PRIMARY KEY,
  application_id UUID REFERENCES applications(id),
  block_name VARCHAR(50),
  score INTEGER CHECK (score BETWEEN 1 AND 5),
  suggested_by VARCHAR(20), -- 'manual', 'ai_questionnaire', 'ai_transcript'
  confidence DECIMAL(3,2),
  rationale TEXT,
  created_at TIMESTAMP,
  approved_by VARCHAR(100),
  approved_at TIMESTAMP
)

-- Tabela de Insights Gerados
insights (
  id UUID PRIMARY KEY,
  application_id UUID REFERENCES applications(id),
  insight_type VARCHAR(50), -- 'integration', 'technology_update', 'consolidation', 'risk', etc.
  title VARCHAR(255),
  description TEXT,
  priority VARCHAR(20), -- 'P1', 'P2', 'P3'
  recommendation VARCHAR(20), -- 'EVOLVE', 'INVEST', 'MAINTAIN', 'ELIMINATE'
  supporting_data JSONB, -- Dados estruturados que embasam o insight
  created_at TIMESTAMP
)

-- Tabela de Histórico de Perguntas (Q&A IA)
qa_history (
  id UUID PRIMARY KEY,
  user_question TEXT,
  ai_response TEXT,
  context_applications JSONB, -- IDs das aplicações relevantes
  sources JSONB, -- Referências usadas na resposta
  response_time_ms INTEGER,
  created_at TIMESTAMP,
  user_feedback VARCHAR(20) -- 'helpful', 'not_helpful', null
)
```

---

## 🎨 DESIGN E INTERFACE (UI/UX)

### Design System

**Paleta de Cores (baseada na identidade Avangrid)**
- Primary: `#E87722` (Laranja Avangrid)
- Secondary: `#0066B3` (Azul corporativo)
- Success: `#10B981` (Verde - EVOLVE)
- Warning: `#F59E0B` (Amarelo - INVEST)
- Info: `#3B82F6` (Azul - MAINTAIN)
- Danger: `#EF4444` (Vermelho - ELIMINATE)
- Neutral: `#444444` / `#F3F4F6` / `#FFFFFF`

**Tipografia**
- Títulos: Inter ou Poppins (Bold)
- Corpo: Inter ou System UI (Regular/Medium)
- Monospace: JetBrains Mono (para dados técnicos)

**Componentes UI**
- Sidebar navegação fixa com acordeão
- Cards com glassmorphism e sombras suaves
- Gráficos interativos com tooltips
- Animações sutis (fade-in, slide, hover effects)
- Loading states e skeleton screens
- Toasts para feedback de ações

### Estrutura de Navegação (Menu Lateral)

```
📊 AVANGRID APM PLATFORM
├── 🏠 Dashboard
│   ├── Overview (Cards com métricas)
│   ├── Portfolio Matrix (2x2 BVI vs THI)
│   └── Quick Actions
│
├── 📤 Uploads
│   ├── Upload Questionário (.xlsx)
│   └── Upload Transcripts (múltiplos .txt/.docx/.pdf)
│
├── 📱 Aplicações
│   ├── Lista de Aplicações (cards ou tabela)
│   └── [Detalhes por Aplicação]
│       ├── Executive Scorecard (8 blocos)
│       ├── Perguntas & Respostas
│       │   ├── Aba: Questionário Original
│       │   ├── Aba: Respostas dos Transcripts
│       │   └── Comparação lado a lado
│       ├── Scores Sugeridos (com aprovação)
│       └── Timeline/Histórico
│
├── 📈 Análises
│   ├── Calculadora (BVI/THI por aplicação)
│   ├── Dashboard Estratégico (scatter plot)
│   ├── Strategic Roadmap (P1/P2/P3)
│   ├── Application Groups (categorias funcionais)
│   └── Value Chain (cadeia de valor utility)
│
├── 💡 Insights
│   ├── Insights Automáticos (cards com gráficos)
│   ├── Oportunidades de Integração
│   ├── Análise de Tecnologia
│   ├── Riscos e Conformidade
│   └── Recomendações Financeiras
│
├── 🤖 Assistente IA (Q&A)
│   ├── Chat interface
│   ├── Sugestões de perguntas
│   └── Histórico de conversas
│
├── 📚 Metodologia
│   ├── Introdução
│   ├── Blocos de Sinergia (definições)
│   ├── Sistema de Scoring
│   └── Matriz de Recomendação
│
└── ⚙️ Configurações
    ├── Gerenciar Perguntas Mestras
    ├── Configurar Pesos dos Blocos
    ├── API Keys (OpenAI)
    └── Exportar para Excel
```

**SUPOSIÇÃO**: Menu lateral será collapsible (pode recolher) para ganhar espaço em tela. Aplicações individuais terão sub-navegação em tabs.

---

## 🚀 FUNCIONALIDADES POR FASE

### **FASE 1 - Fundação & Migração UI** (2-3 semanas)

#### 1.1 Setup da Arquitetura
- [ ] Criar estrutura de pastas (frontend/backend/db)
- [ ] Configurar banco de dados (SQLite local + migrations)
- [ ] Setup FastAPI com endpoints base
- [ ] Configurar Streamlit com custom theme ou migrar para framework escolhido

#### 1.2 Interface Base
- [ ] Implementar layout com sidebar navigation
- [ ] Criar componentes reutilizáveis (Card, Button, Table, Chart)
- [ ] Aplicar design system (cores, tipografia, espaçamento)
- [ ] Adicionar animações e transições suaves

#### 1.3 Upload de Questionário (Migração)
- [ ] Migrar funcionalidade existente de upload
- [ ] Parsear Excel e popular banco de dados
- [ ] Exibir lista de aplicações encontradas
- [ ] Visualizar respostas do questionário por aplicação

#### 1.4 Visualizações Básicas
- [ ] Dashboard com cards de métricas (total apps, BVI médio, THI médio)
- [ ] Lista de aplicações com filtros
- [ ] Página de detalhes de aplicação (scorecard + Q&A)

---

### **FASE 2 - Análise de Transcripts com IA** (3-4 semanas)

#### 2.1 Upload de Transcripts
- [ ] Interface para upload múltiplo de arquivos
- [ ] Suporte a .txt, .docx, .pdf
- [ ] Associar transcripts a aplicações específicas
- [ ] Armazenar transcripts no banco

#### 2.2 Processamento com IA
- [ ] Integrar OpenAI API (GPT-4 ou GPT-4-turbo)
- [ ] Criar prompts para extração de respostas:
  ```
  Prompt Template:
  "Você é um consultor especialista em assessment de aplicações.
  Analise o seguinte transcript de reunião e extraia respostas para
  as perguntas do framework APM. Para cada pergunta, identifique:
  1. A resposta encontrada no transcript
  2. Nível de confiança (0-1)
  3. Trecho do transcript que embasa a resposta

  Perguntas: [lista das 60+ perguntas mestras]
  Transcript: [texto do transcript]

  Formato de saída: JSON estruturado"
  ```
- [ ] Processar transcripts em background (task queue)
- [ ] Armazenar respostas extraídas com confidence score

#### 2.3 Visualização de Respostas
- [ ] Exibir respostas do questionário vs. respostas dos transcripts lado a lado
- [ ] Destacar divergências e complementaridades
- [ ] Permitir edição manual e aprovação de respostas
- [ ] Mostrar nível de confiança da IA (badges coloridos)

#### 2.4 Sugestão Automática de Scores
- [ ] Criar função de análise de respostas (questionnaire + transcripts)
- [ ] Aplicar lógica de scoring existente + melhorias com IA
- [ ] Gerar score sugerido para cada bloco de sinergia
- [ ] Para perguntas sem resposta: score = 1 (conforme solicitado)
- [ ] Exibir rationale (justificativa) do score sugerido
- [ ] Permitir aprovação/rejeição/edição pelo consultor

**SUPOSIÇÃO**: A análise de transcripts será profunda, considerando:
- Contexto completo da conversa
- Sentimento e tom das respostas
- Menções implícitas (ex: "temos problemas frequentes" → baixo score em Maintainability)
- Cross-referencing entre diferentes perguntas
- Análise de padrões (ex: menções a "legacy", "manual", "workarounds")

---

### **FASE 3 - Análises e Visualizações Avançadas** (2-3 semanas)

#### 3.1 Calculadora Interativa
- [ ] Recriar lógica da aba "Calculator" do Excel
- [ ] Calcular BVI e THI automaticamente
- [ ] Exibir fórmulas e pesos de forma transparente
- [ ] Permitir ajustes de pesos (if needed)

#### 3.2 Dashboard Estratégico
- [ ] Criar scatter plot interativo (BVI vs THI)
- [ ] Dividir em 4 quadrantes (EVOLVE/INVEST/MAINTAIN/ELIMINATE)
- [ ] Tooltips com detalhes ao hover
- [ ] Filtros por categoria, OPCO, criticidade
- [ ] Drill-down ao clicar em um ponto

#### 3.3 Strategic Roadmap
- [ ] Tabela interativa com todas as aplicações
- [ ] Colunas: Nome, BVI, THI, Recomendação, Prioridade (P1/P2/P3)
- [ ] Permitir drag-and-drop para priorização
- [ ] Filtros e ordenação
- [ ] Exportar roadmap para Excel/PDF

#### 3.4 Application Groups & Value Chain
- [ ] Visualizar aplicações agrupadas por função
- [ ] Visualizar por cadeia de valor (Generation, Transmission, Distribution, etc.)
- [ ] Gráficos de barras/donut por categoria
- [ ] Análise de redundâncias e gaps

---

### **FASE 4 - Insights Inteligentes com IA** (3-4 semanas)

#### 4.1 Geração de Insights
- [ ] Criar módulo de análise de insights com IA
- [ ] Prompts especializados por tipo de insight:

**Tipos de Insights a Gerar:**

1. **Oportunidades de Integração**
   - Identificar aplicações com sobreposição funcional
   - Sugerir consolidações
   - Estimar benefícios (redução de custos, simplificação)

2. **Planos de Absorção**
   - Para apps marcados como "ELIMINATE", sugerir:
     - Qual aplicação pode absorver as funcionalidades
     - Mapeamento de funcionalidades
     - Roadmap de migração
     - Riscos e dependências

3. **Atualizações Tecnológicas**
   - Identificar apps com tech stack obsoleto
   - Sugerir modernização (cloud, microservices, etc.)
   - Avaliar viabilidade e ROI

4. **Análise de Riscos**
   - Identificar apps críticos com baixo THI
   - Apontar gaps de segurança, conformidade
   - Priorizar ações de mitigação

5. **Análise Financeira**
   - Identificar apps com TCO alto e valor baixo
   - Oportunidades de renegociação de licenças
   - Comparar custo vs. valor entregue

6. **Análise de Dependências**
   - Mapa de integrações críticas
   - Identificar single points of failure
   - Sugerir desacoplamento

#### 4.2 Visualização de Insights
- [ ] Cards de insights com ícones e cores
- [ ] Gráficos de suporte (antes/depois, comparações)
- [ ] Textos curtos e acionáveis
- [ ] Links para aplicações relacionadas
- [ ] Exportar insights para apresentação

---

### **FASE 5 - Assistente IA (Q&A)** (2 semanas)

#### 5.1 Interface de Chat
- [ ] Chat UI moderna (estilo ChatGPT)
- [ ] Input de texto com autocomplete
- [ ] Histórico de conversas
- [ ] Sugestões de perguntas frequentes

#### 5.2 Backend de IA
- [ ] Integrar OpenAI API com contexto completo
- [ ] Criar RAG (Retrieval-Augmented Generation) para buscar dados relevantes
- [ ] Embeddings de respostas para busca semântica
- [ ] Prompt engineering para respostas contextualizadas

**Exemplos de Perguntas que o Assistente Deve Responder:**
- "Quais aplicações são candidatas a consolidação?"
- "Qual o custo total das aplicações legadas?"
- "Quais apps têm problemas de segurança?"
- "Como a aplicação X se integra com Y?"
- "Qual o impacto de eliminar a aplicação Z?"
- "Quais apps deveríamos priorizar para modernização?"

#### 5.3 Respostas Contextualizadas
- [ ] Buscar respostas nos dados reais (não inventar)
- [ ] Citar fontes (qual aplicação, qual resposta, qual transcript)
- [ ] Incluir gráficos e tabelas nas respostas quando apropriado
- [ ] Permitir follow-up questions
- [ ] Feedback do usuário (útil/não útil)

**SUPOSIÇÃO**: O assistente IA será construído com RAG para garantir respostas baseadas em dados reais, não alucinações. Usará embeddings (OpenAI text-embedding-3-small) para busca semântica eficiente.

---

### **FASE 6 - Metodologia e Exportações** (1-2 semanas)

#### 6.1 Seção de Metodologia
- [ ] Migrar conteúdo das abas Introduction, Methodology, User Guide
- [ ] Formato de documentação navegável
- [ ] Vídeos explicativos (opcional)
- [ ] Glossário de termos

#### 6.2 Exportação para Excel
- [ ] Manter funcionalidade de gerar Excel completo
- [ ] Botão de exportação em múltiplos pontos
- [ ] Incluir todos os dados + insights gerados
- [ ] Formato idêntico ao Excel atual (compatibilidade)

#### 6.3 Exportação para Apresentação
- [ ] Gerar slides (PowerPoint/Google Slides/PDF)
- [ ] Templates profissionais
- [ ] Incluir gráficos, insights, recomendações
- [ ] Customização de conteúdo

---

### **FASE 7 - Polimento e Otimizações** (2 semanas)

#### 7.1 Performance
- [ ] Otimizar queries de banco
- [ ] Cache de respostas da IA
- [ ] Lazy loading de componentes
- [ ] Compressão de assets

#### 7.2 UX/UI Refinements
- [ ] Testes de usabilidade
- [ ] Ajustes de responsividade (mobile/tablet)
- [ ] Acessibilidade (WCAG 2.1)
- [ ] Dark mode (opcional)

#### 7.3 Testes
- [ ] Testes unitários (backend)
- [ ] Testes de integração
- [ ] Testes end-to-end
- [ ] Testes de carga (performance)

#### 7.4 Documentação
- [ ] Documentação técnica (API, banco)
- [ ] Manual do usuário
- [ ] Guia de troubleshooting
- [ ] Vídeos tutoriais

---

## 🔄 FLUXO DE DADOS COMPLETO

```
1. ENTRADA DE DADOS
   ├─ Upload Questionário Excel
   │  └─ Parser → Banco (applications, questionnaire_answers)
   │
   └─ Upload Transcripts
      └─ Processar com IA → Extrair respostas → Banco (transcript_answers)

2. PROCESSAMENTO IA
   ├─ Análise de Respostas (questionnaire + transcripts)
   │  └─ Gerar Scores Sugeridos → Banco (synergy_scores)
   │
   └─ Geração de Insights
      └─ Análise multi-dimensional → Banco (insights)

3. CÁLCULOS
   ├─ BVI = média ponderada blocos Business
   └─ THI = média ponderada blocos Tech

4. VISUALIZAÇÕES
   ├─ Dashboard (cards, métricas)
   ├─ Scatter Plot (BVI vs THI)
   ├─ Roadmap (priorização)
   └─ Insights (cards + gráficos)

5. INTERAÇÃO IA (Q&A)
   ├─ Pergunta do usuário
   ├─ RAG: buscar dados relevantes (embeddings)
   ├─ GPT-4: gerar resposta contextualizada
   └─ Resposta + fontes

6. EXPORTAÇÃO
   ├─ Excel completo (formato original)
   └─ Apresentação (slides com insights)
```

---

## 🛠️ TECNOLOGIAS E BIBLIOTECAS DETALHADAS

### Backend (Python - Opção A)
```python
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9

# Excel Processing
openpyxl==3.1.2
pandas==2.2.0
xlsxwriter==3.1.9

# IA/ML
openai==1.10.0
langchain==0.1.4
langchain-openai==0.0.5
tiktoken==0.5.2
chromadb==0.4.22  # Vector DB para RAG

# Data Processing
numpy==1.26.3
python-docx==1.1.0  # Para .docx
PyPDF2==3.0.1  # Para PDF
```

### Frontend (Python - Opção A)
```python
# UI Framework
streamlit==1.30.0
streamlit-extras==0.3.6
streamlit-option-menu==0.3.6

# Visualizations
plotly==5.18.0
altair==5.2.0

# Utils
python-dotenv==1.0.0
pydantic==2.5.3
```

### Frontend (JavaScript - Opção B)
```json
{
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "typescript": "5.3.3",
    "tailwindcss": "3.4.1",
    "shadcn/ui": "latest",
    "recharts": "2.10.3",
    "d3": "7.8.5",
    "axios": "1.6.5",
    "openai": "4.24.1",
    "exceljs": "4.4.0"
  }
}
```

---

## 📝 SUPOSIÇÕES E DECISÕES DE DESIGN

### Suposições Feitas:

1. **Análise Profunda de Transcripts**: A IA não fará análise superficial. Usará:
   - Contextualização completa da conversa
   - Análise de sentimento
   - Identificação de menções implícitas
   - Cross-referencing entre perguntas

2. **Scores para Perguntas Sem Resposta**: Conforme solicitado, quando não houver resposta no grupo de sinergia, o score será 1.

3. **Navegação por Aplicações**: Proponho ter menu principal com "Aplicações" e ao clicar, abre lista. Ao selecionar uma aplicação, abre página de detalhes com tabs (Scorecard, Q&A, Scores Sugeridos). **Isso evita ter 20+ itens no menu lateral.**

4. **Aprovação de Scores**: Consultores poderão revisar scores sugeridos pela IA antes de finalizar. Haverá flag de "aprovado" vs "sugerido".

5. **Multilingual**: Manteremos suporte a inglês/português como já existe.

6. **Exportação Excel**: Manteremos compatibilidade com formato atual para não quebrar fluxos existentes.

### Decisões Técnicas:

1. **RAG para Q&A**: Usaremos Retrieval-Augmented Generation para garantir que o assistente IA responda com base em dados reais.

2. **Embeddings**: OpenAI text-embedding-3-small para vetorização de respostas (busca semântica).

3. **Async Processing**: Processamento de transcripts será assíncrono (background tasks) para não travar UI.

4. **Cache**: Respostas da IA serão cacheadas para economizar custos e melhorar performance.

---

## 🎯 ENTREGAS POR FASE

| Fase | Duração | Entregas |
|------|---------|----------|
| Fase 1 | 2-3 semanas | Interface base funcional, upload de questionário, visualizações básicas |
| Fase 2 | 3-4 semanas | Upload de transcripts, extração IA de respostas, sugestão de scores |
| Fase 3 | 2-3 semanas | Calculadora, Dashboard 2x2, Roadmap, grupos e value chain |
| Fase 4 | 3-4 semanas | Módulo de insights com IA (6 tipos de análises) |
| Fase 5 | 2 semanas | Assistente IA com chat interface e RAG |
| Fase 6 | 1-2 semanas | Metodologia, exportações para Excel/PPT |
| Fase 7 | 2 semanas | Polimento, testes, documentação |
| **TOTAL** | **15-20 semanas** | **Aplicação web completa e produção-ready** |

---

## ❓ PERGUNTAS PARA VALIDAÇÃO

Antes de iniciar a implementação, preciso de suas decisões sobre:

### 1. Stack Tecnológica
**Qual stack prefere?**
- [ ] **Opção A**: Python (Streamlit/FastAPI) - Mais rápido, aproveita código existente
- [ ] **Opção B**: JavaScript (Next.js/React) - Mais moderno, melhor para web
- [ ] Outra sugestão?

### 2. Navegação de Aplicações
**Como prefere navegar pelas aplicações individuais?**
- [ ] **Opção A**: Menu lateral com lista de todas as aplicações (pode ficar longo)
- [ ] **Opção B**: Menu "Aplicações" que abre lista/grid, depois página de detalhes (RECOMENDADO)
- [ ] **Opção C**: Outra abordagem?

### 3. OpenAI API
**Você já tem API key da OpenAI?**
- [ ] Sim, já tenho
- [ ] Não, preciso criar
- [ ] Prefere usar outro modelo (Azure OpenAI, Claude, etc.)?

### 4. Hospedagem/Deploy
**Onde pretende hospedar a aplicação?**
- [ ] Local (uso interno)
- [ ] Cloud (AWS, Azure, GCP)
- [ ] Heroku/Vercel/Railway
- [ ] Ainda não definido

### 5. Priorização
**Alguma fase específica que seja mais crítica/urgente?**
- [ ] Priorizar análise de transcripts (Fase 2)
- [ ] Priorizar insights (Fase 4)
- [ ] Priorizar Q&A (Fase 5)
- [ ] Seguir ordem sequencial do plano

### 6. Inovações/Sugestões
**Posso implementar estas melhorias adicionais?**
- [ ] Dark mode
- [ ] Comparação de cenários (what-if analysis)
- [ ] Alertas automáticos (ex: "App X tem licença vencendo em 30 dias")
- [ ] Collaborative features (múltiplos consultores editando)
- [ ] Versionamento de assessments (histórico de mudanças)

---

## 🚦 PRÓXIMOS PASSOS

Após sua aprovação do plano:

1. **Confirmar decisões** (stack, navegação, hospedagem)
2. **Criar branch de desenvolvimento** no Git
3. **Setup inicial** (estrutura de pastas, configurações)
4. **Implementar Fase 1** (fundação + UI base)
5. **Demos iterativas** ao final de cada fase

---

## 📞 OBSERVAÇÕES FINAIS

- Este plano é **iterativo**: podemos ajustar prioridades e escopo durante o desenvolvimento
- **Validação contínua**: faremos checkpoints ao final de cada fase
- **Sem suposições críticas**: quando houver dúvida, irei perguntar antes de implementar
- **Boas práticas**: código limpo, documentado, testável e escalável
- **Foco em UX**: a aplicação será tão profissional quanto as apresentações McKinsey

---

**Status**: ⏳ Aguardando validação e respostas às perguntas acima para iniciar implementação.
