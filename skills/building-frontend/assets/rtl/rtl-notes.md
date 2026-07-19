# RTL support

RTL is asked **separately** from the locale list — it changes layout, not just
strings, so Arabic/Hebrew in scope is a bigger commitment than French/German.

If RTL is in scope:

- Set `dir="rtl"` on `<html>` for RTL locales (drive it from the active locale).
- Use **CSS logical properties** everywhere: `margin-inline-start` not `margin-left`,
  `padding-inline-end` not `padding-right`, `inset-inline-start` not `left`,
  `text-align: start` not `left`. These flip automatically with `dir`.
- Mind directional icons (arrows, chevrons, back/next) — mirror them for RTL.
- Keep numerals and code LTR inside RTL text where appropriate (`unicode-bidi`).
- Add an RTL locale to the Playwright language-switch matrix so layout direction
  is actually exercised, not assumed.

If RTL is NOT in scope: still prefer logical properties — they cost nothing now and
save a full layout pass later (invariant-2 scope clause: cheap conventions adopted
by default).
