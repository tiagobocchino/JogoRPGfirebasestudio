# Como Usar os Agentes do Adele CRM

Este guia explica como invocar cada agente especializado e como usar o Orchestrator para coordenar tarefas complexas.

---

## O que são os Agentes?

Os agentes são instruções estruturadas que definem o papel, as skills e o protocolo de trabalho de cada especialista no sistema Adele CRM. Quando você inicia uma conversa com Claude Code e quer acionar um agente, você:

1. Cita o nome do agente
2. Descreve o que precisa
3. Fornece o contexto necessário

O agente lerá os arquivos de skill correspondentes e atuará como aquele especialista.

---

## Usando Cada Agente Diretamente

### 1. Backend Engineer
**Quando usar:** Criar endpoint, modificar modelo de DB, regra de negócio no backend.

```
Aja como o BackendEngineer (leia agents/BackendEngineer.md).

Preciso criar um endpoint GET /api/v1/hub/ que lista todos os
HubContent publicados e acessíveis ao role do usuário logado.
Filtre por tenant_id e is_published=True.
```

---

### 2. Frontend Engineer
**Quando usar:** Nova página, componente, ajuste visual, integração com API.

```
Aja como o FrontendEngineer (leia agents/FrontendEngineer.md).

Na página /hub, quando o usuário clicar em "Ler agora",
abra um modal com um leitor de PDF usando iframe.
A URL do PDF vem do endpoint GET /api/v1/hub/{slug}/read.
```

---

### 3. Automation Engineer
**Quando usar:** Fluxo WhatsApp, estágios de intake, AutomationService, webhook.

```
Aja como o AutomationEngineer (leia agents/AutomationEngineer.md).

Preciso adicionar um estágio 12 ao fluxo de intake que pergunta
ao lead qual horário de preferência para retorno do advogado.
Salvar no campo lead.preferred_time.
```

---

### 4. Infra Engineer
**Quando usar:** Problema de deploy, variável de ambiente, Docker, Render.

```
Aja como o InfraEngineer (leia agents/InfraEngineer.md).

O deploy do backend no Render está falhando com erro de
conexão com o banco. Verifique o render.yaml e me ajude
a diagnosticar o problema.
```

---

### 5. Integrations Engineer
**Quando usar:** Supabase RLS, bucket Storage, Meta API, Google Calendar, webhooks.

```
Aja como o IntegrationsEngineer (leia agents/IntegrationsEngineer.md).

Preciso criar o bucket "ebooks" no Supabase Storage com
acesso privado e configurar as políticas RLS para que
somente o service_role do backend possa acessar diretamente.
```

---

### 6. QA Engineer
**Quando usar:** Antes de qualquer deploy, auditoria de segurança, validação PT-BR.

```
Aja como o QAEngineer (leia agents/QAEngineer.md).

Execute a Master Battery completa no módulo Hub recém-criado.
Verifique: segurança, localização PT-BR, UX e comportamento
de acesso restrito por role.
```

---

### 7. Marketing Manager
**Quando usar:** Estratégia de conteúdo, estrutura de ebook, campanha, copy.

```
Aja como o MarketingManager (leia agents/MarketingManager.md).

Preciso de um briefing completo para o primeiro ebook do Hub:
"Por Que Seu Escritório Precisa de um CRM em 2026".
Inclua estrutura de capítulos, tom de voz e CTA final.
```

---

## Usando o Orchestrator (Agente Regente)

O Orchestrator é para quando você não sabe qual agente acionar,
ou quando a tarefa envolve múltiplas camadas do sistema.

**Sintaxe básica:**

```
Aja como o Orchestrator (leia agents/Orchestrator.md).

[Descreva seu pedido aqui]
```

**Exemplos:**

### Exemplo 1 — Feature nova completa
```
Aja como o Orchestrator (leia agents/Orchestrator.md).

Quero implementar o sistema completo de push notifications
dentro do Adele: quando um novo lead chega pelo WhatsApp,
o advogado deve receber uma notificação no painel.
O que isso afeta? Quem implementa? Qual a ordem?
```

### Exemplo 2 — Análise arquitetural
```
Aja como o Orchestrator (leia agents/Orchestrator.md).

Estamos pensando em adicionar um sistema de assinatura
por plano (Basic/Pro/Enterprise) que libera diferentes
módulos para o tenant. Analise o impacto no sistema atual.
```

### Exemplo 3 — Diagnóstico de problema
```
Aja como o Orchestrator (leia agents/Orchestrator.md).

Os leads captados pelo WhatsApp não estão aparecendo
no painel de Leads do frontend. O backend parece estar
recebendo as mensagens. O que pode estar errado?
```

---

## Fluxo Recomendado para Novas Features

```
1. Orchestrator  →  Analisa o pedido e cria o plano
2. BackendEngineer  →  Implementa modelos e endpoints
3. FrontendEngineer  →  Implementa a UI
4. IntegrationsEngineer  →  Configura serviços externos (se necessário)
5. QAEngineer  →  Auditoria final antes do deploy
6. InfraEngineer  →  Deploy e monitoramento
```

---

## Fluxo para Conteúdo do Hub

```
1. MarketingManager  →  Define estrutura e briefing do ebook
2. [Sócio escreve o conteúdo]
3. FrontendEngineer  →  Ajustes de UI no Hub se necessário
4. IntegrationsEngineer  →  Upload no Supabase Storage
5. BackendEngineer  →  Registra HubContent no banco
6. QAEngineer  →  Valida acesso, visualização e segurança
```

---

## Tabela de Decisão Rápida

| Você quer... | Use este agente |
|-------------|----------------|
| Criar ou mudar algo no backend | BackendEngineer |
| Criar ou mudar algo na UI | FrontendEngineer |
| Mexer no fluxo WhatsApp | AutomationEngineer |
| Resolver problema de deploy | InfraEngineer |
| Configurar Supabase ou Meta API | IntegrationsEngineer |
| Fazer auditoria ou testar | QAEngineer |
| Planejar campanha ou ebook | MarketingManager |
| Não saber qual usar / tarefa grande | **Orchestrator** |

---

## Dica: Contexto é tudo

Quanto mais contexto você der ao agente, melhor a resposta.

**Ruim:**
> "Cria uma página de ebooks"

**Bom:**
> "Aja como FrontendEngineer. Cria a página /hub com grid de cards
> mostrando os conteúdos do endpoint GET /api/v1/hub/. Cada card
> deve ter título, categoria, e botão 'Ler agora' que abre o PDF
> em modal. Role gerencial vê botão de upload. Usar padrão Chakra UI."
