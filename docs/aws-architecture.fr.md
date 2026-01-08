# Recherche sur l'Architecture et le Deploiement Cloud AWS

**Auteur :** hhdonglo - OpenClassrooms (DataSoluTech)  
**Projet :** Pipeline de Migration de Donnees de Sante  
**Date :** Janvier 2026

[![English](https://img.shields.io/badge/📖_Documentation-English-blue?style=for-the-badge)](aws-architecture.md)
[![Français](https://img.shields.io/badge/📖_Documentation-Français-red?style=for-the-badge)](aws-architecture.fr.md)

---

## Table des Matieres
- [Apercu de la Recherche](#apercu-de-la-recherche)
- [Comprendre les Serveurs](#comprendre-les-serveurs)
- [Apercu des Services AWS](#apercu-des-services-aws)
- [Options de Deploiement MongoDB](#options-de-deploiement-mongodb)
- [Configuration du Compte AWS](#configuration-du-compte-aws)
- [Modeles de Tarification et Analyse des Couts](#modeles-de-tarification-et-analyse-des-couts)
- [Avantages de la Migration Cloud](#avantages-de-la-migration-cloud)
- [Recommandations](#recommandations)

---

## Apercu de la Recherche

**Defi du Client** : Fournisseur de soins de sante confronte a des problemes de scalabilite avec la gestion quotidienne des dossiers des patients utilisant une base de donnees relationnelle traditionnelle. Ils ont besoin d'une solution Big Data horizontalement evolutive avec une surcharge informatique minimale.

**Objectifs de la Recherche** :
- Explorer les options de deploiement MongoDB sur AWS
- Comparer les services AWS (S3, DocumentDB, ECS)
- Analyser les modeles de tarification et l'optimisation des couts
- Evaluer les avantages de la migration cloud
- Fournir des recommandations exploitables

**Portee** : Recherche exploratoire pour eclairer la prise de decision du client.

---


## Comprendre les Serveurs

### Comparaison des Types de Serveurs

| Type | Description | Avantages | Inconvenients | Modele de Cout |
|------|-------------|-----------|---------------|----------------|
| **Physique** | Materiel possede dans un centre de donnees | Performance maximale, controle complet | Cout initial eleve (5k-50k $), provisionnement long, capacite fixe | Depense en capital |
| **Virtuel (EC2)** | Defini par logiciel sur materiel partage | Provisionnement instantane, mise a l'echelle facile, pas de maintenance materielle | Ressources partagees, dependance internet | Paiement a l'utilisation |
| **Gere (DocumentDB)** | Entierement gere par le fournisseur | Zero gestion de serveur, mise a l'echelle automatique, haute disponibilite integree | Moins de controle, verrouillage fournisseur | Abonnement mensuel |
| **Sans serveur (Lambda)** | Aucune infrastructure visible | Zero gestion, paiement par execution | Limites d'execution, demarrages a froid | Par invocation |

**Point Cle** : Pour les besoins du client (scalabilite, personnel informatique minimal, conformite sante), les serveurs geres ou virtuels sont les plus appropries. Les serveurs physiques contredisent l'exigence de scalabilite.

---

## Apercu des Services AWS

Cette section fournit des presentations de haut niveau des services AWS evalues pour le projet. Des comparaisons detaillees apparaissent dans [Options de Deploiement MongoDB](#options-de-deploiement-mongodb).

### Amazon S3 (Simple Storage Service)

**Objectif** : Stockage d'objets evolutif pour tout type de donnees.

**Capacites Cles** :
- Capacite de stockage illimitee avec mise a l'echelle automatique
- 99,999999999% de durabilite (donnees repliquees entre installations)
- Plusieurs niveaux de stockage : Standard (0,023 $/Go), Glacier (0,004 $/Go)
- Politiques de cycle de vie pour archivage automatique

**Cas d'Usage Sante** :
- Stocker les fichiers CSV bruts et les ensembles de donnees traites
- Sauvegardes automatiques de base de donnees
- Archivage a long terme pour la conformite (retention de 7 ans)

---

### Amazon DocumentDB

**Qu'est-ce que c'est** : Base de donnees documentaire geree par AWS compatible avec les API MongoDB 3.6, 4.0 et 5.0.

**Fonctionnalites Principales** :
- Compatibilite avec les pilotes MongoDB (fonctionne avec pymongo)
- Mise a l'echelle automatique
- **Haute disponibilite Multi-AZ (6 copies dans 3 zones)**
- **Eligible HIPAA avec chiffrement integre**
- Sauvegardes automatisees avec recuperation a un point dans le temps

**Compromis** :
- Compatible API, pas MongoDB natif complet (certaines fonctionnalites non supportees)
- Cout plus eleve que l'auto-gestion (~200 $/mois vs ~150 $/mois)
- Configuration limitee par rapport a l'auto-hebergement

Avantages/inconvenients detailles dans [Option 1](#option-1-amazon-documentdb-recommande) ci-dessous.

---

### Amazon ECS (Elastic Container Service)

**Qu'est-ce que c'est** : Orchestration de conteneurs geree pour les charges de travail Docker.

**Deux Types de Lancement** :

| Fonctionnalite | Fargate (Sans serveur) | EC2 (Auto-gere) |
|----------------|------------------------|-----------------|
| Gestion | Entierement geree | Gerer les instances |
| Cout | Plus eleve par heure | Plus faible pour utilisation soutenue |
| Mise a l'echelle | Automatique | Manuel |
| Meilleur Pour | Charges de travail variables | Charges de travail previsibles |

**Avantages de l'Integration** :
- Execute les conteneurs Docker existants sans modification
- ECR pour le stockage d'images de conteneurs
- EFS pour les donnees MongoDB persistantes
- CloudWatch pour la journalisation centralisee

Comparaison detaillee dans [Option 4](#option-4-mongodb-conteneurise-sur-ecs) ci-dessous.

---

### RDS pour MongoDB - Clarification

**Important** : AWS n'offre pas "RDS pour MongoDB".

Amazon RDS ne prend en charge que les bases de donnees relationnelles (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Aurora). Pour MongoDB sur AWS, utilisez :
- Amazon DocumentDB (gere, compatible MongoDB)
- MongoDB Atlas (tiers sur infrastructure AWS)
- Auto-gere sur EC2 ou ECS

---

## Options de Deploiement MongoDB

Comparaison complete de toutes les approches de deploiement, avec avantages et inconvenients detailles.

---

### Option 1 : Amazon DocumentDB (Recommande)

**Type** : Service de base de donnees entierement gere  
**Gestion de Serveur** : AWS gere tout

#### Avantages

**Operationnel** :
- Zero administration de base de donnees (pas de correctifs, sauvegardes, decisions de mise a l'echelle)
- Surveillance et gestion AWS 24h/24 et 7j/7 incluses
- Basculement automatique en <30 secondes

**Scalabilite** :
- Le stockage se met a l'echelle automatiquement jusqu'a 128 To sans intervention
- Ajout jusqu'a 15 repliques de lecture pour la mise a l'echelle horizontale
- Mise a l'echelle verticale (redimensionnement d'instance) avec temps d'arret minimal

**Fiabilite** :
- SLA de disponibilite de 99,99%
- 6 copies de donnees dans 3 zones de disponibilite
- Sauvegardes continues vers S3 avec recuperation a un point dans le temps (1-35 jours)
- Copies de sauvegarde inter-regions pour la reprise apres sinistre

**Securite et Conformite** :
- Eligible HIPAA pret a l'emploi
- Chiffrement automatique au repos (KMS) et en transit (TLS)
- Isolation reseau VPC
- Authentification de base de donnees IAM
- Journalisation d'audit integree

**Predictibilite des Couts** :
- Tarification mensuelle fixe (~200 $/mois production)
- Pas de couts operationnels caches
- Instances Reservees : 75% d'economies avec engagement de 3 ans

#### Inconvenients

**Compatibilite** :
- Compatible API, pas MongoDB natif (certaines fonctionnalites manquantes : recherche en texte integral, traitement de graphes)
- Ajustements de code mineurs potentiels requis
- Impossible d'utiliser tous les outils MongoDB

**Controle** :
- Configuration au niveau du serveur limitee
- Impossible d'acceder a l'infrastructure sous-jacente
- Fenetres de maintenance controlees par AWS

**Cout** :
- Tarification premium par rapport a l'auto-gestion
- Depense mensuelle continue (vs achat materiel unique)

**Meilleur Pour** : Charges de travail de production necessitant la conformite HIPAA, haute disponibilite et surcharge operationnelle minimale.

---

### Option 2 : MongoDB Atlas sur AWS

**Type** : Service gere par un tiers par MongoDB Inc.  
**Gestion de Serveur** : MongoDB Inc. gere tout

#### Avantages

- **MongoDB Natif** : Compatibilite des fonctionnalites a 100%, dernieres versions immediatement disponibles
- **Multi-Cloud** : Migration facile entre AWS, Azure, GCP
- **Support Expert** : Gere par les createurs de MongoDB
- **Fonctionnalites Avancees** : Recherche en texte integral, graphes, series temporelles, flux de modifications

#### Inconvenients

- **Cout** : ~300-400 $/mois (2x DocumentDB)
- **Integration** : Moins transparente avec les services AWS
- **Complexite** : Facturation et gestion separees d'AWS
- **Surcharge** : Deux relations fournisseurs (AWS + MongoDB)

**Meilleur Pour** : Applications necessitant toutes les fonctionnalites MongoDB ou strategie multi-cloud.

---

### Option 3 : MongoDB Auto-gere sur EC2

**Type** : Installation manuelle sur serveurs virtuels  
**Gestion de Serveur** : Votre equipe gere tout

#### Avantages

- **Controle Complet** : Acces root, toute configuration, toutes les fonctionnalites MongoDB
- **Cout de Base Inferieur** : ~100-150 $/mois calcul (avant couts operationnels)
- **Flexibilite** : Choix des types d'instances, personnalisation complete
- **Pas de Verrouillage** : MongoDB standard, facile a migrer

#### Inconvenients

- **Charge Operationnelle Elevee** :
  - Sauvegardes manuelles, mises a jour, correctifs de securite
  - Configurer la haute disponibilite soi-meme
  - Surveillance 24h/24 et 7j/7 requise
  - Necessite une expertise en administration de base de donnees
  
- **Couts Caches** :
  - Temps du personnel pour la gestion (cout salarial important)
  - Licences d'outils de surveillance
  - Risque de temps d'arret

- **Complexite de Scalabilite** :
  - Configuration manuelle du sharding
  - Planification de capacite requise
  - La mise a l'echelle cause des temps d'arret sans planification soigneuse

**Meilleur Pour** : Organisations avec DBA MongoDB experimentes et besoin de configurations specifiques.

---

### Option 4 : MongoDB Conteneurise sur ECS

**Type** : Conteneurs Docker sur infrastructure AWS  
**Gestion de Serveur** : Semi-geree (AWS gere les conteneurs, vous gerez la base de donnees)

#### Avantages

- **Compatibilite Docker** : Notre configuration existante fonctionne sans modification
- **Parite de Developpement** : Environnements locaux et cloud identiques
- **Architecture Moderne** : Pret pour les microservices, CI/CD facile
- **Flexibilite des Couts** : Fargate (20 $/mois occasionnel) ou EC2 (150 $/mois soutenu)

#### Inconvenients

- **Anti-Pattern de Base de Donnees** : Conteneurs concus pour applications sans etat, pas bases de donnees
- **Complexite** : Necessite une connaissance de l'orchestration de conteneurs
- **Gestion Manuelle** : Sauvegardes, replication, surveillance toutes manuelles
- **Surcharge de Stockage** : EFS coute 0,30 $/Go-mois pour la persistence

**Meilleur Pour** : Developpement/tests uniquement. Non recommande pour les bases de donnees de production.

---

### Option 5 : Serveurs Physiques (Sur Site)

**Type** : Materiel possede  
**Gestion de Serveur** : Responsabilite complete

#### Avantages

- Depense en capital unique
- Controle maximal
- Les donnees restent sur site

#### Inconvenients

- **Contredit le Besoin du Client** : Capacite fixe vs exigence de scalabilite
- **Investissement Initial Massif** : 50k-200k $ cout initial
- **Complexite Operationnelle** : Necessite une equipe complete d'infrastructure informatique
- **Couts Caches** : Electricite, refroidissement, location d'espace, renouvellement materiel (3-5 ans)
- **Point de Defaillance Unique** : Pas de redondance geographique sans cout supplementaire

**Non Recommande** : Les problemes de scalabilite du client necessitent la flexibilite du cloud.

---

### Matrice de Decision de Deploiement

| Option | Cout Mensuel | Gestion | Scalabilite | Pret HIPAA | Recommande Pour |
|--------|-------------|---------|-------------|------------|-----------------|
| **DocumentDB** | ~200 $ | Entierement geree | Automatique | Oui | **Production** |
| **MongoDB Atlas** | ~400 $ | Entierement geree | Automatique | Configurable | Fonctionnalites MongoDB completes |
| **EC2 Auto-gere** | ~150 $* | Manuel | Manuel | Bricolage | Expertise MongoDB |
| **Conteneurs ECS** | ~20-150 $ | Semi-geree | Semi-auto | Bricolage | Developpement uniquement |
| **Physique** | Initial eleve | Complete | Tres difficile | Bricolage | Non applicable |

*Plus couts operationnels importants

### Criteres de Selection

**Choisir DocumentDB si** :
- Besoin de conformite HIPAA immediate
- Personnel d'infrastructure informatique limite
- Necessite d'une disponibilite de 99,99%
- Souhaite des couts mensuels previsibles

**Choisir MongoDB Atlas si** :
- Necessite de l'ensemble complet des fonctionnalites MongoDB
- Planification d'une strategie multi-cloud
- Le budget permet une tarification premium

**Choisir EC2 Auto-gere si** :
- Dispose de DBA MongoDB experimentes
- Besoin de personnalisations specifiques
- Pret a investir dans la surcharge operationnelle

**Choisir ECS si** :
- Developpement/tests uniquement
- Pas pour les bases de donnees de production

---

## Configuration du Compte AWS

### Creation de Compte (5 Etapes)

**Etape 1 : Inscription**
1. Naviguer vers [aws.amazon.com](https://aws.amazon.com)
2. Cliquer sur "Creer un compte AWS"
3. Entrer l'adresse e-mail
4. Choisir le nom du compte (ex : "DataSoluTech-Healthcare")
5. Definir le mot de passe de l'utilisateur root

**Etape 2 : Informations de Contact**
1. Selectionner le type de compte :
   - **Entreprise** : Pour utilisation en entreprise (recommande)
   - **Personnel** : Pour utilisation individuelle
2. Entrer les details de l'entreprise/personnels
3. Fournir un numero de telephone valide
4. Entrer l'adresse de facturation

**Etape 3 : Informations de Paiement**
1. Entrer les details de la carte de credit/debit
2. Carte debitee de 1 $ pour verification (rembourse)
3. Requis meme pour l'utilisation de l'Offre Gratuite

**Etape 4 : Verification d'Identite**
1. Choisir la methode de verification :
   - Message texte SMS (plus rapide)
   - Appel vocal
2. Entrer le code de verification recu
3. Completer la verification

**Etape 5 : Selection du Plan de Support**

| Plan | Cout | Niveau de Support | Temps de Reponse |
|------|------|------------------|------------------|
| **Basic** | Gratuit | Forums, documentation | Communautaire |
| **Developer** | 29 $/mois | E-mail heures ouvrables | <24 heures |
| **Business** | 100 $/mois | Telephone/e-mail 24h/24 et 7j/7 | <1 heure |
| **Enterprise** | 15 000 $/mois | TAM dedie | <15 minutes |


**Activation du Compte** :
- Attendre l'activation du compte (minutes a 24 heures)
- Recevoir l'e-mail de confirmation
- Se connecter a la Console de Gestion AWS

### Avantages de l'Offre Gratuite

**Offre Gratuite de 12 Mois** (commence a partir de la date d'inscription) :

**Calcul** :
- 750 heures/mois instances EC2 t2.micro
- 750 heures/mois ECS Fargate (2 vCPU, 4 Go RAM)

**Stockage** :
- 5 Go stockage S3 Standard
- 30 Go stockage EBS

**Base de Donnees** :
- 750 heures/mois RDS db.t2.micro
- 25 Go stockage DocumentDB (essai de 30 jours)

**Surveillance** :
- 10 metriques CloudWatch
- 10 alarmes

**Transfert de Donnees** :
- 15 Go transfert de donnees sortant/mois

**Toujours Gratuit** (sans expiration) :
- 1 million de requetes Lambda/mois
- 25 Go stockage DynamoDB

### Securite Post-Configuration du Compte

**Etapes de Securite Critiques** (a faire immediatement) :

**1. Activer MFA sur le Compte Root**
```
Console IAM → Utilisateur root → Informations d'identification de securite → 
Activer MFA → Utiliser l'application d'authentification (Google Authenticator, Authy)
```

**2. Creer un Utilisateur Admin IAM**
```
Ne pas utiliser le compte root pour les operations quotidiennes
Creer un utilisateur IAM avec des autorisations d'administrateur
Utiliser l'utilisateur IAM pour tout travail
```

**3. Configurer les Alertes de Facturation**
```
Console de Facturation → Budgets → Creer un budget
Definir le seuil : alerte a 50 $/mois
Alerte par e-mail
```

**4. Activer CloudTrail**
```
Console CloudTrail → Creer une piste
Journaliser tous les appels API pour l'audit
Stocker les journaux dans S3
```

**5. Configurer les Alarmes de Budget**
```
Definir plusieurs seuils :
- 25 $ (50% du budget) - avertissement
- 50 $ (100% du budget) - critique
- 75 $ (150% du budget) - arret d'urgence
```

---

## Modeles de Tarification et Analyse des Couts

### Modeles de Tarification AWS

| Modele | Engagement | Remise | Meilleur Pour |
|--------|-----------|--------|---------------|
| **A la Demande** | Aucun | 0% | Tests, charges de travail imprevisibles |
| **Reserve (1 an)** | 1 an | ~40% | Production avec certaine flexibilite |
| **Reserve (3 ans)** | 3 ans | ~75% | Charges de travail de production stables |
| **Plans d'Economie** | 1-3 ans | ~66% | Flexible entre services |
| **Instances Spot** | Aucun | ~90% | Charges de travail interruptibles uniquement |

### Philosophie de Tarification de Base

AWS utilise une tarification **paiement a l'utilisation** sans engagements initiaux (pour la plupart des services).

**Principes Cles** :
- Payer uniquement ce que vous utilisez
- Pas de couts initiaux (sauf Instances Reservees)
- Pas de contrats a long terme requis
- Arreter a tout moment
- Augmenter/diminuer selon les besoins

### Outils de Gestion des Couts AWS

**Calculateur de Tarification AWS** : [calculator.aws](https://calculator.aws)
- Estimer les couts avant le deploiement
- Comparer differentes configurations
- Exporter les estimations en PDF/CSV

**AWS Cost Explorer** :
- Visualiser les 13 derniers mois de depenses
- Prevoir les 3 prochains mois
- Filtrer par service, region, etiquettes
- Identifier les anomalies de couts

**Budgets AWS** :
- Definir des limites de depenses personnalisees
- Alerter en cas de depassement des seuils
- Suivre l'utilisation des Instances Reservees

### Analyse des Couts du Projet

#### Environnement de Developpement

| Service | Configuration | Cout |
|---------|--------------|------|
| ECS Fargate | Taches de migration occasionnelles | 20 $ |
| S3 | 10 Go de donnees | 0,50 $ |
| CloudWatch | Journalisation de base | 2 $ |
| **Total Developpement** | | **23 $/mois** |

#### Environnement de Production

| Service | Configuration | Cout |
|---------|--------------|------|
| DocumentDB | db.r5.large (2 vCPU, 16 Go RAM) | 202 $ |
| Stockage DocumentDB | 100 Go | 10 $ |
| S3 | 100 Go Standard + 500 Go Glacier | 5 $ |
| ECS Fargate | Taches de migration | 20 $ |
| CloudWatch | Surveillance detaillee | 5 $ |
| Transfert de Donnees | 50 Go sortant | 5 $ |
| **Total Production (A la Demande)** | | **247 $/mois** |
| **Avec Reserve 3 ans** | | **62 $/mois** |

### Cout Total de Possession sur 3 Ans

**AWS (avec Instances Reservees)** :
- Annee 1 : 247 $ × 12 = 2 964 $
- Annee 2-3 : 62 $ × 24 = 1 488 $
- **Total : 4 452 $**

**Equivalent Sur Site** :
- Materiel : 30 000 $
- Personnel (DBA) : 60k $/an × 3 = 180 000 $
- Infrastructure : 7 200 $
- **Total : 217 200 $**

**Economies AWS : 212 748 $ (98%)** en tenant compte de l'administration de base de donnees dediee et de la surcharge d'infrastructure requise pour le deploiement sur site.

> **Note** : Cette comparaison inclut les couts operationnels (salaire de l'administrateur de base de donnees, gestion de l'infrastructure) qui representent la plus grande difference de cout entre les deploiements cloud et sur site. Les couts materiels seuls montreraient ~85% d'economies.

### Strategies d'Optimisation des Couts

**1. Dimensionnement Correct**
- Commencer avec des instances plus petites
- Surveiller l'utilisation reelle
- Augmenter uniquement si necessaire

**2. Instances Reservees (Production)**
- Engagement de 3 ans pour DocumentDB
- Economiser 75% (247 $ → 62 $/mois)
- Rentabilite : 4 mois

**3. Cycle de Vie du Stockage**
- Deplacer les anciennes donnees vers S3 Glacier (82% moins cher)
- Supprimer automatiquement les fichiers temporaires
- Compresser les sauvegardes

**4. Optimisation du Developpement**
- Arreter les ressources de dev lorsqu'elles ne sont pas utilisees
- Utiliser les instances Spot pour les tests
- Planifier l'arret automatique (nuits/week-ends)
- Economies potentielles : 70%

**5. Reduction du Transfert de Donnees**
- Garder les donnees dans la meme region
- Utiliser CloudFront CDN pour les fichiers statiques
- Compresser les transferts de donnees

---

## Avantages de la Migration Cloud

### Impact Commercial

| Probleme Client | Solution AWS | Avantage Mesurable |
|-----------------|--------------|-------------------|
| Goulot d'etranglement de scalabilite | Mise a l'echelle automatique stockage/calcul | Capacite de croissance illimitee |
| Temps d'arret systeme | Deploiement Multi-AZ | Disponibilite de 99,99% (8,76 h/an max) |
| Risque de perte de donnees | Sauvegardes automatisees + PITR | Recuperation a n'importe quelle seconde |
| Couts d'infrastructure eleves | Tarification a l'utilisation | Reduction des couts de 98% |
| Personnel informatique limite | Services entierement geres | Zero exigence DBA |
| Charge de conformite | Services eligibles HIPAA | Conformite integree |

### Avantages Techniques

**Performance** :
- Stockage SSD (plus rapide que les disques traditionnels)
- Repliques de lecture pour la distribution de requetes
- Emplacements peripheriques mondiaux (faible latence)

**Innovation** :
- Integration AI/ML (SageMaker)
- Analytique (Athena, QuickSight)
- Fonctions sans serveur (Lambda)

**Fiabilite** :
- Infrastructure auto-reparatrice
- Basculement automatise
- Eprouve a l'echelle de Netflix/Airbnb

**Scalabilite** :
- Mise a l'echelle horizontale (ajouter plus de ressources)
- Mise a l'echelle verticale (ressources plus importantes)
- Mise a l'echelle automatique basee sur la demande
- Distribution mondiale

---

## Recommandations

### Principal : Amazon DocumentDB

**Justification** (en reference a l'analyse precedente) :

1. **Repond au Besoin Principal** : Les problemes de scalabilite du client necessitent une mise a l'echelle automatique → DocumentDB fournit une mise a l'echelle automatique du stockage (10 Go a 128 To) et du calcul sans intervention manuelle (voir [Option 1](#option-1-amazon-documentdb-recommande))

2. **Effort de Migration Minimal** : La compatibilite de l'API MongoDB signifie que notre code existant base sur pymongo fonctionne avec des ajustements mineurs, reduisant le risque de migration et le calendrier

3. **Conformite Sante** : Eligible HIPAA pret a l'emploi avec chiffrement integre, journalisation d'audit et documentation de conformite (critique pour les dossiers medicaux)

4. **Adequation Operationnelle** : Le client manque de personnel d'infrastructure informatique dedie → service entierement gere elimine le besoin d'administrateurs de base de donnees

5. **Rentable** : 247 $/mois initialement, reduit a 62 $/mois avec Instances Reservees de 3 ans apres periode de validation (voir [Analyse des Couts](#analyse-des-couts-du-projet))

**Pourquoi les Autres Options Ont Ete Rejetees** :

- **MongoDB Atlas** : Elimine en raison d'un cout 2x superieur (400 $/mois) sans valeur supplementaire suffisante pour ce cas d'utilisation
- **EC2 Auto-gere** : Rejete en raison de la capacite d'administration de base de donnees limitee du client et de la complexite operationnelle
- **Conteneurs ECS** : Convient uniquement au developpement/tests, pas aux bases de donnees de production (anti-pattern de charge de travail avec etat)
- **Serveurs Physiques** : Contredit fondamentalement les exigences de scalabilite du client et necessite un investissement initial massif

### Feuille de Route de Deploiement

**Phase 1 : Preuve de Concept (Mois 1)** - 50 $
- Deployer une instance DocumentDB minimale (db.t3.medium)
- Migrer 1 000 enregistrements echantillons
- Valider la compatibilite et les performances

**Phase 2 : Developpement (Mois 2)** - 100 $/mois
- Cluster de developpement complet
- Migration complete de l'ensemble de donnees (54 966 enregistrements)
- Tests d'integration

**Phase 3 : Production (Mois 3)** - 247 $/mois
- Mise a l'echelle vers db.r5.large
- Activer le deploiement Multi-AZ
- Configurer les sauvegardes automatisees de 7 jours
- Implementer la reprise apres sinistre

**Phase 4 : Optimisation (Mois 4+)** - 62 $/mois
- Acheter des Instances Reservees de 3 ans (75% d'economies)
- Implementer les politiques de cycle de vie S3
- Dimensionner correctement en fonction de l'utilisation reelle

### Alternative : Approche Hybride

Pour les scenarios sensibles aux couts :
- **Developpement** : ECS + conteneurs MongoDB (20 $/mois)
- **Production** : DocumentDB (200 $/mois)
- **Total** : 220 $/mois (12% d'economies vs tout-DocumentDB)

Cette approche maintient la parite de l'environnement de developpement tout en assurant la fiabilite de la production.

---

**Recommandation Finale** : Proceder avec Amazon DocumentDB en utilisant la feuille de route de deploiement par phases. Cette solution repond directement aux defis de scalabilite du client tout en fournissant la conformite HIPAA, la haute disponibilite et une charge operationnelle minimale. Le calendrier de 3-4 mois permet une validation approfondie avant l'engagement complet de production, et les Instances Reservees fournissent une optimisation des couts a long terme une fois que les modeles de charge de travail sont confirmes.

---

## Liste de Verification de Mise en OEuvre

### Etapes de Migration

**1. Preparation**
- Exporter les donnees actuelles (termine)
- Telecharger vers le compartiment S3
- Creer une sauvegarde

**2. Infrastructure**
- Creer VPC et groupes de securite
- Lancer le cluster DocumentDB
- Configurer la surveillance

**3. Migration**
- Executer le script de migration Python
- Valider l'integrite des donnees
- Tests de performance

**4. Basculement**
- Planifier la fenetre de maintenance
- Mettre a jour les chaines de connexion
- Surveiller pendant 48 heures

### Attenuation des Risques

| Risque | Attenuation |
|--------|------------|
| Problemes de compatibilite | Tests approfondis Phase 1, maintenir le repli |
| Meconnaissance de l'equipe | Formation AWS, documentation complete |
| Depassements de couts | Alertes de budget a 25 $/50 $/75 $ seuils |
| Violation de donnees | Chiffrement partout, VPN, journalisation d'audit |

---

## Conclusion de la Recherche

**Statut** : Evaluation complete terminee  
**Date** : Janvier 2026  
**Recommandation Principale** : Amazon DocumentDB avec deploiement par phases  
**Investissement Total** : 247 $/mois production (reduit a 62 $/mois avec Instances Reservees)

### Resume des Principales Conclusions

- DocumentDB repond a toutes les exigences du client : scalabilite, conformite HIPAA, surcharge operationnelle minimale
- Reduction des couts de 98% vs sur site en incluant les couts du personnel
- Migration realisable en 3-4 mois avec risque minimal
- L'approche par phases permet la validation avant l'engagement complet

### Ressources Supplementaires

**Documentation AWS** :
- [Documentation DocumentDB](https://docs.aws.amazon.com/documentdb/)
- [Documentation ECS](https://docs.aws.amazon.com/ecs/)
- [Documentation S3](https://docs.aws.amazon.com/s3/)

**Outils AWS** :
- [Calculateur de Tarification](https://calculator.aws)
- [Cadre Bien Architecte](https://aws.amazon.com/architecture/well-architected/)
- [Formation et Certification](https://aws.amazon.com/training/)

**Canaux de Support** :
- Support AWS (si abonne)
- Forums AWS
- Stack Overflow (etiquette aws)
- Communaute AWS re:Post

---

**Prepare par** : Hope Donglo, Stagiaire Ingenieur de Donnees  
**Entreprise** : DataSoluTech  
**Programme** : OpenClassrooms Ingenierie des Donnees - Projet 5

---

*Cette recherche a ete menee pour explorer les options de deploiement cloud pour la migration de donnees de sante sans mise en oeuvre reelle. Toutes les recommandations sont basees sur l'analyse des exigences du client et les capacites des services AWS.*