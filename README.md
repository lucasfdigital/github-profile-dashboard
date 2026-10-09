<div align="center">

<picture>
<source media="(prefers-color-scheme: dark)" srcset="./profile-top.svg?v=20261009-2058">
<img src="./profile-top-light.svg?v=20261009-2058" width="860" />
</picture>

</div>

# github-profile-dashboard 👋

Dashboard animado pro seu perfil do GitHub, estilo BoardUI dark/light: KPIs (contribuições, streak, melhor dia, mês, PRs, stars), gráfico mensal, linguagens mais usadas e calendário de contribuições — tudo com **dados reais e públicos**.

> 🇺🇸 English version: [README.en.md](./README.en.md)

## Jeito mais fácil (recomendado)

Entre em **[github-profile-dash.vercel.app](https://github-profile-dash.vercel.app)**, conecte o GitHub e pronto: o site coloca o painel no README do seu perfil e ele **se atualiza sozinho a cada 4 horas**, sem nada rodando na sua conta. Lá dá pra ver o painel de qualquer usuário antes de conectar, e ele tem o visual mais novo.

Sem login? Cole isto no README do seu repo de perfil (troque `SEU-USER`):

```html
<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://github-profile-dash.vercel.app/api/painel/SEU-USER">
<img src="https://github-profile-dash.vercel.app/api/painel/SEU-USER?tema=claro" width="860" />
</picture>
```

## Prefere rodar na sua conta? (este template, 3 passos)

Aqui o painel é gerado por um GitHub Action no seu próprio repo. Atenção: o agendamento (cron) do GitHub não é garantido e às vezes atrasa ou nem roda (veja *Limites honestos*).

1. Clique em [**Use this template**](https://github.com/new?template_name=github-profile-dashboard&template_owner=lucasfdigital) e crie um repositório **com o seu username** (ex: `seu-user/seu-user`)
2. No repo criado, abra `profile/README.md`, copie o conteúdo e cole no `README.md` da raiz (é esse README que aparece no seu perfil — o da raiz do template é só documentação)
3. Abra a aba **Actions** e aguarde o primeiro run (~2 min) — ou dispare manualmente em *Update profile art → Run workflow*. Depois abra `github.com/seu-user` e pronto 🎉

Nada pra configurar: o workflow detecta o dono do repo sozinho (`github.repository_owner`).

## Configuração (`dashboard.json`)

| Chave | Default | O que faz |
|---|---|---|
| `github_username` | `null` (auto) | Override manual (útil pra rodar local). No CI sempre usa o dono do repo |
| `exclude_repos` | `[]` | `["dono/repo"]` que nunca entram nas linguagens (docs, playground...) |
| `sections.kpis` | `true` | Linha Contribuições · Este mês · Melhor dia · Streak |
| `sections.extras` | `true` | Linha PRs · Stars |
| `sections.chart` | `true` | Gráfico mensal do ano atual |
| `sections.languages` | `true` | Barras de linguagens (cores oficiais) |
| `sections.heatmap` | `true` | Calendário 53 semanas |

## Como funciona

- `scripts/fetch_contributions.py` — lê seu calendário público (`/users/<você>/contributions`, incluindo anos fechados) e salva `data/contributions.json`
- `scripts/fetch_github_stats.py` — soma linguagens dos seus repos (sem forks) + atividade recente + PRs + stars via REST pública
- `scripts/render_profile_top.py` — gera `profile-top.svg` (dark) e `profile-top-light.svg` (animações SMIL/CSS, que o GitHub toca)
- `.github/workflows/update-profile-art.yml` — cron a cada 4h + a cada push + manual; commita os SVGs e troca o `?v=` do README pra furar o cache de imagens do GitHub

## Limites honestos

- Sem token = API pública: repos privados e de organização **não** entram nas linguagens (as contribuições do gráfico, essas o GitHub conta)
- Forks são ignorados de propósito (se não, código alheio engole seu gráfico)
- Rate limit anônimo é 60 req/hora; cada execução usa ~40 — e se estourar, o script mantém os dados anteriores em vez de quebrar
- O agendamento (cron) do GitHub não é garantido: pode atrasar ou nem rodar. Se o dashboard parar no tempo, abra *Actions → Update profile art → Run workflow* (todo push na `main` também atualiza)

## Licença

MIT — use, modifique e venda à vontade. Se curtir, deixa uma ⭐.
