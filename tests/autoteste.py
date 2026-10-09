"""Testa o app no navegador (tela de celular). Uso: python tests/autoteste.py docs/index.html"""
import re
import sys
import pathlib
from playwright.sync_api import sync_playwright

html = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'docs/index.html').resolve()
falhas, erros = [], []


def confere(nome, cond, detalhe=''):
    print(('ok    ' if cond else 'FALHA ') + nome + (f'  [{detalhe}]' if detalhe and not cond else ''))
    if not cond:
        falhas.append(nome)


with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={'width': 390, 'height': 844})
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(html.as_uri())
    pg.wait_for_timeout(300)

    rod = pg.inner_text('#rodape')
    m = re.search(r'contas conferidas (\d+)/(\d+)', rod)
    confere('autoteste interno das contas', bool(m) and m.group(1) == m.group(2), rod)

    # vasoativas
    confere('nora padrão 4 amp/250 = 64 mcg/mL', pg.inner_text('#ps-nora').startswith('64 '), pg.inner_text('#ps-nora'))
    pg.fill('input[data-d="nora"][data-k="mlh"]', '12')
    confere('sem peso: pede o peso', pg.inner_text('#t-nora') == 'Informe o peso', pg.inner_text('#t-nora'))
    pg.fill('#peso', '70')
    confere('nora 12 mL/h com 70 kg = 0,18', pg.input_value('input[data-d="nora"][data-k="dose"]') == '0,18')
    confere('nora 0,18 fica verde', 's-ok' in (pg.get_attribute('#fd-nora', 'class') or ''))
    tit = pg.inner_text('#r-nora').replace('\n', ' ')
    confere('nora titulação 6,6 / +3,3 / 65,6 mL/h', all(x in tit for x in ['6,6', '+3,3', '65,6']), tit)
    pg.fill('#peso', '7')
    confere('peso absurdo é recusado', pg.inner_text('#t-nora') == 'Peso fora de faixa: confira', pg.inner_text('#t-nora'))
    pg.fill('#peso', '70')

    # sedação
    pg.click('.tabbar button[data-t="sed"]')
    pg.fill('input[data-d="prop"][data-k="mlh"]', '40')
    confere('propofol 40 mL/h = 95,24', pg.input_value('input[data-d="prop"][data-k="dose"]') == '95,24')
    confere('propofol acima do teto fica vermelho', 's-bad' in (pg.get_attribute('#fd-prop', 'class') or ''))
    confere('propofol mostra o teto', 'Acima do teto (67)' in pg.inner_text('#t-prop'), pg.inner_text('#t-prop'))
    pg.fill('input[data-d="rocu"][data-k="mlh"]', '40')
    confere('rocurônio mostra o lembrete', pg.is_visible('#w-rocu'))

    # ventilação
    pg.click('.tabbar button[data-t="vent"]')
    confere('ventilação começa sem resultados', pg.is_hidden('#mec_res') and pg.is_hidden('#gas_res'))
    pg.click('#v_sexo button[data-v="M"]')
    for k, v in [('v_alt', '180'), ('v_vc', '450'), ('v_peep', '10'), ('v_plato', '23'), ('v_pico', '35'),
                 ('v_fluxo', '60'), ('v_po2', '69'), ('v_fio2', '60'), ('v_pco2', '60')]:
        pg.fill('#' + k, v)
    vt = pg.inner_text('#vt_res').replace('\n', ' ')
    mec = pg.inner_text('#mec_res').replace('\n', ' ')
    gas = pg.inner_text('#gas_res').replace('\n', ' ')
    confere('peso predito 75,1 e VC 451/526/601', all(x in vt for x in ['75,1', '451', '526', '601']), vt)
    confere('driving 13, Cst 34,6, Rva 12,0, tau 0,42', all(x in mec for x in ['13', '34,6', '12,0', '0,42']), mec)
    confere('P/F 115 e A-a 248', all(x in gas for x in ['115', '248']), gas)

    # assincronias
    pg.click('.tabbar button[data-t="asinc"]')
    confere('8 assincronias', pg.locator('#l-asinc .ac').count() == 8)
    pg.click('#filtros button[data-f="ciclagem"]')
    confere('filtro ciclagem mostra 2', pg.locator('#l-asinc .ac:not(.hide)').count() == 2)
    pg.click('#filtros button[data-f="todas"]')
    pg.click('#a-duplo .ac-h')
    confere('abrir mostra desenho e resolução', pg.locator('#a-duplo [data-onda] svg').count() == 1 and pg.is_visible('#a-duplo .resol'))

    # Glasgow
    pg.click('.tabbar button[data-t="gcs"]')
    for k, v in [('O', '3'), ('V', '4'), ('M', '6')]:
        pg.click(f'#g_linhas [data-g="{k}"] button[data-v="{v}"]')
    confere('Glasgow O3 V4 M6 = 13', pg.inner_text('#g_tot') == '13')

    # novo paciente
    pg.click('#novo')
    confere('novo paciente zera o peso', pg.input_value('#peso') == '')
    nav.close()

confere('sem erro de JavaScript', not erros, '; '.join(erros))
print()
print('RESULTADO:', 'tudo certo' if not falhas else f'{len(falhas)} falha(s)')
sys.exit(1 if falhas else 0)
