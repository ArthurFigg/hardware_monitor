from hardware.thresholds import Status
from ui.components.semaphore import CORES, Semaforo


def test_semaforo_status_inicial_normal(raiz):
    semaforo = Semaforo(raiz)
    assert semaforo.status_atual == Status.NORMAL


def test_semaforo_atualizar_para_atencao(raiz):
    semaforo = Semaforo(raiz)
    semaforo.atualizar(Status.ATENCAO)
    assert semaforo.status_atual == Status.ATENCAO


def test_semaforo_atualizar_para_alerta(raiz):
    semaforo = Semaforo(raiz)
    semaforo.atualizar(Status.ALERTA)
    assert semaforo.status_atual == Status.ALERTA


def test_semaforo_volta_para_normal(raiz):
    semaforo = Semaforo(raiz)
    semaforo.atualizar(Status.ALERTA)
    semaforo.atualizar(Status.NORMAL)
    assert semaforo.status_atual == Status.NORMAL


def test_semaforo_cores_distintas():
    assert len(set(CORES.values())) == 3
