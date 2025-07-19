# ovos-skill-my-german-public-api
Dieser Skill ist grundsätzlich nur für deutschsprachige Benutzer geeignet. Aktuell ist nur eine Postleitzahlensuche möglich.
## Beispiele
- Suche eine Postleitzahl
- Nenne eine Postleitzahl
## Dialoge
Danach erfolgt eine Abfrage der Stadt oder Gemeinde und anschließend der Straße.
##Bekannte Probleme
Da es sich bei all diesen Begriffen um Eigennamen handelt, haben STT(speech to text)-Syteme erfahrungsgemäß große Schwierigkeiten, wenn es sich nicht gerade um Orte wie Hamburg oder Berlin handelt. Orte wie Lübbow beispelsweise werden als französiert als Lübbeau wiedergegeben. An eine Buchstabierfunktion ist gedacht, aber noch nicht implementiert. Wichtig ist auch, dass sich die Ortsbezeichnung abhängig ist von der staatlichen Organisation. D. h. nicht jedes Dorf findet sich in der PLZ-Datenbank sondern nur die ihnen übergestellte Gemeinde.
