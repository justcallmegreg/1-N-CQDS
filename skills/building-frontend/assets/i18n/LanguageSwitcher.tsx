// LanguageSwitcher.tsx — minimal, accessible, testable.
import { useI18n } from "./i18n";

const LABELS: Record<string, string> = { en: "English", de: "Deutsch", ar: "العربية", he: "עברית" };

export function LanguageSwitcher() {
  const { locale, setLocale, locales, t } = useI18n();
  return (
    <label data-testid="language-switcher" style={{ display: "inline-flex", gap: ".5rem", alignItems: "center" }}>
      <span>{t("actions.switch_language")}</span>
      <select
        data-testid="language-select"
        value={locale}
        onChange={(e) => setLocale(e.target.value)}
        aria-label={t("actions.switch_language")}
      >
        {locales.map((l) => (
          <option key={l} value={l}>{LABELS[l] ?? l}</option>
        ))}
      </select>
    </label>
  );
}
