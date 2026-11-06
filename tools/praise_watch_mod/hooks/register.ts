import type { Register } from 'claude-code'

// 칭찬 크레딧 자동 감지 훅. 대표님 승인: 2026-11-06 20:56(조건부)·21:01(승인·적용 명령).
// 안전 규칙: 프롬프트를 막거나 바꾸지 않고(next(e)를 먼저 호출해 그대로 통과), 실패해도 조용히 지나간다.
// 칭찬 판별·원장 기록·중복 방지·끔 스위치(/tmp/claude-0/praise_watch.off)는 praise_watch.py가 맡는다.
const SCRIPT = '/tmp/claude-0/hs/tools/praise_watch.py'
const USER_ORIGINS = new Set(['composer', 'bridge', 'sdk'])

export const register: Register = on => {
  on('prompt.submit', async ($, e, next) => {
    const entered = next(e)
    try {
      if (!e.isMeta && !e.command && e.text && USER_ORIGINS.has(e.origin.kind)) {
        const sid = String(await $.session.id())
        const cwd = String(await $.session.cwd())
        const dir = cwd.replace(/[^A-Za-z0-9]/g, '-')
        const transcript = `/root/.claude/projects/${dir}/${sid}.jsonl`
        void $.process
          .run(['python3', SCRIPT, '--hook'], {
            stdin: JSON.stringify({ prompt: e.text, session_id: sid, transcript_path: transcript }),
            timeoutMs: 8000,
            env: { PW_REPO: '/tmp/claude-0/hs' },
          })
          .catch(() => undefined)
      }
    } catch {
      // 감지 실패는 입력에 영향을 주지 않는다
    }
    return entered
  }).catch(($, e, next) => next(e))
}
