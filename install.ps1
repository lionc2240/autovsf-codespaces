# =====================================================
# AutoVSF Installer - One-click install
# =====================================================

Write-Host "AutoVSF Installer" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow

$RepoName = "autovsf"
$RepoUrl  = "https://github.com/lionc2240/autovsf.git"

# 1. Cài Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Dang cai Git..." -ForegroundColor Yellow
    winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + 
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 2. Cài Python 3.12
if (-not (Get-Command python -ErrorAction SilentlyContinue) -or 
    (python --version 2>&1) -notmatch "3\.1[2-9]") {
    Write-Host "Dang cai Python 3.12..." -ForegroundColor Yellow
    winget install --id Python.Python.3.12 -e --source winget --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + 
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 3. Clone / Update repo (đã bao gồm VideoSubFinder)
Write-Host "Dang clone/cap nhat repository..." -ForegroundColor Yellow
$currentDirName = Split-Path $PWD -Leaf

if ($currentDirName -eq $RepoName -and (Test-Path ".git")) {
    Write-Host "Ban dang dung san trong thu muc autovsf -> Dang cap nhat..." -ForegroundColor Yellow
    git pull
} elseif (Test-Path $RepoName) {
    Write-Host "Thu muc autovsf da ton tai → Dang cap nhat..." -ForegroundColor Yellow
    Set-Location $RepoName
    git pull
} else {
    git clone $RepoUrl
    Set-Location $RepoName
}

# 4. Kiểm tra và tải VideoSubFinder (nếu thiếu)
$vsfDir = Join-Path $PWD "program"
$vsfZipUrl = "https://github.com/lionc2240/autovsf/releases/download/VideoSubFinder_6.10_x64/VideoSubFinder_6.10_x64.zip"
$vsfZipFile = Join-Path $vsfDir "VideoSubFinder_6.10_x64.zip"
$vsfExe = Join-Path $vsfDir "VideoSubFinder_6.10_x64\Release_x64\VideoSubFinderWXW_intel.exe"

# Đảm bảo có thư mục program
if (-not (Test-Path $vsfDir)) {
    New-Item -ItemType Directory -Force -Path $vsfDir | Out-Null
}

Write-Host "`n────────────────────────────────────────" -ForegroundColor White
Write-Host "[..] Dang kiem tra VideoSubFinder..." -ForegroundColor Yellow
$osArch = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
Write-Host "  [OK] Environment: Windows ($osArch)" -ForegroundColor White

if (Test-Path $vsfExe) {
    Write-Host "[OK] VideoSubFinderWXW_intel.exe da co san!" -ForegroundColor White
} else {
    Write-Host "[..] Thieu VideoSubFinder -> Dang tai tu Github Release..." -ForegroundColor Yellow
    
    $downloaded = $false
    
    # 1. Thử dùng curl.exe (Tích hợp sẵn trong Windows 10/11)
    if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
        Write-Host "  [..] Dang tai bang curl.exe..." -ForegroundColor Yellow
        curl.exe -L -o $vsfZipFile $vsfZipUrl
        if ($LASTEXITCODE -eq 0 -and (Test-Path $vsfZipFile) -and (Get-Item $vsfZipFile).Length -gt 10MB) {
            $downloaded = $true
            Write-Host "  [OK] Tai bang curl.exe thanh cong!" -ForegroundColor White
        }
    }
    
    # 2. Thử dùng Invoke-WebRequest (Dự phòng 1)
    if (-not $downloaded) {
        Write-Host "  [..] curl.exe that bai hoac khong co. Thu dung Invoke-WebRequest..." -ForegroundColor Yellow
        try {
            # Set TLS 1.2/1.3 bằng số nguyên để tránh lỗi enum trên máy cũ
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor 3072
            
            $oldProgress = $ProgressPreference
            $ProgressPreference = 'SilentlyContinue'
            
            Invoke-WebRequest -Uri $vsfZipUrl -OutFile $vsfZipFile -UseBasicParsing
            
            $ProgressPreference = $oldProgress
            if ((Test-Path $vsfZipFile) -and (Get-Item $vsfZipFile).Length -gt 10MB) {
                $downloaded = $true
                Write-Host "  [OK] Tai bang Invoke-WebRequest thanh cong!" -ForegroundColor White
            }
        } catch {
            Write-Host "  [❌] Invoke-WebRequest that bai: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    # 3. Thử dùng WebClient đồng bộ (Dự phòng cuối - không dùng event bất đồng bộ để tránh crash luồng)
    if (-not $downloaded) {
        Write-Host "  [..] Thu dung WebClient dong bo..." -ForegroundColor Yellow
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor 3072
            $webClient = New-Object System.Net.WebClient
            $webClient.Headers.Add("User-Agent", "Mozilla/5.0")
            $webClient.DownloadFile($vsfZipUrl, $vsfZipFile)
            if ((Test-Path $vsfZipFile) -and (Get-Item $vsfZipFile).Length -gt 10MB) {
                $downloaded = $true
                Write-Host "  [OK] Tai bang WebClient thanh cong!" -ForegroundColor White
            }
        } catch {
            Write-Host "  [❌] WebClient that bai: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    if ($downloaded) {
        try {
            # Giải nén tự động vào program\VideoSubFinder_6.10_x64
            Write-Host "[..] Dang giai nen VideoSubFinder..." -ForegroundColor Yellow
            $extractDir = Join-Path $vsfDir "VideoSubFinder_6.10_x64"
            if (-not (Test-Path $extractDir)) {
                New-Item -ItemType Directory -Force -Path $extractDir | Out-Null
            }
            Expand-Archive -Path $vsfZipFile -DestinationPath $extractDir -Force
            Remove-Item -Path $vsfZipFile -Force
            
            if (Test-Path $vsfExe) {
                Write-Host "[OK] Giai nen thanh cong! Da kich hoat VideoSubFinder." -ForegroundColor White
            } else {
                Write-Host "[❌] Canh bao: File chay van thieu sau khi giai nen!" -ForegroundColor Red
            }
        } catch {
            Write-Host "[❌] Giai nen that bai: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "[❌] Tai VideoSubFinder that bai hoan toan bang moi phuong thuc!" -ForegroundColor Red
        Write-Host "Vui long tu tai file zip tai link: $vsfZipUrl" -ForegroundColor White
        Write-Host "Sau do giai nen vao thu muc: program/VideoSubFinder_6.10_x64" -ForegroundColor White
    }
}
Write-Host "────────────────────────────────────────" -ForegroundColor White

# 5. Cài Python packages
Write-Host "`n[..] Dang cai thu vien Python..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
python -m pip install watchdog google-api-python-client oauth2client httplib2 opencv-python psutil Pillow --quiet
Write-Host "[OK] Da cai dat day du thu vien Python." -ForegroundColor White

# Đăng ký lệnh nhanh 'autovsf' vào PowerShell Profile để gọi từ bất kỳ đâu
try {
    $profileDir = Split-Path $PROFILE -Parent
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
    }
    $fnDef = "`nfunction autovsf { Set-Location `"$PWD`"; python main.py }`n"
    if (Test-Path $PROFILE) {
        $content = Get-Content $PROFILE -Raw
        if ($content -notmatch "function autovsf") {
            Add-Content -Path $PROFILE -Value $fnDef
        }
    } else {
        New-Item -ItemType File -Path $PROFILE -Force | Out-Null
        Add-Content -Path $PROFILE -Value $fnDef
    }
} catch {}

# 6. Hoàn tất & Tương tác Menu
Write-Host "`n=======================================" -ForegroundColor Yellow
Write-Host "   Cai dat AutoVSF HOANTAT!" -ForegroundColor White
Write-Host "=======================================" -ForegroundColor Yellow
Write-Host "Thu muc: $(Get-Location)" -ForegroundColor White
Write-Host "VSF Path: $vsfExe" -ForegroundColor White
Write-Host "Lệnh nhanh: autovsf (Gõ ở bất kỳ cửa sổ PowerShell nào để mở tool)" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────" -ForegroundColor White

$shouldExit = $false
while (-not $shouldExit) {
    Write-Host "`n[1] Launch AutoVSF (Chay ngay)" -ForegroundColor White
    Write-Host "[2] Configure Google Cloud (Cai dat Google Drive OCR)" -ForegroundColor Yellow
    Write-Host "[0] Cancel / Discard (Thoat)" -ForegroundColor Red
    Write-Host "───────────────────────────────────────" -ForegroundColor White
    
    $choice = Read-Host "Nhap lua chon cua ban [1/2/0]"
    
    switch ($choice) {
        "1" {
            Write-Host "`n[..] Dang khoi chay AutoVSF..." -ForegroundColor Yellow
            python main.py
            $shouldExit = $true
            break
        }
        "2" {
            Write-Host "`n[..] Dang mo link huong dan GOOGLE_SETUP.md..." -ForegroundColor Yellow
            Start-Process "https://github.com/lionc2240/autovsf/blob/main/docs/GOOGLE_SETUP.md"
            
            Write-Host "[..] Dang mo Google Cloud Console..." -ForegroundColor Yellow
            Start-Process "https://console.cloud.google.com/"
            
            Write-Host "`n[!] HUONG DAN:" -ForegroundColor Yellow
            Write-Host "  1. Doc ky tai lieu tren Github de lam theo 4 buoc." -ForegroundColor White
            Write-Host "  2. Sau khi co file 'credentials.json', hay bo vao thu muc: $(Get-Location)" -ForegroundColor White
            Write-Host "  3. Ban co the quay lai day va chon [1] de chay AutoVSF ngay." -ForegroundColor White
            continue
        }
        "0" {
            Write-Host "`n[OK] Tam biet! Ban co the chay lai nhanh bang cach go: autovsf hoac double click run.bat" -ForegroundColor White
            $shouldExit = $true
            break
        }
        default {
            Write-Host "Lua chon khong hop le! Vui long nhap 1, 2 hoac 0." -ForegroundColor Red
        }
    }
}