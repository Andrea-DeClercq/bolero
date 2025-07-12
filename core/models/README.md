# Gestion des modèles

Les modèles tournent avec la bibliothèque [SqlService](https://github.com/dgilland/sqlservice), elle-même manipulant la bibliothèque [SQLAlchemy](https://www.sqlalchemy.org/).

Le présent moteur de modèle sql va analyser la base de données pour automatiquement créer les classes python correspondantes, sans avoir besoin de créer des modules python de descriptions.
Il est possible d'enrichir cette analyse pour par exemple refléter les relations entre les tables.

L'analyse d'une base n'est lancée qu'au moment de la première utilisation de cette même base, pour des raisons de performances (cela évite de ralentir le lancement d'une application qui contient une dizaine de binding, mais dont on teste seulement des données provant d'un seul binding).

Pour mettre en place les modèles ORM sql, il faut appeler la fonction `core.models.build_modules`.
Par exemple :

```bash
Arborescence:
app.py
test/
    __init__.py
    models/
        __init__.py
        server1/
            __init__.py
            db1.py
            db_2.py
        server2/
            __init__.py
            db1.py
```

```python
# Dans le fichier test/models/__init__.py
from core.models import build_modules

# La configuration de connexion qui sera envoyé à sqlalchemy
bindings = {
    'server1.db1': 'mysql://user:password@server1/db1',
    'server1.db-2': 'mysql://user:password@server1/db2',
    'server2.db1': 'mysql://user:password@server2/db1',
}
# Pour chaque clé de binding
base_setup_module = __package__
databases = build_modules(bindings, base_setup_module)

# Un exemple d'utilisation
instance1 = databases.server1.db_2.Revue.get('UNE CLÉ PRIMAIRE')
```

La fonction `build_modules` va récupérer pour chaque clé de binding un sous-module situé dans le second paramètre fournie (le plus souvent à `__package__` pour automatiquement indiquer le module dans lequel la fonction est appelée).
Pour chacun de ses sous-modules, elle va appeler une fonction setup qui aura comme paramètre `db` représentant l'instance SqlService de la base de données. Par exemple, pour représenter une relation entre Table1 et Table2 de la base db2 sur le serveur 1 :

```python
# Dans le fichier test/models/server1/db_2.py

# Nous n'avons pas besoin de décrire les colonnes de la table, le moteur s'en occupe lui-même.
# Cela permet (par exemple) de ne pas avoir à mettre le jour le code en cas de modifications d'une table, cette information étant redondante. Pas besoin non plus d'avoir représenté sous forme de classe dans le code python l'ensemble des tables pour pouvoir les utiliser
def setup(db):
    class Table1(db.Model):
        __tablename__ = 'TABLE_1'
        __format__ = "{self.id!r} {self.title!r}"
        cleos = relationship(
            'Table2',
            primaryjoin='Table1.id == foreign(Table2.id_table_1)',
        )



    class Table2(db.Model):
        __tablename__ = 'TABLE_2'
        __format__ = "{self.id!r} {self.title!r}"
        revue = relationship(
            'Table2',
            primaryjoin='Table2.id_table_1 == foreign(Table1.id)',
            uselist=False,
        )
```
