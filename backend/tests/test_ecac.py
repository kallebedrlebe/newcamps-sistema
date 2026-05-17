"""
Testes do módulo e-CAC — DCTFWeb eSocial.

Testes de API usam as fixtures do conftest.py (banco SQLite em memória).
Testes de automação usam mocks do Selenium — sem portal real.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.models.empresa import Empresa
from tests.conftest import TestSession


# ── Fixture: empresa com credenciais gov.br ─────────────────────────────────

@pytest.fixture
def empresa_com_creds(admin_token):
    db = TestSession()
    emp = Empresa(
        razao_social="eSocial Corp Ltda",
        cnpj="11222333000181",
        credenciais={"govbr_cpf": "12345678901", "govbr_senha": "senha_govbr"},
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    db.close()
    return emp.id


# ── Testes de validação do endpoint ────────────────────────────────────────

class TestDctfWebEndpoint:
    def test_competencia_invalida_formato(self, client, admin_token, empresa_com_creds):
        resp = client.post(
            "/ecac/dctfweb/esocial",
            json={"empresa_id": empresa_com_creds, "competencia": "2024-01"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 422

    def test_competencia_mes_invalido(self, client, admin_token, empresa_com_creds):
        resp = client.post(
            "/ecac/dctfweb/esocial",
            json={"empresa_id": empresa_com_creds, "competencia": "13/2024"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 422

    def test_competencia_anterior_esocial(self, client, admin_token, empresa_com_creds):
        resp = client.post(
            "/ecac/dctfweb/esocial",
            json={"empresa_id": empresa_com_creds, "competencia": "01/2015"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 422

    def test_cria_tarefa_com_competencia_valida(self, client, admin_token, empresa_com_creds):
        with patch("app.services.ecac_service._executar_dctfweb"):
            resp = client.post(
                "/ecac/dctfweb/esocial",
                json={"empresa_id": empresa_com_creds, "competencia": "01/2024"},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        assert resp.status_code == 202
        data = resp.json()
        assert data["tipo"] == "ECAC_DCTFWEB_ESOCIAL"
        assert data["status"] == "PENDENTE"
        assert data["parametros"]["competencia"] == "01/2024"

    def test_sem_autenticacao_retorna_401(self, client, empresa_com_creds):
        resp = client.post(
            "/ecac/dctfweb/esocial",
            json={"empresa_id": empresa_com_creds, "competencia": "01/2024"},
        )
        assert resp.status_code == 401

    def test_com_codigo_mfa(self, client, admin_token, empresa_com_creds):
        with patch("app.services.ecac_service._executar_dctfweb"):
            resp = client.post(
                "/ecac/dctfweb/esocial",
                json={"empresa_id": empresa_com_creds, "competencia": "03/2024", "codigo_mfa": "123456"},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        assert resp.status_code == 202
        assert resp.json()["parametros"]["codigo_mfa"] == "123456"


# ── Testes da automação (com mock do Selenium) ──────────────────────────────

class TestDctfWebAutomacao:
    def test_extrair_dados_darf_regex(self):
        from automation.ecac.dctfweb import _extrair_valor, _extrair_regex, _extrair_codigo_barras

        texto = """
        Código da Receita: 2484
        Valor do Principal: 15.000,00
        Multa: 0,00
        Juros: 0,00
        Valor Total: 15.000,00
        Vencimento: 20/02/2024
        Nosso Número: 9999999999
        10497.24849 99999.999990 99999.999990 1 10000000150000
        """
        assert _extrair_regex(texto, r"C[oó]digo\s*(?:da\s*)?Receita[:\s]+(\d{4})", "") == "2484"
        assert _extrair_valor(texto, r"Valor\s*Total[:\s]+([\d.,]+)") == 15000.0
        assert _extrair_regex(texto, r"(?:Data\s*de\s*)?Vencimento[:\s]+(\d{2}/\d{2}/\d{4})", "") == "20/02/2024"
        assert "10497" in _extrair_codigo_barras(texto)

    def test_localizar_linha_esocial_por_texto(self):
        from automation.ecac.dctfweb import _localizar_linha_esocial
        from selenium.webdriver.support.ui import WebDriverWait

        driver = MagicMock()
        linha_esocial = MagicMock()
        linha_esocial.text = "01/2024  eSocial  Ativa  R$ 15.000,00"
        linha_outro = MagicMock()
        linha_outro.text = "01/2024  FGTS  Ativa  R$ 500,00"
        driver.find_elements.return_value = [linha_outro, linha_esocial]

        wait = MagicMock(spec=WebDriverWait)
        wait.until.return_value = True

        assert _localizar_linha_esocial(driver, wait) is linha_esocial

    def test_localizar_linha_esocial_por_codigo(self):
        from automation.ecac.dctfweb import _localizar_linha_esocial
        from selenium.webdriver.support.ui import WebDriverWait

        driver = MagicMock()
        linha = MagicMock()
        linha.text = "01/2024  2484  Transmitida  R$ 8.500,00"
        driver.find_elements.return_value = [linha]

        wait = MagicMock(spec=WebDriverWait)
        wait.until.return_value = True

        assert _localizar_linha_esocial(driver, wait) is linha

    def test_sem_declaracao_esocial_retorna_none(self):
        from automation.ecac.dctfweb import _localizar_linha_esocial
        from selenium.webdriver.support.ui import WebDriverWait

        driver = MagicMock()
        linha = MagicMock()
        linha.text = "01/2024  IRPJ  Ativa  R$ 1.000,00"
        driver.find_elements.return_value = [linha]

        wait = MagicMock(spec=WebDriverWait)
        wait.until.return_value = True

        assert _localizar_linha_esocial(driver, wait) is None

    def test_validacao_competencia_formato(self):
        from app.routers.ecac import _validar_competencia
        from fastapi import HTTPException

        _validar_competencia("01/2024")   # OK
        _validar_competencia("12/2023")   # OK

        with pytest.raises(HTTPException):
            _validar_competencia("2024-01")
        with pytest.raises(HTTPException):
            _validar_competencia("13/2024")
        with pytest.raises(HTTPException):
            _validar_competencia("01/2015")

    def test_extrair_valor_formato_brasileiro(self):
        from automation.ecac.dctfweb import _extrair_valor
        assert _extrair_valor("Total: 1.234,56", r"Total:\s*([\d.,]+)") == 1234.56
        assert _extrair_valor("Total: 500,00", r"Total:\s*([\d.,]+)") == 500.0
        assert _extrair_valor("Sem valor aqui", r"Total:\s*([\d.,]+)") is None
