# How to Upload This Knowledge Base to GitHub

Follow either **Method 1 (Fastest — 1-Command Script)** or **Method 2 (Manual Git Commands)** below.

---

## Prerequisites
1. Unzip `frontend-craft-and-prompt-knowledge-v5.zip` and open a terminal inside the extracted `frontend-craft-and-prompt-knowledge-v5` folder.
2. Make sure [Git](https://git-scm.com/downloads) is installed (`git --version`).
3. *(Optional for Method 1)* Install [GitHub CLI (`gh`)](https://cli.github.com/) and sign in once with `gh auth login`.

---

## Method 1: One-Command Publish (Recommended)

### On Windows (Command Prompt / PowerShell)
```bat
publish-to-github.bat frontend-craft-and-prompt-knowledge public
```

### On macOS / Linux
```bash
chmod +x publish-to-github.sh
./publish-to-github.sh frontend-craft-and-prompt-knowledge public
```

*(Change `public` to `private` if you want a private repository.)*

---

## Method 2: Manual Git Upload (No GitHub CLI Needed)

1. Go to [https://github.com/new](https://github.com/new).
2. Name your repository **`frontend-craft-and-prompt-knowledge`**.
3. Leave **"Add a README file"**, **".gitignore"**, and **"License"** **UNCHECKED** (this zip already includes them).
4. Click **Create repository**, then run these commands inside the extracted folder (replace `<YOUR_USERNAME>` with your GitHub handle):

```bash
git init -b main
git add .
git commit -m "Initial commit: Spec-verified frontend craft, 3D PBR, ML/Crypto & AI builder budget KB (v5)"
git remote add origin https://github.com/<YOUR_USERNAME>/frontend-craft-and-prompt-knowledge.git
git push -u origin main
```

---

## Step 3: Verify GitHub Actions CI Automatically
As soon as you push to `main`, open the **Actions** tab on your GitHub repository:
- **`Knowledge Base Verification CI`** (`.github/ci/ci.yml`) will automatically run:
  1. Python 3.12 unit tests (`tests/test_domain_algorithms.py`)
  2. Node 22 unit tests (`tests/frontend_math.test.mjs`)
  3. Automated link & SHA-256 evidence validation (`scripts/validate_links_and_refs.py`)
  4. Quick benchmark smoke test (`benchmarks/run_benchmarks.py --quick`)

---

## Step 4 (Optional): Capture & Commit Live Screenshots
To populate `docs/screenshots/` with Retina desktop (`1440x900`) and mobile (`390x844`) PNGs of your 5 builds:
```bash
npm install --no-save playwright
npx playwright install chromium
VE_V0_URL="https://venkateshwara-brown.vercel.app" node scripts/capture-screenshots.mjs
git add docs/screenshots/*.png
git commit -m "Add reference build screenshots"
git push
```
*(Or trigger the manual **Capture Live Build Screenshots** workflow directly from the GitHub Actions tab.)*
