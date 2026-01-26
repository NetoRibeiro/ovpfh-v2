# 📝 Como Atualizar Jogos (Fluxo SSG)

Este guia explica o novo processo otimizado para adicionar ou atualizar jogos. Graças ao sistema de **Geração Estática (SSG)**, você só precisa editar o JSON e rodar um script.

---

## 🚀 Fluxo de Trabalho em 3 Passos

### 1. Editar os Dados
Abra o arquivo `data/matches.json` e adicione ou altere as informações das partidas (placar, data, canais, etc).

> [!TIP]
> Use um validador como o [JSONLint](https://jsonlint.com/) se tiver dúvidas sobre a sintaxe.

### 2. Gerar as Páginas (SSG)
Após salvar o arquivo JSON, você **deve** rodar o script de geração para criar os arquivos HTML físicos e atualizar os links.

Abra o terminal na pasta do projeto e execute:
```powershell
.venv\Scripts\python spiders/generate_match_pages.py
```

**O que este script faz?**
- ✅ Cria pastas físicas para cada jogo (ex: `/paulistao26/18-01-2026/guarani-vs-santos/`).
- ✅ Injeta os dados do jogo diretamente no HTML para carregamento instantâneo.
- ✅ Atualiza o campo `matchURL` no `matches.json` para garantir que os links funcionem.
- ✅ Atualiza Títulos e Meta Tags para SEO.

### 3. Fazer o Deploy
Após rodar o script, suba os arquivos alterados para sua hospedagem (Hostinger).
- Veja o guia completo de deploy em [README_Deploy.md](README_Deploy.md).

---

## 📋 Detalhes do JSON (`matches.json`)

Exemplo de objeto de jogo:

```json
{
  "id": "paulistao26-corinthians-vs-pontepreta-11-01-2026",
  "tournament": "paulistao26",
  "homeTeam": "corinthians",
  "awayTeam": "pontepreta",
  "matchDate": "2026-01-11T16:00:00-03:00",
  "status": "finished",
  "score": { "home": 2, "away": 0 },
  "broadcasting": [
    { "channel": "Record", "type": "tv-aberta" }
  ]
}
```

### Campos Importantes:
- **`status`**: Use `"scheduled"` (agendado), `"live"` (ao vivo) ou `"finished"` (encerrado).
- **`matchDate`**: Use o formato ISO (`YYYY-MM-DDTHH:MM:SS-03:00`).
- **`matchURL`**: **NÃO EDITE MANUALMENTE**. Este campo é gerado automaticamente pelo script Python.

---

## ⚠️ Checklist de Erros comuns
1. **Esqueceu de rodar o script**: Os links no site darão erro 404 se a pasta do jogo não for gerada.
2. **Erro de sintaxe no JSON**: Falta de vírgula ou aspas quebrará o carregamento.
3. **ID de Time/Campeonato**: Certifique-se de usar os IDs que constam em `teams.json` e `tournaments.json`.

---
© 2026 Onde Vai Passar Futebol Hoje
