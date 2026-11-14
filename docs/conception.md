# Conception de la bibliothèque bujo

Ce document décrit le modèle objet de la bibliothèque et les choix de
conception de l'équipe.

## Diagramme de classes

```mermaid
classDiagram
    class Entry {
        <<abstract>>
        -str _id
        -str _name
        -str _description
        -datetime _created_at
        -date _log_date
        -Signifier _signifier
        +symbol() str*
    }
    class Task {
        -TaskStatus _status
        -str _migrated_from
        +complete()
        +cancel()
        +migrate(target_date) Task
        +schedule(target_date) Task
        +is_pending() bool
    }
    class Event {
        -time _event_time
        +event_date() date
    }
    class Note
    Entry <|-- Task
    Entry <|-- Event
    Entry <|-- Note

    class TaskStatus {
        <<enumeration>>
        TODO
        DONE
        MIGRATED
        SCHEDULED
        CANCELLED
    }
    class Signifier {
        <<enumeration>>
        PRIORITY
        IDEA
    }
    Task --> TaskStatus
    Entry --> Signifier

    class Log {
        <<abstract>>
        -dict _entries
        +title() str*
        +accepts(day) bool*
        +add(entry)
        +remove(entry_id) Entry
        +get(entry_id) Entry
        +entries() list
        +tasks() list
        +pending_tasks() list
    }
    class DailyLog {
        -date _day
    }
    class MonthlyLog {
        -int _year
        -int _month
    }
    Log <|-- DailyLog
    Log <|-- MonthlyLog
    Log o-- Entry

    class Journal {
        -dict _daily_logs
        -dict _monthly_logs
        -dict _locations
        +daily_log(day) DailyLog
        +monthly_log(year, month) MonthlyLog
        +add_task(name, description, day, signifier) Task
        +add_monthly_task(name, description, year, month, signifier) Task
        +add_event(name, description, event_date, event_time, signifier) Event
        +add_note(name, description, day, signifier) Note
        +get_entry(entry_id) Entry
        +get_task(entry_id) Task
        +find_by_name(name) list
        +complete_task(entry_id) Task
        +cancel_task(entry_id) Task
        +delete_entry(entry_id) Entry
        +set_signifier(entry_id, signifier) Entry
        +pending_tasks() list
        +events_on(day) list
        +migrate_task(entry_id, target_date) Task
        +migrate_day(from_day, to_day) list
        +migrate_month(year, month) list
        +schedule_task(entry_id, target_date) Task
    }
    Journal *-- DailyLog
    Journal *-- MonthlyLog
```

Le Future Log, les collections et l'index seront ajoutés au niveau 3.

## Cycle de vie d'une tâche

```mermaid
stateDiagram-v2
    [*] --> TODO : création
    TODO --> DONE : complete()
    TODO --> MIGRATED : migrate()
    TODO --> SCHEDULED : schedule()
    TODO --> CANCELLED : cancel()
    DONE --> [*]
    MIGRATED --> [*]
    SCHEDULED --> [*]
    CANCELLED --> [*]
```

Seule une tâche à faire peut changer d'état : les quatre autres états
sont définitifs. Toute autre transition lève `InvalidTransitionError`.

## Exceptions

```text
BujoError
├── EntryNotFoundError        identifiant inconnu
├── DuplicateEntryError       entrée ajoutée deux fois dans un log
├── ValidationError           donnée invalide
│   ├── EmptyNameError        nom vide
│   └── InvalidDateError      date ou heure invalide ou incohérente
└── InvalidTransitionError    changement d'état interdit
```

## Choix de conception

1. **Identifiant unique.** Chaque entrée reçoit un identifiant généré
   avec `uuid4`. Toutes les opérations utilisent cet identifiant ; la
   recherche par nom n'est qu'une facilité, car deux entrées peuvent
   porter le même nom.
2. **Encapsulation.** Les attributs sont privés et lus par des
   propriétés. L'état d'une tâche n'a pas de setter : il ne change que
   par `complete`, `cancel`, `migrate` et `schedule`, qui vérifient
   les règles du cycle de vie.
3. **Migration.** Comme sur papier, la tâche d'origine reste dans son
   log avec l'état « migrée ». Une copie à faire, avec un nouvel
   identifiant, est créée dans le log cible ; son attribut
   `migrated_from` contient l'identifiant de l'originale. Un nouvel
   identifiant est nécessaire car une entrée appartient à un seul log.
4. **Migration de fin de mois.** Toutes les tâches à faire du mois
   (Monthly Log et Daily Logs du mois) sont reportées dans le Monthly
   Log du mois suivant.
5. **Planification.** Une tâche planifiée est copiée dans le Monthly
   Log du mois visé (au niveau 3, elle ira dans le Future Log).
6. **Façade.** La classe `Journal` est le point d'entrée unique. Elle
   mémorise dans `_locations` le log de chaque entrée, ce qui permet de
   retrouver une entrée immédiatement.
7. **Séparation des responsabilités.** Le modèle (`entries`, `logs`,
   `journal`) ne sait pas comment il est affiché (`display`). La
   validation des saisies est regroupée dans `validation`.
8. **Dates.** Les dates sont des objets `date` du module `datetime`,
   jamais des chaînes. Les objets `datetime` sont refusés, car Python
   ne sait pas les comparer avec des `date`.