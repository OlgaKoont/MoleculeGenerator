# MoleculeGenerator

Этот репозиторий содержит исходный SMILES RNN generator и отдельный каталог ML-генераторов белков/антител.

## Документация по protein/antibody generators

Каталог: [`site/README.md`](site/README.md)

Сборка и просмотр:

```bash
cd site
python scripts/validate.py
python src/build.py
python -m http.server 8000 --directory dist
```

Откройте http://127.0.0.1:8000/

Публичный сайт: https://olgakoont.github.io/MoleculeGenerator/

Сборка GitHub Actions из `site/` на каждый push в `main`.
