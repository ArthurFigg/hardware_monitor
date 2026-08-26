"""Acesso aos contadores de desempenho do Windows (PDH), sem dependência externa.

Só `ctypes`, da biblioteca padrão. A consulta é aberta uma vez e reaproveitada: abrir
uma consulta por leitura custaria caro num ciclo de um segundo.

O nome do contador é resolvido pelo **número**, não pelo texto. `Processor Information`
vira "Informações do Processador" num Windows em português, e um app distribuído para
outras pessoas não pode depender do idioma de quem instalou. O número é o mesmo em
qualquer lugar. Quando a tradução não vier, cai para o nome em inglês — que é o que a
própria API aceita como alternativa.

Nada aqui levanta exceção para quem chama: contador ausente, consulta que não abre ou
valor absurdo devolvem `None`, e o cartão correspondente some da tela.
"""

import ctypes
from ctypes import wintypes

# Índices dos objetos e contadores, iguais em qualquer idioma (chave Perflib\009).
IDX_PROCESSOR_INFORMATION = 2610
IDX_PROCESSOR_PERFORMANCE = 2660

_PDH_FMT_DOUBLE = 0x00000200
_ERRO_SUCESSO = 0

# A primeira coleta de um contador de taxa nunca tem valor: ele precisa de duas
# amostras para calcular a diferença. Não é falha, é o primeiro ciclo.
_PDH_INVALID_DATA = 0xC0000BC6
_PDH_CSTATUS_INVALID_DATA = 0xC0000BBA

_TAMANHO_NOME = 1024


class _ValorContador(ctypes.Structure):
    _fields_ = [
        ("CStatus", wintypes.DWORD),
        ("doubleValue", ctypes.c_double),
    ]


def _carregar():
    try:
        return ctypes.WinDLL("pdh.dll")
    except (OSError, AttributeError):
        return None


_pdh = _carregar()


def disponivel() -> bool:
    return _pdh is not None


def nome_por_indice(indice: int) -> str | None:
    """Nome traduzido de um objeto ou contador, a partir do número dele."""
    if _pdh is None:
        return None
    buffer = ctypes.create_unicode_buffer(_TAMANHO_NOME)
    tamanho = wintypes.DWORD(_TAMANHO_NOME)
    resultado = _pdh.PdhLookupPerfNameByIndexW(
        None, wintypes.DWORD(indice), buffer, ctypes.byref(tamanho)
    )
    if resultado != _ERRO_SUCESSO or not buffer.value:
        return None
    return buffer.value


def caminho(objeto: str, contador: str, instancia: str = "_Total") -> str:
    if instancia:
        return f"\\{objeto}({instancia})\\{contador}"
    return f"\\{objeto}\\{contador}"


class Contador:
    """Uma consulta PDH aberta e mantida, com um contador dentro.

    Construir não levanta erro nem quando o contador não existe: `.ok` diz se a leitura
    vai funcionar, e `ler()` devolve `None` enquanto não funcionar.
    """

    def __init__(
        self,
        indice_objeto: int,
        indice_contador: int,
        objeto_ingles: str,
        contador_ingles: str,
        instancia: str = "_Total",
    ):
        self._consulta = None
        self._contador = None
        self._primeira_leitura = True
        self.ok = False
        try:
            self._abrir(
                indice_objeto,
                indice_contador,
                objeto_ingles,
                contador_ingles,
                instancia,
            )
        except OSError:
            self.ok = False

    def _abrir(
        self, indice_objeto, indice_contador, objeto_ingles, contador_ingles, instancia
    ) -> None:
        if _pdh is None:
            return

        consulta = wintypes.HANDLE()
        if _pdh.PdhOpenQueryW(None, 0, ctypes.byref(consulta)) != _ERRO_SUCESSO:
            return
        self._consulta = consulta

        objeto = nome_por_indice(indice_objeto) or objeto_ingles
        contador = nome_por_indice(indice_contador) or contador_ingles

        for caminho_tentado in (
            caminho(objeto, contador, instancia),
            caminho(objeto_ingles, contador_ingles, instancia),
        ):
            alca = wintypes.HANDLE()
            resultado = _pdh.PdhAddCounterW(
                consulta, caminho_tentado, 0, ctypes.byref(alca)
            )
            if resultado == _ERRO_SUCESSO:
                self._contador = alca
                self.ok = True
                break

        if not self.ok:
            # Nada foi adicionado: a consulta não serve para nada e ninguém mais tem
            # referência a ela para fechar depois.
            _pdh.PdhCloseQuery(consulta)
            self._consulta = None
            return

        # Primeira amostra do par que todo contador de taxa exige.
        _pdh.PdhCollectQueryData(consulta)

    def ler(self) -> float | None:
        """Valor atual, ou None enquanto não houver leitura válida.

        A primeira chamada é sempre descartada. Um contador de taxa calcula a diferença
        entre duas amostras, e a amostra de abertura fica a microssegundos desta — o
        valor sai sem sentido (medido: 43% num processador que estava em 107%). Não dá
        para distinguir isso de uma queda real, então a saída é não olhar.
        """
        if not self.ok or _pdh is None:
            return None
        if self._primeira_leitura:
            self._primeira_leitura = False
            try:
                _pdh.PdhCollectQueryData(self._consulta)
            except OSError:
                return None
            return None
        try:
            return self._ler_bruto()
        except OSError:
            # Alça invalidada, contador removido no meio do caminho. É leitura que não
            # deu, não motivo para derrubar a tela.
            return None

    def _ler_bruto(self) -> float | None:
        if _pdh.PdhCollectQueryData(self._consulta) != _ERRO_SUCESSO:
            return None

        valor = _ValorContador()
        resultado = _pdh.PdhGetFormattedCounterValue(
            self._contador, _PDH_FMT_DOUBLE, None, ctypes.byref(valor)
        )
        if resultado & 0xFFFFFFFF in (_PDH_INVALID_DATA, _PDH_CSTATUS_INVALID_DATA):
            return None
        if resultado != _ERRO_SUCESSO:
            return None
        return valor.doubleValue

    def fechar(self) -> None:
        if _pdh is not None and self._consulta is not None:
            _pdh.PdhCloseQuery(self._consulta)
        self._consulta = None
        self._contador = None
        self.ok = False
