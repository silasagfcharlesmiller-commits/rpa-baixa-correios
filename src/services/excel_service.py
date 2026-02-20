import os
from datetime import datetime
from openpyxl import Workbook

def salvar_codigos_em_xlsx(codigos):
    base_dir = os.getcwd()
    pasta = os.path.join(base_dir, "baixados_xlsx")
    os.makedirs(pasta, exist_ok=True)

    datahora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for i in range(0, len(codigos), 50):
        lote = codigos[i:i+50]
        indice = (i // 50) + 1

        caminho = os.path.join(
            pasta,
            f"baixados_{datahora}_{indice:03d}.xlsx"
        )

        wb = Workbook()
        ws = wb.active
        ws.title = "Baixados"
        ws.append(["Código de Rastreio", "Data/Hora"])

        for codigo in lote:
            ws.append([codigo, datetime.now().strftime("%d/%m/%Y %H:%M:%S")])

        wb.save(caminho)