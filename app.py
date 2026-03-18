import streamlit as st
from fpdf import FPDF
import datetime
from num2words import num2words

# --- BANCO DE DADOS DE CUSTOS ---
dados_custo = {
    "limite": [70000, 150000, 300000, 450000, 600000, 850000, 1000000, 3000000],
    12: [2500.0, 2917.8, 11671.2, 14589.0, 17506.8, 23342.4, 26260.2, 29178.0],
    24: [3890.4, 5835.6, 11671.2, 14589.0, 17506.8, 23342.4, 26260.2, 29178.0],
    36: [5835.6, 8753.4, 11671.2, 14589.0, 17506.8, 23342.4, 26260.2, 29178.0],
    48: [7780.8, 11671.2, 15561.6, 19452.0, 23342.4, 31123.2, 35013.6, 38904.0],
    60: [9726.0, 14589.0, 19452.0, 24315.0, 29178.0, 38904.0, 43767.0, 48630.0]
}

def formatar_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def valor_por_extenso(valor):
    inteiro = int(valor)
    centavos = int(round((valor - inteiro) * 100))
    extenso = num2words(inteiro, lang='pt_BR') + " reais"
    if centavos > 0:
        extenso += " e " + num2words(centavos, lang='pt_BR') + " centavos"
    return extenso

st.title("📄 Gerador de Proposta Dr. Fiscal")
razao_social = st.text_input("Razão Social do Cliente")
valor_credito = st.number_input("Faixa de Crédito (R$)", min_value=0.0, format="%.2f")
meses = st.selectbox("Meses", [12, 24, 36, 48, 60])
percentual_unidade = st.sidebar.slider("Margem Unidade (%)", 0, 100, 25) / 100
qtd_parcelas = st.number_input("Parcelas", 1, 12, 5)

if st.button("GERAR PROPOSTA COM CAPA"):
    # Cálculos
    idx = next((i for i, lim in enumerate(dados_custo["limite"]) if valor_credito <= lim), -1)
    total = dados_custo[meses][idx] / (1 - percentual_unidade)
    parc = total / qtd_parcelas
    hoje = datetime.date.today().strftime("%d/%m/%Y")

    pdf = FPDF()
    
    # Fontes
    try:
        pdf.add_font('AmpleSoft', '', 'AmpleSoft-Regular.ttf', uni=True)
        pdf.add_font('AmpleSoft', 'B', 'AmpleSoft-Bold.ttf', uni=True)
        f_reg, f_bold = 'AmpleSoft', 'AmpleSoft'
    except:
        f_reg, f_bold = 'Arial', 'Arial'

    # --- PÁGINA 1: CAPA VERMELHA ---
    pdf.add_page()
    pdf.set_fill_color(218, 41, 28) # Vermelho Dr. Fiscal
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Logo Branco na Capa (Ativar se houver o arquivo)
    # pdf.image('logo_branco.png', x=85, y=50, w=40) 

    pdf.set_text_color(255, 255, 255)
    pdf.set_y(120)
    pdf.set_font(f_bold, 'B', 24)
    pdf.multi_cell(0, 12, "PROPOSTA DE PRESTAÇÃO\nDE SERVIÇOS - RPC", align='C')
    
    pdf.ln(20)
    pdf.set_font(f_reg, '', 14)
    pdf.cell(0, 10, f"Preparado para: {razao_social.upper()}", ln=True, align='C')
    pdf.cell(0, 10, f"Data: {hoje}", ln=True, align='C')

    # --- PÁGINA 2: CONTEÚDO TÉCNICO ---
    pdf.add_page()
    pdf.set_text_color(0, 0, 0) # Volta para preto
    pdf.set_margins(20, 20, 20)
    
    # Tabela Inicial
    pdf.set_font(f_bold, 'B', 10)
    pdf.cell(45, 10, " EMPRESA", 1)
    pdf.set_font(f_reg, '', 10)
    pdf.cell(0, 10, f" {razao_social.upper()}", 1, ln=True)
    pdf.cell(45, 10, " SERVIÇO", 1)
    pdf.cell(0, 10, " Retificações Das Declarações e Compensações Mensais", 1, ln=True)

    # Texto Jurídico
    pdf.ln(10)
    pdf.set_font(f_reg, '', 10)
    pdf.multi_cell(0, 6, f"A {razao_social}, após a identificação das oportunidades no Diagnóstico Tributário da Dr. Fiscal, verificou a necessidade de retificação das informações constantes da DCTF, ECF e EFD Contribuições.")
    
    # Investimento
    pdf.ln(10)
    pdf.set_font(f_bold, 'B', 11)
    pdf.cell(0, 10, "Investimento", ln=True)
    pdf.set_font(f_reg, '', 10)
    pdf.multi_cell(0, 6, f"Remuneração: {formatar_br(total)} ({valor_por_extenso(total)}).")
    pdf.cell(0, 7, f"Pagamento: {int(qtd_parcelas)} parcelas mensais de {formatar_br(parc)}.", ln=True)
    pdf.cell(0, 7, "Prazo: 60 dias.", ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
    st.download_button("📥 BAIXAR PROPOSTA COM CAPA", data=pdf_bytes, file_name="Proposta_Completa.pdf")