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
## Weitere intents
Geplant sind weitere intents, die Informationen von öffentlichen Servern holen wie z. B. aktuelle statistische Daten zu Deutschland.
