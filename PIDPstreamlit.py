import streamlit as st
import pandas as pd

# --- Configurações Iniciais da Página ---
st.set_page_config(
    page_title="Sintonia PID: ZN (Acesso Web)",
    layout="wide",
)

st.title("🔧 Sintonia de Malhas PID - Método Ziegler-Nichols (Web)")
st.markdown("Acesse de qualquer dispositivo para calcular os parâmetros de sintonia.")

# --- Estrutura de Abas ---
tab_sintonia, tab_ajuda = st.tabs(["⚙️ Sintonia (Cálculo)", "ℹ️ Ajuda / Como Usar"])

# ===================================================================
# CONTEÚDO DA ABA 1: SINTONIA (Cálculo)
# ===================================================================

with tab_sintonia:
    st.header("1. Coleta de Dados do Processo (Curva de Reação)")
    
    st.info("Siga as instruções na aba 'Ajuda' para coletar os valores de ΔMV, ΔPV, L e T.")

    # Colunas para Inputs
    col_mv, col_pv = st.columns(2)

    with col_mv:
        st.subheader("Entrada (Ação de Controle)")
        delta_mv = st.number_input(
            "Variação na Saída do Controlador (ΔMV, %):",
            min_value=0.01,
            value=10.0,
            step=1.0,
            format="%f",
            key="delta_mv_web"
        )

    with col_pv:
        st.subheader("Saída (Variável de Processo)")
        delta_pv = st.number_input(
            "Variação Final da PV (ΔPV):",
            min_value=0.01,
            value=5.0,
            step=0.1,
            format="%f",
            key="delta_pv_web"
        )

    st.divider()

    st.header("2. Identificação dos Parâmetros do Modelo")

    col_l, col_t = st.columns(2)

    with col_l:
        L = st.number_input(
            "Tempo Morto / Atraso (L, em Segundos):",
            min_value=0.01,
            value=5.0,
            step=0.1,
            format="%f",
            key="L_web"
        )

    with col_t:
        T = st.number_input(
            "Constante de Tempo (T, em Segundos):",
            min_value=0.01,
            value=20.0,
            step=0.1,
            format="%f",
            key="T_web"
        )
    
    st.divider()
    
    # Botão e Lógica de Cálculo
    if st.button("Calcular Parâmetros ZIEGLER-NICHOLS", type="primary"):
        if delta_pv <= 0 or delta_mv <= 0 or L <= 0 or T <= 0:
            st.error("🚨 Todos os valores de ΔMV, ΔPV, L e T devem ser maiores que zero.")
        else:
            try:
                # 1. Cálculo do Ganho do Processo (K)
                K = delta_pv / delta_mv
                
                st.header("✅ 3. Resultados da Sintonia")
                st.markdown(f"### Parâmetros do Modelo FOPTD")
                st.markdown(f"**Ganho do Processo (K):** `{K:.4f}`")
                st.markdown(f"**Tempo Morto (L):** `{L:.2f}` s")
                st.markdown(f"**Constante de Tempo (T):** `{T:.2f}` s")
                
                st.subheader("Parâmetros do Controlador (Tabela de Ziegler-Nichols)")

                # 2. Cálculo dos Parâmetros PID por ZN
                Kp_p = T / (K * L)
                Kp_pi = 0.9 * T / (K * L)
                Ti_pi = 3.33 * L
                Kp_pid = 1.2 * T / (K * L)
                Ti_pid = 2.0 * L
                Td_pid = 0.5 * L
                
                # 3. Exibição dos Resultados em Tabela
                dados = {
                    "Controlador": ["P (Proporcional)", "PI (Prop.-Integral)", "PID (Prop.-Int.-Der.)"],
                    "Kp (Ganho Proporcional)": [f"{Kp_p:.4f}", f"{Kp_pi:.4f}", f"{Kp_pid:.4f}"],
                    "Ti (Tempo Integral em Segundos)": ["-", f"{Ti_pi:.2f}", f"{Ti_pid:.2f}"],
                    "Td (Tempo Derivativo em Segundos)": ["-", "-", f"{Td_pid:.2f}"],
                }
                
                df_resultados = pd.DataFrame(dados)
                st.dataframe(df_resultados, use_container_width=True, hide_index=True)
                
                st.warning("""
                **NOTA SOBRE UNIDADES:** O controlador pode usar diferentes formatos. Verifique o manual para a conversão:
                * **Ki (Ganho Integral):** Kp / Ti
                * **Kd (Ganho Derivativo):** Kp * Td
                """)
                
            except Exception as e:
                st.error(f"Ocorreu um erro no cálculo: {e}")

# ===================================================================
# CONTEÚDO DA ABA 2: AJUDA / COMO USAR
# ===================================================================
with tab_ajuda:
    st.header("📝 Procedimento Ziegler-Nichols (Malha Aberta)")
    
    st.subheader("Passo 1: Preparação do Teste")
    st.markdown("""
    1.  **Modo Manual:** Coloque o seu controlador (CLP, etc.) em modo **MANUAL**.
    2.  **Estabilização:** Mantenha a saída (**MV**) estável e aguarde a Variável de Processo (**PV**) também estabilizar.
    """)

    st.subheader("Passo 2: Execução do Degrau e Coleta de Variações")
    st.markdown("""
    1.  **Aplique o Degrau:** Mude a **MV** rapidamente (ex: de 40% para 50%).
    2.  **ΔMV (Variação da MV):** É a diferença entre o valor final e inicial da MV (ex: 10%). Insira este valor no campo **ΔMV**.
    3.  **ΔPV (Variação da PV):** Aguarde a PV se estabilizar. Meça a variação total na PV. Insira este valor no campo **ΔPV**.
    """)
    
    st.subheader("Passo 3: Medição dos Parâmetros L e T (Curva)")
    st.image("https://i.imgur.com/zV4Xn6i.png", caption="Curva de Reação e Parâmetros L e T (Fonte: Adaptação de literatura de controle)")
    st.markdown("""
    1.  **Tempo Morto (L):** Meça o tempo (em segundos) desde que o degrau foi aplicado até o **início da reação** da PV. Insira no campo **L**.
    2.  **Constante de Tempo (T):** Calcule a inclinação da tangente no ponto de inflexão. O valor de **T** é o tempo entre a intersecção da tangente com o valor inicial e a intersecção com o valor final da PV.
    """)

# --- Fim do Arquivo ---