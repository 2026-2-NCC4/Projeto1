# O fluxo completo (login/cadastro + dashboard) fica em main.py.
# Este arquivo apenas o executa, para quem ainda roda "streamlit run app.py".
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("main.py")), run_name="__main__")
