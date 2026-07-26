# Riscos de crash / falha — Ponto Eletrônico v.2

Varredura do código (UI, services, repository, paths, export).  
Atualizado em: 26/07/2026.

Use este doc como backlog de hardening. Itens marcados `[ ]` ainda não foram tratados.

---

## Crítico — pode derrubar o handler / travar o app

### 1. Banco travado (Dropbox / segundo processo)

- [ ] Quase todo SQL abre conexão sem `try` na UI de lista / dashboard / exclusão.
- [ ] `lista.refresh()`, `dashboard.refresh()`, `excluir`, `excluir_todos` → `sqlite3.OperationalError: database is locked` sobe sem tratamento.
- **Cenário:** `.exe` aberto + Dropbox sincronizando `ponto_v2.db`, ou Python e `.exe` ao mesmo tempo.
- **Nota:** o fluxo de confirmar lançamento trata `Exception`; lista/dashboard não.

### 2. Startup sem permissão de escrita

- [ ] `data_dir()` / `exports_dir()` fazem `mkdir`.
- [ ] Se o `.exe` estiver em pasta só-leitura → falha em `init_db()` e o app não abre.

### 3. Linha corrompida no SQLite

- [ ] `_row_to_registro` faz `date.fromisoformat(row["data"])` sem proteção.
- [ ] Data inválida no banco → crash ao listar / dashboard / export.

### 4. Exclusão / edição sem try

- [ ] Callbacks de lixeira e “Excluir todos” não envolvem o SQL em `try/except`.
- [ ] Erro de I/O = exceção não tratada no evento Flet.

---

## Alto — falha funcional (não necessariamente crash)

### 5. Split com mais dias que horas → dias com 0h

- [ ] Ex.: 3h em 5 dias → alguns dias ficam `0h` e **são gravados**.
- [ ] `atualizar` exige `horas > 0`, mas o insert **não**.

### 6. Saída “vira o dia” e só guarda horário

- [ ] `calcular_saida` com 20h: `08:00 + 20h = 04:00` (dia seguinte).
- [ ] O CSV mostra saída `04:00:00` sem indicar o dia — dado errado no relatório, não crash.

### 7. Edição sem checagem de duplicata

- [ ] Dá pra editar um registro e cair no mesmo épico+data de outro.
- [ ] Gera duplicata que o lançamento em lote bloquearia.

### 8. Export com Excel/CSV aberto

- [ ] Arquivo já aberto no Excel → `PermissionError`.
- [ ] Na lista isso é capturado e vira mensagem (ok), mas a operação falha.

### 9. Dois “mundos” de dados

- [ ] `.exe` em `dist\` vs `python -m app.main` usam bancos diferentes.
- [ ] Parece “sumiu meu registro” / “duplicou” — confusão operacional, não bug de código.

---

## Médio — UX / edge cases

| Situação | Comportamento atual | Status |
|---|---|---|
| Horas `40.5` / texto | Bloqueia (`isdigit`) | OK |
| Preview sem datas/épico | `ValueError` tratado | OK |
| Confirmar 2x o mesmo lote | Trava sessão + banco | OK |
| Editar data `31/02` ou `abc` | `ValueError` no dialog | OK |
| Editar horas vazias | `int("")` → mensagem | OK |
| Lista com muitos registros | UI pode ficar lenta (DataTable inteira) | Atenção |
| `pop_dialog` se dialog já fechou | Possível erro Flet raro | Atenção |
| SnackBar com path longo | Só visual | OK |

---

## Baixo / improvável

- [ ] `page.window.*` no theme — ok no Flet 0.86 atual; mudaria se a API mudar.
- [ ] `os.startfile` falha → cai no `explorer` — ok.
- [ ] Export vazio (0 registros) — pandas gera CSV só com header — ok.

---

## Prioridade sugerida de correção

1. `try/except sqlite3.Error` em `refresh`, excluir, excluir todos, dashboard (mensagem tipo v1: “banco travado / feche o Dropbox”).
2. Bloquear dias com 0h no split (`if horas == 0: raise` ou redistribuir).
3. Checagem de duplicata na edição.
4. `PRAGMA busy_timeout=5000` (ou similar) no SQLite para mitigar Dropbox.
5. Validar `date.fromisoformat` no repo com mensagem clara.

---

## Arquivos mais envolvidos

| Área | Arquivos |
|---|---|
| UI | `app/ui/lista.py`, `app/ui/dashboard.py`, `app/ui/lancamento.py` |
| Banco | `app/db/database.py`, `app/repository/registro_repo.py` |
| Regras | `app/services/ponto_service.py`, `app/models/registro.py` |
| Paths | `app/paths.py` |
| Export | `app/services/export_service.py` |
