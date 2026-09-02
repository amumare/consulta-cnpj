import re

def clean_cnpj(cnpj: str) -> str:
    """
    Remove todos os caracteres não numéricos de uma string de CNPJ.
    Exemplo: '12.345.678/0001-90' -> '12345678000190'
    """
    if not cnpj:
        return ""
    return re.sub(r'\D', '', cnpj)


def format_cnpj(cnpj_digits: str) -> str:
    """
    Formata uma string de 14 dígitos no padrão XX.XXX.XXX/XXXX-XX.
    """
    if len(cnpj_digits) != 14:
        return cnpj_digits
    return f"{cnpj_digits[:2]}.{cnpj_digits[2:5]}.{cnpj_digits[5:8]}/{cnpj_digits[8:12]}-{cnpj_digits[12:]}"


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida se o CNPJ possui 14 dígitos e se os seus dígitos verificadores são matematicamente válidos.
    Utiliza o algoritmo de Módulo 11 oficial da Receita Federal.
    """
    digits = clean_cnpj(cnpj)

    # CNPJ deve ter exatamente 14 dígitos
    if len(digits) != 14:
        return False

    # Elimina sequências conhecidas de dígitos idênticos (ex: 00000000000000, 11111111111111)
    if digits == digits[0] * 14:
        return False

    # Cálculo do 1º Dígito Verificador
    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_1 = sum(int(digit) * weight for digit, weight in zip(digits[:12], weights_1))
    remainder_1 = sum_1 % 11
    digit_1 = 0 if remainder_1 < 2 else 11 - remainder_1

    if int(digits[12]) != digit_1:
        return False

    # Cálculo do 2º Dígito Verificador
    weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_2 = sum(int(digit) * weight for digit, weight in zip(digits[:13], weights_2))
    remainder_2 = sum_2 % 11
    digit_2 = 0 if remainder_2 < 2 else 11 - remainder_2

    if int(digits[13]) != digit_2:
        return False

    return True