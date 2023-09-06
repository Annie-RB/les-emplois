# Itou - Les emplois de l'inclusion

> Les emplois de l'inclusion est un service numérique de délivrance des PASS IAE
> et de mise en relation d'employeurs solidaires avec des candidats éloignés de
> l'emploi par le biais de tiers (prescripteurs habilités, orienteurs) ou en
> autoprescription.

# Environnement de développement

## Dépendances

Les dépendances (base de données PostgreSQL et le stockage objet *S3*) sont
rendues disponibles par [Docker](https://docs.docker.com/engine/install/) et
[docker-compose](https://docs.docker.com/compose/).

- [Installer Docker](https://docs.docker.com/engine/install/)
- [Installer Docker Compose](https://docs.docker.com/compose/install/)

L’application peut être installée de deux manières différentes :

1. dans un [Virtualenv](https://docs.python.org/3/library/venv.html), ce qui
   permet une meilleure intégration avec les outils de développement.

   Démarrez les dépendances de développement avec la commande :
   ```sh
   docker compose up
   ```

2. dans un [Docker](https://docs.docker.com/), ce qui facilite la mise en place.

   Démarrez les dépendances de développement avec la commande :
   ```sh
   docker compose --profile=django up
   ```

**Note** : Vous pouvez personnaliser la configuration des dépendances gérée par
docker-compose en créant [un fichier
`.env`](https://docs.docker.com/compose/env-file/) à partir d'une copie du
fichier racine `.env.template`. Le fichier `.env` doit être au même niveau que
le fichier [README.md](./README.md).

## Application

### Installation dans un Virtualenv

L’adaptateur Python pour le système de gestion de bases de données PostgreSQL,
[psycopg](https://www.psycopg.org/), a quelques pré-requis auxquels votre
système doit répondre :
https://www.psycopg.org/docs/install.html#build-prerequisites

La commande make suivante crée un virtualenv et installe les dépendances pour
le développement. Elle peut être exécutée régulièrement pour s’assurer que les
dépendances sont bien à jour.

```bash
$ make venv
```

Dans un virtualenv, vous pouvez utiliser les commandes Django habituelles
(`./manage.py`) mais également certaines recettes du Makefile, celles-ci
seront lancées directement dans votre venv si `USE_VENV=1` est utilisé.

Cette variable peut être définie en global dans votre environnement shell
(`export`, `.env`, …).

### Installation dans un Docker

#### Mise à jour des dépendances Python

L’image doit être reconstruite régulièrement pour utiliser la bonne version des
dépendances Python. Pour chaque changement de `requirements/dev.txt` (assez
fréquent), reconstruire (*rebuild*) l’image docker avec :

```sh
docker compose up --build
```

#### Déboguer interactif

Pour utiliser [un débogueur
interactif](https://github.com/docker/compose/issues/4677#issuecomment-320804194)
type `ipdb` :

```sh
$ docker compose run --service-ports django
```

## Définition des variables d'environnement

Les valeurs par défaut de `dev.py` permettent de lancer un environnement fonctionnel.

Cependant, il est recommandé d'en prendre connaissance pour noter par exemple
que les emails ne sont pas réellement envoyés mais que leur contenu est
simplement écrit dans la sortie standard.

Le reste de la configuration se fait avec des variables d'environnement.

Celles concernant notre hébergeur CleverCloud sont définis au niveau du déploiement et
de l'app CleverCloud tandis que les autres paramètres applicatifs indépendants du PaaS
sont définis dans le projet `itou-secrets`.

## Serveur de développement

Utilisation de Virtualenv :
```sh
$ make runserver
```

Utilisation de Docker :
```sh
$ make run
```

Une fois votre serveur de développement lancé, vous pouvez accéder au site de
développement à l'adresse http://localhost:8000/.

## Création des *buckets*

Les fichiers téléversés sont enregistrés dans un stockage objet type *S3*. En
local, le service est rendu par [MinIO](https://min.io/). Sa console
d’administration est disponible à l’adresse http://localhost:9001/.

Login : `minioadmin`
Password : `minioadmin`

Afin de créer les *buckets* nécessaires au développement et aux tests, lancer la commande :
```sh
$ make buckets
```

## Peupler la base de données

```sh
$ make populate_db
```

### Accéder au serveur de développement

Une fois votre serveur de développement lancé, vous pouvez accéder au frontend à
l'adresse http://localhost:8000/.

### Peupler la base de données

    $ make populate_db

### Avant un commit

    $ make quality  # Will run black, ruff and djlint

### Mettre à jour les dépendances

La version des dépendances est consignée dans les fichiers `requirements/*.in`.
Une fois ces fichiers modifiés, les dépendances sont figées avec l’outil
[pip-tools](https://pypi.org/project/pip-tools/). La commande suivante permet
de mettre à jour une dépendance, par exemple `flake8` :

```sh
$ PIP_COMPILE_OPTIONS="-P flake8" make compile-deps
```

Si les changements paraissent corrects, ils peuvent être ajoutés à `git` et
*commit*.

## Lancer les tests

Le projet utilise [pytest](https://docs.pytest.org/).

Lancer la suite complète, comme sur la CI :
```sh
make test
```

Lancer un test en particulier :
```sh
pytest itou/utils/tests.py::JSONTest::test_encoder
```

### MacOS

Les Mac utilisant l’architecture M1 ont besoin d’émuler le jeu d’instructions
`amd64`, ce qui rend l’exécution de la suite de test plus longue et peut
rapidement rencontrer les sécurités (_timeout_) configurées.

Pour éviter ces erreurs,
[pytest-timeout](https://github.com/pytest-dev/pytest-timeout#usage) propose
deux options :

1. Définir la variable d’environnement `PYTEST_TIMEOUT`, par exemple à une
   valeur de `60` secondes.
2. Utiliser `--timeout` lors de l’invocation de `pytest` :
    ```sh
    pytest --timeout 60
    ```

## Manipulation utiles

### Avant un commit

    $ make quality  # Will run black, ruff and djlint

### Effacer l'ancienne base de données

Pour supprimer la base de données dans Docker vous devez supprimer les volumes
de l'image docker, en exécutant les commandes suivantes :

```sh
docker volume rm itou_postgres_data
# ou
docker compose down --volumes
```

### Mettre à jour les dépendances

La version des dépendances est consignée dans les fichiers `requirements/*.in`.
Une fois ces fichiers modifiés, les dépendances sont figées avec l’outil
[pip-tools](https://pypi.org/project/pip-tools/). La commande suivante permet
de mettre à jour une dépendance, par exemple `flake8` :

```sh
$ PIP_COMPILE_OPTIONS="-P flake8" make compile-deps
```

Si les changements paraissent corrects, ils peuvent être ajoutés à `git` et
*commit*.

## Front-end

- https://getbootstrap.com/docs/4.3/getting-started/introduction/

- https://django-bootstrap4.readthedocs.io/en/latest/index.html

- http://remixicon.com/
