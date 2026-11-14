"""Démonstration de la bibliothèque bujo.

Lancer ``python demo.py`` depuis la racine du projet. Le script
affiche un journal dans le terminal et remplit les fichiers
``logs/debug.log`` (tous les messages) et ``logs/errors.log``
(erreurs seulement).
"""

from datetime import date, time, timedelta

from bujo import BujoError, Journal, Signifier, setup_logging
from bujo.display import render_key, render_log, render_month, render_tasks


def main() -> None:
    """Déroule un scénario complet d'utilisation du journal."""
    setup_logging("logs")
    journal = Journal()
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)

    # 1. Remplir le Daily Log d'aujourd'hui.
    revise = journal.add_task(
        "Réviser Python", "Chapitre POO", signifier=Signifier.PRIORITY
    )
    shopping = journal.add_task("Faire les courses")
    bank = journal.add_task("Appeler la banque")
    report = journal.add_task("Rendre le rapport")
    journal.add_event("Cours de Python", today, time(10, 0))
    journal.add_event("Réunion de projet", today, time(14, 30))
    idea = journal.add_note("Une version en ligne de commande")
    journal.set_signifier(idea.id, Signifier.IDEA)

    # 2. Faire vivre les tâches.
    journal.complete_task(shopping.id)
    journal.cancel_task(bank.id)
    journal.add_monthly_task("Préparer le rendu du projet")
    journal.schedule_task(report.id, next_month)
    journal.migrate_day(today, tomorrow)

    # 3. Afficher le journal.
    print(render_key())
    print()
    print(render_log(journal.daily_log()))
    print()
    print(render_log(journal.daily_log(tomorrow)))
    print()
    print(render_month(journal.monthly_log()))
    print()
    print(render_month(journal.monthly_log(next_month.year, next_month.month)))
    print()
    print("Tâches encore à faire")
    print(render_tasks(journal.pending_tasks))

    # 4. Deux erreurs volontaires, pour remplir logs/errors.log.
    print()
    print("Erreurs volontaires (voir logs/errors.log) :")
    try:
        journal.complete_task(revise.id)  # déjà migrée : interdit
    except BujoError as error:
        print(f"  Erreur attendue : {error}")
    try:
        journal.add_event("Fête", "demain")  # pas une vraie date
    except BujoError as error:
        print(f"  Erreur attendue : {error}")


if __name__ == "__main__":
    main()
