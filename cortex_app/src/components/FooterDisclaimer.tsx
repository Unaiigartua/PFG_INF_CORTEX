import { Info } from "lucide-react";
import { useI18n } from "../context/I18nContext";

export default function FooterDisclaimer() {
  const { t } = useI18n();

  return (
    <div className="flex items-center text-[var(--color-text-light)] text-sm backdrop-blur-sm px-6 py-3 rounded-full shadow-lg border border-[var(--color-primary)]/20 hover:shadow-xl transition-all duration-300 group"
         style={{ backgroundColor: 'var(--color-background-card)' }}>
      <Info className="icon-md mr-3 text-[var(--color-warning)] group-hover:scale-105 transition-transform duration-300" />
      <p className="group-hover:text-[var(--color-text)] transition-colors duration-300">
        {t('footer.disclaimer')}
      </p>
    </div>
  );
}