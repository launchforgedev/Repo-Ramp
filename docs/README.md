# RepoRamp Docs — Quick Start UI

Responsive static documentation website with a clean developer-docs layout: left navigation, central article, right-side table of contents, search, copyable commands, callouts, and responsive mobile navigation.

## Preview locally
Open `index.html` in a browser, or run:

```powershell
python -m http.server 8000
```

Then visit http://localhost:8000.

## Deploy with GitHub Pages
1. Copy the files into the root of a documentation repository or a `/docs` folder in RepoRamp.
2. Open GitHub **Settings → Pages**.
3. Select **Deploy from a branch**, select `main`, and choose `/ (root)` or `/docs`.
4. Save and add the published URL to RepoRamp's About → Website field.

No build step is required. Review CLI examples against the exact release you publish.
