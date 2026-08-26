from unittest.mock import MagicMock, patch

from hardware import pdh


def test_caminho_com_instancia():
    esperado = "\\Processor Information(_Total)\\% Processor Performance"
    assert pdh.caminho("Processor Information", "% Processor Performance") == esperado


def test_caminho_sem_instancia():
    assert pdh.caminho("Memory", "Available MBytes", instancia="") == (
        "\\Memory\\Available MBytes"
    )


def test_nome_por_indice_sem_pdh_devolve_none():
    """Windows sem pdh.dll, ou o CI rodando em Linux."""
    with patch.object(pdh, "_pdh", None):
        assert pdh.nome_por_indice(2610) is None


def test_nome_por_indice_com_erro_devolve_none():
    falso = MagicMock()
    falso.PdhLookupPerfNameByIndexW.return_value = 0xC0000BB8
    with patch.object(pdh, "_pdh", falso):
        assert pdh.nome_por_indice(2610) is None


def test_contador_sem_pdh_nao_abre():
    with patch.object(pdh, "_pdh", None):
        contador = pdh.Contador(2610, 2660, "Processor Information", "% Perf")
        assert not contador.ok


def test_contador_sem_pdh_le_none():
    with patch.object(pdh, "_pdh", None):
        contador = pdh.Contador(2610, 2660, "Processor Information", "% Perf")
        assert contador.ler() is None


def _pdh_falso(erro_ao_adicionar=0, erro_ao_abrir=0):
    falso = MagicMock()
    falso.PdhOpenQueryW.return_value = erro_ao_abrir
    falso.PdhAddCounterW.return_value = erro_ao_adicionar
    falso.PdhCollectQueryData.return_value = 0
    falso.PdhLookupPerfNameByIndexW.return_value = 0xC0000BB8
    return falso


def test_contador_com_consulta_que_nao_abre_nao_fica_ok():
    with patch.object(pdh, "_pdh", _pdh_falso(erro_ao_abrir=0xC0000BC0)):
        contador = pdh.Contador(2610, 2660, "Processor Information", "% Perf")
        assert not contador.ok


def test_contador_inexistente_nao_fica_ok():
    with patch.object(pdh, "_pdh", _pdh_falso(erro_ao_adicionar=0xC0000BB8)):
        contador = pdh.Contador(2610, 2660, "Processor Information", "% Perf")
        assert not contador.ok


def test_contador_cai_para_o_nome_em_ingles_quando_nao_ha_traducao():
    """Sem tradução, o caminho tentado tem que ser o inglês — não uma string vazia."""
    falso = _pdh_falso()
    with patch.object(pdh, "_pdh", falso):
        pdh.Contador(2610, 2660, "Processor Information", "% Processor Performance")
    caminho_usado = falso.PdhAddCounterW.call_args_list[0].args[1]
    assert caminho_usado == ("\\Processor Information(_Total)\\% Processor Performance")


def test_contador_usa_o_nome_traduzido_quando_existe():
    """O nome em inglês não existe num Windows em português — por isso o índice."""
    falso = _pdh_falso()

    def traduzir(_maquina, indice, buffer, _tamanho):
        buffer.value = {2610: "Informações do Processador", 2660: "% de Desempenho"}[
            indice.value
        ]
        return 0

    falso.PdhLookupPerfNameByIndexW.side_effect = traduzir
    with patch.object(pdh, "_pdh", falso):
        pdh.Contador(2610, 2660, "Processor Information", "% Processor Performance")
    caminho_usado = falso.PdhAddCounterW.call_args_list[0].args[1]
    assert caminho_usado == "\\Informações do Processador(_Total)\\% de Desempenho"


def test_leitura_com_dado_invalido_devolve_none():
    """Primeira amostra de um contador de taxa nunca tem valor. Não é erro."""
    falso = _pdh_falso()
    falso.PdhGetFormattedCounterValue.return_value = 0xC0000BC6
    with patch.object(pdh, "_pdh", falso):
        contador = pdh.Contador(2610, 2660, "Processor Information", "% Perf")
        assert contador.ler() is None


def test_leitura_com_coleta_que_falha_devolve_none():
    falso = _pdh_falso()
    with patch.object(pdh, "_pdh", falso):
        contador = pdh.Contador(2610, 2660, "Processor Information", "% Perf")
        falso.PdhCollectQueryData.return_value = 0xC0000BC0
        assert contador.ler() is None


def test_fechar_deixa_o_contador_inoperante():
    with patch.object(pdh, "_pdh", _pdh_falso()):
        contador = pdh.Contador(2610, 2660, "Processor Information", "% Perf")
        contador.fechar()
        assert not contador.ok


def test_primeira_leitura_e_descartada():
    """A amostra de abertura fica a microssegundos da primeira leitura: valor sem sentido."""
    falso = _pdh_falso()
    falso.PdhGetFormattedCounterValue.return_value = 0
    with patch.object(pdh, "_pdh", falso):
        contador = pdh.Contador(2610, 2660, "Processor Information", "% Perf")
        assert contador.ler() is None


def test_segunda_leitura_devolve_o_valor():
    falso = _pdh_falso()

    def formatar(_alca, _formato, _reservado, ponteiro):
        ponteiro._obj.doubleValue = 107.5
        return 0

    falso.PdhGetFormattedCounterValue.side_effect = formatar
    with patch.object(pdh, "_pdh", falso):
        contador = pdh.Contador(2610, 2660, "Processor Information", "% Perf")
        contador.ler()
        assert contador.ler() == 107.5


def test_consulta_e_fechada_quando_nenhum_contador_entra():
    """Senão a alça fica aberta até o processo morrer, justo no PC sem o contador."""
    falso = _pdh_falso(erro_ao_adicionar=0xC0000BB8)
    with patch.object(pdh, "_pdh", falso):
        pdh.Contador(2610, 2660, "Processor Information", "% Perf")
    falso.PdhCloseQuery.assert_called_once()


def test_consulta_nao_e_fechada_quando_o_contador_entra():
    falso = _pdh_falso()
    with patch.object(pdh, "_pdh", falso):
        pdh.Contador(2610, 2660, "Processor Information", "% Perf")
    falso.PdhCloseQuery.assert_not_called()
