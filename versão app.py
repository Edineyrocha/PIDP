import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem # Importação para Abas
from kivy.core.window import Window

kivy.require('1.9.0')

class SintoniaTab(BoxLayout):
    """Conteúdo da aba principal de Cálculo."""
    def __init__(self, **kwargs):
        super(SintoniaTab, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10

        # ScrollView para o conteúdo principal
        scroll = ScrollView(size_hint=(1, 1))
        content_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content_box.bind(minimum_height=content_box.setter('height'))
        
        # --- 1. ENTRADAS (MV e PV) ---
        input_grid = GridLayout(cols=2, spacing=5, size_hint_y=None, height=120, padding=5)
        input_grid.add_widget(Label(text="ΔMV (%):", halign='left', text_size=(150, None)))
        self.entry_mv = TextInput(input_type='number', multiline=False, text="10.0")
        input_grid.add_widget(self.entry_mv)

        input_grid.add_widget(Label(text="ΔPV (Unidade PV):", halign='left', text_size=(150, None)))
        self.entry_pv = TextInput(input_type='number', multiline=False, text="5.0")
        input_grid.add_widget(self.entry_pv)
        
        content_box.add_widget(Label(text="[b]1. Variações (Malha Aberta)[/b]", size_hint_y=None, height=30, markup=True))
        content_box.add_widget(input_grid)
        
        # --- 2. PARÂMETROS L e T ---
        lt_grid = GridLayout(cols=2, spacing=5, size_hint_y=None, height=120, padding=5)
        lt_grid.add_widget(Label(text="Tempo Morto L (s):", halign='left', text_size=(150, None)))
        self.entry_L = TextInput(input_type='number', multiline=False, text="5.0")
        lt_grid.add_widget(self.entry_L)

        lt_grid.add_widget(Label(text="Constante T (s):", halign='left', text_size=(150, None)))
        self.entry_T = TextInput(input_type='number', multiline=False, text="20.0")
        lt_grid.add_widget(self.entry_T)

        content_box.add_widget(Label(text="[b]2. Parâmetros do Modelo (L e T)[/b]", size_hint_y=None, height=30, markup=True))
        content_box.add_widget(lt_grid)
        
        # --- 3. Resultados ---
        content_box.add_widget(Label(text="[b]3. Resultados da Sintonia[/b]", size_hint_y=None, height=30, markup=True))
        
        # Resultados do Modelo
        self.label_K_result = Label(text="Ganho (K): -", size_hint_y=None, height=20, halign='left', text_size=(self.width, None))
        content_box.add_widget(self.label_K_result)

        # Cabeçalho da Tabela
        header = GridLayout(cols=4, size_hint_y=None, height=30)
        header.add_widget(Label(text="Controlador", bold=True))
        header.add_widget(Label(text="Kp", bold=True))
        header.add_widget(Label(text="Ti (s)", bold=True))
        header.add_widget(Label(text="Td (s)", bold=True))
        content_box.add_widget(header)

        # Linhas de Resultados
        self.result_lines = {}
        for i, ctrl in enumerate(["P", "PI", "PID"]):
            line = GridLayout(cols=4, size_hint_y=None, height=30)
            line.add_widget(Label(text=ctrl))
            self.result_lines[f'Kp_{ctrl}'] = Label(text="-")
            line.add_widget(self.result_lines[f'Kp_{ctrl}'])
            self.result_lines[f'Ti_{ctrl}'] = Label(text="-" if ctrl == "P" else "-")
            line.add_widget(self.result_lines[f'Ti_{ctrl}'])
            self.result_lines[f'Td_{ctrl}'] = Label(text="-" if ctrl in ("P", "PI") else "-")
            line.add_widget(self.result_lines[f'Td_{ctrl}'])
            content_box.add_widget(line)
        
        # Nota sobre conversão
        content_box.add_widget(Label(text="Nota: Verifique o manual do controlador para Ki (Kp/Ti) e Kd (Kp*Td).", 
                                     size_hint_y=None, height=40, font_size='10sp', color=(1, 0.5, 0, 1)))
        
        scroll.add_widget(content_box)
        self.add_widget(scroll)

        # Botão de Ação - A referência da função será passada pelo MainApp
        self.calc_button = Button(text="CALCULAR PID", size_hint=(1, 0.1))
        self.add_widget(self.calc_button)
    
    # Esta função agora reside na classe principal para fácil acesso
    # mas a lógica de update permanece aqui para simplificar

class AjudaTab(ScrollView):
    """Conteúdo da aba de Ajuda e Instruções."""
    def __init__(self, **kwargs):
        super(AjudaTab, self).__init__(**kwargs)
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        titulo_style = {'font_size': '16sp', 'bold': True, 'size_hint_y': None, 'height': 30, 'color': (0, 0.5, 1, 1)}
        instrucao_style = {'font_size': '12sp', 'halign': 'left', 'text_size': (Window.width * 0.9, None)}

        content.add_widget(Label(text="[b]PROCEDIMENTO ZIEGLER-NICHOLS (MALHA ABERTA)[/b]", markup=True, **titulo_style))
        content.add_widget(Label(text="Este método é baseado na Curva de Reação (resposta ao degrau).", **instrucao_style))

        content.add_widget(Label(text="[b]PASSO 1: Preparação do Teste[/b]", markup=True, **titulo_style))
        content.add_widget(Label(text="1.1. Coloque o controlador em modo [b]MANUAL[/b].\n1.2. Deixe a saída (MV) estabilizada em um ponto de operação estável.", markup=True, **instrucao_style))

        content.add_widget(Label(text="[b]PASSO 2: Execução do Degrau e Coleta de Dados[/b]", markup=True, **titulo_style))
        content.add_widget(Label(text="2.1. Aplique um degrau na MV (ex: mude de 40% para 50%). O valor da mudança é o [b]ΔMV[/b].\n2.2. Aguarde a PV estabilizar no novo valor.\n2.3. O valor total de mudança da PV é o [b]ΔPV[/b].", markup=True, **instrucao_style))
        
        content.add_widget(Label(text="[b]PASSO 3: Medição do Modelo[/b]", markup=True, **titulo_style))
        content.add_widget(Label(text="3.1. [b]Tempo Morto (L):[/b] Meça o tempo (em segundos) desde o degrau até o PV começar a reagir.\n3.2. [b]Constante de Tempo (T):[/b] Meça o tempo necessário para a PV alcançar 63.2% de sua mudança total, após o tempo L. (Ou use o método da tangente no ponto de inflexão).", markup=True, **instrucao_style))

        content.add_widget(Label(text="[b]PASSO 4: Inserção no Aplicativo[/b]", markup=True, **titulo_style))
        content.add_widget(Label(text="4.1. Insira os valores de ΔMV, ΔPV, L e T nos campos da aba 'Sintonia'.\n4.2. Clique em 'CALCULAR PID' para obter os parâmetros Kp, Ti e Td.", markup=True, **instrucao_style))

        self.add_widget(content)


class PIDApp(App):
    def build(self):
        # Container Principal com Abas
        self.tab_panel = TabbedPanel(do_default_tab=False)
        self.tab_panel.tab_pos = 'top_mid' # Abas no topo

        # --- Criação da Aba 1: Sintonia (Cálculos) ---
        self.sintonia_tab_content = SintoniaTab()
        self.sintonia_tab = TabbedPanelItem(text='Sintonia')
        self.sintonia_tab.add_widget(self.sintonia_tab_content)
        self.tab_panel.add_widget(self.sintonia_tab)

        # Conecta o botão de cálculo à função principal
        self.sintonia_tab_content.calc_button.bind(on_press=self.calcular_pid_zn_kivy)

        # --- Criação da Aba 2: Ajuda ---
        self.ajuda_tab_content = AjudaTab()
        self.ajuda_tab = TabbedPanelItem(text='Ajuda / Como Usar')
        self.ajuda_tab.add_widget(self.ajuda_tab_content)
        self.tab_panel.add_widget(self.ajuda_tab)

        return self.tab_panel
    
    def mostrar_erro(self, titulo, mensagem):
        """Exibe uma janela pop-up de erro."""
        popup = Popup(title=titulo, 
                      content=Label(text=mensagem), 
                      size_hint=(0.9, 0.4))
        popup.open()

    def calcular_pid_zn_kivy(self, instance):
        """Lógica de cálculo e atualização da interface Kivy."""
        try:
            # 1. Obter Valores de Entrada
            delta_mv = float(self.sintonia_tab_content.entry_mv.text)
            delta_pv = float(self.sintonia_tab_content.entry_pv.text)
            L = float(self.sintonia_tab_content.entry_L.text)
            T = float(self.sintonia_tab_content.entry_T.text)

            # Validação
            if delta_mv <= 0 or delta_pv <= 0 or L <= 0 or T <= 0:
                self.mostrar_erro("Erro de Entrada", "Todos os valores de ΔMV, ΔPV, L e T devem ser maiores que zero.")
                return

            # 2. Cálculo do Ganho do Processo (K)
            K = delta_pv / delta_mv

            # 3. Cálculo dos Parâmetros PID por ZN
            Kp_p = T / (K * L)
            Kp_pi = 0.9 * T / (K * L)
            Ti_pi = 3.33 * L
            Kp_pid = 1.2 * T / (K * L)
            Ti_pid = 2.0 * L
            Td_pid = 0.5 * L

            # 4. Atualizar Interface (Resultados)
            results = self.sintonia_tab_content.result_lines
            
            self.sintonia_tab_content.label_K_result.text = f"Ganho (K): {K:.4f}"

            results['Kp_P'].text = f"{Kp_p:.4f}"
            results['Kp_PI'].text = f"{Kp_pi:.4f}"
            results['Ti_PI'].text = f"{Ti_pi:.2f}"
            results['Kp_PID'].text = f"{Kp_pid:.4f}"
            results['Ti_PID'].text = f"{Ti_pid:.2f}"
            results['Td_PID'].text = f"{Td_pid:.2f}"
            
        except ValueError:
            self.mostrar_erro("Erro de Formato", "Por favor, insira apenas números válidos em todos os campos.")
        except Exception as e:
            self.mostrar_erro("Erro Inesperado", f"Ocorreu um erro no cálculo: {e}")


if __name__ == '__main__':
    # Define o tamanho inicial da janela para melhor visualização em desktop (opcional)
    try:
        Window.size = (400, 650)
    except Exception:
        # Ignora se não puder definir o tamanho (como em um celular real)
        pass 
        
    PIDApp().run()