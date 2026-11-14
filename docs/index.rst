Documentation de bujo
=====================

**bujo** est une bibliothèque Python pour tenir un Bullet Journal :
tâches, événements et notes, rangés dans des Daily Logs et des
Monthly Logs, avec la migration des tâches non terminées et
l'affichage avec les symboles du rapid logging.

Exemple
-------

.. code-block:: python

   from datetime import date, timedelta

   from bujo import Journal, Signifier
   from bujo.display import render_log

   journal = Journal()
   journal.add_task("Réviser Python", "Chapitre POO",
                    signifier=Signifier.PRIORITY)
   journal.add_note("Idée", "Une appli de BuJo en ligne de commande")
   journal.migrate_day(date.today(), date.today() + timedelta(days=1))
   print(render_log(journal.daily_log()))

.. toctree::
   :maxdepth: 2
   :caption: Contenu

   api