# Protein AbGen — документация ML-генераторов белков и антител

Статический научный сайт: задача → workflow → инструмент → архитектура → paper.

Контент хранится в YAML (`content/`) и валидируется pydantic-схемой. HTML собирается без Node.js.

Источник карточек инструментов, DOI и GitHub: `../ML_generators_protein_antibody_landscape_RU (1).xlsx` (проверено 13.08.2026).

## Локальный запуск

Из каталога `site/`:

```bash
python -m pip install jinja2 pyyaml pydantic openpyxl pytest
python scripts/import_xlsx.py
python scripts/seed_tasks.py
python scripts/seed_workflows.py
python scripts/seed_architectures.py
python scripts/seed_glossary.py
python scripts/enrich_tools.py
python scripts/validate.py
python src/build.py
python -m http.server 8000 --directory dist
```

Откройте http://127.0.0.1:8000/

Если YAML уже сгенерирован, достаточно:

```bash
python scripts/validate.py
python src/build.py
python -m http.server 8000 --directory dist
```

Тесты:

```bash
python -m pytest tests -q
```

`PYTHONPATH` для тестов: `site/src` (см. `pytest.ini`).

## Как добавить записи

Не дублируйте описание инструмента на страницах задач. Каноническая карточка живёт в `content/tools/<slug>.yaml`. Обратные ссылки считаются автоматически.

### Инструмент

1. Создайте `content/tools/<slug>.yaml` по полям схемы `src/schema.py` (`Tool`).
2. Обязательны: `identity.id/name/slug`, `generation.exact_generated_object`, `classification.task_ids`, `relations.paper_ids`.
3. Неизвестное пишите как `null` (на сайте будет **NR**), не выдумывайте hardware/runtime/N designs.
4. Добавьте `content/papers/<slug>.yaml` с DOI или URL.
5. Проставьте `architecture_ids`, `workflow_ids`.
6. `python scripts/validate.py` — сборка падает на битых id.

### Задача

`content/tasks/<slug>.yaml`. Список инструментов указывать не нужно: достаточно `task_ids` у tool.

### Workflow

`content/workflows/<slug>.yaml`. На стадиях явно разделите `generation`, `evaluation`, `external_evaluation`, `experiment`.

### Архитектура

`content/architectures/<slug>.yaml`. Общая теория только здесь; на странице tool — только implementation.

### Paper

`content/papers/<slug>.yaml`. Preprint нельзя помечать как peer-reviewed. Workshop ≠ main track. Помечайте `Author-reported` / `Interpretation` / `NR`.

## Что не является generator

AlphaFold, docking, MD, affinity/developability predictors попадают только как dependencies. Их страницы — в About, не в каталоге tools.

## Лицензии и коммерческое использование

Поле `commercial_use_status` копируется из матрицы. Если лицензия custom/NR — нужен legal review, сайт это не утверждает.
