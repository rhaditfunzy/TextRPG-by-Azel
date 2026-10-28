
# TextRPG - Automatic GitHub Sync
# Default interval: 10 minutes

$ErrorActionPreference = "Stop"
$IntervalSeconds = 600
$RepoPath = $PSScriptRoot

Set-Location $RepoPath

function Invoke-Git {
    param([string[]]$GitArgs)

    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Git command gagal: git $($GitArgs -join ' ')"
    }
}

Write-Host "===================================="
Write-Host " TextRPG Automatic GitHub Sync"
Write-Host " Interval: 10 menit"
Write-Host " Tekan Ctrl+C untuk berhenti"
Write-Host "===================================="

# Pastikan direktori ini repository Git.
git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Folder ini bukan repository Git."
}

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

            # Beri waktu agar proses penyuntingan selesai.
            Write-Host "Menunggu 60 detik sebelum commit..."
            Start-Sleep -Seconds 60

            # Periksa kembali setelah jeda.
            $Changes = git status --porcelain
            if ($LASTEXITCODE -ne 0) {
                throw "Pemeriksaan ulang Git gagal."
            }

            if ($Changes) {
                Invoke-Git -GitArgs @("add", "-A")

                # Commit hanya jika ada perubahan yang di-stage.
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

        # Selalu coba push, termasuk untuk commit lokal
        # yang sebelumnya gagal diunggah.
        Invoke-Git -GitArgs @("push")

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
