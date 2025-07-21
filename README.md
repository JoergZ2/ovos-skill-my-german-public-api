## ovos-skill-my-german-public-api
Dieser Skill ist grundsätzlich nur für deutschsprachige Benutzer geeignet. Aktuell ist nur eine Postleitzahlensuche möglich.
## Beispiele
- Suche eine Postleitzahl
- Nenne eine Postleitzahl
## Dialoge
Danach erfolgt eine Abfrage der Stadt oder Gemeinde und anschließend der Straße.
## Bekannte Probleme
Da es sich bei all diesen Begriffen häufig um Eigennamen handelt, haben STT(speech to text)-Syteme erfahrungsgemäß große Schwierigkeiten, wenn es sich nicht gerade um Orte wie Hamburg oder Berlin handelt. Orte wie Lübbow beispielsweise werden als französiert als Lübbeau wiedergegeben. An eine Buchstabierfunktion ist gedacht, aber noch nicht implementiert. Wichtig ist auch, dass die Ortsbezeichnung abhängig ist von der staatlichen Organisation. D. h. nicht jedes Dorf findet sich in der PLZ-Datenbank sondern nur die ihnen übergeordnete Gemeinde.
## Weitere intents
Geplant sind weitere intents, die Informationen von öffentlichen Servern holen wie z. B. Unwetterwarnungen, Verkehrsmeldungen oder aktuelle statistische Daten zu Deutschland.
