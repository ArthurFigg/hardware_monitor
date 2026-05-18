from unittest.mock import patch

from hardware.thresholds import Status
from notifications.manager import GerenciadorNotificacoes


def test_notifica_ao_entrar_em_alerta():
    gerenciador = GerenciadorNotificacoes()
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.ALERTA)
        mock_notify.assert_called_once()


def test_nao_notifica_no_estado_normal():
    gerenciador = GerenciadorNotificacoes()
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.NORMAL)
        mock_notify.assert_not_called()


def test_nao_notifica_no_estado_atencao():
    gerenciador = GerenciadorNotificacoes()
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.ATENCAO)
        mock_notify.assert_not_called()


def test_nao_notifica_duas_vezes_seguidas_em_alerta():
    gerenciador = GerenciadorNotificacoes()
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.ALERTA)
        gerenciador.processar(Status.ALERTA)
        mock_notify.assert_called_once()


def test_notifica_novamente_apos_recuperacao():
    gerenciador = GerenciadorNotificacoes()
    with patch("notifications.manager.notification.notify") as mock_notify:
        gerenciador.processar(Status.ALERTA)
        gerenciador.processar(Status.NORMAL)
        gerenciador.processar(Status.ALERTA)
        assert mock_notify.call_count == 2
