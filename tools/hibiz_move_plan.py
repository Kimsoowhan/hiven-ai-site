#!/usr/bin/env python3
# HiBiz 정리 실행 준비(DR-08·DR-02): 검사 K07(옛 판이 맨 위에 남음)·K08(옛 폴더안내)의 줄을 이전판 폴더로 옮기는 계획표와
# PC에서 도는 PowerShell 스크립트를 만든다. 지우지 않는다. 옮기기 전·뒤 SHA256을 기록한다.
import re,os,sys
C='cowork/ctl/hibiz/';YMD='261113';ROOT='C:\\Users\\marty\\Documents\\HiBiz'
todo=[l.split('\t') for l in open(C+'HiBiz_정리할_것-%s_0.1_작업.tsv'%YMD,encoding='utf-8').read().split('\n')[1:] if l]
dirs={l.split('\t')[0] for l in open(C+'hibiz_tree.tsv',encoding='utf-8').read().split('\n')[1:] if l and l.split('\t')[1]=='dir'}
plan=[];hold=[]
for k,rule,sev,p,why,act in todo:
    if k not in('K07','K08'): continue
    d,fn=p.rsplit('/',1)
    ex=sorted(x for x in dirs if x.startswith(d+'/') and x.count('/')==d.count('/')+1 and x.endswith('이전판'))
    if ex: dst=ex[0]
    else:
        m=re.match(r'^(\d\d(?:_\d\d)*)_',d.rsplit('/',1)[1])
        if not m: hold.append([k,p,'폴더 이름에 번호가 없어 이전판 폴더 이름을 정하지 못함(Fable 판정)']);continue
        dst=d+'/'+m.group(1)+'_02_이전판'
    plan.append([k,rule,p,dst+'/'+fn,why,'있던 이전판 폴더' if ex else '새로 만드는 이전판 폴더'])
def W(n,h,b):
    with open(n,'w',encoding='utf-8') as f:
        f.write('\t'.join(h)+'\n')
        for r in b: f.write('\t'.join(r)+'\n')
W(C+'HiBiz_옮김_계획-%s_0.1_작업.tsv'%YMD,['검사','규칙','지금 자리','옮길 자리','까닭','이전판 폴더'],plan)
W(C+'HiBiz_옮김_보류-%s_0.1_작업.tsv'%YMD,['검사','지금 자리','보류 까닭'],hold)
ps=['# HiBiz 정리 실행(옛 판·옛 폴더안내를 이전판 폴더로 옮김) · Fable 5.2 · 2026-11-13','# 지우지 않습니다. 옮기기 전·뒤 SHA256을 기록하고, 해시가 다르면 그 줄에서 멈춥니다.','# 쓰는 법: powershell -ExecutionPolicy Bypass -File 이_파일.ps1   (먼저 보기만: -WhatIf 를 붙임)','param([switch]$WhatIf)','$ErrorActionPreference="Stop"',"$root='%s'"%ROOT,"$plan=Join-Path $PSScriptRoot 'HiBiz_옮김_계획-%s_0.1_작업.tsv'"%YMD,"$log=Join-Path $PSScriptRoot ('HiBiz_옮김_기록-'+(Get-Date -Format 'yyMMdd_HHmm')+'_작업.tsv')",'"때`t지금 자리`t옮긴 자리`t옮기기 전 SHA256`t옮긴 뒤 SHA256`t결과" | Out-File -FilePath $log -Encoding utf8','$n=0;$skip=0','Import-Csv -Path $plan -Delimiter "`t" -Encoding UTF8 | ForEach-Object {',' $src=Join-Path $root ($_."지금 자리" -replace "/","\\"); $dst=Join-Path $root ($_."옮길 자리" -replace "/","\\")',' if(-not (Test-Path -LiteralPath $src)){ "$(Get-Date -Format s)`t$src`t$dst`t`t`t원본 없음(이미 옮겼거나 이름이 바뀜)" | Out-File $log -Append -Encoding utf8; $skip++; return }',' if(Test-Path -LiteralPath $dst){ "$(Get-Date -Format s)`t$src`t$dst`t`t`t옮길 자리에 같은 이름이 있음(옮기지 않음)" | Out-File $log -Append -Encoding utf8; $skip++; return }',' $h1=(Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash',' if($WhatIf){ "$(Get-Date -Format s)`t$src`t$dst`t$h1`t`t보기만" | Out-File $log -Append -Encoding utf8; return }',' New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null',' Move-Item -LiteralPath $src -Destination $dst',' $h2=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash',' if($h1 -ne $h2){ "$(Get-Date -Format s)`t$src`t$dst`t$h1`t$h2`t해시 다름: 멈춤" | Out-File $log -Append -Encoding utf8; throw "해시 다름: $dst" }',' "$(Get-Date -Format s)`t$src`t$dst`t$h1`t$h2`t옮김" | Out-File $log -Append -Encoding utf8; $n++','}','Write-Output "옮김 $n 건 · 건너뜀 $skip 건 · 기록 $log"']
open(C+'HiBiz_정리_실행-%s_0.1_작업.ps1'%YMD,'w',encoding='utf-8-sig').write('\r\n'.join(ps)+'\r\n')
print('옮길 것',len(plan),'보류',len(hold),'새 이전판 폴더',len({r[3].rsplit('/',1)[0] for r in plan if r[5].startswith('새로')}))
