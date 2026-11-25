# 영어판 만들기

en.html은 index.html에서 자동으로 만든다. index.html을 고친 뒤:

1. `npm i acorn@8.11.3` (ext.js용)
2. 경로를 맞추고 `python3 gen.py index.html en.html`
3. 'missing'에 새 한국어 문장이 나오면 o23.json 같은 새 파일에 번역을 넣는다 (all.json의 id 기준, 새 문장은 id를 새로 매긴다)

- o00~o22.json: 문장별 번역 (id → 영어)
- overrides.json: 같은 조각이 문맥마다 다르게 번역돼야 할 때 (앞 문맥 → 영어)
- 업데이트 로그(CHANGES)는 gen.py 안의 영어 목록으로 바뀐다
