---
title: Bereitstellen neuer Tutorials für den Schulstick
---

<!-- TODO: ist der titel erforderlich? welche anderen metadaten sind erwünscht? wo ist das spezifiziert? -->

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
3. Tutorials im Lernportal auf dem Unistick zu testen
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

<!-- TODO -->


### preview.png

<!-- TODO -->


### scripte

<!-- TODO -->


### Aufteilung und Verlinkung von Tutorials und Lektionen


## Neue Tutorials erstellen

<!-- TODO -->


## Tutorials im Lernportal auf dem Unistick testen

<!-- TODO -->

## Inhalte veröffentlichen

<!-- TODO -->


## FAQ

### Etwas funktioniert nicht — Wo kann ich Fehler melden und um Korrektur oder Hilfe bitten?

<!-- TODO -->

### Ich habe einen Fehler gefunden — Wie kann ich etwas berichtigen und meine erste Änderung veröffentlichen?

<!-- TODO -->

