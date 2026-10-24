import unittest
import tempfile
import os
import gc
from pathlib import Path
import app

class ProfissaTests(unittest.TestCase):
    def setUp(self):
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        f.close()
        self.dbfile = f.name
        self.old = app.DB_PATH
        app.DB_PATH = Path(self.dbfile)
        app.app.config.update(TESTING=True, SECRET_KEY="test")
        app.init_db()
        self.client = app.app.test_client()

    def tearDown(self):
        self.client = None
        app.DB_PATH = self.old
        gc.collect()
        for suffix in ("", "-journal", "-wal", "-shm"):
            path = self.dbfile + suffix
            if os.path.exists(path):
                try:
                    os.unlink(path)
                except PermissionError:
                    pass

    def register(self):
        return self.client.post("/cadastro", data={
            "name": "Pessoa Teste",
            "email": "teste@example.com",
            "password": "senha-forte-123",
            "profession": "Prestador de serviços"
        }, follow_redirects=True)

    def test_home(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_register_and_dashboard(self):
        response = self.register()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Suas ferramentas", response.data)

    def test_login_required(self):
        self.assertEqual(self.client.get("/painel").status_code, 302)

    def test_record_create_and_delete(self):
        self.register()
        response = self.client.post("/modulo/Clientes", data={
            "title": "Cliente teste",
            "detail": "Contato",
            "notes": "Nota"
        }, follow_redirects=True)
        self.assertIn(b"Cliente teste", response.data)
        response = self.client.post("/registro/1/excluir", follow_redirects=True)
        self.assertNotIn(b"Cliente teste", response.data)

if __name__ == "__main__":
    unittest.main()
