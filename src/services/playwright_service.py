from playwright.sync_api import sync_playwright

def gerar_baixa(codigos, usuario, senha):
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False, slow_mo=60)
        pagina = navegador.new_page()

        pagina.goto("https://sroweb.correios.com.br/app/index.php", wait_until="networkidle")
        pagina.fill('input[name="username"]', usuario)
        pagina.fill('input[name="password"]', senha)
        pagina.click('button[type="submit"]')
        pagina.wait_for_timeout(3500)

        pagina.goto(
            "https://sroweb.correios.com.br/app/entregainterna/baixainterna/",
            wait_until="networkidle"
        )

        pagina.select_option("#selMotivoBaixa", value="1")
        campo = "#txtObjetoDocumento"
        pagina.wait_for_selector(campo)

        for codigo in codigos:
            pagina.fill(campo, codigo)
            pagina.keyboard.press("Enter")
            pagina.wait_for_timeout(250)

        pagina.keyboard.press("F6")
        pagina.wait_for_timeout(2000)