# Exploitation Infomaniak de Samstag

**Référence documentaire au 1er novembre 2026.** [samstagloz.ch](https://samstagloz.ch) est servi par l’application Flask sur le VPS Infomaniak. Aucune commande de ce dossier ne doit être exécutée sur le VPS sans autorisation explicite, sauvegarde et retour arrière préparé.

## Organisation documentée

```text
/opt/samstag/
├── app/       code applicatif
└── venv/      environnement Python

/var/lib/samstag/   base SQLite, sauvegardes et état persistant
```

| Fichier | Rôle |
|---|---|
| `samstag.service` | lance `run_service.py`, qui supervise le web et la collecte |
| `samstag-backup.service` | exécute une sauvegarde SQLite cohérente |
| `samstag-backup.timer` | planifie les sauvegardes locales |
| `backup.py` | implémente la sauvegarde et la rétention |
| `samstag.env` | exemple historique de variables à adapter sans y placer de secret réel |
| `beta/nginx-samstag.conf.example` | exemple historique de proxy Nginx public |
| `beta/samstag-observation.service` | observateur borné utilisé pendant la bêta |

## Contraintes

- le web et la collecte doivent utiliser le même chemin absolu `SAMSTAG_DB` ;
- `DEMO_ENABLED=0` et le debug Flask doivent rester désactivés ;
- la base, les secrets et les journaux ne doivent pas être versionnés ;
- la route de rafraîchissement ne doit pas être exposée publiquement ;
- les données doivent être sauvegardées avec une méthode cohérente SQLite avant une livraison.

Le dépôt documente cette topologie, mais la session du 1er novembre 2026 n’a pas vérifié par SSH les chemins, les unités, les variables ni les versions effectivement actives. Suivre [docs/EXPLOITATION.md](../../docs/EXPLOITATION.md) et consigner les preuves dans la [passation](../../docs/PASSATION_PROJET.md).
