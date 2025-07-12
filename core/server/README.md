# Règles concernant le moteur de l'api

## Nommage des noms d'attributs dans les réponses

Il est possible de fournir un en-tête `Attribute-Convention` avec les valeurs suivantes :

- camel-case
- snake-case
- dash-case
- without-convention

afin que les attributs dans les réponses corresponde à cette casse. Très pratique pour s'adapter au langage appelant.
