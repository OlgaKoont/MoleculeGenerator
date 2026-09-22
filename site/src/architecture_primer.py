"""Class-level primers and per-section overviews for architecture pages.

These texts explain the *class* before any paper-specific analysis. They are
INTERPRETATION of the seed YAML, not claims from a single experiment.
"""

from __future__ import annotations

import re
from typing import Any


def _txt(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _join(items: list[str] | None, *, empty: str = "") -> str:
    if not items:
        return empty
    cleaned = [str(x).strip() for x in items if x]
    return "; ".join(cleaned) if cleaned else empty


def primer_paragraphs(arch) -> list[str]:
    custom = PRIMERS.get(arch.id) or PRIMERS.get(arch.slug)
    if custom:
        return list(custom)
    return _generic_primer(arch)


def section_overview(arch, section_id: str) -> str | None:
    fn = SECTION_OVERVIEWS.get(section_id)
    if not fn:
        return None
    return fn(arch)


_NUM_TO_SECTION_ID = {
    1: "domain",
    2: "intuition",
    3: "math",
    4: "data-repr",
    5: "physical-repr",
    6: "physchem",
    7: "learned",
    8: "forward",
    9: "training",
    10: "inference",
    11: "conditioning",
    12: "complexity",
    13: "strengths",
    14: "limits",
    15: "failures",
    16: "tools",
    17: "applicability",
    18: "method-sources",
}


def canonical_section_id(section: dict[str, Any] | None) -> str | None:
    """Map analysis section id or 'N. Title' headings onto the 18 class slots."""
    if not section:
        return None
    sid = str(section.get("id") or "").strip()
    if sid in SECTION_OVERVIEWS:
        return sid
    title = str(section.get("title") or "")
    match = re.match(r"^\s*(\d+)\.", title)
    if match:
        return _NUM_TO_SECTION_ID.get(int(match.group(1)))
    return None


def _generic_primer(arch) -> list[str]:
    name = arch.name
    ru = arch.name_ru
    return [
        f"**{ru}** ({name}) — это **класс методов**, а не название одной нейросети и не карточка одного checkpoint. "
        f"Разные инструменты каталога могут реализовать этот класс по-разному: другой state, другой loss, другой sampler.",
        _txt(arch.intuition) or f"Краткое определение класса: {name}.",
        (
            f"**Что метод производит или оценивает:** {arch.generated_state or 'NR'}. "
            f"**На каком представлении он работает:** {arch.input_representation or 'NR'}."
        ),
        (
            "Это **не** экспериментальный assay и **не** structure predictor, даже если в пайплайне рядом стоят AlphaFold, docking или ELISA. "
            "Внутренний score (likelihood, pLDDT, acquisition, predicted ΔΔG) не равен измеренному $K_d$."
        ),
        (
            f"**Когда класс уместен:** задачи {_join(arch.applicable_task_ids, empty='NR')}. "
            f"**Когда нет:** {_join(arch.not_for_task_ids, empty='NR')}."
        ),
    ]


PRIMERS: dict[str, list[str]] = {
    "active-learning": [
        "**Активное обучение (active learning)** — это способ **тратить экспериментальный бюджет**, а не архитектура сети. "
        "Есть пул ещё не измеренных вариантов (мутанты, комбинаторная библиотека). Модель-суррогат смотрит на уже полученные метки $y$ и предлагает, **кого измерить в следующем раунде**. После assay данные обновляются, суррогат переобучается, цикл повторяется.",
        "Представьте directed evolution, в котором шаг «какие колонии взять дальше» делает алгоритм, а не только интуиция. Суррогатом может быть random forest, Gaussian process, линейный слой на PLM-эмбеддингах — сама нейросеть здесь часто **замороженный encoder**, а учится маленькая голова под ваши labels.",
        "**Чего класс не делает.** Он не рисует новый fold из шума и не заменяет de novo antibody design. Если пул $\\mathcal{X}$ не содержит хорошего binder, AL его не изобретёт: он только выбирает, какие точки из уже заданного пространства измерить.",
        "**Два разных рычага, которые нельзя смешивать.** (1) Как порождаются кандидаты (single-site scan, комбинаторика, PLM). (2) По какому правилу из них берут batch: top-$N$ по $\\hat y$, UCB $\\mu+\\kappa\\sigma$, Expected Improvement. Released EVOLVEpro в каталоге — top-$N$ по предсказанному среднему, **не** классический UCB.",
        "**Связь с соседними классами.** Bayesian optimization — частный случай AL с вероятностным суррогатом и acquisition по неопределённости. Few-shot mutation optimization описывает тот же практический режим «мало labels», но не обязан быть циклическим. Zero-shot scoring **не** AL: там нет новых assay labels в петле.",
        "Ниже по разделам сначала сказано, что этот пункт значит **для класса**, затем — как это выглядит в прочитанных papers/code каталога (в первую очередь EVOLVEpro).",
    ],
    "bayesian-optimization": [
        "**Байесовская оптимизация (Bayesian optimization, BO)** — это **поиск следующего эксперимента**, когда измерений мало, а каждый assay дорогой. Ставят вероятностный суррогат на неизвестную функцию приспособленности $y(x)$ (часто Gaussian process) и выбирают следующую точку, максимизируя **acquisition**: баланс «где уже хорошо» и «где модель неуверена».",
        "В белковом дизайне $x$ — обычно мутант или эмбеддинг варианта, $y$ — ELISA, активность, экспрессия. BO не генерирует геометрию: она предлагает, какой sequence из допустимого множества измерить.",
        "**Чем BO отличается от «просто обучить регрессор». ** Регрессор выдаёт $\\hat y$. BO требует **распределение** $p(y\\mid x,D)$ (среднее и неопределённость) и правило вроде UCB, EI, Thompson sampling. Random forest с точечным $\\hat y$ без $\\sigma$ — это не каноническая BO, даже если его крутят в цикле.",
        "**Чего класс не делает.** Не de novo backbone, не inverse folding, не замена SPR. Предсказанный acquisition ≠ измеренный affinity. На огромных combinatorial spaces без сжатия (эмбеддинги, низкая размерность) GP плохо масштабируется.",
        "В каталоге BO пересекается с active learning и few-shot оптимизацией. EVOLVEpro **не** следует читать как учебниковую GP-UCB, пока это не подтверждено кодом: released правило — ranking по предсказанному среднему.",
        "Дальше: общее определение каждого раздела, затем детали papers, если они есть на странице.",
    ],
    "coordinate-diffusion": [
        "**Диффузия координат (coordinate diffusion)** — генератор **непрерывной 3D-геометрии**. Берут нативные Cartesian координаты атомов или Cα, постепенно добавляют шум, пока структура не станет «облаком». Сеть учится **снимать шум**: предсказывать чистые координаты, шум $\\varepsilon$ или score $\\nabla\\log p(x_t)$. На inference запускают обратный процесс и получают новую укладку.",
        "Интуиция как у image diffusion, но объект — точки в $\\mathbb{R}^3$, связанные пептидной химией. Поэтому важны эквивариантность, centering, constraints на связи. Промежуточный шумный $x_t$ — **не** MD-траектория фолдинга и не энергия.",
        "**Что на выходе.** Координаты backbone или all-atom. Sequence часто ставят **после**, отдельным inverse folding (LigandMPNN, ProteinMPNN, design-net). Не путать этот класс с диффузией **токенов** sequence и с диффузией **frames** (ориентаций residual).",
        "**Чего класс не делает.** Не считает $K_d$. pLDDT / scRMSD / split-GFP после генерации — evaluator или эксперимент, не train target диффузии. Не inverse folding: фиксированный backbone туда не «диффундирует», его зажимают как conditioner или вообще не трогают.",
        "В каталоге канон — Chroma (polymer-correlated diffusion + отдельная design GNN) и частично RFdiffusion-AA (гибрид с ligand context). RFdiffusion vanilla ближе к [frame diffusion](/architectures/frame-diffusion.html).",
        "Ниже каждый раздел сначала описывает класс, затем — как это реализовано в конкретных papers.",
    ],
    "frame-diffusion": [
        "**Диффузия frames (frame diffusion)** задаёт каждый residue не облаком атомов, а **жёстким репером** $T_i=(R_i,t_i)$: ориентация пептидной плоскости плюс положение Cα (или N–Cα–C). Шум идёт по вращениям (часто IGSO(3) / geodesic) и по трансляциям. Denoiser предсказывает, как поправить кадры. Из чистых frames собирают backbone.",
        "Зачем так, а не сырые xyz. Белковая кинематика ближе к «куда смотрит пептидная плоскость», чем к независимым атомам. Мотив и hotspot удобно **зажать** как фиксированные frames. Это индуктивный bias RFdiffusion / FrameDiff / RFantibody.",
        "**Что на выходе.** Backbones (иногда с вспомогательными головами). Sequence почти всегда **следующий модуль** (ProteinMPNN), не часть того же DDPM, если статья явно не делает joint type-канал.",
        "**Чего класс не делает.** Не ELISA. Не гарантия, что vanilla protein prior нарисует antibody CDR. Не coordinate-only DDPM и не torsion-on-a-torus. FAPE может быть auxiliary loss у родственников, но не определение класса.",
        "Соседи: [coordinate diffusion](/architectures/coordinate-diffusion.html) (xyz), [SE(3) networks](/architectures/se3-equivariant-models.html) (слой, не процесс), [joint seq–struct diffusion](/architectures/joint-sequence-structure-diffusion.html) (ещё и типы аминокислот в том же reverse).",
        "Дальше разделы: сначала общая механика класса, затем papers каталога (RFdiffusion, FrameDiff, RFantibody).",
    ],
    "sequence-diffusion": [
        "**Диффузия sequences** — генератор **дискретных аминокислотных токенов**. Вперёд: identity постепенно заменяется случайными буквами алфавита (D3PM, absorbing / mask, Gaussian-on-logits — подтипы разные). Назад: сеть восстанавливает чистую sequence. Не нужно писать белок слева направо.",
        "Удобно **зажать** мотив или каркас: эти позиции не шумят или клемпятся на inference. Отсюда infilling и humanization-like redesign без полной AR-цепочки.",
        "**Что на выходе.** Sequence (иногда с likelihood). 3D **не** следует из токенов: фолд проверяют внешним predictor. Это не Cartesian DDPM и не frame diffusion.",
        "**Чего класс не делает.** Не гарантирует сворачиваемость и не измеряет affinity. Мало шагов $T$ даёт недоденoise. Слишком большой mask превращает модель почти в безусловную генерацию.",
        "Каталог: EvoDiff (D3PM/OADM), HuDiff / HuAbDiffusion и родственные discrete diffusion. ESM3 — скорее masked multimodal LM, его канон на [masked infilling](/architectures/masked-token-infilling.html) / [joint generation](/architectures/joint-sequence-structure-generation.html), не «ещё один D3PM».",
        "В разделах ниже — общая дискретная постановка, затем различия papers.",
    ],
    "torsion-diffusion": [
        "**Диффузия торсионных углов** описывает белок углами $\\varphi,\\psi,\\omega,\\chi$ на окружности или торе, а не точками в $\\mathbb{R}^3$. Шум заворачивается (wrapped Gaussian, Riemannian score). После семпла углы **кинематически** превращают в Cartesian (NeRF / реконструкция backbone).",
        "Степеней свободы меньше, чем у all-atom xyz, и локальная химия пептидной связи легче удержать — если не сломать $\\omega$ и замыкание петель.",
        "**Что на выходе.** Углы → координаты. Sequence может быть условием или отдельным этапом. Промежуточный noisy torsion **не** MD.",
        "**Чего класс не делает.** Плохо подходит как единственный инструмент для target-conditioned binder с жёстким dock: нет прямого Cartesian epitope clamp, пока его не встроили отдельно. Ошибки углов копятся вдоль цепи.",
        "В каталоге foundational — FoldingDiff (Wu) и small-molecule torsional diffusion (Jing); слот DOI нужно не путать. Это **не** frame diffusion RFdiffusion.",
        "Разделы: сначала геометрия на торе, затем конкретные реализации, если они прочитаны.",
    ],
    "joint-sequence-structure-diffusion": [
        "**Совместная диффузия sequence и structure** зашумляет **и** тип аминокислоты, **и** геометрию (Cα, ориентации, иногда side-chain) в одном generative process. Обратный ход выдаёт согласованную пару $(s,x)$, а не «сначала fold, потом ProteinMPNN».",
        "Типичный forward факторизуют: $q(s_t\\mid s_0)\\,q(x_t\\mid x_0)$, но сеть видит оба канала. Для антител часто зажимают framework и antigen, шумят только CDR.",
        "**Что на выходе.** Совместный sample. Это всё ещё модель, не кристалл. DockQ / AAR / predicted ΔΔG — не SPR.",
        "**Чего класс не делает.** Не few-shot AL. Не staged inverse folding. Не ESM3 masked LM. Chroma ближе к coordinate diffusion + design-net **после** backbone, даже если в каталоге у неё несколько architecture_id.",
        "Каталог: DiffAb, AbDiffuser, BoltzGen. Соседние страницы — [joint generation](/architectures/joint-sequence-structure-generation.html) (надкласс) и [frame diffusion](/architectures/frame-diffusion.html) (часто без discrete type-канала).",
        "Ниже: общая joint-постановка, затем различия инструментов.",
    ],
    "joint-sequence-structure-generation": [
        "**Совместная генерация sequence и structure** — **надкласс**: один sampling process возвращает связанную пару (иногда ещё function-токены), а не конвейер «backbone generator → inverse folding». Подтипы разные: multimodal masked LM (ESM3), sequence-space diffusion (ProteinGenerator), joint DDPM (DiffAb), flow matching (FlowDesign), iterative GNN (dyMEAN).",
        "Зачем объединять. Если sequence и fold семплируют независимо, легко получить «красивый» остов с несовместимой последовательностью или наоборот. Совместный prior штрафует такую рассинхронизацию на уровне модели — но **не** заменяет эксперимент.",
        "**Что на выходе.** Пара $(s,x)$ (у ESM3 ещё текстовые/функциональные треки). Generated structure ≠ validated PDB.",
        "**Чего класс не делает.** Не developability assay. Не few-shot цикл с ELISA. Staged Chroma (diffusion coords, затем design GNN) помечен в каталоге, но **не** канон simultaneous joint sampler.",
        "Читайте подтип, прежде чем копировать уравнение: MLM unmask ≠ DDPM ≠ ODE flow. Эта страница — карта семейства; детали диффузии/FM — на дочерних классах.",
        "Разделы сначала фиксируют общее $p_\\theta(s,x\\mid c)$, затем ветки каталога.",
    ],
    "flow-matching": [
        "**Flow matching** учит **детерминированное векторное поле** $v_\\theta(x,t)$, которое везёт простой prior (шум) в распределение данных по заданному пути — часто почти прямой линии $x_t=(1-t)x_0+t x_1$. Семплирование — интегрирование ODE $\\dot x=v_\\theta$, обычно за меньшее число шагов, чем длинный DDPM.",
        "В белках $x$ может быть геометрией frames/координат, иногда вместе с sequence-эмбеддингами. Это родственник диффузии по цели (transport noise→data), но **другой** train target: регрессия на условный поток, не score matching.",
        "**Что на выходе.** Состояние при $t=1$ (часто CDR sequence+structure в FlowDesign). Не энергия и не $K_d$.",
        "**Чего класс не делает.** Не AL. Не «diffusion с другим маркетинговым именем»: формулы и sampler другие. Меньше накопленной antibody-практики, чем у RFdiffusion/DiffAb; не обобщать одну кампанию на класс.",
        "Соседи: [frame](/architectures/frame-diffusion.html) / [joint](/architectures/joint-sequence-structure-diffusion.html) diffusion. Не копировать CFM MSE на ProteinMPNN или UCB.",
        "Дальше — общая ODE-постановка, затем tool-specific FlowDesign, если прочитан.",
    ],
    "inverse-folding": [
        "**Inverse folding** — задача **подобрать sequence под заданный остов**. Прямая задача («фолдинг») идёт sequence→structure. Здесь $x$ (backbone, иногда с лигандом) фиксирован, модель оценивает $p(s\\mid x)$ и семплирует аминокислоты, которые этот fold «любят» в обучающей статистике PDB.",
        "Это **не** смена topology: Cα не двигаются генератором IF. De novo сначала рисует backbone другим классом (diffusion), затем вызывает IF. На антительном комплексе можно зажать antigen chain как контекст — всё равно это sequence design, не docking.",
        "**Что на выходе.** Токены AA, иногда χ packing отдельной головой. Recovery / likelihood / scRMSD после AF2 — не $K_d$.",
        "**Чего класс не делает.** Не генерация fold из шума. Не affinity head, пока его явно нет. Общий ProteinMPNN на CDR без antibody fine-tune — частый failure mode.",
        "Реализации разные: residue MPNN (ProteinMPNN, LigandMPNN), GVP-Transformer (ESM-IF1, AntiFold). Не называть ESM-IF1 «просто GNN».",
        "Разделы ниже: сначала постановка $p(s\\mid x)$, затем различия encoder/decoder в papers.",
    ],
    "graph-neural-networks": [
        "**Графовые сети (GNN / MPNN)** представляют белок как **граф**: узлы — residues или атомы, рёбра — kNN, радиус, химические связи, иногда атомы лиганда. Слой обновляет признак узла сообщениями от соседей. Это **индуктивный bias локального packing**, а не generative process сам по себе.",
        "Генератор появляется, только когда к MPNN вешают голову: AR sequence, обновление координат, χ, или GNN внутри чужого diffusion denoiser. Dense pair Transformer и IPA — другие классы.",
        "**Что на выходе.** Зависит от головы: AA logits (ProteinMPNN), sequence+χ (LigandMPNN), full-atom+dock (dyMEAN), denoised coords (Chroma как слой). Не «GNN = Kd».",
        "**Чего класс не делает.** Не гарантирует дальние контакты за cutoff. Не считает электростатику, пока нет energy head. AAR / DockQ / predicted ΔΔG ≠ assay.",
        "Не путать с [geometric transformers](/architectures/geometric-transformers.html) (GVP затем Transformer) и с [SE(3)](/architectures/se3-equivariant-models.html) (эквивариантные векторные слои: у ProteinMPNN features в основном invariant distances).",
        "Сначала общая схема сообщений, затем подтипы каталога — у каждого свой train target.",
    ],
    "geometric-transformers": [
        "**Геометрические трансформеры** — сети, в которых Transformer (или AF-like pair track + IPA) видит **3D**: расстояния, ориентации, frames, pair features, а не только позицию в последовательности. GVP или другой геометрический encoder часто стоит **перед** attention и переводит векторы в инвариантные токены.",
        "Зачем. Дальние контакты и глобальный контекст цепи плохо лезут в маленький kNN-граф. Attention по всем residues дороже, но видит дальше. Это backbone **архитектуры**, не отдельный diffusion process и не задача IF сама по себе.",
        "**Что на выходе.** Sequence logits (ESM-IF1, AntiFold) или обновлённые frames/комплекс (tFold structure module). Зависит от головы.",
        "**Чего класс не делает.** Не PLM без геометрии. Не ProteinMPNN. Seed-формула pair-bias **не** является loss ESM-IF1. Квадратичная память бьёт по большим комплексам.",
        "Каталог: ESM-IF1, AntiFold, tFold. RFdiffusion / FlowDesign имеют другие architecture_id.",
        "Разделы: общая композиция encoder→Transformer/IPA, затем подтипы A/B без смешения уравнений.",
    ],
    "se3-equivariant-models": [
        "**SE(3)-эквивариантные сети** — свойство слоя: если весь вход повернуть и сдвинуть, векторный/координатный выход повернётся так же, $f(Rx+t)=Rf(x)+t$. Скалярные головы (типы AA, энергии) при этом **инвариантны**. Это не loss и не sampler, а геометрический prior «лабораторная поза не должна менять физику».",
        "Реализации: GVP vector channels, TFN/сферические гармоники, EGNN, IPA, frame updates. Одна и та же модель может смешивать invariant и equivariant пути — нельзя одной фразой «модель equivariant».",
        "**Что на выходе.** Features или координаты/frames, согласованные с позой. Sequence logits обычно invariant.",
        "**Чего класс не делает.** Не задаёт сам по себе diffusion. ProteinMPNN на distances **не** в этом id. Сломанная реализация equivariance даёт зависимость от ориентации PDB.",
        "Страница про слой; generative process смотрите на diffusion/flow. dyMEAN имеет оба id, потому что AME одновременно GNN и E(3).",
        "Ниже: общее определение группы, затем как equivariance устроена в GVP / DiffAb / FrameDiff / dyMEAN.",
    ],
    "invariant-models": [
        "**Инвариантные модели** — снова **свойство отображения**, не генератор fold. Скаляр $f(Rx+t)=f(x)$: distances, углы, dihedrals, GVP-скаляры, 2D templates, sequence logits. Поза комплекса в лабораторных осях не должна менять тип аминокислоты или score.",
        "Этого **недостаточно**, чтобы семплировать абсолютные координаты: для xyz нужен equivariant путь или отдельный reconstruction. Inverse folding как раз хочет invariant $p(s\\mid x)$.",
        "**Что на выходе.** Скаляры и дискретные метки, не docked pose (pose — другой класс).",
        "**Чего класс не делает.** Не чинит chirality сам по себе (неподписанные расстояния). Не thermodynamics. 2D framework template RFantibody — conditioner, не генератор CDR.",
        "Не путать invariance и equivariance. Не восстанавливать xyz из одних distances без доп. ограничений.",
        "Разделы объясняют, какие признаки инвариантны в IF и RF-семействе, затем papers.",
    ],
    "protein-language-models": [
        "**Белковые языковые модели (PLM)** учатся на sequences как на тексте: предсказать следующую аминокислоту (autoregressive, ProGen/IgLM) или закрытый токен (masked, ESM-2/ESM-1v; generative MLM у ESM3). Из этого получаются **эволюционные статистики** и семплы sequences **без** обязательной 3D-геометрии.",
        "Один и тот же класс играет разные роли: генератор, frozen encoder для few-shot головы, zero-shot scorer $\\Delta\\ell$. Это не «магический affinity oracle».",
        "**Что на выходе.** Токены и/или правдоподобия 20 AA. Structure, если есть, приходит из другого модуля (ESM3 structure tokens — отдельный трек, не PDB-эксперимент).",
        "**Чего класс не делает.** Не de novo backbone из шума (кроме multimodal подтипов с явным structure track). Likelihood ≠ функция. Bias корпусов (human IGHV, UniRef) бьёт по редким форматам.",
        "Соседи: [autoregressive generation](/architectures/autoregressive-generation.html) (как пишут токены), [masked infilling](/architectures/masked-token-infilling.html), [zero-shot scoring](/architectures/zero-shot-mutation-scoring.html).",
        "Сначала семейство ролей PLM, затем ProGen / ESM / IgLM / EVOLVEpro-как-голова — без смешения их losses.",
    ],
    "autoregressive-generation": [
        "**Авторегрессионная генерация** пишет объект **по порядку**: каждый токен (аминокислота, иногда с conditioner) зависит только от уже сгенерированного префикса, $p(x_i\\mid x_{<i},c)$. Это схема факторизации likelihood, а не обязательно «GPT про белки»: тот же принцип у ProteinMPNN, но порядок там **случайная перестановка узлов**, не N→C.",
        "Обучение — next-token cross-entropy (teacher forcing). Inference — последовательный softmax, temperature, top-k, иногда beam. Ошибка в начале каскадирует; низкая температура сужает разнообразие.",
        "**Что на выходе.** Дискретная последовательность. Геометрия, если нужна, приходит снаружи (backbone как $c$) или не приходит вовсе.",
        "**Чего класс не делает.** Не рисует fold. Не AL. Не diffusion. Не путать causal LM и masked LM.",
        "Каталог пересекается с ProGen, IgLM, ProteinMPNN, ESM-IF1 (AR decoder). Смотрите, какой **порядок** и какой **conditioner**.",
        "Разделы: общая факторизация, затем отличия order и контекста в tools.",
    ],
    "autoregressive-structure-generation": [
        "**Авторегрессионная генерация структуры** наращивает 3D **последовательно**: каждый новый residue frame или fragment conditioned на уже поставленные. Likelihood структуры явна, $p(x)=\\prod p(x_i\\mid x_{<i},c)$, но порядок вдоль цепи — искусственный для трёхмерного объекта: природа не «печатает» белок с N-конца в координатах.",
        "**Что на выходе.** Упорядоченные frames/координаты. Sequence может быть условием или отсутствовать.",
        "**Чего класс не делает.** Не humanization. На длинных цепях ошибка дрейфует. Это не параллельный DDPM всех residues сразу.",
        "В каталоге мало канонических tools с этим id; не подставлять RFdiffusion (он не AR по residues). Сравнивать с [frame diffusion](/architectures/frame-diffusion.html), где все кадры шумят совместно.",
        "Ниже — общая sequential 3D-постановка и честные NR там, где papers не прочитаны.",
    ],
    "masked-token-infilling": [
        "**Заполнение masked-токенов (infilling)** скрывает часть sequence и просит восстановить только дыру, глядя на **левый и правый** контекст. Это удобно для CDR: framework известен, гипервариабельный участок нет. Обучение — $p(x_M\\mid x_{\\setminus M})$.",
        "Inference бывает однопроходным или итеративным unmask (сначала уверенные позиции). Если замаскировать почти всё, задача вырождается в безусловную генерацию — это уже другой режим.",
        "**Что на выходе.** Identity на masked позициях. Topology остова не меняется, если 3D не в том же процессе (у ESM3 structure — отдельный трек).",
        "**Чего класс не делает.** Не de novo fold. Не гарантирует binding. Зависит от качества контекста (неверный FR даёт неверный CDR prior).",
        "Каталог: IgLM (infilling CDRs), ESM3, EvoDiff inpaint. Не путать с AR «только слева направо» без правого контекста.",
        "Сначала общая masked-постановка, затем ILM / unmask / OADM как подтипы.",
    ],
    "few-shot-mutation-optimization": [
        "**Few-shot оптимизация мутаций** — режим, в котором у вас уже есть **небольшой** набор измерений на вариантах одного parent (~десятки, не миллионы) и вы хотите предложить следующие mutants. Обычно берут frozen PLM-эмбеддинги и учат лёгкую голову $f_\\phi(E(s))\\approx y$.",
        "Это **не** zero-shot (там labels не нужны) и не обязательно полный AL-цикл, хотя на практике часто запускают несколько раундов. Кандидаты — single-site или комбинаторика разрешённых позиций, не de novo antibody.",
        "**Что на выходе.** Список следующих вариантов под ваш бюджет. Предсказание головы — не SPR, пока не измерили.",
        "**Чего класс не делает.** Без данных не стартует. Легко переобучиться на шум assay и «предсказать» клоны из train. Не рисует новый fold.",
        "Каталог: EVOLVEpro, частично Makowski co-optimization как multi-objective с labels. Смотрите [active learning](/architectures/active-learning.html), если важен именно цикл batch→assay.",
        "Разделы: общая few-shot постановка, затем как устроены головы и библиотеки в papers.",
    ],
    "zero-shot-mutation-scoring": [
        "**Zero-shot оценка мутаций** ранжирует substitutions **без новых экспериментальных labels**. Сравнивают, насколько мутант «естественен» для pretrained PLM или совместим с backbone у inverse folding: типично $\\Delta\\ell=\\log p(s^{\\mathrm{mut}}\\mid c)-\\log p(s^{\\mathrm{wt}}\\mid c)$.",
        "Это **скоринг уже заданных точечных замен**, не генерация библиотеки с нуля и не обучение на вашем ELISA. Высокий $\\Delta\\ell$ значит «модель меньше удивлена», не «лучше $K_d$». Эпистаз и дальние эффекты обычно не поймать.",
        "**Что на выходе.** Ранжированный список single substitutions (19 × позиции). Ensemble моделей может стабилизировать ранг, не калибруя affinity.",
        "**Чего класс не делает.** Не few-shot (нет $D_t$). Не de novo. Не замена BLI. Переоценка evolutionary plausibility — главный failure mode.",
        "Каталог: ESM-1v masked-marginal (Meier) и кампании Hie / Shanker (IF Δℓ на комплексе). Не смешивать masked-marginal и wild-type-marginal без оговорки.",
        "Сначала общая формула скоринга, затем различия протоколов papers.",
    ],
    "multi-objective-optimization": [
        "**Многокритериальная оптимизация** ищет варианты, которые одновременно хороши по **нескольким** $y$: affinity, specificity, экспрессия, полиспецифичность. Один scalar score прячет конфликт. Честная постановка — вектор $y(s)\\in\\mathbb{R}^k$ и **Pareto**: нельзя улучшить один критерий, не ухудшив другой.",
        "На практике встречаются scalarization (взвешенная сумма), каскад фильтров и многоголовые суррогаты. Каскад порогов **не** то же самое, что Pareto-фронт, хотя оба «режут» библиотеку.",
        "**Что на выходе.** Набор trade-off вариантов, не «один победитель», если фронт реален. Нужны **одновременные** labels или честно независимые орacles — иначе цели выдуманы.",
        "**Чего класс не делает.** Не генерация sequences из языковой модели как таковая. Спрятанная scalarization внутри «reward» — типичный самообман. Predicted multi-head ≠ multi-assay.",
        "Каталог: Makowski affinity–specificity, фильтры BindCraft, humanization constraints. Не сравнивать как один benchmark с EVOLVEpro single $y$.",
        "Разделы: общая Pareto-постановка, затем как papers кодируют несколько целей.",
    ],
}


LOOP_IDS = frozenset(
    {
        "active-learning",
        "bayesian-optimization",
        "few-shot-mutation-optimization",
        "zero-shot-mutation-scoring",
        "multi-objective-optimization",
    }
)
SEQ_IDS = frozenset(
    {
        "sequence-diffusion",
        "protein-language-models",
        "autoregressive-generation",
        "masked-token-infilling",
    }
)
LAYER_IDS = frozenset(
    {
        "se3-equivariant-models",
        "invariant-models",
        "graph-neural-networks",
        "geometric-transformers",
    }
)


def _q(value: Any, *, empty: str = "NR") -> str:
    text = _txt(value).rstrip(" .")
    return f"«{text}»" if text else empty


def _family(arch) -> str:
    ident = arch.id
    if ident in LOOP_IDS:
        return "loop"
    if ident in SEQ_IDS:
        return "seq"
    if ident in LAYER_IDS:
        return "layer"
    return "geom"


def _not_assay(arch) -> str:
    return (
        f"Для **{arch.name}** внутренние числа модели (likelihood, score, acquisition, pLDDT, DockQ, predicted $\\Delta\\Delta G$) "
        "не являются экспериментальным affinity / $K_d$ / ELISA / BLI, пока это явно не измерено вне сети."
    )


def _domain(arch) -> str:
    yes = _join(arch.applicable_task_ids, empty="NR")
    no = _join(arch.not_for_task_ids, empty="NR")
    extra = {
        "loop": "Класс стоит **вокруг эксперимента**: он выбирает или ранжирует варианты, а не рисует новый fold.",
        "seq": "Класс работает с **дискретной sequence** (токены аминокислот). 3D, если нужна, приходит снаружи.",
        "layer": "Это **свойство или тип слоя**, а не generative process. Голова сверху задаёт, sequence это, score или coords.",
        "geom": "Класс оперирует **геометрией** (координаты, frames, углы) или парой sequence+structure.",
    }[_family(arch)]
    return (
        f"Этот пункт фиксирует **роль класса** в пайплайне и границу с соседями. {extra} "
        f"Краткая seed-формула: {_q(arch.intuition)}. "
        f"Что метод выдаёт или оценивает: {_q(arch.generated_state)}. Вход: {_q(arch.input_representation)}. "
        f"Задачи каталога, которые класс закрывает: {yes}. Явно не для: {no}. "
        "Дальше по разделу — какие tools имеют этот architecture_id и какие постановки нельзя смешивать."
    )


def _intuition(arch) -> str:
    lever = {
        "loop": "бюджет раунда, состав пула, правило acquisition, шум assay",
        "seq": "температура / mask rate / число шагов unmask или denoising",
        "layer": "cutoff графа, число слоёв, какие величины invariant vs equivariant",
        "geom": "шум train, число шагов sampler, какие frames/coords зажаты",
    }[_family(arch)]
    return (
        f"Общий механизм **{arch.name}**: что меняется за один шаг inference и за счёт какого inductive bias метод может работать. "
        f"{_q(arch.intuition)}. Главный эмпирический рычаг класса — {lever}; это не «магия одной статьи». "
        f"{_not_assay(arch)} Абзацы ниже — как принцип формулируют конкретные papers, не определение всего класса."
    )


def _math(arch) -> str:
    return (
        f"Сначала **родовая математика класса** (что оптимизируют / что семплируют), общая для реализаций с этим id. "
        f"Seed-запись: {_q(arch.mathematical_formulation, empty='NR — родовая формула не задана')}. "
        "Подтипы имеют **отдельные** уравнения: нельзя переносить diffusion score, UCB, AR NLL, FAPE или MLM $\\Delta\\ell$ "
        "на эту страницу, если это не её train target. Формулы с пометкой tool-specific относятся к одному инструменту. "
        "Ниже — разбор papers по подтипам."
    )


def _data(arch) -> str:
    tensors = {
        "loop": "эмбеддинги вариантов, таблица labels $y$, индекс пула / library",
        "seq": "токены AA, mask / time index, опционально conditioner (framework, motif)",
        "layer": "узлы/рёбра или pair features, геометрические скаляры и векторы",
        "geom": "координаты / frames / torsions, time, masks, иногда discrete type-канал",
    }[_family(arch)]
    files = {
        "loop": "CSV библиотеки, assay table, fasta parent",
        "seq": "fasta, IMGT numbering, CDR mask",
        "layer": "PDB графа, ligand context, kNN cutoff",
        "geom": "PDB, contig, hotspot, antigen chain",
    }[_family(arch)]
    return (
        f"Класс читает {_q(arch.input_representation)}. "
        f"Нужно отличать **тензор сети** ({tensors}) от **внешнего файла** ({files}). "
        "Размерности и аугментации без paper/code остаются NR. Дальше — как это кодируют конкретные реализации."
    )


def _physical(arch) -> str:
    fam = _family(arch)
    core = f"Математический объект класса соответствует такому физическому state: {_q(arch.generated_state)}. "
    extra = {
        "loop": (
            "Обычно это **вариант sequence** (мутант) плюс, для AL/BO, ещё не измеренный пул. "
            "Эмбеддинг PLM — не координаты и не энергия. Глобальный поворот PDB здесь ни при чём: структуры в state нет, "
            "пока метод явно не берёт IF-эмбеддинги комплекса."
        ),
        "seq": (
            "State — **identity токенов**. Перестановка residues ломает биологическую sequence; лабораторная поза кристалла "
            "на токены не действует. Masked / noisy token ≠ фолдинг."
        ),
        "layer": (
            "Слой преобразует признаки. Invariance/equivariance говорит, что будет с поворотом входа; "
            "сам слой **не обязан** выдавать готовую укладку. Side chains — только если голова их предсказывает."
        ),
        "geom": (
            "Перестановка residues, склейка цепей и глобальный поворот ломают разные инварианты — это свойство представления. "
            "Промежуточный noisy state ≠ MD-траектория и ≠ энергия. Side chains либо в state, либо pack post-hoc, либо отсутствуют."
        ),
    }[fam]
    return core + extra + " Ниже papers фиксируют, какой вариант они выбрали."


def _physchem(arch) -> str:
    seen = {
        "loop": "в первую очередь experimental $y$ и эволюционную статистику PLM, если encoder frozen",
        "seq": "в первую очередь identity и sequence statistics; геометрию — только если conditioner её подаёт",
        "layer": "локальную геометрию (distances, ориентации) в том виде, в каком её закодировали features",
        "geom": "backbone / frames / атомы в том разрешении, которое есть в state; не автоматически $\\Delta G$",
    }[_family(arch)]
    return (
        f"Какие физико-химические оси класс **вообще может «видеть»**. Этот класс — {seen}. "
        "H-bonds, электростатика, растворитель, энтропия и experimental affinity отсутствуют, пока нет явной energy / assay головы: "
        "модель тогда **не считает** $\\Delta G$. Таблица ниже — как конкретные методы кодируют эти оси; строка про один tool не обобщается на класс."
    )


def _learned(arch) -> str:
    return (
        f"Общий train target класса: {_q(arch.training_objective)}. "
        "Нужно назвать, какие модули обучаются, какие frozen (PLM, MSA, RoseTTAFold trunk), и есть ли в loss negative / non-binder / affinity labels. "
        "Если в постановке класса labels нет — ответ «нет», даже если кто-то доучивает голову в приложении. "
        "Fine-tune vs pretrain различается объектом (PDB identities, SAbDab, assay $y$), не маркетингом. Детали сплитов — в подразделах papers."
    )


def _forward(arch) -> str:
    flow = {
        "loop": "пул или список мутаций → (опционально encoder) → суррогат/scorer → выбор batch или ранжирование → **внешний assay** → обновление данных",
        "seq": "токены (± mask/шум) → сеть → новые токены / logits. Геометрия, pack, AF, docking — чужие блоки",
        "layer": "граф или pair features → слои → голова (logits, coords, score). Sampler, если есть, живёт в другом классе",
        "geom": "шум или частичная структура → denoiser / decoder → coords/frames → часто отдельный inverse folding, pack, AF",
    }[_family(arch)]
    return (
        f"Прямой проход класса: {flow}. "
        "Чужие блоки (pack, AlphaFold, docking, ELISA) нельзя прятать внутрь «одной сети». "
        "Схема ниже, если есть, — оригинал по прочитанным источникам, не копипаст figure. Затем — где у tools generator, а где evaluator."
    )


def _training(arch) -> str:
    corpora = {
        "loop": "набор измеренных вариантов parent-а и, отдельно, pretrain корпуса PLM, если encoder не с нуля",
        "seq": "sequence corpora (UniRef, OAS, antibody subsets) — не «все PDB» автоматически",
        "layer": "то, на чём учили голову: IF identities, denoising PDB, docking complexes",
        "geom": "структуры PDB / SAbDab / complexes; фильтры resolution и redundancy — у реализации, не у класса",
    }[_family(arch)]
    return (
        f"У класса **нет единого корпуса**. Типичные данные: {corpora}. "
        "Split и leakage — свойства датасета реализации. Не выводить split из README. "
        "Не смешивать in silico designability с prospective wet-lab. Ниже каждый paper описывает свой корпус; нет цифры = NR."
    )


def _inference(arch) -> str:
    start = {
        "loop": "не «шум из $\\mathcal{N}(0,I)$», а библиотека / список мутаций / уже посчитанные эмбеддинги",
        "seq": "маска, полностью случайная sequence или prefix",
        "layer": "один forward (или несколько recycle), если нет внешнего sampler",
        "geom": "шум / partial structure / contig",
    }[_family(arch)]
    return (
        f"Общий inference класса: {_q(arch.inference)}. Старт — {start}. "
        "Pack / relax / AF / likelihood rerank помечаются как evaluator, не generator. "
        "Чего в классе нет (beam, recycle, assay-in-the-loop), пока tool явно не добавляет, — тоже общее свойство. "
        "Число шагов $T$, temperature, $k$ — tool-specific, если не оговорено."
    )


def _conditioning(arch) -> str:
    warn = {
        "loop": "пул $\\mathcal{X}$, разрешённые позиции, бюджет $k$, parent — не epitope tensor и не CFG, пока их нет",
        "seq": "mask / framework / motif tokens — не hotspot Cα, пока 3D не подают",
        "layer": "какие узлы и рёбра видны (ligand, antigen chain) — не diffusion contig",
        "geom": "contig / motif / hotspot / antigen frames; ELISA labels не являются conditioner, пока нет такой головы",
    }[_family(arch)]
    return (
        f"Что класс умеет зажимать по постановке: {_q(arch.conditioning)}. {warn}. "
        "Contig, mask, motif, hotspot и library — разные объекты. Ниже papers перечисляют свой conditioner без переноса с соседа."
    )


def _complexity(arch) -> str:
    return (
        f"Драйверы стоимости класса: {_q(_join(arch.complexity_drivers, empty=''), empty='NR')}. "
        "Сравнение «дешевле diffusion» допустимо только если paper дал NFE/steps; иначе это INTERPRETATION или молчание. "
        "GPU hours / wall-clock без источника — NR. Цифры одной кампании не становятся сложностью всего класса."
    )


def _strengths(arch) -> str:
    return (
        "Преимущества должны следовать из **механизма класса** (цикл с малым бюджетом, локальный граф, joint prior…), не из маркетинга. "
        f"Seed-список: {_q(_join(arch.strengths, empty=''), empty='NR')}. "
        "Любое количественное число ниже обязано иметь PAPER/SI locator и не обобщается с одного белка на класс. "
        "Это не гарантия стабильности, аффинности или экспрессии."
    )


def _limits(arch) -> str:
    return (
        "Ограничения класса по осям: математика представления, физика/химия, bias данных, обобщение, deployment. "
        f"Seed-список: {_q(_join(arch.limitations, empty=''), empty='NR')}. "
        "Не дублировать преимущества с обратным знаком без новой информации. Ниже papers добавляют конкретные дыры (SI, split, gated weights)."
    )


def _failures(arch) -> str:
    typical = {
        "loop": "пул без хорошего binder, переобучение на шум assay, greedy top-$N$ без exploration, $\\hat y$ как будто $K_d$",
        "seq": "слишком большой mask, temperature $\\to 0$, NLL/AAR как affinity",
        "layer": "малый cutoff, сломанная invariance/equivariance, IF-likelihood как ELISA",
        "geom": "неверный contig/hotspot, pLDDT как binder, забытый inverse folding",
    }[_family(arch)]
    return (
        f"Типичные ошибки **пользователя и модели** для этого класса: {typical}. "
        f"Seed-список: {_q(_join(arch.failure_modes, empty=''), empty='NR')}. "
        "Это не общие «может не сработать». Дальше — как эти режимы проявлялись в конкретных работах каталога."
    )


def _tools(arch) -> str:
    return (
        "Реализации класса в каталоге определяются reverse index `architecture_id`, а не похожестью названия. "
        "Колонки таблицы: generic architecture vs tool-specific. Непрочитанный tool — строка с NR, без выдуманных уравнений. "
        "Foundational methods вне карточек tools можно указать явно. Неравные кампании не ставят в одну колонку «успех». "
        "Список ссылок на tools повторяется служебным блоком после нумерованных разделов."
    )


def _applicability(arch) -> str:
    yes = _join(arch.applicable_task_ids, empty="NR")
    no = _join(arch.not_for_task_ids, empty="NR")
    return (
        f"Класс уместен для задач: {yes}. Не уместен: {no}. "
        "Ссылки на workflows имеют смысл, только если стадия реально вызывает этот класс как generator/scorer, а не как соседний модуль. "
        "Чем пользоваться вместо запрещённой задачи — соседний architecture / workflow, не «тот же GNN». "
        "Ниже — разбор papers и явные запреты, затем служебные списки каталога."
    )


def _method_sources(arch) -> str:
    papers = _join(arch.paper_ids, empty="NR")
    return (
        "Этот раздел — какие работы **определяют класс** и какие карточки papers каталога к нему привязаны, что прочитано vs pointer-only. "
        f"Идентификаторы каталога: {papers}. "
        "Это не библиография «всего по теме». Таблица происхождения источников, paywall и статус сверки вынесены **в конец страницы**, чтобы не заслонять определение класса."
    )


SECTION_OVERVIEWS = {
    "domain": _domain,
    "intuition": _intuition,
    "math": _math,
    "data-repr": _data,
    "physical-repr": _physical,
    "physchem": _physchem,
    "learned": _learned,
    "forward": _forward,
    "training": _training,
    "inference": _inference,
    "conditioning": _conditioning,
    "complexity": _complexity,
    "strengths": _strengths,
    "limits": _limits,
    "failures": _failures,
    "tools": _tools,
    "applicability": _applicability,
    "method-sources": _method_sources,
}
