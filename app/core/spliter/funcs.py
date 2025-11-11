from .split import split_normal_file, split_bestiary, split_class
from .combine import combine_normal_file,combine_bestiary
SPLIT_ADVENTURE_FUNC = {
    "prefix": "adventure-",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "adventure",
    "args": {}
}

SPLIT_BOOK_FUNC = {
    "prefix": "book-",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "book",
    "args": {}
}

SPLIT_BESTIARY_FUNC = {
    "prefix": "bestiary-",
    "split_func": split_bestiary,
    "combine_func": combine_bestiary,
    "output_dir": "bestiary",
    "args": {}
}

SPLIT_CLASS_FUNC = {
    "prefix": "class-",
    "split_func": split_class,
    "combine_func": combine_normal_file,
    "output_dir": "class",
    "args": {}
}

SPLIT_SPELLS_FUNC = {
    "prefix": "spells-",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "spells",
    "args": {}
}
SPLIT_ACTIONS_FUNC = {
    "prefix": "actions.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "actions",
    "args": {}
}

SPLIT_BACKGROUND_FUNC = {
    "prefix": "backgrounds.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "backgrounds",
    "args": {}
}

SPLIT_BASTIONS_FUNC = {
    "prefix": "bastions.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "bastions",
    "args": {}
}

SPLIT_CHAROPTIONS_FUNC = {
    "prefix": "charcreationoptions.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "charcreationoptions",
    "args": {}
}

SPLIT_CONTITION_DISEASES_FUNC = {
    "prefix": "conditionsdiseases.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "conditionsdiseases",
    "args": {}
}

# TODO: 这个存在问题，拆分后的文件多一个type导致渲染器生成不出来
SPLIT_CULTS_BOONS_FUNC = {
    "prefix": "cultsboons.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "cultsboons",
    "args": {}
}

SPLIT_DECKS_FUNC = {
    "prefix": "decks.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "decks",
    "args": {}
}

# TODO: 这个存在问题，渲染器生成不出来
SPLIT_DEITIES_FUNC = {
    "prefix": "deities.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "deities",
    "args": {}
}

SPLIT_FEATS_FUNC = {
    "prefix": "feats.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "feats",
    "args": {}
}

SPLIT_ITEMS_FUNC = {
    "prefix": "items.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "items",
    "args": {}
}

SPLIT_OPJECTS_FUNC = {
    "prefix": "objects.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "objects",
    "args": {}
}

SPLIT_OPTIONALFEATURES_FUNC = {
    "prefix": "optionalfeatures.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "optionalfeatures",
    "args": {}
}

SPLIT_RACES_FUNC = {
    "prefix": "races.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "races",
    "args": {}
}

SPLIT_PSIONICS_FUNC = {
    "prefix": "psionics.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "psionics",
    "args": {}
}

SPLIT_REWARDS_FUNC = {
    "prefix": "rewards.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "rewards",
    "args": {}
}

SPLIT_SENCES_FUNC = {
    "prefix": "senses.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "senses",
    "args": {}
}

SPLIT_SKILLS_FUNC = {
    "prefix": "skills.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "skills",
    "args": {}
}

SPLIT_TRAPSHAZARDS_FUNC = {
    "prefix": "trapshazards.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "trapshazards",
    "args": {}
}

SPLIT_VARIANTRULES_FUNC = {
    "prefix": "variantrules.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "variantrules",
    "args": {}
}
SPLIT_VEHICLES_FUNC = {
    "prefix": "vehicles.json",
    "split_func": split_normal_file,
    "combine_func": combine_normal_file,
    "output_dir": "vehicles",
    "args": {}
}

SPLIT_FUNCS = [
    SPLIT_ADVENTURE_FUNC,
    SPLIT_BOOK_FUNC,
    SPLIT_BESTIARY_FUNC,
    SPLIT_CLASS_FUNC,
    SPLIT_SPELLS_FUNC,
    SPLIT_ACTIONS_FUNC,
    SPLIT_BACKGROUND_FUNC,
    SPLIT_BASTIONS_FUNC,
    SPLIT_CHAROPTIONS_FUNC,
    SPLIT_CONTITION_DISEASES_FUNC,
    SPLIT_CULTS_BOONS_FUNC,
    SPLIT_DECKS_FUNC,
    SPLIT_DEITIES_FUNC,
    SPLIT_FEATS_FUNC,
    SPLIT_ITEMS_FUNC,
    SPLIT_OPJECTS_FUNC,
    SPLIT_OPTIONALFEATURES_FUNC,
    SPLIT_RACES_FUNC,
    SPLIT_PSIONICS_FUNC,
    SPLIT_REWARDS_FUNC,
    SPLIT_SENCES_FUNC,
    SPLIT_SKILLS_FUNC,
    SPLIT_TRAPSHAZARDS_FUNC,
    SPLIT_VARIANTRULES_FUNC,
    SPLIT_VEHICLES_FUNC,
]