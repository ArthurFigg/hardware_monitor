from unittest.mock import patch

from hardware.thresholds import Status
from notifications.manager import GerenciadorNotificacoes
from recursos import CAUSA_DESGASTE, CPU, DISCO, RAM, TEMPERATURA


def test_notifica_ao_entrar_em_alerta():
    gerenciador = GerenciadorNotificacoes(CPU)
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.ALERTA)
        mock_notify.assert_called_once()


def test_nao_notifica_no_estado_normal():
    gerenciador = GerenciadorNotificacoes(CPU)
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.NORMAL)
        mock_notify.assert_not_called()


def test_nao_notifica_no_estado_atencao():
    gerenciador = GerenciadorNotificacoes(CPU)
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.ATENCAO)
        mock_notify.assert_not_called()


def test_nao_notifica_duas_vezes_seguidas_em_alerta():
    gerenciador = GerenciadorNotificacoes(CPU)
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.ALERTA)
        gerenciador.processar(Status.ALERTA)
        mock_notify.assert_called_once()


def test_notifica_novamente_apos_recuperacao():
    gerenciador = GerenciadorNotificacoes(CPU)
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.ALERTA)
        gerenciador.processar(Status.NORMAL)
        gerenciador.processar(Status.ALERTA)
        assert mock_notify.call_count == 2


def test_titulo_da_cpu():
    with patch("notifications.manager.notification.notify") as mock_notify:
        GerenciadorNotificacoes(CPU).processar(Status.ALERTA)
        assert mock_notify.call_args.kwargs["title"] == "CPU em sobrecarga"


def test_titulo_da_ram():
    with patch("notifications.manager.notification.notify") as mock_notify:
        GerenciadorNotificacoes(RAM).processar(Status.ALERTA)
        assert mock_notify.call_args.kwargs["title"] == "Memória em sobrecarga"


def test_titulo_do_disco():
    with patch("notifications.manager.notification.notify") as mock_notify:
        GerenciadorNotificacoes(DISCO).processar(Status.ALERTA)
        assert mock_notify.call_args.kwargs["title"] == "Espaço em disco acabando"


def test_titulo_da_temperatura():
    with patch("notifications.manager.notification.notify") as mock_notify:
        GerenciadorNotificacoes(TEMPERATURA).processar(Status.ALERTA)
        assert mock_notify.call_args.kwargs["title"] == "Temperatura crítica"


def test_temperatura_nao_fala_de_memoria():
    with patch("notifications.manager.notification.notify") as mock_notify:
        GerenciadorNotificacoes(TEMPERATURA).processar(Status.ALERTA)
        assert "memória" not in mock_notify.call_args.kwargs["message"]


def test_corpo_da_cpu_nomeia_o_programa():
    with patch("notifications.manager.notification.notify") as mock_notify:
        GerenciadorNotificacoes(CPU).processar(
            Status.ALERTA, programa="chrome.exe", valor=78.0
        )
        assert "chrome.exe está usando 78%" in mock_notify.call_args.kwargs["message"]


def test_corpo_sem_programa_nao_tem_lacuna():
    with patch("notifications.manager.notification.notify") as mock_notify:
        GerenciadorNotificacoes(CPU).processar(Status.ALERTA)
        mensagem = mock_notify.call_args.kwargs["message"]
        assert "{" not in mensagem
        assert mensagem.strip()


def test_disco_por_desgaste_usa_o_outro_texto():
    with patch("notifications.manager.notification.notify") as mock_notify:
        GerenciadorNotificacoes(DISCO).processar(Status.ALERTA, causa=CAUSA_DESGASTE)
        assert mock_notify.call_args.kwargs["title"] == "Disco com sinais de desgaste"
