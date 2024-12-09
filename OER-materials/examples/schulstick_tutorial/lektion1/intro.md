---
title: Bereitstellen neuer Tutorials für den Schulstick
---

<!-- TODO: Ist der titel erforderlich? welche anderen metadaten sind erwünscht? wo ist das spezifiziert? -->
<!-- TODO: (Warum) ist metadata.yml (in späterer zukunft) erforderlich/sinnvoll, statt die metadaten direkt in den markdown-metadaten zu speichern? -->

<!-- TODO: gibt es ein glosar für das wording das wir im kontext des schulsticks verwenden? 
 * „Anleitung“ / „Tutorial“ ?
 * generischer Name für (Schul-)Stick (aka [`usb-live-linux` variants](https://github.com/fsfw-dresden/usb-live-linux/tree/main/variants.build))
-->

# Schulstick Tutorials

Der [**Schulstick**](https://schulstick.org/) ist eine [freie](https://de.wikipedia.org/wiki/Free/Libre_Open_Source_Software) Lern-, und Arbeitsplattform für lernende jeden Alters. Für unterschiedliche Zielgruppen existieren [verschiedene Varianten](https://github.com/fsfw-dresden/usb-live-linux/tree/main/variants.build). <!-- TODO --> Mit dem Wissen aus der folgenden Anleitung ist es Lehrkräften möglich, für die eigenen Bedürfnisse angepasste Varianten des Schulsticks zu erstellen.

Ein besonderer Wert des Schulsticks besteht darin, eine einheitliche **Plattform** für eine Vielzahl speziell angepasster und getesteter **Tutorials** zu bieten. Ziel ist es Nutzern (Schülern, Lehrkräften und Autodidakten) einen besonders zuverlässigen, niedrigschwelligen, frustfreien und effizienten Einstieg in neue Themen, Technologien und Softwarelösungen zu ermöglichen.

Lehrninhalte für den Stick sind [freies Wissen](https://fsfw-dresden.de/themen.html) und werden durch eine **Community** gemeisam erstellt und gepflegt. In der [**FAQ**](#FAQ) werden Fragen beantwortet, wie jeder der das Projekt unterstützen mag, unkompliziert **mithelfen** kann.


Die folgende Anleitung erklärt alle nötigen Schritte um:

1. Zu verstehen wie die Tutorials aufgebaut sind
2. Ein neues Tutorial anzulegen
3. Tutorials im Lernportal auf dem Schulstick zu testen
4. Inhalte zu veröffentlichen

<!-- Kurzvorstellung des FSFW-Stick-Projekts https://youtu.be/9XeJtgMcmKk -->


## Aufbau von Tutorials

Wir sammeln und pflegen Tutorials in einem gemeinsamen [Verzeichnis auf Github](https://github.com/fsfw-dresden/schulstick-portal/tree/main/tutor-next/markdown).
<!-- TODO künftiges Repo/Metaverzeichnis -->

Keine Angst, für keinen der Schritte aus dieser Anleitung ist Wissen über Git notwendig. Um eine einfache Anleitung zu erstellen, müssen nur drei Dateien erstellt und uns zugesendet werden.

Hier ein [einfaches Beispiel](https://github.com/fsfw-dresden/schulstick-portal/tree/main/tutor-next/markdown/schulstick_tutorial/lektion1) eines Tutorials:
<!-- TODO Template statt Selbstreferenz -->

Der Ordner enthällt die nötigen 3 Dateien:
* intro.md
* metadata.yml
* preview.png

Die folgenden Abschnitte erklären für jede der Dateien, was sie beinhalten, wie sie erstellt und getestet werden können.

Für fortgeschrittene Anwendungsfälle kann ein Tutorial noch weitere Dateien enthalten. Diese werden im folgenden mit erklärt; da die Dateien aber nicht zwingend benötigt werden, können die zugehörigen Kapitel aber für das Erstellen des ersten Tutorials gerne übersprungen werden.


### intro.md

Diese Datei beinhaltet die eigentlichen Inhalte.

Die Datei ist in der Auszeichnungssprache [**Markdown**](https://de.wikipedia.org/wiki/Markdown) geschrieben. 

Wie [unser Beispiel](https://raw.githubusercontent.com/fsfw-dresden/schulstick-portal/refs/heads/main/tutor-next/markdown/schulstick_tutorial/lektion1/intro.md) zeigt, die Datei ein einem leicht lesbaren Textformat (Ausgangsform). Da sie eine maschinenlesbare Struktur hat, kann sie automatisch in eine [schöne Zielform](https://github.com/fsfw-dresden/schulstick-portal/tree/main/tutor-next/markdown/schulstick_tutorial/lektion1/intro.md) übersetzt werden.

Markdown zu lernen ist einfach und geht schnell. Die wenigen nötigen Auszeichnugen werden [hier beschrieben](https://de.wikipedia.org/wiki/Markdown#Auszeichnungsbeispiele).

#### LiaScript

Genau genommen wird für die Schulstick-Tutorials eine Markdownerweiterung mit dem Name [LiaScript](https://liascript.github.io/) verwendet.

Zum erstellen unseres ersten Tutorials reicht es vollkommen aus, einfaches Markdown ohne die zusätzlichen Möglichkeiten von LiaScript zu schreiben.

Wer in seinen Tutorials (später) LiaScript nutzen möchte, kann hier [Beispiele](https://liascript.github.io/LiveEditor/examples.html) finden.

Es gibt einen [Online-Editor](https://liascript.github.io/LiveEditor/?/show/file/https://raw.githubusercontent.com/LiaScript/docs/master/README.md), indem nebeneinander die Ausgangsform geschrieben und die Zielform gesehen werden kann. Das verlinkte Beispiel öffnet die offizielle LiaScript-Dokumentation, welche selbst in LiaScript geschrieben ist.


### metadata.yml

Die in Markdown/LiaScript geschriebene Datei (`intro.md`) ist ausreichend um eine Anleitung unabhängig vom Schulscript zu schreiben.

[`metadata.yml`](https://raw.githubusercontent.com/fsfw-dresden/schulstick-portal/refs/heads/main/tutor-next/markdown/schulstick_tutorial/lektion1/metadata.yml) enthällt alle [Metadaten](https://de.wikipedia.org/wiki/Metadaten), welche vom Schulstick-Portal benötigt werden, um zusätzliche Funktionen zu ermöglichen.

Wir werden in einem späteren Abschnitt beschreiben, wie die Datei einfach erstellt/angepasst/getestet werden kann und welche Werte in ihr erlaubt sind.
<!-- TODO
Für Welche Werte gibt es defaults? Welche Werte sind zwingend?
Kann davon ausgegangen werden, dass beim Parsen Fehler rechtzeitig, vollständig und verständlich gemeldet werden?
-->

<!-- TODO
Gibt es eine Maximallänge (oder Empfehlungen) für die Länge des Titels?
-->

<!-- TODO
Schema!
-->

Nunächst ist für uns wichtig zu wissen, dass die Datei `metadata.yml`, welche für jedes Tutorial vorhanden sein muss, folgende beiden Zeilen enthällt:
```yml
markdownFile: "intro.md"
previewImage: "preview.png"
```

Der Wert hinter dem Schlüsselwort `markdownFile` benennt die Markdown/LiaScript-Datei, welche den Anfang des Tutorials beinhaltet.


### preview.png

Das Schulstick-Portal zeigt in der Liste der vorhandenen Tutorials jeweils ein Vorschaubild. In unserem Fall `preview.png`. Die Datei muss unter dem Name existieren, wie sie in `metadata.yml` unter dem Schlüsselwort `previewImage` benannt wurde.
<!-- TODO
Was sind gültige Werte? Relative Pfade? URLs? Anderes?
Gibt es einen Default? Oder wird bei fehlendem Eintrag ein Brauchbarer Fehler angezeigt?
-->

Bitte suche für dein Tutorial ein geeignetes Bild heraus oder erzeuge ein eigenes. Wenn ein vorhandenes Bild verwendet wird, bitte beachte, dass es unter einer freien Lizens steht.

<!-- TODO
Vielleicht sollten wir in metadata.yml die Quelle + Lizens des Bildes aufnehmen?
-->

### optionale Erweiterungen

Die bisher betrachteten 3 Dateien sind ausreichend um ein minimales Tutorial zu erstellen.

Wenn du direkt beginnen magst, kannst du gerne direkt im Kapitel [Neue Tutorials erstellen](#Neue Tutorials erstellen) weiterlesen.
<!-- TODO
Falls das Portal zwischen internen und externen Links unterscheided, wie können wir hier einen internen Link erzwingen?
Das sollte möglich (der default?) sein, egal ob auf ein Kapitel in der gleichen Datei oder in einer anderen lection gelinkt wird…
-->

Der Vollständigkeit halber — falls du später nachschauen magst oder wenn es dich gleich interessiert — im folgenden noch die optionalen Konfigurationsoptionen für das Schulstick-Portal…

#### Aufteilung und Verlinkung von Tutorials und Lektionen

Wenn dein Tutorial sehr lang wird, kann es nützlich sein, das Tutorial in separate Dateien für unterschiedliche Lektionen zu unterteilen.

<!-- TODO Beschreibung was es zu beachten gibt.
Wie wird das im Portal angezeigt?
Welche ist per default die erste Lektion? Die vom Dateinamen alphanumerisch erste?
Um Vorschaubilder wiederzuverwenden werden symlinks verwendet?

Wann lege ich einfach mehrere *.md-files im gleichen lektionsordner ab und wann benötige ich einen neuen Ordner? Immer dann, wenn die metadata.yml gleich/anders ist?
-->

Die Lektionen eines Tutorials können untereinander verlinkt werden. Als Linkziel wird dafür die relative Pfadangebe der verlinkten `.md`-Datei angegeben.
<!-- TODO Beispiel -->

<!-- TODO
Erklärung von „intenen/externen“ Links (im Portal bleibende und im externen Browser öffnende) — Wie ist dafür die genaue Logik?
-->

#### Skripte

##### Motivation

Das Portal soll es ermöglichen, dass Tutorials als eng miteinander verknüpfte Kombination aus Anleitung und Anwendung bzw. Anwendungsumgebung interagieren können. Für viele Lerninhalte wird es ausreichen, wenn eine (oder mehrere) [GUI](https://de.wikipedia.org/wiki/Grafische_Benutzeroberfl%C3%A4che)-Anwendungen am Anfang einer Lektion geöffnet werden.
<!-- TODO schlüsselwort in metadata.yml
genau erklärung des verhaltens
-->

In einigen Fällen ist jedoch gewünscht, dem Ersteller des Tutorials mehr Kontrolle über erforderliche Umgebungen zu ermöglichen, als ein bereits vorinstalliertes Softwarepaket in seiner Originalversion zu starten. Manche Anwendungen müssen mit bestimmten Plugins, Konfigurationsdateien, sonstigen Argumenten oder in einer bestimmten Version vorhanden sein.
Ein großer Mehrwert des bereitstellens der Tutorials auf dem Schulstick ist die Möglichkeit, dass der Ersteller der Lerninhalte genau die später vom Nutzer verwendete Version der Software testen und für die entsprechende Version korrekte Screenshots einbinden kann.
Wenn Software über die Zeit aktuallisiert wird, kann nicht vom Kernteam des Schulsticks erwartet werden, dass immer alle Tutorials im Detail überprüft werden, ob in den Anleitungen Anpassungen nötig geworden sind. Daher ist es wünschenswert, das Wissen der Inhalteersteller zu nutzen, um zu gewährleisten, dass Anwendungen und Anleitungen aufeinander abgestimmt sind.

<!-- TODO Langfristig könnte es hilfreich sein, wenn eine Anzahl generischer Tests implementiert werden, welche über die Metadaten deklatutor-nextrativ konfiguriert werden können (z.B. Versionstest über Semantic Versioning). Sollte aber lieber gründlich durchdacht und sauber implementiert werden… -->

##### Hooks

<!-- TODO Wollen wir die Skripte der übersicht halber in einem unterordner `scripts` ablegen? Das würde auch reuse durch einen einzelnen symlink erlauben. -->

Entwicklern von Tutorials, die sich etwas besser mit Linux auskennen, können im Ordner ihrer Lektionen shell-Skripte ablegen, und bekommen folgende Möglichkeiten sich ins System „einzuhaken“:

* `./scripts/run.sh`
* `./scripts/run_test.sh`
* `./scripts/install.sh`
* `./scripts/install_test.sh`

###### run.sh

Wenn die Datei `./scripts/run.sh` im Lektionsordner existiert, wird anstatt der in `metadata.yml` benannten Anwendung das Shell-Skript ausgeführt.

Auf diese Weise bekommt der Ersteller des Tutorials die Möglichkeit, GUI-Anwendungen und Komandozeilen-Umgebungen nach dem Bedürfnis des Tutorials zu starten. Das Skript läuft mit den Berechtigungen des Portal-Nutzers.

Mittels `run.sh` kann bei Bedarf z.B. der [LiaScript-CodeRunner](https://github.com/liascript/CodeRunner) gestartet werden, welcher Code aus interaktiven LiaScript-Kursen evaluieren kann.

###### run\_test.sh

Wenn die Datei `./scripts/run_test.sh` existiert, wird diese beim Lektionsstart immer vor der eigentlichen Anwendung (bzw. `run.sh`) ausgeführt.

Dieses Skript hat den Zweck unmittelbar vor der Laufzeit zu testen, ob alle Erwartungen des Tutorial-Erstellers erfüllt sind. Beispielsweise kann überprüft werden, ob eine Anwendung in der erwarteten Version installiert ist oder ob Systemeinstellungen und auf dem System vorhandene Ressourcen den Ansprüchen genügen.

<!-- TODO Beispiele implementieren -->

Wenn das Skript vorhanden ist, muss es sich wie folgt verhalten:

* Das Skript sollte möglichst zügig terminieren
* Der [Exit-Code](https://de.wikipedia.org/wiki/Return_Code) muss bei Erfolg `0` sein, in diesem Fall wird die Anwendung wie vom Nutzer erwartet gestartet.
* Der Exit-Code darf bei erkannten Problemen die Exit-Codes gemäß dem Standart von [Nagios-Plugins](https://nagios-plugins.org/doc/guidelines.html#AEN78) zurückgeben.
* Ausgabe an [stdout](https://de.wikipedia.org/wiki/Standard-Datenstr%C3%B6me#Standardausgabe_%28stdout%29) muss sich auf knappe, für die Zielgruppe des Tutorials verständliche Warnungen/Fehlermeldungen beschränken. Das Portal kann diese in einem Dialog an den Nutzer durchreichen.
* Ausgaben an [stderr](https://de.wikipedia.org/wiki/Standard-Datenstr%C3%B6me#Standardfehlerausgabe_%28stderr%29) darf (beliebige) Debug-Ausgaben beinhalten. Sie werden dem Endnutzer vom Portal nicht durchgereicht.

<!-- TODO in künftigen Versionen kann das Portal dem Nutzer interaktives Feedback ausgeben, sofortiges Implementieren im Portal ist nicht zwingend nötig -->

| Exit-Code | Bedeutung | Vorgeschlagenes Verhalten des Portals vor Start der Anwendung                                                                                           |
| --------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0         | OK        | Anwendung startet für den Nutzer transparent (keine zusätzliche Interaktion)                                                                            |
| 1         | Warning   | Der Nutzer wird informiert, dass etwas nicht ganz korrekt ist, vormutlich aber das Tutorial im großen und ganzen dennoch laufen könnte/sollte           |
| 2         | Critical  | Der Nutzer wird darauf hingewiesen, dass es grundlegende Probleme gab und nicht erwartet wird, dass das Tutorial erfolgeich nutzbar ist                 |

###### install.sh

Während die ersten beiden Skripte zur Laufzeit und mit Benutzerprivilegien liefen, ermöglichen `install.sh` und `install_test.sh` ähnliche Funktionalität zum Zeitpunkt der Installation durch einen Nutzer mit Administratorrechten.

`install.sh` kann bei Bedarf Konfigurationsdateien (wie z.B. udev-Regeln) erstellen oder den Nutzer zu einer weiteren Benutzergruppe hinzufügen.

###### install\_test.sh

Im Vergleich zu `install.sh` sollte `install_test.sh` nie die Systemkonfiguration manipulieren, sondern ausschließlich zur Installtionszeit testen.

Ausgabe und Return-Codes sollten sich genau wie bei `run_test.sh` verhalten.

###### Sicherheitsüberlegungen

Dies Skripte führen vom Tutorialersteller generierten und von der Community gereviewten Code auf dem System des Nutzers aus. Skripte und ihre Änderungen sollten daher von der Community genauso gründlich wie der Schulstick selbst überprüft werden. Für Tutorials mit Skripten wird ein Review-Prozess empfohlen, bei dem vor dem Mergen, mindestens ein Approval eines anderen Vertrauten Nutzers erteilt wurde.

`run.sh` und `run_test.sh` laufen mit Nutzerprivilegien. Das Schadenspotential wird ähnlich eingeschätzt, wie jenes, welches Ersteller von Tutorials mittels bösartigen Inhalten in ihren Anleitungen verursachen können.
Das erlauben wohl definierter und überprüfter Hooks kann einen Sicherheitsvorteil bieten, wenn sie einen Beitrag leisten, dass Tutorials höheren Standarts genügen müssen. Der Mechanismus der Hooks sollte genutzt werden, um dubiose Installationsanleitungen in den Tutorials konsequent zu verbieten. Dies betrifft insbesondere das Laden von Code aus Drittquellen.

`install.sh` und `install_test.sh` stellen einen Sicherheitskompromiss zu gunsten der Umsetzbarkeit, Wartbarkeit und Qualität von Inhalten dar.
Idealerweise würde anstelle von `install.sh` alle benötigte Funktionalität ausschließlich vom Ersteller der Distribution („Schulstick“) ermöglicht und durch eine unprivilegierte Ausführung von `install_test.sh` getestet werden. Eine solche Umsetzung ist mittelfristig denkbar. Bis dahin können `install.sh` und `install_test.sh` eine deutliche Vereinfachung der Erstellung neuer Lerninhalte ermöglichen. Wenn vom Ersteller der Distribution `install.sh` und `install_test.sh` aller Lerninhalte reviewed werden, kann das Schadenspotential durch böswillige Ersteller von Inhalten als niedrig eingeschätzt werden.


## Neue Tutorials erstellen

<!-- TODO -->


## Tutorials im Lernportal auf dem Schulsstick testen

<!-- TODO -->

## Inhalte veröffentlichen

<!-- TODO -->


## FAQ

### Etwas funktioniert nicht — Wo kann ich Fehler melden und um Korrektur oder Hilfe bitten?

<!-- TODO -->

### Ich habe einen Fehler gefunden — Wie kann ich etwas berichtigen und meine erste Änderung veröffentlichen?

<!-- TODO -->


## Features auf verschiedenen Umgebungen

<!-- TODO gehört wahrscheinlich nicht ins Tutorial; bei Gelegenheit an passenden Ort verschieben -->

|             | Portal @Schulstick         | externer Browser @Schulstick  | @www $Distribution                                                        |
| ----------- | -------------------------- | ----------------------------- | ------------------------------------------------------------------------- |
| liascript   | devserver/export           | devserver/export              | export                                                                    |
| plattform   | schulstick                 | schulstick                    | (unzuverlässig / könnte durch flakes implementiert werden / out of scope) |
| state       | ja                         | (patch liascript)             | (patch liascript)                                                         |
| interaktion | ja                         | (ja)                          | (nicht ohne zusätzliche Anwendung)                                        |

<!-- TODO gründlicher evaluieren und ausformulieren

Aktuelles Verständnis von J03:
* Es gibt ein Konzept, wie mittels Portal die gewünschte Funktionalität am kurzfristigsten umgesetzt werden kann.
* Ich sehe für die meisten Funktionen keine Notwendigkeit, die Imlementierung im Portal zu tun und eine Nutzung in externen Browsern nicht zu unterstützen.
* Der Schulstick hat als Plattform einen klaren Mehrwert gegenüber bestehenden Lösungen für Tutorials. Wenn eine Community qualitätiv hochwertige Tutorials pflegt, wären Lösungen denkbar, die Tutorials auch auf anderen Systemen zuverlässiger nutzbar zu machen. Das wäre aber ein eigenes Projekt…
-->
