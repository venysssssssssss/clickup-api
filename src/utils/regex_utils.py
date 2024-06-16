import re

FIELD_NAMES = [
    'CARTEIRA DEMANDANTE',
    'E-MAIL',
    'ESCOPO',
    'OBS',
    'OBJETIVO DO GANHO',
    'KPI GANHO',
    '💡 TIPO DE PROJETO',
    'TIPO DE PROJETO',
    'TIPO DE OPERAÇÃO',
    'PRODUTO',
    'OPERAÇÃO',
    'SITE',
    'UNIDADE DE NEGÓCIO',
    'DIRETOR TAHTO',
    'CLIENTE',
    'TIPO',
    '💡 R$ ANUAL (PREVISTO)',
    'GERENTE OI',
    'FERRAMENTA ENVOLVIDA',
    'CENÁRIO PROPOSTO',
    'DATA ALVO',
]

FIELD_PATTERNS = {
    field_name: re.compile(
        rf'{re.escape(field_name)}\s*:\s*(.*?)(?=\s*({"|".join([re.escape(name) for name in FIELD_NAMES])})\s*:|$)',
        re.IGNORECASE,
    )
    for field_name in FIELD_NAMES
}
