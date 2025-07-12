#!/usr/bin/env python
"""
Gestion de l'API et de la documentation Swagger avec Flask-RESTX.
"""

# Imports from stdlib
from flask import jsonify, render_template_string

# Imports from external libraries
from flask_jwt_extended.exceptions import NoAuthorizationError

# Import from local code
from core.server.json_encoder import normalize_json_error
from core.server.views import Api

# Définition des authorizations pour Swagger
authorizations = {
    "BearerAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
    }
}


class BoleroAPI:
    """Classe responsable de la gestion de l'API avec Flask-RESTX"""

    def __init__(self, app):
        self._setup_routes(app)

        self.api = Api(
            app,
            version="1.0",
            title="Boléro API",
            description="Documentation interactive de l'API Boléro",
            doc="/documentation",
            authorizations=authorizations,
            security="BearerAuth",
        )

    def _setup_routes(self, app):
        """Ajoute les routes nécessaires pour la documentation Swagger"""

        @app.route("/swagger.json")
        def swagger_json():
            schema = self.api.__schema__
            schema["basePath"] = app.config.api_prefix
            return jsonify(schema)

        @app.route("/documentation")
        def custom_swagger_ui():
            return render_template_string(
                f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Boléro API Documentation</title>
                    <link rel="stylesheet" href="{app.config.api_prefix}/swaggerui/swagger-ui.css">
                </head>
                <body>
                    <div id="swagger-ui"></div>
                    <script src="{app.config.api_prefix}/swaggerui/swagger-ui-bundle.js"></script>
                    <script src="{app.config.api_prefix}/swaggerui/swagger-ui-standalone-preset.js"></script>
                    <script>
                        SwaggerUIBundle({{
                            url: "{app.config.api_prefix}/swagger.json",
                            dom_id: "#swagger-ui",
                            presets: [
                                SwaggerUIBundle.presets.apis,
                                SwaggerUIStandalonePreset
                            ],
                            layout: "BaseLayout"
                        }});
                    </script>
                </body>
                </html>
                """
            )
