## ovos-skill-my-german-public-api
Dieser Skill ist grundsätzlich nur für deutschsprachige Benutzer geeignet. Aktuell sind nur Postleitzahlensuche und Abruf von Hochwasserwarnungen  möglichmöglich.
## Beispiele
### Postleitzahlsuche
- "Suche eine Postleitzahl"
- "Nenne eine Postleitzahl"
### Dialog
Danach erfolgt eine Abfrage der Stadt oder Gemeinde und anschließend der Straße.
### Bekannte Probleme
Da es sich bei all diesen Begriffen häufig um Eigennamen handelt, haben STT- (speech to text) Syteme erfahrungsgemäß große Schwierigkeiten, wenn es sich nicht gerade um Orte wie Hamburg oder Berlin handelt. Orte wie Lübbow beispielsweise werden als französiert als Lübbeau wiedergegeben. An eine Buchstabierfunktion ist gedacht, aber noch nicht implementiert. Wichtig ist auch, dass die Ortsbezeichnung abhängig ist von der staatlichen Organisation. D. h. nicht jedes Dorf findet sich in der PLZ-Datenbank sondern nur die ihnen übergeordnete Gemeinde.
### Hochwasserwarnungen
- "Gibt es Hochwasserwarnungen"  - alle vorliegenden Warnungen werden aufgezählt.
- "Gibt es Hochwasserwarnungen für Bayern" - nur Warnungen, die das Bundesland Bayern betreffen, werden wiedergegeben.
### Verkehrsmeldungen
- "Verkehrsnachrichten [Staumeldungen] von der [Autobahn] {A 14}"
- "Gibt es Staus [Störungen] [Verkehrsmeldungen] auf [von] der [Autobahn] {A 9}"

Je nach Anzahl der Meldungen des Servers (keine, genau eine oder mehr als eine) unterscheiden sich die Ansagen strukturell. Dabei habe ich versucht je nach Länge der gesprochenen Informationen Pausen einzubauen. Es hängt allerdings auch von der Latenz des verwendeten TTS-Sytems ab, ob die Pausen eher zu kurz oder eher zu lang erscheinen.
## Reisewarnungen des Auswärtigen Amtes
- "Gibt es Reisewarnungen"
- "Welche Reisewarnungen gibt es [aktuell]"

Abgerufen werden aktuelle Reisewarnungen des Auswärtigen Amtes (= Außenministerium Deutschlands). Zur Zeit ist das Ergebnis eine Aufzählung von Ländernamen, für die es Reisewarnungen gibt und Ländern, für die es Sicherheitshinweise gibt. die genauen Hintergründe für die Warnungen und Hinweise sind nicht enthalten. Diese müssen anderweitig recherchiert werden z. B. hier: https://www.auswaertiges-amt.de/de/reiseundsicherheit/10-2-8reisewarnungen.
## Pollenwarnungen des Deutschen Wetterdienstes
- Gibt es heute [morgen, übermorgen] Pollenwarnungen (in|für) Niedersachsen [Hamburg, Bayern, ...]
- Welche (Pollenwarnungen|Allergiewarnungen) gibt es heute [morgen, übermorgen] für Niedersachsen [Hamburg, Bayern, ...]

Erforderlich sind die Angabe des Zeitraumes also "heute", "morgen" oder "übermorgen" sowie der Name eines Bundeslandes z. B. "Hessen". Es werde nur Warnungen genannt, wenn es eine Warnstufe oberhalb von "0" gibt. Für folgende Pflanzen werden i. d. R. Informationen vorgehalten: Ambrosia, Beifuss, Birke, Erle, Esche, Gräser, Hasel und für Roggen. Einige Bundesländer sind in Teilregionen unterteilt. Es werden Pollenwarnungen für alle Teilregionen aufgezählt. Manche Bundesländer sind vom DWD zusammengefasst worden, z.B. Schleswig-Hostein und Hamburg oder Rheinland-Pfalz und das Saarland. In diesem Fall werden die einzelnen Bundesländer als Teilregionen behandelt. Mecklenburg-Vorpommern hat keine Teilregionen.