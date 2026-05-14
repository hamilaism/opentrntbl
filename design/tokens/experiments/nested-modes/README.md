# Experiment : Nested-modes token system

## Concept

C'est l'architecture dont parle Donnie D'Amato dans *Mise en mode* et que Bill Collins formalise avec `resolver.json` dans le DTCG.

**Le problème avec V1** : pour chaque combinaison de modes (`dark + compact`, `dark + HC`, `dark + vision:protan`…), il faut déclarer une clé explicite dans `$extensions`. Avec 4 axes et N valeurs par axe, on arrive rapidement à O(n×m×p) déclarations. C'est du flattening manuel.

**La solution nested-modes** : chaque axe de mode vit dans son propre fichier. Le resolver génère un bloc CSS par fichier, sans jamais déclarer de combinaison. La cascade CSS résout les intersections gratuitement.

```
dark + compact → [data-color="dark"] + [data-density="compact"] sur le même élément
                 → les deux blocs s'appliquent simultanément par cascade
                 → aucune déclaration [data-color="dark"][data-density="compact"] nécessaire
```

C'est O(n + m + p) au lieu de O(n × m × p).

## Structure des fichiers

```
src/
  defaults.tokens.json          ← toutes les valeurs par défaut, zéro mode override
  modes/
    color.dark.tokens.json      ← uniquement les tokens qui changent en dark
    color.hc.tokens.json        ← uniquement les tokens qui changent en HC
    density.compact.tokens.json ← uniquement les spacings en compact
    density.spacious.tokens.json← uniquement les spacings en spacious
    vision.achromatopsia.tokens.json
    vision.deuteranopia.tokens.json
    vision.protanopia.tokens.json
    vision.tritanopia.tokens.json
```

**Règle** : un fichier de mode ne contient que ce qui change. Si `text.primary` ne change pas en compact, il n'apparaît pas dans `density.compact.tokens.json`. Le default de `defaults.tokens.json` s'applique.

## Exemple concret

### `defaults.tokens.json`
```json
{
  "surface": {
    "canvas": { "$type": "color", "$value": "#f2f2f2" },
    "base":   { "$type": "color", "$value": "#ffffff" }
  },
  "spacing": {
    "default": { "$type": "dimension", "$value": "1rem" }
  }
}
```

### `modes/color.dark.tokens.json`
```json
{
  "surface": {
    "canvas": { "$type": "color", "$value": "#0d0d0d" },
    "base":   { "$type": "color", "$value": "#111118" }
  }
}
```
*(spacing absent : il ne change pas en dark)*

### `modes/density.compact.tokens.json`
```json
{
  "spacing": {
    "default": { "$type": "dimension", "$value": "0.75rem" }
  }
}
```
*(surface absent : il ne change pas en compact)*

### CSS généré
```css
[data-token-system="nested-modes"] {
  --surface-canvas: #f2f2f2;
  --spacing-default: 1rem;
}
[data-token-system="nested-modes"][data-color="dark"] {
  --surface-canvas: #0d0d0d;
  /* spacing absent — cascade conserve la valeur du bloc parent */
}
[data-token-system="nested-modes"][data-density="compact"] {
  --spacing-default: 0.75rem;
  /* surface absent — cascade conserve la valeur du bloc parent */
}
/* dark + compact → les deux blocs s'appliquent, aucune déclaration combinée */
```

## Résolution des références primitives

Les fichiers sources référencent les primitives existantes (`{primitives/openTRNTBL.color.neutral.190}`). Le resolver charge la chaîne complète :

```
core.tokens.json → primitives-openTRNTBL.tokens.json → defaults/modes/*.tokens.json
```

et résout toutes les références en valeurs concrètes avant d'émettre le CSS.

## Regénérer

```bash
python3 design/tokens/experiments/nested-modes/resolver.py
```

Pour ajouter un nouveau fichier de mode (ex. `theme.high-energy.tokens.json`), il suffit de l'ajouter dans `src/modes/` et de l'enregistrer dans `resolver.py` :

```python
mode_files = {
    ...
    '[data-theme="high-energy"]': "theme.high-energy.tokens.json",
}
```

## Relation avec V1

`defaults.tokens.json` a été généré automatiquement depuis `src/semantic.tokens.json` en strippant les `$extensions.com.opntrntbl.modes`. Les valeurs par défaut sont identiques à V1.

Les fichiers de mode reprennent les mêmes overrides que V1, mais organisés horizontalement (par mode) plutôt que verticalement (inline dans chaque token).

## Implication pour le design : "imbrication sans flattening"

Dans V1, pour supporter `dark + protanopia`, il faut une clé `"color:dark|vision:protanopia"` dans chaque token concerné. Si on ajoute un 5e axe (`theme:brand-X`), la matrice explose.

Dans nested-modes, `[data-color="dark"][data-vision="protanopia"][data-theme="brand-X"]` se résout automatiquement par la cascade CSS. Ajouter un axe = ajouter un fichier de mode. La complexité est O(n + m + p + q), pas O(n × m × p × q).

**C'est le resolver.json que Collins propose à la spec DTCG** — appliqué côté CSS. Le même principe pourrait s'appliquer côté JSON avec un resolver formel : traverser l'arbre de contextes sans les aplatir.

## Trade-offs

| ✓ Pour | ✗ Contre |
|---|---|
| Scalable : ajouter un axe = ajouter un fichier | Requiert un resolver qui charge plusieurs fichiers |
| Zéro combinaison à maintenir | Pas de contrôle sur la priorité en cas de conflit |
| Source claire par axe (ownership) | Les valeurs résolues ne sont pas visibles dans la source |
| DTCG-compliant (valeurs concrètes dans `$value`) | La "magie" de la cascade peut surprendre |
| Compatible Tokens Studio (valeurs résolues) | Dark + vision non testé explicitement |
