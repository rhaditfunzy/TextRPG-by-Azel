
# TextRPG - Automatic GitHub Sync
# Default interval: 10 minutes

$ErrorActionPreference = "Stop"
$IntervalSeconds = 600
$RepoPath = $PSScriptRoot
$DefaultRepoUrl = "https://github.com/rhaditfunzy/TextRPG-by-Azel.git"
$RepoUrl = if ($env:TEXTRPG_REPO_URL) { $env:TEXTRPG_REPO_URL } else { $DefaultRepoUrl }

Set-Location $RepoPath

function Invoke-Git {
    param([string[]]$GitArgs)

    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Git command gagal: git $($GitArgs -join ' ')"
    }
}

function Ensure-RepoRemote {
    git remote get-url origin *> $null
    if ($LASTEXITCODE -ne 0) {
        Invoke-Git -GitArgs @("remote", "add", "origin", $RepoUrl)
    }
    else {
        $CurrentUrl = git remote get-url origin
        if ($CurrentUrl -ne $RepoUrl) {
            Invoke-Git -GitArgs @("remote", "set-url", "origin", $RepoUrl)
        }
    }
}

function Ensure-Branch {
    $Branch = git branch --show-current
    if (-not $Branch) {
        $Branch = "main"
    }

    git rev-parse --verify $Branch *> $null
    if ($LASTEXITCODE -ne 0) {
        Invoke-Git -GitArgs @("checkout", "-b", $Branch)
    }
    else {
        git checkout $Branch *> $null
        if ($LASTEXITCODE -ne 0) {
            throw "Gagal berpindah ke branch '$Branch'."
        }
    }

    return $Branch
}

Write-Host "===================================="
Write-Host " TextRPG Automatic GitHub Sync"
Write-Host " Interval: 10 menit"
Write-Host " Remote: $RepoUrl"
Write-Host " Tekan Ctrl+C untuk berhenti"
Write-Host "===================================="

# Pastikan direktori ini repository Git.
git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Folder ini bukan repository Git."
}

Ensure-RepoRemote
$CurrentBranch = Ensure-Branch

while ($true) {
    $Time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "`n[$Time] Memeriksa perubahan..."

    try {
        # Stage semua perubahan yang tidak dikecualikan oleh .gitignore.
        $Changes = git status --porcelain
        if ($LASTEXITCODE -ne 0) {
            throw "Tidak dapat memeriksa status Git."
        }

        if ($Changes) {
            Write-Host "Perubahan ditemukan:"
            $Changes | ForEach-Object { Write-Host "  $_" }

            Write-Host "Menunggu 60 detik sebelum commit..."
            Start-Sleep -Seconds 60

            $Changes = git status --porcelain
            if ($LASTEXITCODE -ne 0) {
                throw "Pemeriksaan ulang Git gagal."
            }

            if ($Changes) {
                Invoke-Git -GitArgs @("add", "-A")

                git diff --cached --quiet
                $DiffExit = $LASTEXITCODE

                if ($DiffExit -eq 1) {
                    $Message = "Auto-sync TextRPG: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
                    Invoke-Git -GitArgs @("commit", "-m", $Message)
                }
                elseif ($DiffExit -ne 0) {
                    throw "Gagal memeriksa perubahan yang di-stage."
                }
            }
        }
        else {
            Write-Host "Tidak ada perubahan file."
        }

        git ls-remote --exit-code --heads origin $CurrentBranch *> $null
        if ($LASTEXITCODE -eq 0) {
            try {
                Invoke-Git -GitArgs @("pull", "--rebase", "origin", $CurrentBranch)
            }
            catch {
                Write-Host "Pull rebase dibatalkan atau gagal, tetap lanjut ke push."
            }
        }

        Invoke-Git -GitArgs @("push", "--set-upstream", "origin", $CurrentBranch)
        Write-Host "Sinkronisasi selesai."
    }
    catch {
        Write-Host "Sinkronisasi gagal: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Periksa autentikasi, koneksi, dan status Git."
        Write-Host "Script akan mencoba lagi pada siklus berikutnya."
    }

    Write-Host "Pemeriksaan berikutnya dalam 10 menit."
    Start-Sleep -Seconds $IntervalSeconds
}
