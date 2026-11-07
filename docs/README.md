# RepoRamp Documentation Site

This folder contains RepoRamp's static documentation website.

## Preview locally

From the repository root:

```powershell
python -m http.server 8000 --directory docs
```

Open http://localhost:8000 in a browser.

Alternatively, open `index.html` directly. Running a local server is recommended because browser clipboard features work best on localhost or HTTPS.

## Files

```text
docs/
├── assets/
│   ├── favicon.png
│   └── favicon.ico
├── index.html
├── app.js
└── styles.css
```

- `index.html` contains the guides, CLI reference, integration instructions and command examples.
- `styles.css` controls the responsive documentation layout.
- `app.js` provides navigation, search and copy-command interactions.
- `assets/favicon.png` is the only UI use of the RepoRamp brand image: it is a cropped icon mark for the browser tab.

## GitHub Pages

1. Push the repository to GitHub.
2. Open repository **Settings → Pages**.
3. Choose **Deploy from a branch**.
4. Select the `main` branch and `/docs` folder.
5. Save and wait for the Pages deployment to complete.

Review commands against the checked-in CLI source before publishing a new release.
