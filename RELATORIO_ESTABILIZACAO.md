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

### ⚠️ Bloqueio de Cota (Erro 429)
- O bot agora consegue "falar" com o Google, mas atingiu o limite de requisições do plano gratuito (`ResourceExhausted`).
- **Ação**: Aguardar o reset da cota (geralmente diário ou por minuto) ou verificar o painel do [Google AI Studio](https://aistudio.google.com/).

### 📍 Próximo Objetivo:
- Assim que a cota da IA estabilizar, executar o comando `/setup` no Discord para criar a estrutura final de categorias e canais.

---
*Relatório gerado em 04/05/2026 às 00:45*
