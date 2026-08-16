from nginx_gen.generator import parse_spec_file, render_nginx_config, render_caddy_config


def test_parse_and_render_nginx(tmp_path):
    spec_content = """
    version: "1.0"
    vhosts:
      - server_name: "test.dev"
        listen_port: 80
        locations:
          - path: "/"
            proxy_pass: "http://localhost:3000"
            websocket: true
    """
    spec_file = tmp_path / "spec.yaml"
    spec_file.write_text(spec_content)

    spec = parse_spec_file(str(spec_file))
    nginx_conf = render_nginx_config(spec)

    assert "server_name test.dev;" in nginx_conf
    assert "proxy_pass http://localhost:3000;" in nginx_conf
    assert "proxy_set_header Upgrade $http_upgrade;" in nginx_conf
