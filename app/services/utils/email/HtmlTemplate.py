import re
from pathlib import Path

class HtmlTemplate:
    PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")

    @staticmethod
    def render(filename: str, data: dict = {}, templates_path: Path = Path(__file__).parent / "templates") -> str:
        """
        Renderiza una plantilla HTML con valores de un diccionario.
        - `filename`: nombre del archivo HTML
        - `data`: diccionario con variables a reemplazar
        - `templates_path`: carpeta donde están las plantillas
        """
        file_path = templates_path / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Plantilla no encontrada: {file_path}")

        html = file_path.read_text(encoding="utf-8")

        def replacer(match):
            key = match.group(1)
            return str(data.get(key, ""))

        return HtmlTemplate.PATTERN.sub(replacer, html)