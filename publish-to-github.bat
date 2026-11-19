@echo off
set REPO_NAME=%1
if "%REPO_NAME%"=="" set REPO_NAME=frontend-craft-and-prompt-knowledge
set VISIBILITY=%2
if "%VISIBILITY%"=="" set VISIBILITY=public

git init -b main
git add .
git commit -m "v5 (CI-Verified): Deep-research spec-verified optical UI, Three.js WebGPU/PBR, ML/Crypto & 2026 AI builder budget KB"

where gh >nul 2>nul
if %ERRORLEVEL%==0 (
  gh repo create %REPO_NAME% --%VISIBILITY% --source=. --remote=origin --push
  echo Published to GitHub: %REPO_NAME%
) else (
  echo GitHub CLI ^(gh^) not found. Create an empty repo named %REPO_NAME% on github.com, then run:
  echo   git remote add origin https://github.com/YOUR_USERNAME/%REPO_NAME%.git
  echo   git push -u origin main
)
