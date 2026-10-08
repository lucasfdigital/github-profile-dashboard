<div align="center">

<picture>
<source media="(prefers-color-scheme: dark)" srcset="./profile-top.svg">
<img src="./profile-top-light.svg" width="860" />
</picture>

</div>

# github-profile-dashboard 👋

Animated dashboard for your GitHub profile, BoardUI dark/light style: KPIs (contributions, streak, best day, month, PRs, stars), monthly chart, top languages and contribution calendar — all with **real public data**.

> 🇧🇷 Versão em português: [README.md](./README.md) (principal)

## Easiest way (recommended)

Go to **[github-profile-dash.vercel.app](https://github-profile-dash.vercel.app)**, connect GitHub and you're done: the site adds the dashboard to your profile README and it **refreshes itself every 4 hours**, with nothing running in your account. You can preview anyone's dashboard before connecting, and it has the newest design.

No login? Paste this into your profile repo README (replace `YOUR-USER`):

```html
<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://github-profile-dash.vercel.app/api/painel/YOUR-USER">
<img src="https://github-profile-dash.vercel.app/api/painel/YOUR-USER?tema=claro" width="860" />
</picture>
```

## Rather run it in your own account? (this template, 3 steps)

Here a GitHub Action in your own repo generates the dashboard. Heads up: GitHub's cron scheduler is best-effort and is sometimes late or skipped (see *Honest limits*).

1. Click [**Use this template**](https://github.com/new?template_name=github-profile-dashboard&template_owner=lucasfdigital) and create a repository **named exactly as your username** (e.g. `your-user/your-user`)
2. In the created repo, open `profile/README.md`, copy its contents into the root `README.md` (that one renders on your profile — the template root README is just docs)
3. Open the **Actions** tab and wait for the first run (~2 min) — or trigger it manually under *Update profile art → Run workflow*. Then open `github.com/your-user` and done 🎉

Nothing to configure: the workflow auto-detects the repo owner (`github.repository_owner`).

## Configuration (`dashboard.json`)

| Key | Default | What it does |
|---|---|---|
| `github_username` | `null` (auto) | Manual override (handy for local runs). CI always uses the repo owner |
| `exclude_repos` | `[]` | `["owner/repo"]` never counted in languages (docs, playground...) |
| `sections.kpis` | `true` | Row: Contributions · This month · Best day · Streak |
| `sections.extras` | `true` | Row: PRs · Stars |
| `sections.chart` | `true` | Current-year monthly chart |
| `sections.languages` | `true` | Language bars (official colors) |
| `sections.heatmap` | `true` | 53-week calendar |

## How it works

- `scripts/fetch_contributions.py` — reads your public calendar (`/users/<you>/contributions`, including closed years) into `data/contributions.json`
- `scripts/fetch_github_stats.py` — sums languages across your repos (no forks) + recent activity + PRs + stars via public REST
- `scripts/render_profile_top.py` — renders `profile-top.svg` (dark) and `profile-top-light.svg` (SMIL/CSS animations, which GitHub plays)
- `.github/workflows/update-profile-art.yml` — cron every 4h + on push + manual; commits the SVGs and bumps the README `?v=` to bust GitHub's image cache

## Honest limits

- No token = public API only: private and org repos are **excluded** from languages (the graph still counts your contributions there)
- Forks are ignored on purpose (otherwise other people's code eats your chart)
- Anonymous rate limit is 60 req/hour; each run uses ~40 — and if it's ever hit, scripts keep the previous data instead of breaking
- GitHub's cron scheduler is best-effort: runs can be late or skipped entirely. If the dashboard looks frozen, open *Actions → Update profile art → Run workflow* (every push to `main` refreshes it too)

## License

MIT — use, modify and sell freely. If you like it, leave a ⭐.
