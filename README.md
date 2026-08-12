# CRAK Tracker

A simple GitHub Pages dashboard that tracks changes in the official VanEck Oil Refiners ETF (CRAK) holdings.

## Easiest setup

1. Download and unzip this project.
2. Create a new GitHub repository.
3. Upload every file from the unzipped folder.
4. In GitHub, open **Actions** and allow workflows if prompted.
5. Open **Update CRAK holdings** → **Run workflow**.
6. Wait for the workflow to finish.
7. Open **Settings** → **Pages**.
8. Under **Build and deployment**, choose **Deploy from a branch**.
9. Select branch **main** and folder **/(root)** → Save.
10. GitHub will give you a website link.

The tracker checks the official CRAK holdings page on weekdays at the scheduled time and stores daily snapshots in `data/history`.

Official source:
https://www.vaneck.com/us/en/investments/oil-refiners-etf-crak/

## Important

The dashboard is informational only and is not investment advice. Website layout changes by the source provider can require updates to `scripts/update_crak.py`.
