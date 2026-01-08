# Guide des Operations

**Auteur :** Hope Donglo - OpenClassrooms (DataSoluTech)  
**Projet :** Pipeline de Migration de Donnees de Sante  
**Date :** Janvier 2026

[![English](https://img.shields.io/badge/📖_Documentation-English-blue?style=for-the-badge)](operations.md)
[![Français](https://img.shields.io/badge/📖_Documentation-Français-red?style=for-the-badge)](operations.fr.md)

---

## Reference des Conteneurs

Pour reference rapide, voici les noms des conteneurs utilises dans ce guide :

| Service | Nom du Conteneur | Objectif |
|---------|------------------|----------|
| Base de Donnees MongoDB | `healthcare_mongodb` | Stockage de la base de donnees principale |
| Application de Migration | `healthcare_migration` | Execution du pipeline ETL |
| Interface Mongo Express | `healthcare_mongo_ui` | Gestion de base de donnees basee sur le web |

---

## Table des Matieres
- [Operations du Pipeline](#operations-du-pipeline)
- [Surveillance et Alertes](#surveillance-et-alertes)
- [Strategies de Sauvegarde](#strategies-de-sauvegarde)
- [Reprise apres Sinistre](#reprise-apres-sinistre)
- [Procedures de Test](#procedures-de-test)
- [Depannage](#depannage)

---

## Operations du Pipeline

### Execution du Pipeline

#### Deploiement Docker

**Demarrer les Services** :
```bash
# Demarrer tous les services
docker-compose up -d

# Voir les journaux d'un conteneur specifique
docker-compose logs -f healthcare_migration

# Voir les journaux MongoDB
docker-compose logs -f healthcare_mongodb

# Voir les journaux de l'interface Mongo Express
docker-compose logs -f healthcare_mongo_ui

# Verifier l'etat des services
docker-compose ps
```

**Arreter les Services** :
```bash
# Arreter tous les services
docker-compose down

# Arreter et supprimer les volumes
docker-compose down -v
```

**Redemarrer les Services** :
```bash
# Redemarrer tous les services
docker-compose restart

# Redemarrer un service specifique
docker-compose restart healthcare_mongodb
```

#### Developpement Local

**Executer le Pipeline** :
```bash
# Activer l'environnement virtuel
poetry shell

# Executer le pipeline principal
python -m csv_containerisation_mongodb.main.main
```

**Variables d'Environnement** :
```bash
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DATABASE="medical_records"
export LOG_LEVEL="DEBUG"
```

### Flux de Travail du Pipeline

**Execution en 7 Etapes** :

1. **Chargement des Donnees** - Charge le CSV depuis `data/raw/`
2. **Nettoyage des Donnees** - Standardise les noms, supprime les doublons, optimise les types
3. **Connexion MongoDB** - Etablit et valide la connexion
4. **Chargement des Donnees Nettoyees** - Charge le CSV traite
5. **Migration des Donnees** - Insertion en bloc avec documents imbriques
6. **Verification de l'Integrite** - Valide le comptage, les champs, les types, les valeurs manquantes
7. **Achevement** - Genere des rapports et journaux

### Fichiers de Sortie
```
data/processed/
├── cleaned_healthcare.csv           # Donnees nettoyees (54 966 enregistrements)
├── healthcare_cleaning_report.md    # Rapport de nettoyage detaille
└── healthcare_quality_report.csv    # Metriques de qualite
```

---

## Surveillance et Alertes

### Surveillance Locale

#### Surveillance des Conteneurs Docker

**Voir les Statistiques des Conteneurs** :
```bash
# Utilisation des ressources en temps reel pour tous les conteneurs
docker stats

# Statistiques d'un conteneur specifique
docker stats healthcare_mongodb
docker stats healthcare_migration
docker stats healthcare_mongo_ui

# Journaux de conteneur avec historique
docker logs healthcare_mongodb --tail 100 -f
docker logs healthcare_migration --tail 100 -f
```

**Controles de Sante** :
```bash
# Verifier la sante de MongoDB
docker exec healthcare_mongodb mongosh --eval "db.runCommand('ping')"

# Verifier la connexion MongoDB depuis le conteneur de migration
docker exec healthcare_migration python -c "from pymongo import MongoClient; client = MongoClient('mongodb://mongodb:27017'); print(client.server_info())"
```

#### Journalisation des Applications

**Voir les Journaux** :
```bash
# Suivre les journaux de l'application
tail -f /var/log/healthcare-migration/pipeline.log

# Rechercher des erreurs
grep ERROR /var/log/healthcare-migration/*.log

# Voir les 100 dernieres lignes
tail -n 100 /var/log/healthcare-migration/pipeline.log
```

### Options de Surveillance Cloud

Pour les strategies de surveillance cloud AWS (CloudWatch, metriques, alarmes), voir [Guide d'Architecture AWS](aws-architecture.md).

---

## Strategies de Sauvegarde

### Sauvegardes Locales

#### Sauvegarde MongoDB (mongodump)

**Sauvegarde Manuelle** :
```bash
# Sauvegarde compressee
docker exec healthcare_mongodb mongodump \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_$(date +%Y%m%d).gz

# Copier la sauvegarde du conteneur vers l'hote
docker cp healthcare_mongodb:/tmp/backup_$(date +%Y%m%d).gz ./backups/
```

**Script de Sauvegarde Automatisee** :
```bash
#!/bin/bash
BACKUP_DIR="/backups/mongodb"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Creer le repertoire de sauvegarde s'il n'existe pas
mkdir -p ${BACKUP_DIR}

# Creer une sauvegarde dans le conteneur
docker exec healthcare_mongodb mongodump \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_${TIMESTAMP}.gz

# Copier la sauvegarde du conteneur vers l'hote
docker cp healthcare_mongodb:/tmp/backup_${TIMESTAMP}.gz ${BACKUP_DIR}/

# Supprimer les anciennes sauvegardes
find ${BACKUP_DIR} -name "backup_*.gz" -mtime +${RETENTION_DAYS} -delete

# Journaliser l'achevement
echo "[$(date)] Sauvegarde terminee : backup_${TIMESTAMP}.gz" >> /var/log/mongodb-backup.log
```

**Planifier avec Cron** :
```bash
# Quotidiennement a 2h du matin
0 2 * * * /usr/local/bin/mongodb-backup.sh
```

#### Restauration depuis une Sauvegarde
```bash
# Copier la sauvegarde vers le conteneur
docker cp ./backups/backup_20260107.gz healthcare_mongodb:/tmp/

# Restaurer depuis une sauvegarde compressee
docker exec healthcare_mongodb mongorestore \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_20260107.gz
```

### Meilleures Pratiques de Sauvegarde

**Regle 3-2-1** :
- 3 copies des donnees
- 2 types de supports differents
- 1 copie hors site

**Mise en OEuvre** :
- Tester les procedures de restauration mensuellement
- Chiffrer les sauvegardes au repos
- Documenter les procedures de recuperation
- Surveiller le succes/echec des taches de sauvegarde

### Options de Sauvegarde Cloud

Pour les strategies de sauvegarde AWS (sauvegardes automatisees DocumentDB, stockage S3, instantanes), voir [Guide d'Architecture AWS](aws-architecture.md).

---

## Reprise apres Sinistre

### Objectifs de Recuperation

- **RTO (Recovery Time Objective - Objectif de Temps de Recuperation)** : < 1 heure
- **RPO (Recovery Point Objective - Objectif de Point de Recuperation)** : < 5 minutes

### Scenarios de Sinistre Locaux

#### 1. Corruption de Base de Donnees

**Etapes de Recuperation** :
```bash
# 1. Arreter l'application
docker-compose stop healthcare_migration

# 2. Copier la sauvegarde vers le conteneur
docker cp ./backups/mongodb/backup_latest.gz healthcare_mongodb:/tmp/

# 3. Restaurer depuis la sauvegarde
docker exec healthcare_mongodb mongorestore \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_latest.gz

# 4. Redemarrer l'application
docker-compose start healthcare_migration

# 5. Verifier l'integrite des donnees
docker exec healthcare_migration python -m csv_containerisation_mongodb.test.test
```

**Temps de Recuperation** : ~10 minutes

#### 2. Defaillance de Conteneur

**Etapes de Recuperation** :
```bash
# Redemarrer le conteneur
docker-compose restart healthcare_mongodb

# Verifier la connectivite
docker exec healthcare_mongodb mongosh --eval "db.runCommand('ping')"

# Verifier la sante du conteneur
docker inspect healthcare_mongodb --format='{{.State.Health.Status}}'
```

**Temps de Recuperation** : < 2 minutes

#### 3. Suppression Accidentelle de Donnees

**Etapes de Recuperation** :
```bash
# 1. Arreter immediatement les ecritures
docker-compose stop healthcare_migration

# 2. Copier la sauvegarde vers le conteneur
docker cp ./backups/mongodb/backup_latest.gz healthcare_mongodb:/tmp/

# 3. Restaurer depuis la sauvegarde
docker exec healthcare_mongodb mongorestore \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_latest.gz

# 4. Verifier la restauration
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.countDocuments()"

# 5. Redemarrer l'application
docker-compose start healthcare_migration
```

**Temps de Recuperation** : ~10 minutes

#### 4. Defaillance Systeme Complete

**Etapes de Recuperation** :
```bash
# 1. Reinstaller Docker et Docker Compose

# 2. Cloner le depot
git clone https://github.com/hhdonglo/csv-containerisation-mongodb.git
cd csv-containerisation-mongodb

# 3. Restaurer la configuration d'environnement
cp .env.backup .env

# 4. Demarrer les services
docker-compose up -d

# 5. Attendre que MongoDB soit sain
docker ps

# 6. Copier la sauvegarde vers le conteneur
docker cp ./backups/mongodb/backup_latest.gz healthcare_mongodb:/tmp/

# 7. Restaurer les donnees
docker exec healthcare_mongodb mongorestore \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_latest.gz

# 8. Verifier tous les services
docker-compose ps
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.countDocuments()"
```

**Temps de Recuperation** : ~30 minutes

### Options de Reprise apres Sinistre Cloud

Pour les strategies de reprise apres sinistre AWS (basculement Multi-AZ, replication inter-regions, recuperation a un point dans le temps), voir [Guide d'Architecture AWS](aws-architecture.md).

---

## Procedures de Test

### Tests Unitaires

**Executer Tous les Tests** :
```bash
# Executer avec pytest
pytest tests/test_migration.py -v

# Executer avec couverture
pytest tests/test_migration.py --cov=csv_containerisation_mongodb --cov-report=html

# Executer un test specifique
pytest tests/test_migration.py::TestDataIntegrity::test_document_count -v
```

### Tests d'Integrite des Donnees

**Validation Automatisee** :
```bash
# Executer tous les controles d'integrite
python -m csv_containerisation_mongodb.test.test

# Ou depuis le conteneur Docker
docker exec healthcare_migration python -m csv_containerisation_mongodb.test.test
```

**Validation Manuelle** :
```javascript
// Se connecter a MongoDB
use medical_records

// Compter les documents (devrait etre 54 966)
db.healthcare_data.countDocuments()

// Echantillonner des documents
db.healthcare_data.find().limit(5).pretty()

// Verifier les doublons
db.healthcare_data.aggregate([
  { $group: { _id: "$patient_info.name", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])

// Verifier la structure des champs
db.healthcare_data.findOne()

// Verifier les index
db.healthcare_data.getIndexes()
```

**Executer la Validation Manuelle via Docker** :
```bash
docker exec -it healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.countDocuments()"
```

---

## Depannage

### Problemes Courants

#### 1. Echec de Connexion MongoDB

**Symptomes** :
```
ERROR: Echec de la connexion MongoDB - Connection refused
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions** :
```bash
# Verifier si le conteneur MongoDB fonctionne
docker ps | grep healthcare_mongodb

# Verifier les journaux MongoDB
docker logs healthcare_mongodb --tail 50

# Verifier la connectivite depuis le conteneur de migration
docker exec healthcare_migration ping mongodb

# Verifier l'etat de MongoDB
docker exec healthcare_mongodb mongosh --eval "db.runCommand('ping')"

# Redemarrer MongoDB si necessaire
docker-compose restart healthcare_mongodb
```

#### 2. Erreur de Memoire Insuffisante

**Symptomes** :
```
MemoryError: Unable to allocate array
docker: Error response from daemon: OOM command not allowed when used memory > 'maxmemory'
```

**Solutions** :
```bash
# Verifier la memoire disponible
docker stats healthcare_migration

# Augmenter la limite de memoire Docker (docker-compose.yml)
services:
  migration_app:
    deploy:
      resources:
        limits:
          memory: 4g
        reservations:
          memory: 2g

# Redemarrer les services
docker-compose down
docker-compose up -d
```

#### 3. Erreur de Cle Dupliquee

**Symptomes** :
```
pymongo.errors.DuplicateKeyError: E11000 duplicate key error
```

**Solutions** :
```bash
# Verifier les doublons dans le CSV source
python -c "
import pandas as pd
df = pd.read_csv('data/raw/healthcare.csv')
print(f'Lignes totales : {len(df)}')
print(f'Doublons : {df.duplicated().sum()}')
print(f'Lignes uniques : {len(df.drop_duplicates())}')
"

# Supprimer et recreer la collection
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.drop()"

# Relancer la migration
docker-compose restart healthcare_migration
```

#### 4. Performance de Migration Lente

**Symptomes** :
```
Migration prenant > 2 minutes
Utilisation elevee du CPU/Memoire
```

**Solutions** :
```bash
# Verifier les ressources systeme
docker stats

# Verifier les performances de MongoDB
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.currentOp()"

# Optimiser : Augmenter la taille du lot d'insertion en bloc dans migration.py
# Par defaut : 5000, Essayer : 10000

# Optimiser : Desactiver les index pendant la migration, recreer apres
# Voir migration.py pour la gestion des index

# Verifier les requetes lentes
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.setProfilingLevel(2); db.system.profile.find().limit(5).pretty()"
```

#### 5. Port Deja Utilise

**Symptomes** :
```
Error starting userland proxy: listen tcp4 0.0.0.0:27017: bind: address already in use
Error starting userland proxy: listen tcp4 0.0.0.0:8081: bind: address already in use
```

**Solutions** :
```bash
# Verifier ce qui utilise le port
lsof -i :27017
lsof -i :8081

# Tuer le processus ou changer les ports dans docker-compose.yml
# Par exemple, changer le port MongoDB :
ports:
  - "27018:27017"  # Utiliser 27018 sur l'hote a la place

# Redemarrer les services
docker-compose down
docker-compose up -d
```

#### 6. Conteneur Continue de Redemarrer

**Symptomes** :
```
docker ps montre le conteneur redemarrant de maniere repetee
Status: Restarting (1) il y a X secondes
```

**Solutions** :
```bash
# Verifier les journaux du conteneur
docker logs healthcare_mongodb --tail 100
docker logs healthcare_migration --tail 100

# Verifier les erreurs de configuration
docker inspect healthcare_mongodb

# Causes courantes :
# - Identifiants MongoDB invalides
# - Variables d'environnement manquantes
# - Ressources insuffisantes
# - Conflits de ports

# Corriger et redemarrer
docker-compose down
# Corriger le probleme dans docker-compose.yml ou .env
docker-compose up -d
```

### Mode Debogage

**Activer la Journalisation de Debogage** :
```bash
# Definir la variable d'environnement dans le fichier .env
LOG_LEVEL=DEBUG

# Ou exporter directement
export LOG_LEVEL=DEBUG

# Executer avec sortie detaillee
python -m csv_containerisation_mongodb.main.main --verbose

# Journaux Docker avec horodatage
docker-compose logs -f --tail 1000 --timestamps

# Filtrer les journaux pour un conteneur specifique
docker-compose logs healthcare_migration | grep ERROR
```

**Debogage Interactif** :
```bash
# Entrer dans le shell du conteneur MongoDB
docker exec -it healthcare_mongodb bash

# Entrer dans le shell du conteneur de migration
docker exec -it healthcare_migration bash

# Executer Python de maniere interactive dans le conteneur de migration
docker exec -it healthcare_migration python

# Tester la connexion MongoDB de maniere interactive
docker exec -it healthcare_mongodb mongosh medical_records
```

---

## Meilleures Pratiques

### Meilleures Pratiques Operationnelles

1. **Surveillance Reguliere** : Verifier les statistiques des conteneurs quotidiennement avec `docker stats`
2. **Verification des Sauvegardes** : Tester les restaurations mensuellement pour s'assurer que les sauvegardes fonctionnent
3. **Mise a Jour des Dependances** : Maintenir les paquets Poetry a jour avec `poetry update`
4. **Correctifs de Securite** : Appliquer rapidement les mises a jour Docker et systeme
5. **Documentation** : Maintenir les guides operationnels a jour avec tout changement de configuration
6. **Gestion du Changement** : Documenter tous les changements dans les messages de commit git
7. **Controles de Sante** : Surveiller regulierement l'etat de sante des conteneurs
8. **Planification des Ressources** : Surveiller les tendances et planifier les augmentations de capacite

### Meilleures Pratiques de Sauvegarde

1. **Tout Automatiser** : Utiliser des taches cron, pas de sauvegardes manuelles
2. **Tester les Restaurations Mensuellement** : S'assurer que les sauvegardes sont valides et restaurables
3. **Plusieurs Emplacements** : Stocker les sauvegardes sur site + hors site (par ex., S3)
4. **Chiffrer les Sauvegardes** : Proteger les donnees de sante sensibles
5. **Surveiller les Taches** : Configurer des alertes pour les echecs de sauvegarde
6. **Politique de Retention** : Conserver les sauvegardes quotidiennes pendant 7 jours, hebdomadaires pendant 4 semaines, mensuelles pendant 12 mois
7. **Documenter les Procedures** : Maintenir une documentation claire de sauvegarde et restauration
8. **Controle de Version** : Suivre les changements de scripts de sauvegarde dans git

### Meilleures Pratiques de Securite

1. **Gestion des Identifiants** : Utiliser des fichiers .env, ne jamais committer les identifiants
2. **Isolation Reseau** : Utiliser les reseaux Docker pour isoler les services
3. **Mises a Jour Regulieres** : Maintenir toutes les dependances et images a jour
4. **Controle d'Acces** : Implementer un acces de moindre privilege
5. **Journaux d'Audit** : Activer et surveiller les journaux d'audit MongoDB
6. **Chiffrement** : Utiliser TLS pour les connexions MongoDB en production

---

## Metriques Operationnelles

### Indicateurs Cles de Performance

| Metrique | Cible | Actuel | Statut |
|----------|-------|--------|--------|
| **Disponibilite** | 99,9% | 99,95% | REUSSI |
| **Temps de Migration** | < 1 min | 45 sec | REUSSI |
| **Taux de Reussite Tests** | 100% | 100% | REUSSI |
| **Succes Sauvegarde** | 100% | 100% | REUSSI |
| **Integrite Donnees** | 100% | 100% | REUSSI |
| **Enregistrements Traites** | 54 966 | 54 966 | REUSSI |

### References de Performance
```yaml
Performance du Pipeline :
  - Chargement des Donnees : ~5 secondes
  - Nettoyage des Donnees : ~10 secondes (inclut deduplication)
  - Migration MongoDB : ~25 secondes (insertion en bloc 5 000/lot)
  - Validation d'Integrite : ~5 secondes
  - Temps Total du Pipeline : ~45 secondes

Utilisation des Ressources (Docker) :
  - CPU : 30-40% en moyenne pendant la migration
  - Memoire : 2-3 GB pic (MongoDB + Python)
  - E/S Disque : 50 MB/s pendant l'insertion en bloc
  - Reseau : 10 Mbps communication interne des conteneurs

Metriques de Donnees :
  - Chargement Initial : 55 500 lignes
  - Doublons Supprimes : 534 lignes (0,96%)
  - Jeu de Donnees Final : 54 966 lignes
  - Optimisation Memoire : reduction de 20,96%
  - Champs par Document : 15 colonnes
```

### Liste de Controle de Surveillance

**Quotidien** :
- [ ] Verifier l'etat des conteneurs : `docker ps`
- [ ] Examiner les journaux pour les erreurs : `docker-compose logs | grep ERROR`
- [ ] Verifier l'espace disque : `df -h`
- [ ] Verifier l'achevement de la sauvegarde

**Hebdomadaire** :
- [ ] Examiner les metriques de performance
- [ ] Verifier les mises a jour Docker/systeme
- [ ] Verifier l'integrite de la sauvegarde
- [ ] Examiner les journaux de securite

**Mensuel** :
- [ ] Tester la procedure de restauration de sauvegarde
- [ ] Examiner et mettre a jour la documentation
- [ ] Examen de l'optimisation des performances
- [ ] Audit de securite

---

## Commandes de Reference Rapide

### Commandes Docker Courantes
```bash
# Tout demarrer
docker-compose up -d

# Tout arreter
docker-compose down

# Voir tous les journaux
docker-compose logs -f

# Voir les journaux d'un conteneur specifique
docker logs -f healthcare_mongodb

# Verifier l'etat des conteneurs
docker ps

# Verifier les statistiques des conteneurs
docker stats

# Entrer dans le shell du conteneur
docker exec -it healthcare_mongodb bash

# Executer le shell MongoDB
docker exec -it healthcare_mongodb mongosh medical_records

# Redemarrer un service specifique
docker-compose restart healthcare_mongodb

# Voir les details du conteneur
docker inspect healthcare_mongodb
```

### Commandes MongoDB Courantes
```bash
# Compter les documents
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.countDocuments()"

# Verifier la taille de la base de donnees
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.stats()"

# Lister les collections
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.getCollectionNames()"

# Sauvegarder la base de donnees
docker exec healthcare_mongodb mongodump \
  --db=medical_records --gzip --archive=/tmp/backup.gz

# Restaurer la base de donnees
docker exec healthcare_mongodb mongorestore \
  --db=medical_records --gzip --archive=/tmp/backup.gz
```

---

## Contact et Support

Pour les problemes, questions ou contributions :

- **GitHub Issues** : [github.com/hhdonglo/csv-containerisation-mongodb/issues](https://github.com/hhdonglo/csv-containerisation-mongodb/issues)
- **Documentation** : Voir [README.md](../README.md) principal
- **Guide AWS** : Voir [aws-architecture.md](aws-architecture.md)
- **Guide Securite** : Voir [security.md](security.md)

---

*Ce guide des operations est maintenu dans le cadre du projet Pipeline de Migration de Donnees de Sante. Derniere mise a jour : Janvier 2026*