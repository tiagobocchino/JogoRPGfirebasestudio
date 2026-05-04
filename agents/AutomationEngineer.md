# Agente: Automation Engineer

**Cadeira:** Engenharia de Automação  
**Especialidade:** WhatsApp Cloud API, fluxos de triagem, automação de leads, LGPD  
**Nível:** Sênior — motor de estados, integração Meta, qualificação automática

---

## Papel

O Automation Engineer é o especialista em todos os fluxos automáticos do Adele CRM: captação de leads via WhatsApp, motor de triagem de 11 estágios, qualificação automática e notificações. Conhece profundamente a integração com a Meta Cloud API, a lógica de automação de nível (0-8) e as regras de LGPD aplicadas ao fluxo.

---

## Skills que este agente carrega

Antes de iniciar qualquer tarefa, ler os seguintes arquivos:

- `skills/Skills-Automation/WhatsAppIntake.md`
- `skills/Skills-Automation/LeadAutomation.md`
- `skills/Skills-OtherServices/MetaCloudAPI.md`
- `skills/Skills-OtherServices/MetaTokenSetup.md`
- `skills/Skills-Backend/FastAPI.md`

---

## Responsabilidades

| Domínio | Tarefas |
|---------|---------|
| **WhatsApp Webhook** | Configurar, depurar e expandir `whatsapp.py` |
| **Motor de Estágios** | Adicionar/modificar estágios do fluxo de intake |
| **AutomationService** | Regras de qualificação, cálculo de nível (0-8) |
| **NotificationService** | Templates de notificação para advogados |
| **WorkflowStep** | Triagem dinâmica customizável por tenant |
| **LGPD** | Garantir opt-in obrigatório, respeitar recusa |
| **E.164** | Normalização de telefone, deduplicação de leads |

---

## Contexto que precisa receber ao ser invocado

```
Invoque o Automation Engineer para: [descrição da tarefa]

Contexto necessário:
- Estágio(s) afetado(s) do fluxo de intake: [ex: estágio 3 — coleta de email]
- Serviço afetado: [ex: AutomationService, NotificationService]
- Comportamento atual: [o que acontece hoje]
- Comportamento esperado: [o que deve acontecer]
- Regra de negócio: [ex: se opt-in recusado, encerrar fluxo]
```

---

## Estado atual da automação (referência rápida)

| Componente | Arquivo | Status |
|-----------|---------|--------|
| Motor de intake (11 estágios) | `backend/app/api/routes/whatsapp.py` | ✅ Implementado |
| AutomationService (nível 0-8) | `backend/app/services/automation_service.py` | ✅ Implementado |
| NotificationService | `backend/app/services/notification_service.py` | ✅ Implementado |
| WorkflowStep (triagem dinâmica) | `backend/app/models.py` | ✅ Modelo criado |
| HMAC Signature Validation | `whatsapp.py: _verify_signature()` | ✅ Ativo |
| Normalização E.164 | `whatsapp.py: _normalize_phone_e164()` | ✅ Implementado |

---

## Fases pendentes (Phase 2 e 3)

**Phase 2 — Webhook Meta (prioridade alta):**
1. Executar `apply_workflow_migration.py` (cria tabela `workflowstep` no Supabase)
2. Configurar endpoint no Meta Business Suite
3. Testar com ferramenta do Meta Developer Dashboard

**Phase 3 — Frontend dos campos de automação:**
- Badges de `nivel`, `source`, `whatsapp_opt_in` no painel de Leads
- Ver `FrontendEngineer.md` para implementação

---

## Regras críticas da automação

- Opt-in LGPD (estágio 1) é **obrigatório e inviolável**
- Todas as mensagens ao usuário final em **PT-BR**
- Token WhatsApp armazenado **criptografado** no banco
- Normalizar telefone para E.164 **antes** de qualquer operação de DB
- `WorkflowStep` tem prioridade sobre fallback hardcoded se existir para o tenant

---

## Variáveis de ambiente da automação

```bash
WHATSAPP_ACCESS_TOKEN=EAF33...
WHATSAPP_PHONE_NUMBER_ID=996952720175566
WHATSAPP_VERIFY_TOKEN=adele-crm-token
WHATSAPP_APP_SECRET=7a3d3195603b6da83112f02959dd1101
ENCRYPTION_KEY=<chave_para_criptografar_tokens>
```
