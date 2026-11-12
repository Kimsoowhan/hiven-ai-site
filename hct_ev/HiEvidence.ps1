# HiEvidence 1.0 (작업본) - 시험 증적 기록 앱. Windows PowerShell 5.1 이상, 설치·설정 변경·예약·훅 없음.
# 하는 일: 시험 중 대상 폴더(읽기만)와 대상 프로그램을 지켜보며 증적을 사본·sha256으로 보존하고, 모든 행위를 해시 사슬(증적체인.tsv)에 남긴다.
# 쓰는 곳: Root(증적 폴더)만 쓴다. Watch(시험 결과 폴더)에는 쓰지 않는다(원본 보존).
# 형식: 해시목록.tsv / 인수기록 / GS증빙색인.tsv 는 tools/ev_pack.py 와 같은 칸 순서(서로 verify 가능).
# 사용 예:
#   HiEvidence.ps1 -Mode Start -Case 시험가-2회차 -Root C:\증적\가갑 -Watch C:\HCT_시험가\결과_x -Target HiCoffer -Inputs a.zip,b.exe -Interval 300
#   HiEvidence.ps1 -Mode Snap  -Root C:\증적\가갑 -Label 스냅샷_수동 -Watch C:\HCT_시험가\결과_x
#   HiEvidence.ps1 -Mode Event -Root C:\증적\가갑 -Label 사건_종료 -Note "원인 확인 안 됨"
#   HiEvidence.ps1 -Mode Close -Root C:\증적\가갑          (끝 대조·색인)
#   HiEvidence.ps1 -Mode Verify -Root C:\증적\가갑
# 멈추는 길: Root 안에 중지.txt 파일이 생기면 Start 반복이 끝 처리를 하고 끝낸다.
param(
  [Parameter(Mandatory=$true)][ValidateSet('Start','Snap','Event','Close','Verify')][string]$Mode,
  [string]$Case = '', [string]$Root = '', [string]$Watch = '', [string]$Target = '',
  [string]$Inputs = '', [string]$Label = '', [string]$Note = '',
  [int]$Interval = 300, [int]$MaxMinutes = 1500, [int]$Poll = 5, [int]$MaxFileMB = 8,
  [switch]$NoScreen
)
$ErrorActionPreference = 'Continue'
$Tab = [string][char]9
$Utf8 = New-Object System.Text.UTF8Encoding($true)
function Now { (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss') }
function Stamp { (Get-Date).ToString('yyMMdd_HHmmss') }
function Sha([string]$p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() }
function ShaText([string]$s) {
  $h = [System.Security.Cryptography.SHA256]::Create()
  $b = $Utf8.GetBytes($s)
  ($h.ComputeHash($b) | ForEach-Object { $_.ToString('x2') }) -join ''
}
function Out-Line([string]$path, [string]$line) { [System.IO.File]::AppendAllText($path, $line + "`r`n", $Utf8) }
if ($Root -eq '') { Write-Output 'Root 필요'; exit 2 }
$null = New-Item -ItemType Directory -Force -Path $Root
$ManP = Join-Path $Root '해시목록.tsv'
$LogP = Join-Path $Root '인수기록.tsv'
$ChainP = Join-Path $Root '증적체인.tsv'
if (-not (Test-Path -LiteralPath $ManP)) { Out-Line $ManP ((@('증빙번호','보존시각','라벨','파일','크기','원본수정시각','sha256')) -join $Tab) }
if (-not (Test-Path -LiteralPath $LogP)) { Out-Line $LogP ((@('시각','일감','행위','대상','행위자','메모')) -join $Tab) }

function Add-Chain([string]$act, [string]$obj, [string]$memo) {
  $prev = '0' * 64; $no = 1
  if (Test-Path -LiteralPath $ChainP) {
    $last = Get-Content -LiteralPath $ChainP -Encoding UTF8 | Where-Object { $_ -ne '' } | Select-Object -Last 1
    if ($last -and $last -notlike '번호*') { $f = $last.Split([char]9); $no = [int]$f[0] + 1; $prev = $f[6] }
  } else { Out-Line $ChainP ((@('번호','시각','행위','대상','메모','앞줄해시','이줄해시')) -join $Tab) }
  $memo = ($memo -replace '[\r\n\t]', ' ')
  $body = (@([string]$no, (Now), $act, $obj, $memo, $prev)) -join $Tab
  Out-Line $ChainP ($body + $Tab + (ShaText $body))
  Out-Line $LogP ((@((Now), $Case, $act, $obj, 'HiEvidence', $memo)) -join $Tab)
}
function Next-No { $n = (Get-Content -LiteralPath $ManP -Encoding UTF8 | Where-Object { $_ -ne '' }).Count; 'EV-{0:D5}' -f $n }

function Save-File([string]$src, [string]$label, [string]$dstName) {
  try {
    $dir = Join-Path $Root $label; $null = New-Item -ItemType Directory -Force -Path $dir
    if ($dstName -eq '') { $dstName = (Stamp) + '_' + (Split-Path -Leaf $src) }
    $dst = Join-Path $dir $dstName
    Copy-Item -LiteralPath $src -Destination $dst -Force
    $a = Sha $src; $b = Sha $dst
    if ($a -ne $b) { Add-Chain '복사 불일치' $src ('원본 ' + $a + ' 사본 ' + $b); return }
    $fi = Get-Item -LiteralPath $src
    $rel = $label + '\' + $dstName
    Out-Line $ManP ((@((Next-No), (Now), $label, $rel, [string]$fi.Length, $fi.LastWriteTime.ToString('yyyy-MM-ddTHH:mm:ss'), $b)) -join $Tab)
  } catch { Add-Chain '보존 실패' $src $_.Exception.Message }
}
function Save-Text([string]$text, [string]$label, [string]$name) {
  try {
    $dir = Join-Path $Root $label; $null = New-Item -ItemType Directory -Force -Path $dir
    $dst = Join-Path $dir ((Stamp) + '_' + $name)
    [System.IO.File]::WriteAllText($dst, $text, $Utf8)
    $fi = Get-Item -LiteralPath $dst
    Out-Line $ManP ((@((Next-No), (Now), $label, ($label + '\' + (Split-Path -Leaf $dst)), [string]$fi.Length, $fi.LastWriteTime.ToString('yyyy-MM-ddTHH:mm:ss'), (Sha $dst))) -join $Tab)
  } catch { Add-Chain '보존 실패' $name $_.Exception.Message }
}
function Save-Env([string]$label) {
  $os = Get-CimInstance Win32_OperatingSystem
  $cs = Get-CimInstance Win32_ComputerSystem
  $cpu = (Get-CimInstance Win32_Processor | Select-Object -First 1).Name
  $disk = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 } | ForEach-Object { $_.DeviceID + ' 전체 ' + [math]::Round($_.Size/1GB,1) + 'GB 여유 ' + [math]::Round($_.FreeSpace/1GB,1) + 'GB' }
  $t = @('항목' + $Tab + '값',
    '기록시각' + $Tab + (Now),
    'OS' + $Tab + $os.Caption + ' ' + $os.Version + ' 빌드 ' + $os.BuildNumber + ' ' + $os.OSArchitecture,
    '모델' + $Tab + $cs.Manufacturer + ' ' + $cs.Model,
    '메모리GB' + $Tab + [math]::Round($cs.TotalPhysicalMemory/1GB,1),
    'CPU' + $Tab + $cpu,
    '디스크' + $Tab + ($disk -join ' / '),
    'PowerShell' + $Tab + $PSVersionTable.PSVersion.ToString(),
    '시간대' + $Tab + (Get-TimeZone).Id,
    '앱' + $Tab + 'HiEvidence 1.0 sha256 ' + (Sha $PSCommandPath))
  Save-Text ($t -join "`r`n") $label '환경기록.tsv'
}
function Save-Procs([string]$label) {
  $rows = @('이름' + $Tab + 'PID' + $Tab + '시작' + $Tab + '작업집합MB' + $Tab + 'CPU초' + $Tab + '응답')
  $list = if ($Target -ne '') { Get-Process -Name $Target -ErrorAction SilentlyContinue } else { Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 15 }
  foreach ($p in $list) {
    $st = ''; try { $st = $p.StartTime.ToString('yyyy-MM-ddTHH:mm:ss') } catch {}
    $rows += ($p.ProcessName + $Tab + $p.Id + $Tab + $st + $Tab + [math]::Round($p.WorkingSet64/1MB,1) + $Tab + $p.CPU + $Tab + $p.Responding)
  }
  if ($rows.Count -eq 1) { $rows += ('(대상 ' + $Target + ' 프로세스 없음)') }
  Save-Text ($rows -join "`r`n") $label '프로세스.tsv'
}
function Save-Events([string]$label) {
  try {
    $ev = Get-WinEvent -FilterHashtable @{ LogName = @('Application','System'); StartTime = (Get-Date).AddSeconds(-($Interval + 120)) } -MaxEvents 300 -ErrorAction Stop
    $rows = @('시각' + $Tab + '로그' + $Tab + 'ID' + $Tab + '공급자' + $Tab + '수준' + $Tab + '메시지')
    foreach ($e in $ev) {
      $m = ($e.Message -replace '[\r\n\t]', ' '); if ($m.Length -gt 300) { $m = $m.Substring(0,300) }
      $rows += ($e.TimeCreated.ToString('yyyy-MM-ddTHH:mm:ss') + $Tab + $e.LogName + $Tab + $e.Id + $Tab + $e.ProviderName + $Tab + $e.LevelDisplayName + $Tab + $m)
    }
    Save-Text ($rows -join "`r`n") $label '윈도우이벤트.tsv'
  } catch { Add-Chain '이벤트 기록 없음' $label $_.Exception.Message }
}
function Save-Screen([string]$label) {
  if ($NoScreen) { return }
  try {
    Add-Type -AssemblyName System.Windows.Forms, System.Drawing
    $vs = [System.Windows.Forms.SystemInformation]::VirtualScreen
    if ($vs.Width -le 0) { throw '화면 없음' }
    $bmp = New-Object System.Drawing.Bitmap $vs.Width, $vs.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($vs.Left, $vs.Top, 0, 0, $bmp.Size)
    $dir = Join-Path $Root $label; $null = New-Item -ItemType Directory -Force -Path $dir
    $dst = Join-Path $dir ((Stamp) + '_화면.png')
    $bmp.Save($dst, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
    $fi = Get-Item -LiteralPath $dst
    Out-Line $ManP ((@((Next-No), (Now), $label, ($label + '\' + (Split-Path -Leaf $dst)), [string]$fi.Length, $fi.LastWriteTime.ToString('yyyy-MM-ddTHH:mm:ss'), (Sha $dst))) -join $Tab)
  } catch { Add-Chain '화면 캡처 없음' $label $_.Exception.Message }
}
function Save-Watch([string]$label) {
  if ($Watch -eq '' -or -not (Test-Path -LiteralPath $Watch)) { return }
  $n = 0
  foreach ($f in (Get-ChildItem -LiteralPath $Watch -File -ErrorAction SilentlyContinue)) {
    if ($f.Length -gt ($MaxFileMB * 1MB)) { Add-Chain '큰 파일 건너뜀' $f.FullName ([string]$f.Length); continue }
    Save-File $f.FullName $label ''; $n++
  }
  Add-Chain '대상 폴더 작은 파일 보존' $Watch ($n.ToString() + '건 읽기만 함')
}
function Do-Snap([string]$label, [bool]$screen) {
  Save-Watch $label; Save-Procs $label; Save-Events $label
  if ($screen) { Save-Screen $label }
  Add-Chain '스냅샷' $label ''
}
function Do-Verify {
  $bad = 0
  $rows = Get-Content -LiteralPath $ManP -Encoding UTF8 | Where-Object { $_ -ne '' } | Select-Object -Skip 1
  foreach ($r in $rows) {
    $f = $r.Split([char]9); $p = Join-Path $Root $f[3]
    if (-not (Test-Path -LiteralPath $p)) { Write-Host ('빠짐 ' + $f[0] + ' ' + $f[3]); $bad++ }
    elseif ((Sha $p) -ne $f[6]) { Write-Host ('바뀜 ' + $f[0] + ' ' + $f[3]); $bad++ }
  }
  $prev = '0' * 64
  foreach ($c in (Get-Content -LiteralPath $ChainP -Encoding UTF8 | Where-Object { $_ -ne '' } | Select-Object -Skip 1)) {
    $f = $c.Split([char]9)
    $body = ($f[0..5]) -join $Tab
    if ($f[5] -ne $prev -or (ShaText $body) -ne $f[6]) { Write-Host ('사슬 끊김 ' + $f[0]); $bad++ }
    $prev = $f[6]
  }
  Write-Host ('verify ' + $(if ($bad -eq 0) { '통과' } else { '문제 ' + $bad + '건' }))
  return $bad
}
function Do-Index {
  $out = Join-Path $Root 'GS증빙색인.tsv'
  $rows = @((@('증빙번호','라벨','파일','sha256','보존시각')) -join $Tab)
  foreach ($r in (Get-Content -LiteralPath $ManP -Encoding UTF8 | Where-Object { $_ -ne '' } | Select-Object -Skip 1)) {
    $f = $r.Split([char]9); $rows += ((@($f[0], $f[2], $f[3], $f[6], $f[1])) -join $Tab)
  }
  [System.IO.File]::WriteAllText($out, ($rows -join "`r`n") + "`r`n", $Utf8)
}

switch ($Mode) {
  'Start' {
    Add-Chain '증적 보존 가동' $Root ('일감 ' + $Case + ' · 대상 프로그램 ' + $Target + ' · 대상 폴더 ' + $Watch + ' · 주기 ' + $Interval + '초')
    Save-Env '시작'
    Save-File $PSCommandPath '시작' 'HiEvidence.ps1'
    foreach ($i in ($Inputs.Split(',') | Where-Object { $_ -ne '' })) { if (Test-Path -LiteralPath $i) { Save-File $i '시작_입력' ''; } else { Add-Chain '시작 입력 없음' $i '' } }
    Do-Snap '스냅샷_시작' $true
    $t0 = Get-Date; $next = $t0.AddSeconds($Interval); $seen = $false; $gone = $false
    while ($true) {
      Start-Sleep -Seconds $Poll
      if (Test-Path -LiteralPath (Join-Path $Root '중지.txt')) { Add-Chain '중지 요청 확인' '중지.txt' ''; break }
      if (((Get-Date) - $t0).TotalMinutes -ge $MaxMinutes) { Add-Chain '최대 시간 도달' $MaxMinutes.ToString() ''; break }
      if ($Target -ne '') {
        $alive = [bool](Get-Process -Name $Target -ErrorAction SilentlyContinue)
        if ($alive -and -not $seen) { $seen = $true; Add-Chain '대상 발견' $Target '' }
        if ($alive -and $gone) { $gone = $false; Add-Chain '다시 나타남(사건)' $Target ''; Do-Snap ('사건_다시나타남_' + (Stamp)) $true }
        if ($seen -and -not $alive -and -not $gone) { $gone = $true; Add-Chain '사라짐(사건)' $Target ''; Do-Snap ('사건_사라짐_' + (Stamp)) $true }
      }
      if ((Get-Date) -ge $next) { Do-Snap ('스냅샷_' + (Stamp)) $false; $next = (Get-Date).AddSeconds($Interval) }
    }
    Do-Snap '스냅샷_끝' $true
    $bad = Do-Verify; Do-Index; Add-Chain '끝 대조' $Root ('문제 ' + $bad + '건')
    exit $(if ($bad -eq 0) { 0 } else { 20 })
  }
  'Snap' { Do-Snap $(if ($Label -ne '') { $Label } else { '스냅샷_' + (Stamp) }) $false; exit 0 }
  'Event' { $l = $(if ($Label -ne '') { $Label } else { '사건_' + (Stamp) }); Add-Chain '사건 보존' $l $Note; Do-Snap $l $true; exit 0 }
  'Close' { Do-Snap '스냅샷_끝' $true; $bad = Do-Verify; Do-Index; Add-Chain '끝 대조' $Root ('문제 ' + $bad + '건'); exit $(if ($bad -eq 0) { 0 } else { 20 }) }
  'Verify' { $bad = Do-Verify; exit $(if ($bad -eq 0) { 0 } else { 20 }) }
}
