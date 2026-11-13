# KI in der industriellen Fertigung: Kurzfassung

> Deutsche Kurzfassung der beiden Analysen in diesem Repository. Die vollständigen Texte sind auf Englisch: [Trendanalyse](../trend-scans/2026-11_ai-in-industrial-manufacturing.md) und [Bewertungsmodell](../tools/opportunity-scoring/).
>
> Erster Entwurf des KI-Assistenten, zur Durchsicht durch den Projektinhaber. Stand: 13. November 2026.

## Worum es geht

Zwei aufeinander aufbauende Analysen zu einer Frage: **Welche KI-Anwendungen in der industriellen Fertigung gewinnen an Bedeutung, und womit sollte ein Maschinenbauer beginnen?**

## 1. Trendanalyse: Was wächst schneller als das Feld?

**Vorgehen.** Zwei Signale: die Zahl wissenschaftlicher Veröffentlichungen pro Jahr (Quelle: OpenAlex, 2015 bis 2025) und Belege für den Einsatz in der Industrie. Die Methode und alle Schwellenwerte wurden festgelegt, bevor die Daten abgerufen wurden.

**Ergebnis.** Die Forschung zu KI in der Fertigung wuchs von 2020 bis 2025 um rund 35 % pro Jahr. Ein Thema fällt also nur auf, wenn es schneller wächst.

| Gruppe | Themen |
|---|---|
| Wachsen schneller als das Feld, in allen vier Robustheitstests | Digitale Zwillinge (+20,8 Prozentpunkte), visuelle Qualitätsprüfung (+8,3), additive Fertigung (+5,5) |
| Zu jung für eine Wachstumsrate, aber jedes Jahr gestiegen | Industrielle Copiloten (2020: 1 Veröffentlichung, 2025: 608), Produktionsplanung, Energieoptimierung |
| Etabliert, wachsen nur im Tempo des Feldes | Vorausschauende Instandhaltung, Prozessoptimierung, Robotik |
| Klein und uneinheitlich | Generatives Design |

Digitale Zwillinge führen bei beiden Signalen. Industrielle Copiloten zeigen das Gegenteil: den steilsten Anstieg in der Forschung, aber keinen bestätigten Einsatz in der Produktion.

**Empfehlung.** Sieben Themen wurden zur Bewertung ausgewählt: die ersten sechs und die vorausschauende Instandhaltung.

## 2. Bewertungsmodell: Womit beginnen?

**Vorgehen.** Die sieben Themen wurden als konkrete Vorhaben für einen **fiktiven** Maschinenbauer (rund 2.000 Beschäftigte) formuliert und nach fünf gewichteten Kriterien bewertet: Wertpotenzial, technische Machbarkeit, strategische Passung, Zeit bis zum Nutzen und Risiko. Anschließend wurde geprüft, wie stabil die Rangfolge ist: 1.000 Durchläufe mit veränderten Gewichten, und jede auf einer Annahme beruhende Bewertung um einen Punkt verändert.

**Ergebnis.**

| Einstufung | Vorhaben |
|---|---|
| **Verfolgen** | Digitaler Zwilling für die virtuelle Inbetriebnahme: 3,85 von 5 Punkten, in allen 1.000 Durchläufen auf Platz 1 |
| **Prüfen** | Vorausschauende Instandhaltung als Service, KI-Sichtprüfung als Maschinenoption, Service-Copilot, KI-gestützte Fertigungsplanung: 3,15 bis 3,25 Punkte, zu nah beieinander für eine Rangfolge |
| **Zurückstellen** | Energieoptimierter Betriebsmodus, KI-gestützter 3D-Druck von Teilen: unter 2,5 Punkte |

**Wirtschaftlichkeit.** Der digitale Zwilling amortisiert sich innerhalb von drei Jahren, wenn er 3,4 % der Inbetriebnahmestunden einspart. Hersteller berichten von 25 % bis 70 %.

**Empfehlung.** Mit dem digitalen Zwilling beginnen. Unter den vier eng beieinanderliegenden Vorhaben nicht nach Rang entscheiden, sondern zuerst die jeweils entscheidende Schätzung absichern, meist den jährlichen Wert.

## Was die Analysen nicht leisten

- **Veröffentlichungen sind keine Anwendung.** Forschung kann der Praxis um Jahre vorauslaufen. Die Einsatzbelege gleichen das nur grob aus und stammen teils von Anbietern.
- **Das Unternehmen ist fiktiv, die Bewertungen sind Einschätzungen.** 19 von 35 beruhen auf Annahmen, und genau diese entscheiden über das Mittelfeld der Rangfolge.
- **Die Suchbegriffe bestimmen das Ergebnis.** Sie wurden an Stichproben geprüft, aber nur auf Treffergenauigkeit, nicht auf Vollständigkeit.

## Wie das Projekt entstanden ist

Das Projekt wurde wie ein echtes Projekt geführt: Projektauftrag, Anforderungen mit prüfbaren Abnahmekriterien, dokumentierte Änderungsanträge und eine kritische Prüfung der Methoden vor der Umsetzung. Es entstand mit einem KI-Assistenten (Claude Code). Der Projektinhaber legte Umfang, Methoden und Regeln fest und prüft die Ergebnisse; der Assistent schrieb den Code, recherchierte Quellen und verfasste die ersten Entwürfe der Bewertungen und Texte. Alle Tabellen und Abbildungen lassen sich mit einem Befehl aus den gespeicherten Daten neu erzeugen.
