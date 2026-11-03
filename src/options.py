"""Language-neutral identifiers for controller shortcuts."""
from src.i18n import tr

NONE = "none"
INPUT_IDS = ["up", "down", "left", "right", "a", "b", "x", "y"]
MODIFIER_IDS = ["l2", "r2"]

# Legacy buffs.json files stored Portuguese labels; convert them when loading.
LEGACY_IDS = {
    "Nenhum": "none", "Cima": "up", "Baixo": "down", "Esquerda": "left", "Direita": "right",
    "Botão A": "a", "Botão B": "b", "Botão X": "x", "Botão Y": "y", "L2": "l2", "R2": "r2",
}


def normalize_id(value):
    return LEGACY_IDS.get(value, value)


def input_label(input_id):
    return tr("combo.none") if input_id == NONE else tr(f"input.{input_id}")


def modifier_label(modifier_id):
    return tr("combo.none") if modifier_id == NONE else modifier_id.upper()


def modifier_items():
    return [(modifier_label(NONE), NONE)] + [(modifier_label(m), m) for m in MODIFIER_IDS]
