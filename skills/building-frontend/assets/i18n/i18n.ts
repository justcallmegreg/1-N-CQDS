// i18n.ts — minimal runtime i18n for Vite+React. YAML is imported as objects
// (via vite-plugin-yaml or a loader); here we type the shape.
import { createContext, useContext, useState, useCallback, createElement } from "react";
import type { ReactNode } from "react";

export type Dict = Record<string, unknown>;
const COOKIE = "locale";

function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
  return m ? decodeURIComponent(m[1]) : null;
}
function writeCookie(name: string, value: string) {
  // 1 year, root path, Lax
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=31536000; SameSite=Lax`;
}

function lookup(dict: Dict, key: string): string {
  const val = key.split(".").reduce<unknown>(
    (o, k) => (o && typeof o === "object" ? (o as Dict)[k] : undefined), dict);
  return typeof val === "string" ? val : key;
}

interface I18n { t: (key: string) => string; locale: string; setLocale: (l: string) => void; locales: string[]; }
const I18nContext = createContext<I18n | null>(null);

export function I18nProvider(props: { locales: Record<string, Dict>; initial?: string; children: ReactNode }) {
  const available = Object.keys(props.locales);
  const start = readCookie(COOKIE) ?? props.initial ?? available[0];
  const [locale, setLocaleState] = useState(available.includes(start) ? start : available[0]);
  const setLocale = useCallback((l: string) => {
    if (!available.includes(l)) return;
    writeCookie(COOKIE, l);
    setLocaleState(l);
  }, [available]);
  const t = useCallback((key: string) => lookup(props.locales[locale], key), [props.locales, locale]);
  return createElement(I18nContext.Provider, { value: { t, locale, setLocale, locales: available } }, props.children);
}

export function useI18n(): I18n {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within <I18nProvider>");
  return ctx;
}

export function initialLocaleFromCookie(fallback: string): string {
  return readCookie(COOKIE) ?? fallback;
}
