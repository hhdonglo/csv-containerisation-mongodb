# Pipeline de Migration de Données de Santé
## Migration de Base de Données NoSQL avec MongoDB, Docker & AWS
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-8.2-green.svg)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Activé-blue.svg)](https://www.docker.com/)
[![Poetry](https://img.shields.io/badge/Poetry-Gestion_des_Dépendances-purple.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/Licence-MIT-yellow.svg)](LICENSE)
[![English](https://img.shields.io/badge/📖_Documentation-English-blue?style=for-the-badge)](README.md)
[![Français](https://img.shields.io/badge/📖_Documentation-Français-red?style=for-the-badge)](README.fr.md)
[![Statut de Traduction](https://img.shields.io/badge/Traduction-À_jour-green.svg)](README.fr.md)

> **Projet 5 d'Ingénierie des Données OpenClassrooms** | Solution de Migration de Données Médicales DataSoluTech

---

## Résumé Exécutif

Pipeline ETL prêt pour la production migrant **54 966 dossiers médicaux** de CSV vers MongoDB avec assurance qualité automatisée, conteneurisation Docker et recherche complète sur le déploiement AWS. Conçu pour un prestataire de soins de santé confronté à des problèmes d'évolutivité dans ses activités quotidiennes.

**Réalisations Clés** : Zéro problème d'intégrité des données, optimisation de la mémoire de 21%, taux de réussite des tests de 100%, temps de traitement de 45 secondes.

---

## Table des Matières
- [Problématique & Solution](#problématique--solution)
- [Fonctionnalités Clés](#fonctionnalités-clés)
- [Architecture](#architecture)
- [Démarrage Rapide](#démarrage-rapide)
- [Schéma de Base de Données](#schéma-de-base-de-données)
- [Qualité des Données](#qualité-des-données)
- [Technologies](#technologies)
- [Structure du Projet](#structure-du-projet)
- [Documentation](#documentation)
- [Contribution](#contribution)
- [Licence](#licence)
- [Auteur](#auteur)

---

## Problématique & Solution

**Défi Client** : Prestataire de soins de santé confronté à des problèmes d'évolutivité dans la gestion quotidienne des dossiers patients.

**Solution Livrée** : 
- Pipeline de migration CSV vers MongoDB automatisé avec workflow ETL en 7 étapes
- Infrastructure Dockerisée pour la portabilité et l'évolutivité
- Recherche sur le déploiement AWS (analyse des coûts DocumentDB, ECS, S3)
- Documentation et directives de sécurité prêtes pour la production

---

## Fonctionnalités Clés

### Automatisation ETL
- Workflow orchestré en 7 étapes du CSV brut aux documents MongoDB validés
- Nettoyage automatisé des données : standardisation des noms, suppression des doublons
- Optimisation de la mémoire : réduction de 21% via types catégoriels, conversion datetime

### Qualité & Validation des Données
- Suite de tests d'intégrité à 5 niveaux : comptage de documents, structure des champs, types de données, valeurs manquantes, doublons
- Validation pytest automatisée avec taux de réussite de 100%

### Déploiement Conteneurisé
- Orchestration complète Docker + Docker Compose
- MongoDB avec contrôles de santé et politiques de redémarrage automatique
- Interface web Mongo Express pour la gestion de base de données - port 8081
- Configuration basée sur l'environnement pour la sécurité des identifiants

### Architecture Prête pour le Cloud
- Recherche sur le déploiement AWS (DocumentDB vs Atlas vs EC2 vs ECS)
- Analyse des coûts
- Planification de la reprise après sinistre (RTO <1h, RPO <5min)
- Considérations de conformité HIPAA

---

## Architecture

### Flux du Pipeline ETL

![Flux du Pipeline ETL](docs/images/etl_pipeline_flow.png)

**Étapes du Pipeline** :

**[1] Chargement CSV Brut** - Ingère 55 500 dossiers patients depuis le fichier CSV source

**[2] Nettoyage des Données** - Traite les données via 4 opérations parallèles :
- **Std. Noms** : Standardise les noms des patients (casse titre, suppression espaces)
- **Suppr. Doublons** : Supprime 534 enregistrements dupliqués (-0,96%)
- **Opt. Types** : Optimise les types de données pour une réduction de mémoire de 20,96%
- **Rapports Qualité** : Génère métriques et rapports de validation

**[3] Connexion MongoDB** - Établit une connexion de base de données authentifiée avec validation de santé

**[4] Chargement Données Nettoyées** - Charge le jeu de données traité : 54 966 lignes, 15 colonnes

**[5] Insertion en Bloc** - Effectue l'insertion par lot dans MongoDB : 5 000 documents par lot

**[6] Validation d'Intégrité** - Exécute la suite de validation à 5 niveaux (taux de réussite 100%)

**[7] Succès** - Achèvement du pipeline avec statistiques récapitulatives

**Temps de Traitement** : ~45 secondes (5s chargement + 10s nettoyage + 25s migration + 5s validation)

---

### Infrastructure Docker

![Infrastructure Docker](docs/images/docker_infrastructure.png)

**Architecture des Conteneurs** :

**healthcare_mongo_ui** (Mongo Express)
- Interface de gestion MongoDB basée sur le web
- Port 8081 (accessible sur http://localhost:8081)
- Fournit des outils d'exploration et de requête de base de données visuels

**healthcare_migration** (Python 3.13)
- Exécute le pipeline de migration ETL
- Se connecte à MongoDB via `mongodb://27017`
- Exécute le traitement et la validation automatisés des données

**healthcare_mongodb** (MongoDB 8.2)
- Conteneur de base de données principal
- Port 27017 (réseau interne)
- Stockage de données persistant via volume monté

**healthcare_network** (Réseau Bridge)
- Réseau Docker isolé pour la communication inter-conteneurs
- Résolution DNS interne sécurisée
- Isolation réseau de l'hôte

**mongo_data** (Volume Docker)
- Stockage persistant pour les fichiers de données MongoDB
- Survit aux redémarrages et mises à jour de conteneurs
- Permet les opérations de sauvegarde et de récupération

**Flux de Connexion** :
- Application de migration → MongoDB : `mongodb://27017` (opérations de base de données)
- Mongo Express → MongoDB : `http://27017` (interface de gestion)
- Tous les conteneurs communiquent via le réseau bridge dédié
- Le volume assure la persistance des données tout au long du cycle de vie du conteneur

---

### Composants du Pipeline

| Composant | Responsabilité | Sortie |
|-----------|---------------|---------|
| **load_data.py** | Ingestion CSV avec validation | DataFrame |
| **cleaning.py** | Standardisation des données & contrôles qualité | CSV nettoyé + Rapports |
| **migration.py** | Connexion MongoDB & insertion en bloc | Documents structurés |
| **test.py** | Validation de l'intégrité des données | Rapports de test |
| **pipeline.py** | Orchestration et gestion des erreurs | Statut du pipeline |

---

## Démarrage Rapide

### Prérequis

- **Python** v3.13+
- **Docker** v29.1.2+
- **Docker Compose** v2.40.3
- **Poetry** v2.2.1

### Installation

**1. Cloner le Dépôt**
```bash
git clone https://github.com/yourusername/healthcare-data-migration.git
cd healthcare-data-migration
```

**2. Installer les Dépendances**
```bash
# Utilisant Poetry (Recommandé)
poetry install
poetry shell

# Ou utilisant pip
pip install -r requirements.txt
```

**3. Configurer l'Environnement**
```bash
cp .env.example .env
nano .env
```

**Configuration .env**
```env
MONGO_USERNAME=votre_nom_utilisateur
MONGO_PASSWORD=votre_mot_de_passe_securise
MONGO_DATABASE=medical_records
MONGO_URI=mongodb://votre_nom_utilisateur:votre_mot_de_passe@mongodb:27017/medical_records?authSource=admin
```

**4. Préparer les Données**
```bash
mkdir -p data/raw
cp votre_donnees_sante.csv data/raw/healthcare.csv
```

### Exécuter le Pipeline

**Déploiement Docker (Recommandé)** :
```bash
# Démarrer toute la pile
docker-compose up -d

# Voir les journaux en temps réel
docker-compose logs -f <nom_conteneur>

# Accéder à l'interface Mongo Express
# http://localhost:8081

# Arrêter les services
docker-compose down
```

**Développement Local** :
```bash
# Exécuter le pipeline
python -m csv_containerisation_mongodb.main.main

# Exécuter les tests
pytest tests/test_migration.py -v
```

### Vérifier le Succès

**Vérifier la Sortie du Pipeline** :
```
data/processed/
├── cleaned_healthcare.csv           # Données nettoyées (54 966 lignes)
├── healthcare_cleaning_report.md    # Rapport de nettoyage détaillé
└── healthcare_quality_report.csv    # Métriques de qualité
```

**Vérifier les Données MongoDB** :
```bash
# Via l'interface Mongo Express : http://localhost:8081

# Ou via CLI
docker exec -it healthcare_mongodb mongosh medical_records \
  -u votre_nom_utilisateur -p votre_mot_de_passe --authenticationDatabase admin \
  --eval "db.healthcare_data.countDocuments()"
```

---

## Schéma de Base de Données

### Structure du Document (Conception Imbriquée)
![Le schéma des données de santé](docs/images/mongodb_patient_schema.png)

### Stratégie d'Indexation
```javascript
// Index optimisés pour les requêtes courantes
db.healthcare_data.createIndex({ "patient_info.name": 1 })
db.healthcare_data.createIndex({ "admission_details.admission_date": 1 })
db.healthcare_data.createIndex({
  "medical_details.medical_condition": 1,
  "hospital_info.hospital": 1
})
```

**Justification de la Conception** :
- Les documents imbriqués éliminent les jointures complexes
- Les index optimisent les recherches de patients, les requêtes par plage de dates et les analyses hospitalières
- Le regroupement logique améliore les performances de lecture et l'expérience développeur

Pour la documentation détaillée du schéma et des exemples de requêtes, voir [Guide des Opérations](docs/operations.md).

---

## Qualité des Données

### Suite de Tests Automatisés

| Test | Validation | Critère de Réussite |
|------|-----------|---------------|
| **Comptage de Documents** | Total d'enregistrements correspondant | Lignes CSV = Documents MongoDB |
| **Structure des Champs** | Complétude du schéma | Toutes les colonnes CSV présentes |
| **Valeurs Manquantes** | Gestion des valeurs nulles | % manquant correspondant (<0,01% diff) |
| **Types de Données** | Correction du type | Types correspondent au schéma |
| **Doublons** | Préservation des doublons | Comptage des doublons correspondant |

**Couverture des Tests** : 100% (5/5 tests réussis)

### Métriques de Qualité

**Résultats du Pipeline** :
```
Chargement Initial :  55 500 lignes, 15 colonnes
Doublons :           534 lignes supprimées (0,96%)
Jeu de Données Final : 54 966 lignes, 15 colonnes
Mémoire Avant :      37,97 MB
Mémoire Après :      30,01 MB
Mémoire Économisée : 7,96 MB (réduction de 20,96%)
Temps de Traitement : ~45 secondes
Résultats Tests :    5/5 réussis (100%)
```

**Exécuter les Tests** :
```bash
pytest tests/test_migration.py -v
```

Pour les procédures de test complètes et la documentation d'assurance qualité, voir [Guide des Opérations](docs/operations.md).

---

## Technologies

### Pile Principale
- **Python 3.13** : Langage principal
- **MongoDB 8.2** : Base de données NoSQL
- **Docker & Docker Compose** : Conteneurisation
- **Poetry** : Gestion des dépendances

### Bibliothèques Clés
```toml
[tool.poetry.dependencies]
python = "^3.13"
pandas = "^2.2.0"              # Manipulation de données
pymongo = "^4.6.1"             # Pilote MongoDB
pytest = "^7.4.3"              # Framework de test
python-dotenv = "^1.0.0"       # Gestion d'environnement
```

### Outils de Développement
- **pytest** : Tests automatisés
- **Black** : Formatage du code
- **Ruff** : Linting
- **Mongo Express** : Interface graphique de base de données

---

## Structure du Projet
```
healthcare-data-migration/
├── src/csv_containerisation_mongodb/    # Code d'application Python
│   ├── main/                            # Point d'entrée et orchestration
│   ├── data/                            # Chargement et nettoyage de données
│   ├── migration/                       # Opérations MongoDB
│   ├── test/                            # Validation d'intégrité
│   └── utils/                           # Fonctions utilitaires
├── tests/                               # Suite de tests
├── data/
│   ├── raw/                             # Fichiers CSV sources
│   └── processed/                       # Données nettoyées et rapports
├── docs/
│   ├── aws-architecture.md              # Recherche déploiement cloud
│   ├── operations.md                    # Opérations et surveillance
│   ├── security.md                      # Sécurité et conformité
│   └── images/                          # Diagrammes d'architecture
├── docker/
│   └── Dockerfile                       # Conteneur d'application
├── docker-compose.yml                   # Orchestration des services
├── pyproject.toml                       # Dépendances
└── README.md                            # Documentation principale
```

---

## Documentation

Documentation complète organisée par public et cas d'utilisation :

### Suite Documentaire

| Document | Public | Objectif |
|----------|---------|---------|
| **[README.md](README.md)** | Toutes les parties prenantes | Vue d'ensemble et démarrage rapide |
| **[Architecture AWS](docs/aws-architecture.md)** | Ingénieurs cloud, architectes | Options de déploiement, analyse des coûts, comparaisons de services |
| **[Guide des Opérations](docs/operations.md)** | Équipes DevOps, SRE | Opérations du pipeline, surveillance, sauvegardes, reprise après sinistre |
| **[Guide de Sécurité](docs/security.md)** | Ingénieurs sécurité, auditeurs | Authentification, autorisation, conformité HIPAA |

### Ressources Supplémentaires

- [Meilleures Pratiques MongoDB](https://www.mongodb.com/docs/manual/administration/production-notes/)
- [Documentation Docker](https://docs.docker.com/)
- [Guide AWS DocumentDB](https://docs.aws.amazon.com/documentdb/)
- [Documentation Poetry](https://python-poetry.org/docs/)

### Rapports Générés

Toutes les exécutions du pipeline génèrent :
- **Rapport de Nettoyage** : `data/processed/healthcare_cleaning_report.md`
- **CSV Qualité** : `data/processed/quality_report_healthcare.csv`
- **Résultats Tests** : sortie terminal pytest avec validation détaillée

---

## Contribution

Les contributions sont les bienvenues ! Veuillez suivre ces directives :

1. Fork le dépôt
2. Créer une branche de fonctionnalité (`git checkout -b feature/FonctionnaliteIncroyable`)
3. Commiter les modifications (`git commit -m 'Ajouter FonctionnaliteIncroyable'`)
4. Pousser vers la branche (`git push origin feature/FonctionnaliteIncroyable`)
5. Ouvrir une Pull Request

### Standards de Code
- Suivre le guide de style PEP 8
- Ajouter des docstrings à toutes les fonctions
- Inclure des tests unitaires pour les nouvelles fonctionnalités
- Mettre à jour la documentation au besoin

---

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## Auteur

**hhdonglo**  
*Étudiante en Ingénierie des Données | OpenClassrooms*

- **Organisation** : OpenClassrooms
- **Projet** : Parcours d'Ingénierie des Données OpenClassrooms - Projet 5
- **Certification** : Ingénierie des Données (Octobre 2025 - Octobre 2026)
- **GitHub** : [github.com/hhdonglo](https://github.com/hhdonglo)

---

## Statut du Projet

**Statut** : Terminé  
**Version** : 1.0.0  
**Dernière Mise à Jour** : Janvier 2026

### Statistiques du Pipeline
- **Enregistrements Traités** : 54 966 (sur 55 500 bruts)
- **Doublons Supprimés** : 534 (0,96%)
- **Optimisation Mémoire** : Réduction de 20,96%
- **Temps de Traitement** : ~45 secondes
- **Couverture Tests** : 100% (5/5 tests réussis)
- **Intégrité Données** : Zéro problème détecté

---

**Si vous trouvez ce projet utile, merci de lui donner une étoile !**

---

*Ce projet a été développé dans le cadre du programme de certification en Ingénierie des Données d'OpenClassrooms, démontrant une expertise pratique en bases de données NoSQL, développement de pipelines ETL, conteneurisation Docker et recherche en architecture cloud.*