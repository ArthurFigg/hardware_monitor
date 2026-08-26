import recursos
from hardware.collector import DadosHardware
from hardware.thresholds import Status
from recursos import (
    CAUSA_DESGASTE,
    CAUSA_ESPACO,
    CPU,
    DISCO,
    RAM,
    RECURSOS,
    TEMPERATURA,
    pior_status,
    por_nome,
)


def test_todos_os_recursos_tem_nome_unico():
    nomes = [r.nome for r in RECURSOS]
    assert len(nomes) == len(set(nomes))


def test_por_nome_encontra_o_recurso():
    assert por_nome("cpu") is CPU


def test_cada_recurso_usa_a_propria_funcao_de_classificacao():
    assert CPU.classificar(90.0) == Status.ALERTA
    assert TEMPERATURA.classificar(90.0) == Status.ALERTA
    assert TEMPERATURA.classificar(50.0) == Status.NORMAL


def test_cpu_e_temperatura_classificam_o_mesmo_numero_de_formas_diferentes():
    # 70 é ALERTA em nenhuma das duas, mas por limites distintos
    assert CPU.classificar(70.0) == Status.ATENCAO
    assert TEMPERATURA.classificar(70.0) == Status.ATENCAO
    assert CPU.classificar(62.0) == Status.ATENCAO
    assert TEMPERATURA.classificar(58.0) == Status.NORMAL


def test_disco_tem_duas_variantes_de_alerta():
    por_espaco = DISCO.descricao(Status.ALERTA, CAUSA_ESPACO)
    por_desgaste = DISCO.descricao(Status.ALERTA, CAUSA_DESGASTE)
    assert por_espaco != por_desgaste


def test_disco_alerta_por_espaco_manda_apagar_arquivos():
    assert "Apague arquivos" in DISCO.descricao(Status.ALERTA, CAUSA_ESPACO)


def test_disco_alerta_por_desgaste_manda_copiar_e_nao_apagar():
    texto = DISCO.descricao(Status.ALERTA, CAUSA_DESGASTE)
    assert "cópia" in texto
    assert "Apague" not in texto


def test_causa_ausente_cai_na_causa_padrao():
    assert DISCO.descricao(Status.ALERTA, "inexistente") == DISCO.descricao(
        Status.ALERTA, CAUSA_ESPACO
    )


def test_recurso_que_nao_notifica_devolve_nada():
    mudo = recursos.Recurso(
        nome="mudo",
        rotulo="Mudo",
        classificar=CPU.classificar,
        extrair=lambda d: 0.0,
        formatar_valor=CPU.formatar_valor,
        descricoes=CPU.descricoes,
        notificacoes=CPU.notificacoes,
        notifica=False,
    )
    assert mudo.texto_notificacao(Status.ALERTA) is None


def test_notificacao_de_cpu_nomeia_o_programa():
    titulo, corpo = CPU.texto_notificacao(
        Status.ALERTA, programa="chrome.exe", valor=78.0
    )
    assert titulo == "CPU em sobrecarga"
    assert "chrome.exe está usando 78% da CPU" in corpo


def test_notificacao_de_ram_fala_de_memoria():
    titulo, corpo = RAM.texto_notificacao(
        Status.ALERTA, programa="chrome.exe", valor=62.0
    )
    assert titulo == "Memória em sobrecarga"
    assert "da memória" in corpo


def test_notificacao_sem_programa_nao_deixa_lacuna():
    _, corpo = CPU.texto_notificacao(Status.ALERTA)
    assert "{" not in corpo
    assert corpo.strip()


def test_temperatura_nao_anuncia_problema_de_memoria():
    titulo, corpo = TEMPERATURA.texto_notificacao(Status.ALERTA)
    assert titulo == "Temperatura crítica"
    assert "memória" not in corpo


def test_disco_notifica_desgaste_com_titulo_proprio():
    titulo, _ = DISCO.texto_notificacao(Status.ALERTA, CAUSA_DESGASTE)
    assert titulo == "Disco com sinais de desgaste"


def test_nao_ha_notificacao_fora_do_alerta():
    assert CPU.texto_notificacao(Status.ATENCAO) is None
    assert CPU.texto_notificacao(Status.NORMAL) is None


def test_so_cpu_e_ram_varrem_processos():
    varrem = {r.nome for r in RECURSOS if r.varre_processos}
    assert varrem == {"cpu", "ram"}


def test_temperatura_e_extraida_da_cpu():
    dados = DadosHardware(cpu=100.0, ram=10.0, disco=10.0)
    assert TEMPERATURA.extrair(dados) == 85.0


def test_formato_do_valor_por_recurso():
    assert CPU.formatar_valor(74.0) == "74%"
    assert TEMPERATURA.formatar_valor(66.0) == "~66°C"


def test_pior_status_e_o_mais_grave():
    assert pior_status([Status.NORMAL, Status.ATENCAO, Status.NORMAL]) == Status.ATENCAO
    assert pior_status([Status.ATENCAO, Status.ALERTA]) == Status.ALERTA
    assert pior_status([Status.NORMAL, Status.NORMAL]) == Status.NORMAL


def test_pior_status_ignora_recurso_indisponivel():
    assert pior_status([Status.NORMAL, None, Status.ATENCAO]) == Status.ATENCAO


def test_pior_status_sem_nenhum_recurso_e_normal():
    assert pior_status([]) == Status.NORMAL


def test_texto_de_interface_nao_existe_em_outro_lugar():
    """Cada frase da interface tem origem única em recursos.py."""
    import pathlib

    raiz = pathlib.Path(__file__).parent.parent
    frases = [
        texto
        for recurso in RECURSOS
        for por_causa in recurso.descricoes.values()
        for texto in por_causa.values()
    ]

    outros = [
        p
        for p in raiz.rglob("*.py")
        if ".venv" not in str(p) and "tests" not in str(p) and p.name != "recursos.py"
    ]

    for frase in frases:
        trecho = frase[:40]
        duplicados = [str(p) for p in outros if trecho in p.read_text(encoding="utf-8")]
        assert not duplicados, f"texto duplicado em {duplicados}: {trecho}"


def test_status_sem_texto_cai_no_normal_em_vez_de_quebrar():
    """A placa de vídeo (spec 6) não terá texto de ALERTA — não pode derrubar a tela."""
    sem_alerta = recursos.Recurso(
        nome="parcial",
        rotulo="Parcial",
        classificar=CPU.classificar,
        extrair=lambda d: 0.0,
        formatar_valor=CPU.formatar_valor,
        descricoes={
            Status.NORMAL: {recursos.CAUSA_PADRAO: "tudo bem"},
            Status.ATENCAO: {recursos.CAUSA_PADRAO: "atenção"},
        },
    )
    assert sem_alerta.descricao(Status.ALERTA) == "tudo bem"
