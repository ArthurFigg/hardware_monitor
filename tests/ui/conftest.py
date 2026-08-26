import customtkinter as ctk
import pytest


@pytest.fixture(scope="session")
def raiz():
    app = ctk.CTk()
    app.withdraw()
    yield app
    app.destroy()
