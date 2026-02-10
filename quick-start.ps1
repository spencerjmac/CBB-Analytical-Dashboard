#!/usr/bin/env pwsh
# Quick Start Script for CBB Analytics Web App

Write-Host "🏀 CBB Analytics Web App - Quick Start" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "web")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "   Expected: /CBB Analytical Dashboard/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Installing web app dependencies..." -ForegroundColor Green
Set-Location web
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ npm install failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Building unified dataset..." -ForegroundColor Green
Set-Location ../scripts
npx tsx build-data.ts
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Data pipeline failed" -ForegroundColor Red
    Write-Host "   Make sure CSV files exist in parent directories:" -ForegroundColor Yellow
    Write-Host "   - ../KenPom Data/kenpom_tableau.csv" -ForegroundColor Yellow
    Write-Host "   - ../Bart Torvik/torvik_tableau.csv" -ForegroundColor Yellow
    Write-Host "   - ../CBB Analytics/cbb_analytics_tableau_cleaned.csv" -ForegroundColor Yellow
    Set-Location ../web
    exit 1
}
Write-Host "✅ Data built successfully" -ForegroundColor Green
Write-Host ""

# Check if teams.json was created
if (-not (Test-Path "../web/public/data/teams.json")) {
    Write-Host "❌ teams.json was not created" -ForegroundColor Red
    Set-Location ../web
    exit 1
}

Write-Host "Step 3: Copying team logos..." -ForegroundColor Green
$logosSource = "../College Logos/output/logos"
$logosDest = "../web/public/logos"

if (Test-Path $logosSource) {
    New-Item -ItemType Directory -Force -Path $logosDest | Out-Null
    Copy-Item "$logosSource/*" $logosDest -Force
    Write-Host "✅ Logos copied" -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: Logo directory not found" -ForegroundColor Yellow
    Write-Host "   Expected: $logosSource" -ForegroundColor Yellow
    Write-Host "   The app will use placeholder logos" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Step 4: Starting development server..." -ForegroundColor Green
Set-Location ../web
Write-Host ""
Write-Host "🎉 Setup complete! Your app is starting..." -ForegroundColor Cyan
Write-Host "   Open: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

npm run dev
