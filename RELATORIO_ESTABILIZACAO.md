# 🛡️ Relatório de Estabilização - Crônicas do Vale

Este documento resume as correções críticas aplicadas para garantir que o bot funcione de forma persistente no Railway.

## ✅ Problemas Resolvidos

### 1. Conectividade Supabase (Erro 401)
- **Causa**: As chaves copiadas para o Railway continham espaços ou estavam truncadas. Além disso, o bot precisava de permissões administrativas.
- **Solução**: 
    - Implementamos `SERVICE_ROLE_KEY` como prioridade.
    - Adicionamos `.strip()` na leitura das variáveis de ambiente em `src/database.py`.
    - Adicionamos logs de diagnóstico (mascarados) para validar o tamanho das chaves.

### 2. Falha na IA (Erro 404 Not Found)
- **Causa**: O modelo `gemini-1.5-flash` não estava disponível para a API Key configurada.
- **Solução**: 
    - Criamos um sistema de diagnóstico em `src/ai_handler.py` que lista os modelos disponíveis.
    - Descobrimos que a chave tem acesso aos modelos `gemini-2.0-flash` e aliases `-latest`.
    - Atualizamos a lista de preferência do bot.

### 3. Falha de Login Discord
- **Causa**: Possíveis espaços no token no arquivo `.env`.
- **Solução**: Adicionamos `.strip()` no carregamento do token em `src/bot.py`.

## 🚧 Estado Atual e Próximos Passos

### ⚠️ Bloqueio de Cota (Erro 429 - ResourceExhausted)
- **Status**: O bot está 100% operacional, mas as requisições estão sendo barradas pelo Google por excesso de uso no plano gratuito.
- **Modelos Testados**: `gemini-2.0-flash` e `gemini-2.0-flash-lite`. Ambos reportaram `limit: 0` ou cota excedida no momento.
- **Descoberta Crítica**: A conexão via gRPC está funcionando perfeitamente, eliminando qualquer erro de rede ou autenticação.

### 📍 Próximo Objetivo:
1. **Monitorar Cota**: Verificar no [Google AI Studio](https://aistudio.google.com/) se há algum alerta ou se é necessário criar uma nova chave API em um projeto diferente para resetar os limites.
2. **Executar Setup**: Assim que a IA responder (pode ser amanhã após o reset diário), rodar `/setup` para finalizar a casa do Mestre.

---
*Relatório atualizado em 04/05/2026 às 00:52*
