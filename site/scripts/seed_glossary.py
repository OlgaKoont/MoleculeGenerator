from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"


def dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=96), encoding="utf-8")


TERMS = [
    {"id": "inverse-folding", "slug": "inverse-folding", "term": "Inverse folding", "term_ru": "Обратное сворачивание", "definition": "Генерация sequence, совместимой с заданным backbone. Не создаёт новую topology.", "related_ids": ["backbone", "conditioning"]},
    {"id": "backbone", "slug": "backbone", "term": "Backbone", "term_ru": "Остов", "definition": "Геометрия основной цепи (N, Cα, C, часто O). Sequence design и diffusion часто работают на этом уровне.", "related_ids": ["inverse-folding"]},
    {"id": "diffusion", "slug": "diffusion", "term": "Diffusion model", "term_ru": "Диффузионная модель", "definition": "Генерация через постепенное зашумливание данных и обучение denoiser восстанавливать чистое состояние.", "related_ids": ["flow-matching", "sampling"]},
    {"id": "flow-matching", "slug": "flow-matching", "term": "Flow matching", "term_ru": "Flow matching", "definition": "Обучение векторного поля, которое непрерывно транспортирует prior в data distribution; sampling через ODE.", "related_ids": ["diffusion"]},
    {"id": "conditioning", "slug": "conditioning", "term": "Conditioning", "term_ru": "Обусловливание", "definition": "Способ подать в генератор ограничение: antigen, epitope, backbone, mask, tags.", "related_ids": ["epitope"]},
    {"id": "cdr", "slug": "cdr", "term": "CDR", "term_ru": "Гипервариабельные петли", "definition": "Complementarity-determining regions — петли variable domain, обычно ответственные за antigen contacts.", "related_ids": ["framework", "epitope"]},
    {"id": "framework", "slug": "framework", "term": "Framework", "term_ru": "Каркас", "definition": "Не-CDR части variable domain. Часто фиксируются при de novo CDR design и humanization.", "related_ids": ["cdr", "humanization"]},
    {"id": "inference", "slug": "inference", "term": "Inference", "term_ru": "Инференс", "definition": "Применение уже обученной модели для sampling или scoring. Не путать с training.", "related_ids": ["sampling"]},
    {"id": "fine-tuning", "slug": "fine-tuning", "term": "Fine-tuning", "term_ru": "Дообучение", "definition": "Продолжение обучения pretrained модели на узком корпусе (например, antibody structures).", "related_ids": ["protein-language-model"]},
    {"id": "benchmark", "slug": "benchmark", "term": "Benchmark", "term_ru": "Бенчмарк", "definition": "Фиксированная оценка на retrospective данных. Не заменяет prospective wet-lab.", "related_ids": ["evidence-level"]},
    {"id": "developability", "slug": "developability", "term": "Developability", "term_ru": "Развиваемость/технологичность", "definition": "Совокупность свойств, важных для разработки (solubility, aggregation, viscosity, nonspecific binding). Score ≠ клинический успех.", "related_ids": ["humanization"]},
    {"id": "epitope", "slug": "epitope", "term": "Epitope / hotspot", "term_ru": "Эпитоп / hotspot", "definition": "Участок target, к которому должен bind designed paratope. Ошибки hotspot specification ломают target-conditioned design.", "related_ids": ["cdr", "conditioning"]},
    {"id": "equivariance", "slug": "equivariance", "term": "SE(3) equivariance", "term_ru": "SE(3)-эквивариантность", "definition": "Свойство сети: поворот/сдвиг входа поворачивает/сдвигает выход. Нужно для 3D generators.", "related_ids": ["diffusion"]},
    {"id": "sampling", "slug": "sampling", "term": "Sampling", "term_ru": "Сэмплирование", "definition": "Процедура получения кандидатов: AR decoding, masked unmasking, diffusion steps, flow ODE, mutation enumeration.", "related_ids": ["inference", "diffusion"]},
    {"id": "protein-language-model", "slug": "protein-language-model", "term": "Protein language model (PLM)", "term_ru": "Белковая языковая модель", "definition": "Модель, обученная на amino-acid sequences; даёт embeddings и/или generative distribution.", "related_ids": ["fine-tuning"]},
    {"id": "infilling", "slug": "infilling", "term": "Infilling", "term_ru": "Заполнение пропуска", "definition": "Генерация masked span при известном левом и правом контексте.", "related_ids": ["cdr"]},
    {"id": "humanization", "slug": "humanization", "term": "Humanization", "term_ru": "Гуманизация", "definition": "Перенос non-human CDRs на human-like framework. Humanness ≠ immunogenicity.", "related_ids": ["framework", "developability"]},
    {"id": "active-learning", "slug": "active-learning", "term": "Active learning", "term_ru": "Активное обучение", "definition": "Итеративный выбор следующих экспериментов моделью.", "related_ids": ["few-shot"]},
    {"id": "few-shot", "slug": "few-shot", "term": "Few-shot", "term_ru": "Малопримерный режим", "definition": "Оптимизация по малому числу experimental labels, обычно десятки на раунд.", "related_ids": ["active-learning"]},
    {"id": "multi-objective", "slug": "multi-objective", "term": "Multi-objective / Pareto", "term_ru": "Многокритериальность", "definition": "Одновременная оптимизация нескольких свойств; компромиссы видны как Pareto-фронт.", "related_ids": ["developability"]},
    {"id": "evidence-level", "slug": "evidence-level", "term": "Evidence class", "term_ru": "Класс доказательности", "definition": "1 in silico; 2 retrospective; 3 prospective binding; 4 prospective function; 5 developability/manufacturability.", "related_ids": ["benchmark"]},
    {"id": "plddt", "slug": "plddt", "term": "pLDDT / ipTM / PAE", "term_ru": "Метрики structure predictor", "definition": "Confidence scores AlphaFold-семейства. Не являются experimental affinity.", "related_ids": ["evidence-level"]},
    {"id": "likelihood", "slug": "likelihood", "term": "Likelihood / log-probability", "term_ru": "Правдоподобие", "definition": "Оценка модели, насколько sequence вероятна при условии. Не Kd и не function.", "related_ids": ["inverse-folding"]},
]


def main() -> None:
    for t in TERMS:
        dump(CONTENT / "glossary" / f"{t['slug']}.yaml", t)
    print(f"wrote {len(TERMS)} glossary terms")


if __name__ == "__main__":
    main()
