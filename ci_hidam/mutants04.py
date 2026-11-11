# -*- coding: utf-8 -*-
"""0.4에서 더하는 변이(엔진을 일부러 틀리게 바꾼 사본). (이름, [(바꿀 글, 바꾼 글)], 실패해야 할 시나리오)."""
NEW_MUTANTS = [
    # 검수 K의 t12에서 0.2의 시나리오가 잡지 못했던 것(X1~X4 · X11 · X12)
    ("K-X1 엇갈린 기기 파일도 거울로 보냄", [('            elif rel in unsettled and rel not in self.finals:\n                skipped.append((rel, "판이 엇갈림 — 정합 먼저"))\n', '')], ["TS-119"]),
    ("K-X2 보호 등급도 자동 정합에 넣음", [('if max(grades) >= "D3":', 'if False:')], ["TS-119"]),
    ("K-X3 자동 실행의 구독 문을 없앰", [('        if self.tier != "구독" or not self.auto:\n            return None', '        if not self.auto:\n            return None')], ["TS-119"]),
    ("K-X4 대량 변경의 10건 바닥을 없앰", [('len(have) >= 10 and', 'len(have) >= 0 and')], ["TS-119"]),
    ("K-X11 미러링 해시 대조를 하지 않음", [('if sha(open(tmp, "rb").read()) != want[r]:', 'if False:')], ["TS-119"]),
    ("K-X12 거울에서 물러난 것을 보류함에 두지 않고 지움", [('shutil.move(os.path.join(mroot, r), hd)', 'os.remove(os.path.join(mroot, r))')], ["TS-119"]),
    # OP-2 ① 옛 판으로 덮어씀
    ("옛 판으로 덮어쓴 글자 문서를 뒤 판으로 이음", [('            return "확인"                                 # 글자 문서는 날짜를 믿지 않는다', '            return "잇기"                                 # 글자 문서는 날짜를 믿지 않는다')], ["TS-112"]),
    ("글자가 아닌 것을 옛 날짜의 판으로 덮어써도 이음", [('        if it["ext"] not in TEXT or not it["size"] or not old_it["size"]:\n            return "확인" if older else "잇기"', '        if it["ext"] not in TEXT or not it["size"] or not old_it["size"]:\n            return "잇기"')], ["TS-113"]),
    ("판 확인 제안을 내지 않음", [('                        if how == "확인":', '                        if False:')], ["TS-112"]),
    # ② 번갈아 고친 문서
    ("번갈아 고친 문서를 계보의 바탕에서 합치지 않음", [('                        if not self._lineage_merge(uniq, hs, e, row):', '                        if True:')], ["TS-114"]),
    ("같은 줄을 두 쪽이 고친 것을 글자 단위로 합치지 않음", [('                elif (i1, i2) == (k1, k2) and len(ra) == len(rb) == i2 - i1', '                elif False and (i1, i2) == (k1, k2) and len(ra) == len(rb) == i2 - i1')], ["TS-114"]),
    ("두 쪽이 같은 자리에 더한 줄을 겹침으로 봄", [('                    both.append((i1, ra, rb))', '                    return None')], ["TS-114"]),
    ("같은 줄을 다르게 고쳐도 합침(겹침 검사를 끔)", [('                elif max(i1, k1) < min(i2, k2) or (i1 == i2 and k1 < i1 < k2) or (k1 == k2 and i1 < k1 < i2):\n                    return None', '                elif False:\n                    return None')], ["TS-15"]),
    ("첫날: 다 담은 판을 고친 시각을 보지 않고 자동", [('            if sup and all(mt[sup[0]] >= mt[o] for o in hs):', '            if sup:')], ["TS-101"]),
    ("첫날: 모두가 담은 판을 바탕으로 합치지 않음", [('            if sub and len(hs) >= 3:', '            if False:')], ["TS-115"]),
    ("이름·폴더만 같은 다른 그림을 판으로 묶음", [('        return bool(ia and ib and self._aid(ia) == self._aid(ib))', '        return True')], ["TS-17"]),
    ("엔진이 만든 최종본의 시각도 고친 시각으로 셈", [('                if it_["hash"] in mt and not in_ref(r_):', '                if it_["hash"] in mt:')], ["TS-115"]),
    # ③ 금고 거울
    ("보호 등급을 금고 대신 거울에 그대로 비춤", [('                    vault[rel] = it["hash"]                # 보호 등급', '                    want[rel] = it["hash"]                # 보호 등급')], ["TS-44"]),
    ("금고를 잠그지 않고 그대로 씀", [('    ct = bytes(a ^ b for a, b in zip(pt, _ks(key, nonce, len(pt))))', '    ct = pt')], ["TS-117"]),
    ("금고 칸의 확인값을 보지 않음", [('    if not hmac.compare_digest(tag, hmac.new(key, b"mac" + nonce + ct, hashlib.sha256).digest()):', '    if False:')], ["TS-117"]),
    ("금고에 간 보호 등급을 화면에서 빼지 않음(늘 살핌 필요)", [('rel not in in_vault) if has_mirror else 0', 'True) if has_mirror else 0')], ["TS-108"]),
    # ④ 확신 중간
    ("받아들인 범주를 배우지 않음", [('and plan[r]["code"] in self.learned))', 'and False))')], ["TS-116"]),
    ("묶음 확인의 다섯 건 문턱을 없앰", [('(not asked_before or len(wait) >= 5)', 'True')], ["TS-116"]),
    ("엔진이 옮긴 파일을 다시 묶음 확인에 넣음", [(' and norm(p["rel"]) not in self.placed]', ']')], ["TS-116"]),
    # 원장
    ("원장 파일이 같은 크기로 바뀌면 모름", [('            full = full or bool(self.rows)', '            full = full')], ["TS-118"]),
    ("원장 사슬이 끊긴 뒤 예외로 죽음", [('                if not outer or "원장 사슬 끊김" not in str(e):', '                if True:')], ["TS-118"]),
    ("받는 쪽이 엔진이 아니어도 받으려 함(엔진 확인을 없앰)", [(' or not (led and hasattr(led, "verify") and led.verify() and isinstance(getattr(other, "anc", None), dict)):', ':')], ["TS-118"]),
]
