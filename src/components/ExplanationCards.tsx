import type { ExplanationCard } from "@/lib/types";

type ExplanationCardsProps = {
  cards: ExplanationCard[];
};

export function ExplanationCards({ cards }: ExplanationCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {cards.map((card) => (
        <article
          key={card.card_id}
          className="rounded-2xl border border-amber-200 bg-amber-50/70 p-4"
        >
          <div className="flex items-center justify-between gap-3">
            <span className="rounded-full bg-white px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-amber-700">
              {card.severity}
            </span>
            <span className="text-xs text-amber-800">
              confidence {Math.round(card.confidence.score * 100)}%
            </span>
          </div>
          <h3 className="mt-3 text-lg font-semibold text-slate-950">
            {card.title}
          </h3>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {card.summary}
          </p>
          <div className="mt-4 space-y-2 text-sm text-slate-700">
            {card.evidence.map((item) => (
              <p key={`${card.card_id}-${item.field}`}>
                <span className="font-medium">{item.field}</span>:{" "}
                {String(item.value)}{" "}
                <span className="text-slate-500">({item.origin})</span>
              </p>
            ))}
          </div>
          <p className="mt-4 text-xs uppercase tracking-[0.16em] text-amber-700">
            {card.annotation_status.replaceAll("_", " ")}
          </p>
        </article>
      ))}
    </div>
  );
}
