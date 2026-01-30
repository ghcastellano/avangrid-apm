# 🚀 Quick Start Guide - Avangrid APM Platform

## Para Começar Agora (5 minutos)

### 1. Abra o Terminal e navegue até a pasta webapp
```bash
cd "/Users/gustavohenriquecastellano/Downloads/Gerador Excel Avandrig/webapp"
```

### 2. Execute a aplicação
```bash
streamlit run app.py
```

**OU use o script de inicialização:**
```bash
./start.sh
```

### 3. A aplicação abrirá automaticamente no seu navegador
```
http://localhost:8501
```

---

## 📋 Fluxo de Uso Recomendado

### Passo 1: Upload do Questionário
1. Clique em **"Uploads"** no menu lateral
2. Na aba **"Questionnaire"**, faça upload do seu Excel
3. Aguarde o parsing (você verá a lista de aplicações encontradas)
4. Clique em **"Save to Database"**

### Passo 2: Upload de Transcripts (Opcional mas Recomendado)
1. Ainda em **"Uploads"**, vá para a aba **"Transcripts"**
2. Selecione a aplicação
3. Faça upload dos arquivos de transcript (TXT, PDF ou DOCX)
4. Clique em **"Process with AI"**
5. A IA extrairá automaticamente as respostas dos transcripts

### Passo 3: Gerar Scores
1. Vá para **"Applications"** no menu
2. Clique em uma aplicação para ver detalhes
3. Vá para a aba **"Suggested Scores"**
4. Clique em **"Generate Suggested Scores"**
5. Revise e aprove os scores sugeridos pela IA

### Passo 4: Visualizar Análises
1. Vá para **"Analyses"** no menu
2. Explore:
   - **2x2 Matrix**: Visualize o posicionamento estratégico
   - **Strategic Roadmap**: Veja as prioridades
   - **Calculator**: Entenda como os scores foram calculados

### Passo 5: Gerar Insights
1. Vá para **"Insights"** no menu
2. Clique em **"Generate Insights with AI"**
3. A IA analisará todo o portfólio e gerará insights automáticos sobre:
   - Oportunidades de integração
   - Planos de absorção
   - Atualizações tecnológicas
   - Riscos
   - Otimizações financeiras

### Passo 6: Fazer Perguntas
1. Vá para **"Q&A Assistant"** no menu
2. Digite sua pergunta (ex: "Quais aplicações têm problemas de segurança?")
3. A IA responderá com base nos seus dados reais

---

## 🎯 Exemplos de Perguntas para o Assistente IA

```
- Quais aplicações são candidatas para consolidação?
- Qual o custo total das aplicações legadas?
- Quais aplicações têm problemas de segurança?
- Como a aplicação X se integra com Y?
- Qual seria o impacto de eliminar a aplicação Z?
- Quais aplicações deveríamos priorizar para modernização?
- Quantas aplicações estão em cloud vs on-premises?
- Quais aplicações são críticas mas têm baixa saúde técnica?
```

---

## ⚠️ Troubleshooting

### A aplicação não inicia
```bash
# Verifique se todas as dependências estão instaladas
pip install -r requirements.txt

# Tente uma porta diferente
streamlit run app.py --server.port 8502
```

### Erro de API Key
- Verifique se o arquivo `.env` existe e contém sua API key da OpenAI
- Formato: `OPENAI_API_KEY=sk-...`

### Erro ao processar transcripts
- Verifique se o arquivo não está vazio
- Formatos suportados: TXT, PDF, DOCX
- PDFs escaneados (imagens) não funcionarão

---

## 💡 Dicas

1. **Primeiro o Questionário**: Sempre faça upload do questionário antes dos transcripts
2. **Qualidade dos Transcripts**: Quanto melhor a qualidade, melhores as extrações da IA
3. **Revise os Scores**: Sempre revise e ajuste os scores sugeridos pela IA antes de aprovar
4. **Perguntas Específicas**: Quanto mais específica a pergunta, melhor a resposta da IA
5. **Custo da API**: O modelo usado (gpt-4o-mini) é econômico, mas ainda assim tem custo

---

## 📊 O que a Plataforma Faz

✅ **Automatiza** a análise de questionários
✅ **Extrai** informações de transcripts usando IA
✅ **Sugere** scores baseados em análise profunda
✅ **Visualiza** o portfólio em matriz estratégica 2x2
✅ **Gera** insights automáticos sobre integração, riscos, custos
✅ **Responde** perguntas sobre o portfólio em linguagem natural
✅ **Mantém** todos os dados localmente (privacidade total)

---

## 📞 Estrutura de Arquivos

```
webapp/
├── app.py                # Aplicação principal (interface Streamlit)
├── database.py           # Modelos de banco de dados SQLite
├── ai_processor.py       # Integração com OpenAI (gpt-4o-mini)
├── requirements.txt      # Dependências Python
├── .env                  # Chave API (NÃO commitar no git!)
├── start.sh             # Script de inicialização
├── data/                # Banco de dados SQLite
│   └── avangrid.db      # Criado automaticamente
├── README.md            # Documentação completa
└── QUICK_START.md       # Este arquivo
```

---

## 🎨 Tecnologias Usadas

- **Frontend**: Streamlit (Python)
- **Backend**: SQLAlchemy + SQLite
- **IA**: OpenAI API (gpt-4o-mini - custo-benefício)
- **Visualizações**: Plotly + Altair
- **Documentos**: openpyxl, PyPDF2, python-docx

---

## ✨ Cores da Marca Avangrid

- 🟠 Laranja Primário: #E87722
- 🔵 Azul Secundário: #0066B3
- 🟢 Verde (EVOLVE): #10B981
- 🟡 Amarelo (INVEST): #F59E0B
- 🔵 Azul (MAINTAIN): #3B82F6
- 🔴 Vermelho (ELIMINATE): #EF4444

---

## 🚀 Pronto para Começar!

Execute agora:
```bash
streamlit run app.py
```

Boa análise! ⚡
