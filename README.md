# Api BOLERO


## Environnement virtuel

TODO

## Serveur de développement

Le moteur de configuration étant Dynaconf, il faut initialiser l'api en mode développement.
Ajouter un fichier `.env` à la racine du dépôt contenant :

```
PYTHONDEVMODE=true
ENV_FOR_DYNACONF=development
FLASK_DEBUG=true
MERGE_ENABLED_FOR_DYNACONF=true
```

Pour surcharger une entrée dans la configuration (par exemple pour les codes d'accès à une bdd), ajouter un fichier `.secrets.yaml`.

Exécuter `flask run` pour lancer le serveur.

L'ensemble des urls est disponible avec la commande `flask routes`.
L'ensemble des commandes cli sont disponibles en tapant `flask --help`.
