from sistema import uptime


def test_formata_horas_e_minutos():
    assert uptime.formatar(5 * 3600 + 23 * 60) == "Ligado há 5h 23min"


def test_formata_menos_de_uma_hora():
    assert uptime.formatar(23 * 60) == "Ligado há 0h 23min"


def test_ignora_os_segundos_que_sobram():
    assert uptime.formatar(5 * 3600 + 23 * 60 + 59) == "Ligado há 5h 23min"


def test_leitura_indisponivel_devolve_vazio():
    """Vazio esconde a linha inteira — o rodapé nunca exibe mensagem de erro."""
    assert uptime.formatar(None) == ""


def test_valor_negativo_devolve_vazio():
    assert uptime.formatar(-10) == ""


def test_maquina_ligada_ha_dias_continua_em_horas():
    """Decisão registrada: horas e minutos exatos, sem virar 'há 3 dias'."""
    assert uptime.formatar(73 * 3600 + 12 * 60) == "Ligado há 73h 12min"
