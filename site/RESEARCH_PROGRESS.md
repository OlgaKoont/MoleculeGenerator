# RESEARCH_PROGRESS — выпуск 10 (2026-08-27)

Канонические источники: `site/content/**/*.yaml` и `site/content/analysis/**/*.yaml`. HTML в `site/dist` генерируется (`python src/build.py`), его не редактировать вручную.

Статусы: `not_started` | `sources_identified` | `paper_read` | `code_inspected` | `drafted` | `verified` | `partially_verified` | `blocked`.

**Ни одна страница не помечена `verified`:** журнальный Science EVOLVEpro SI, часть Methods ProteinMPNN, PMLR Table A.1, IgLM Table S2 и Nature SI RFantibody остаются неполными.

## Что сделано в выпуске 10

- Восстановлен конвейер: `content/analysis` и содержательный `content/research` (18 разделов архитектур) снова рендерятся; KaTeX + Mermaid в шаблоне.
- Исправлен seed active learning: UCB больше не выдаётся за универсальное уравнение класса.
- EVOLVEpro: antibody example в каталоге — **REGN10987** (preprint), не C143.
- Глубокий разбор (paper + code) трёх workhorse-инструментов, связанных с шаблонами выпуска 9: ProteinMPNN, ESM-IF1, IgLM.

## Приоритетный набор + workhorses

| Page | Page type | Primary sources found | SI found | Repository inspected | Status | Missing information |
|---|---|---|---|---|---|---|
| `/architectures/active-learning.html` | architecture | bioRxiv EVOLVEpro; Settles (context) | Science SI нет | EvolvePro `1c77697d` | partially_verified | Science PDF; Data S1 |
| `/architectures/inverse-folding.html` | architecture | AntiFold + Hsu bioRxiv + Dauparas Science HTML | AntiFold SI earlier; Hsu Table A.1 no; ProteinMPNN Methods partial | AntiFold `789d467`; ProteinMPNN `8907e667`; esm `2b369911` (SHA only) | partially_verified | Hsu Table A.1; ProteinMPNN Methods SI |
| `/architectures/joint-sequence-structure-diffusion.html` | architecture | DiffAb NeurIPS + code (v9) | NR | diffab `c3e29666` | partially_verified | NeurIPS result tables |
| `/architectures/frame-diffusion.html` | architecture | RFantibody Nature HTML (v9) | Nature SI no | RFantibody SHA NR | partially_verified | RFdiffusion Methods; Ab FT corpora |
| `/architectures/graph-neural-networks.html` | architecture | Dauparas Science HTML; research YAML 18 sections | Fig. S1 not re-extracted | ProteinMPNN `8907e667` | partially_verified | LigandMPNN/dyMEAN code this pass |
| `/architectures/geometric-transformers.html` | architecture | Hsu bioRxiv; research YAML | Table A.1 no | esm SHA only | partially_verified | IF1 module line audit |
| `/architectures/masked-token-infilling.html` | architecture | IgLM Cell Systems; research YAML | Table S2 no | IgLM `de819b56` | partially_verified | ESM-1v close-read |
| `/tools/evolvepro.html` | tool | bioRxiv **read**; Science **not read** | Data S1 no | `1c77697d` | partially_verified | Science vs preprint sixth protein |
| `/tools/antifold.html` | tool | arXiv+SI (v9) | in arXiv | `789d467` | partially_verified | OUP HTML |
| `/tools/diffab.html` | tool | NeurIPS + code (v9) | NR | `c3e29666` | partially_verified | paper tables |
| `/tools/rfantibody.html` | tool | Nature HTML partial (v9) | no | SHA NR | partially_verified | Methods/SI; commit |
| `/tools/proteinmpnn.html` | tool | Science HTML **read** | SI PDF no | `8907e6671bfbfc92303b5f79c4b5e6ce47cdef57` | partially_verified | Methods SI; Grb2 numeric Kd |
| `/tools/esm-if1.html` | tool | bioRxiv Hsu **read** | Table A.1 no | facebookresearch/esm `2b369911bb5b4b0dda914521b9475cad1656b2ac` (repo SHA; IF1 `.py` not line-audited) | partially_verified | inverse_folding/*.py; weight hash |
| `/tools/iglm.html` | tool | Cell Systems HTML **read** | S-tables partial | Graylab/IgLM `de819b56238b5cb9c23d7a6fec4c55d7fc0395e4` | partially_verified | Table S2 prompts; wet-lab independent |
| `/papers/proteinmpnn.html` | paper | Science HTML | no | code yes | partially_verified | SI |
| `/papers/esm-if1.html` | paper | bioRxiv HTML | Table A.1 no | SHA only | partially_verified | PMLR PDF tables |
| `/papers/iglm.html` | paper | Cell Systems HTML | S-tables no | code yes | partially_verified | STAR PDF |

## Архитектуры из `content/research` (конвертируются при сборке)

Статус **`partially_verified` или `drafted` по YAML**: geometric-transformers, graph-neural-networks, invariant-models, se3-equivariant-models, protein-language-models, few-shot-mutation-optimization, bayesian-optimization, zero-shot-mutation-scoring, masked-token-infilling, и др. с ≥5 секциями / явным status. Это **не** новый close-read каждого tool paper, кроме страниц выше.

Короткие stubs (`sources_identified`, 1 секция «верификация не завершена») **не** подставляются вместо fallback.

## Остальные tools без analysis YAML

Статус **`sources_identified`** (каркас из матрицы + fallback 15 разделов): abdiffuser, alphaproteo, bindcraft, boltzgen, chroma, dymean, esm-1v-efficient-evolution, esm3, evodiff, flowdesign, framediff, huabdiffusion, hudiff, humatch, ligandmpnn, makowski-affinity-specificity, palm-h3, progen, protein-generator, rfdiffusion, rfdiffusion-aa, structural-evolution, tfold.

## Инспектированные commits (накопительно)

| Repo | Commit | Files |
|---|---|---|
| mat10d/EvolvePro | `1c77697d0c09bf6989a1562a55da99301a12e2cd` | `model.py`, `evolve.py` |
| oxpig/AntiFold | `789d46786624c01eb44f177ef4c0deeeb6e77469` | README, `main.py` |
| luost26/diffab | `c3e2966601bf8025025ab87717b31b08fdd4834e` | `diffab.py`, `dpm_full.py` |
| dauparas/ProteinMPNN | `8907e6671bfbfc92303b5f79c4b5e6ce47cdef57` | `protein_mpnn_utils.py`, `protein_mpnn_run.py` |
| facebookresearch/esm | `2b369911bb5b4b0dda914521b9475cad1656b2ac` | repo SHA; IF1 module not line-read |
| Graylab/IgLM | `de819b56238b5cb9c23d7a6fec4c55d7fc0395e4` | `iglm/model/IgLM.py` |
| RosettaCommons/RFantibody | NR | — |

## Недоступные полные тексты

- Science EVOLVEpro PDF/SI.
- ProteinMPNN Science SI PDF.
- Hsu PMLR Table A.1 numeric grid.
- IgLM supplemental tables S1–S2.
- RFantibody Nature SI; DiffAb full result tables.
- Bioinformatics Advances AntiFold (ранее Cloudflare).

## Сборка

```bash
cd site
python scripts/validate.py
python src/build.py
python -m pytest tests -q
python -m http.server 8000 --directory dist
```

Preview (не хранить в контенте): `http://127.0.0.1:8000/`.
