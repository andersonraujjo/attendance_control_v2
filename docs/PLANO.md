# Ponto Eletrônico v.2 — Esboço e decisões

Documento de baseline do produto. O projeto v1 (`ponto_eletronico`) permanece **intacto**; tudo da v2 vive em `attendance_control_v2`.

Atualizado em: 26/07/2026.

---

## 1. Objetivo

App desktop leve (Windows) para lançar horas por **épico** em **várias datas**, com divisão igualitária, listagem, export no formato v1 e dashboard de totais — sem bater ponto em tempo real.

### Problema que resolve

No v1 o fluxo é entrada/saída em tempo real + correção manual no SQLite quando se atrasa uma semana. Na v2 o fluxo passa a ser: informar total de horas → escolher datas → gravar em lote.

---

## 2. Stack

| Camada | Escolha |
|---|---|
| Nome do app | **Ponto Eletrônico v.2** |
| UI | **Flet** |
| Linguagem | Python 3.10+ |
| Banco | SQLite (arquivo na pasta do app / Dropbox ok) |
| Export | pandas + openpyxl |
| Build | PyInstaller ou `flet pack` |
| Arquitetura | Camadas desde o início: UI → Services → Repository → Models |
| Plataforma | Windows apenas (uso local) |

### Por que Flet (e não CustomTkinter)

- Continua 100% Python
- UI mais moderna que CustomTkinter
- Adequado a formulários, listas e cards de dashboard
- Empacota para Windows
- Leve o suficiente para uso semanal/local

---

## 3. Decisões de produto

| Tema | Decisão |
|---|---|
| Campo “comentário” | Vira **Épico** (texto livre no MVP) |
| Fluxo | Horas da leva → selecionar datas → dividir igualitário |
| Meta semanal | Variável (40h, 32h, 20h…), não fixa |
| Fim de semana | Pode incluir se o usuário selecionar |
| Multi-épico no período | Raro; resolve com múltiplos lançamentos (ex.: Seg–Qui épico A, Sex épico B) |
| Granularidade de horas | Preferência por **inteiras** |
| Divisão que não fecha | `horas // n_dias`; **resto nos últimos dias** (soma sempre = total informado) |
| Seleção de datas | **Calendário multi-select** + atalho **“Esta semana”** |
| Dashboard MVP | Só **totais** (semana atual, mês, por épico) — sem gráfico |
| Cadastro de épicos | Não no MVP (texto livre); futuro: possível pull do Jira |
| Migração do banco v1 | **Não** — começa do zero |
| Entrada/saída reais | **Impl futura**; no MVP o export gera automático |
| Export | Mantém **formato v1** (o chefe já consome assim) |
| Pasta do v1 | **Não mexer** |

### Export v1 (MVP)

- `entrada` = `08:00:00`
- `saida` = `08:00` + horas daquele dia (após o split)
- `total_horas` = duração formatada (ex.: `8:00:00`)
- `comentario` = texto do épico

### Impl futuras (fora do MVP)

- Opção de incluir/editar entrada–saída manualmente
- Cadastro reutilizável de épicos / integração Jira
- Gráficos no dashboard
- Clientes, valor/hora, PDF

---

## 4. Fluxo principal (MVP)

1. Informar **quantidade de horas** (inteiro, ex.: 40)
2. Digitar **épico** (texto livre)
3. Selecionar datas: multi-select + atalho **“Esta semana”**
4. App divide as horas; resto vai para os últimos dias se não fechar redondo
5. Preview antes de confirmar (datas + horas/dia)
6. Confirmar → gera **1 registro por dia**
7. Listar / editar / excluir
8. Export CSV / XLSX no formato v1
9. Dashboard: totais da semana, do mês e por épico

### Exemplo de split

40h em 7 dias → `base = 40 // 7 = 5`, `resto = 5` → últimos 5 dias ganham +1h  
Resultado típico: `5, 5, 6, 6, 6, 6, 6` (soma = 40).

---

## 5. Schema SQLite (proposto)

```text
registros
  id            INTEGER PRIMARY KEY AUTOINCREMENT
  data          TEXT NOT NULL          -- YYYY-MM-DD (ISO no banco)
  horas         INTEGER NOT NULL       -- horas do dia
  epico         TEXT NOT NULL
  entrada       TEXT                   -- gerada: 08:00:00
  saida         TEXT                   -- gerada a partir de horas
  total_horas   TEXT                   -- "8:00:00" (compat export v1)
  criado_em     TEXT                   -- ISO datetime
```

Índices úteis: `(data)`, `(epico)`.

Display de data na UI: `dd/mm/yyyy`. Persistência: sempre ISO.

---

## 6. Estrutura de pastas

```text
attendance_control_v2/
├── app/
│   ├── main.py                 # entrypoint Flet
│   ├── ui/
│   │   ├── app.py              # shell / navegação
│   │   ├── lancamento.py       # tela de lançamento
│   │   ├── lista.py            # listar / editar / excluir
│   │   └── dashboard.py        # totais
│   ├── services/
│   │   ├── ponto_service.py    # split, validação, CRUD orquestrado
│   │   └── export_service.py
│   ├── repository/
│   │   └── registro_repo.py
│   ├── models/
│   │   └── registro.py
│   └── db/
│       └── database.py         # connect + init/migrate
├── data/                       # ponto_v2.db
├── exports/
├── requirements.txt
├── README.md
└── docs/
    └── PLANO.md                # este arquivo
```

---

## 7. Telas (MVP)

1. **Lançamento** — horas, épico, seletor de datas, preview, confirmar
2. **Registros** — tabela + editar / excluir
3. **Dashboard** — cards: horas da semana atual, horas do mês, lista agrupada por épico
4. **Exportar** — botão CSV / XLSX (formato v1)

---

## 8. Fases

| Fase | Escopo |
|---|---|
| **MVP** | Lançamento + split + lista/editar + export v1 + dashboard totais + `.exe` |
| **v2.1** | Opção de editar entrada/saída manualmente |
| **v2.2** | Épicos reutilizáveis / integração Jira |
| **v2.3** | Gráficos, clientes, valor/hora, PDF |

---

## 9. Fora do escopo agora

- Importar / migrar banco do v1
- Bater ponto em tempo real (relógio / entrada–saída ao vivo)
- Cadastro de épicos / Jira
- Gráficos no dashboard
- Alterar qualquer arquivo em `ponto_eletronico`

---

## 10. Critérios de pronto do MVP

- [ ] Lançar N horas em M datas com preview e persistência
- [ ] Soma dos dias = total informado
- [ ] Editar / excluir registro
- [ ] Export CSV/XLSX com colunas v1 e entrada `08:00` → saída calculada
- [ ] Dashboard com 3 totais (semana, mês, por épico)
- [ ] `.exe` rodando no Windows
- [ ] Projeto v1 (`ponto_eletronico`) intacto

---

## 11. Comparativo rápido v1 × v2

| | v1 | v2 |
|---|---|---|
| Paradigma | Cronômetro (entrada/saída) | Lançamento em lote |
| Campo livre | `comentario` | `epico` |
| Datas | Sempre “hoje” | Multi-select + atalho semana |
| UI | CustomTkinter | Flet |
| Arquitetura | Monolítica (`main.py`) | Camadas |
| Correção atrasada | Manual no SQLite | Fluxo nativo do app |

---

## 12. Próximos passos de implementação

1. Inicializar projeto (venv, `requirements.txt`, skeleton em camadas)
2. Banco + models + repository
3. Service de split + tela de lançamento
4. Lista / editar / excluir
5. Export formato v1
6. Dashboard de totais
7. Pack do `.exe`
