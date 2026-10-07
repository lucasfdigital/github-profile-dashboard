<div align="center">

<picture>
<source media="(prefers-color-scheme: dark)" srcset="./profile-top.svg">
<img src="./profile-top-light.svg" width="860" />
</picture>

</div>

# github-profile-dashboard 👋

Animated dashboard for your GitHub profile, BoardUI dark/light style: KPIs (contributions, streak, best day, month, PRs, stars), monthly chart, top languages and contribution calendar — all with **real public data, no token, no third-party services**. A cron refreshes it every 4 hours.

> 🇧🇷 Versão em português: [README.md](./README.md) (principal)

## Get started in 3 steps

1. Click [**Use this template**](https://github.com/new?template_name=github-profile-dashboard&template_owner=lucasfdigital) and create a repository **named exactly as your username** (e.g. `your-user/your-user`) — its README renders on your profile
2. Open the **Actions** tab of the created repo and wait for the first run (~2 min) — or trigger it manually under *Update profile art → Run workflow*
3. Open `github.com/your-user` and done 🎉

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

## License

MIT — use, modify and sell freely. If you like it, leave a ⭐.
