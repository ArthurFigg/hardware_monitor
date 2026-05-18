import pytest
import customtkinter as ctk


@pytest.fixture(scope="session")
def raiz():
    app = ctk.CTk()
    app.withdraw()
    yield app
    app.destroy()
